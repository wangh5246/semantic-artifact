#!/usr/bin/env python3
"""Materialize a complete scoped R1CS and witness with bounded working memory.

Every Circom kernel constraint is emitted after explicit wire substitution.
There is no extrapolated row count and no global post-link minimization.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import shutil
import secrets
import struct
import subprocess
import time
import numpy as np

HERE=Path(__file__).resolve().parent
P=21888242871839275222246405745257275088548364400416034343698204186575808495617
Q=340282366920938462946865773367900766209
FIELD=P.to_bytes(32,'little')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024**2),b''):h.update(chunk)
    return h.hexdigest()

def sec(raw):
    assert raw[:4] in (b'r1cs',b'wtns')
    n=struct.unpack_from('<I',raw,8)[0];pos=12;out={}
    for _ in range(n):
        t,size=struct.unpack_from('<IQ',raw,pos);pos+=12
        out[t]=raw[pos:pos+size];pos+=size
    return out

class Server:
    def __init__(self,log):
        self.log=log.open('xb')
        self.p=subprocess.Popen(['node','--max-old-space-size=1536',str(HERE/'witness_server.cjs')],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1)
    def call(self,name,inputs,fail_ok=False):
        self.p.stdin.write(json.dumps({'kernel':name,'input':inputs},separators=(',',':'))+'\n');self.p.stdin.flush()
        line=self.p.stdout.readline()
        if not line:raise RuntimeError('WITNESS_SERVER_EXITED:'+str(self.p.poll()))
        row=json.loads(line)
        if not row['ok'] and not fail_ok:raise RuntimeError(row['error'])
        return row
    def close(self):
        self.p.stdin.close();self.p.wait(timeout=20);self.log.close()

class Kernel:
    def __init__(self,name):
        self.name=name;root=HERE/'kernels'/name;raw=(root/(name+'.r1cs')).read_bytes();s=sec(raw)
        header=s[1];assert header[:4]==struct.pack('<I',32) and header[4:36]==FIELD
        self.wires,self.nout,self.npub,self.nprivate=struct.unpack_from('<IIII',header,36)
        self.constraints=struct.unpack_from('<I',header,60)[0]
        self.body=bytearray(s[2]);positions=[];pos=0
        for _ in range(self.constraints):
            for _ in range(3):
                n=struct.unpack_from('<I',self.body,pos)[0];pos+=4
                for _ in range(n):positions.append(pos//4);pos+=36
        assert pos==len(self.body)
        self.positions=np.array(positions,dtype=np.int64)
        self.words=np.frombuffer(self.body,dtype='<u4')
        self.original=self.words[self.positions].copy()
        self.inputs={}
        for line in (root/(name+'.sym')).read_text().splitlines():
            _,w,_,label=line.split(',',3)
            if int(w)>0:self.inputs[label]=int(w)
        self.sha256=hashlib.sha256(raw).hexdigest()

class Circuit:
    def __init__(self,out,public,private_count):
        self.root=out;out.mkdir(exist_ok=False)
        self.r=(out/'binding.r1cs').open('xb',buffering=8*1024**2)
        self.w=(out/'binding.wtns').open('xb',buffering=8*1024**2)
        self.r.write(b'r1cs'+struct.pack('<II',1,3)+struct.pack('<IQ',1,64)+b'\0'*64+struct.pack('<IQ',2,0))
        self.w.write(b'wtns'+struct.pack('<II',2,2)+struct.pack('<IQ',1,40)+struct.pack('<I',32)+FIELD+struct.pack('<I',0)+struct.pack('<IQ',2,0))
        self.next=0;self.constraints=0;self.constraint_bytes=0;self.rows=[];self.private_count=private_count
        for v in [1,*public]:self.value(v)
    def value(self,n):
        assert 0<=n<P
        i=self.next;self.next+=1;self.w.write(int(n).to_bytes(32,'little'));return i
    def manual(self,a,b,c):
        for terms in [a,b,c]:
            merged={}
            for wire,coef in terms:merged[wire]=(merged.get(wire,0)+coef)%P
            terms=[(i,x) for i,x in sorted(merged.items()) if x]
            self.r.write(struct.pack('<I',len(terms)));self.constraint_bytes+=4
            for wire,coef in terms:
                self.r.write(struct.pack('<I',wire)+int(coef%P).to_bytes(32,'little'));self.constraint_bytes+=36
        self.constraints+=1
    def fixed(self,n):
        if n==1:return 0
        i=self.value(n);self.manual([(i,1)],[(0,1)],[(0,n)]);return i
    def equal(self,a,b):self.manual([(a,1),(b,-1)],[(0,1)],[])
    def instance(self,kernel,aliases,witness,tag):
        # Every remaining local wire receives exactly one fresh global wire.
        mapping=np.zeros(kernel.wires,dtype='<u4')
        mask=np.ones(kernel.wires,dtype=np.bool_);mask[0]=False
        for local,global_wire in aliases.items():
            assert 0<local<kernel.wires and 0<=global_wire<self.next
            mapping[local]=global_wire;mask[local]=False
        fresh=np.flatnonzero(mask);start=self.next
        mapping[fresh]=np.arange(start,start+len(fresh),dtype='<u4');self.next+=len(fresh)
        assert self.next<2**32
        if kernel.name=='keccak12':
            bits=np.unpackbits(np.frombuffer(base64.b64decode(witness['bits']),dtype=np.uint8),bitorder='little')[:kernel.wires]
            values=np.zeros((len(fresh),32),dtype=np.uint8);values[:,0]=bits[fresh]
            self.w.write(values.tobytes())
        else:
            values=np.frombuffer(base64.b64decode(witness['raw']),dtype=np.uint8).reshape((-1,32))
            assert len(values)==kernel.wires
            self.w.write(values[fresh].tobytes())
        # These are the complete actual constraint bytes, with every reference
        # linked to its predecessor. All original field coefficients survive.
        kernel.words[kernel.positions]=mapping[kernel.original]
        body=kernel.body
        # Standard r1cs readers use a map indexed by wire, so duplicate aliases
        # must be summed before serialization (especially constants 0/1 in
        # the initial sponge state and padding in the final commitment fold).
        assigned=list(aliases.values())
        if 0 in assigned or len(set(assigned))!=len(assigned):
            normalized=bytearray();pos=0
            for _ in range(kernel.constraints*3):
                count=struct.unpack_from('<I',body,pos)[0];pos+=4;terms={}
                for _ in range(count):
                    i=struct.unpack_from('<I',body,pos)[0];coef=int.from_bytes(body[pos+4:pos+36],'little');pos+=36
                    terms[i]=(terms.get(i,0)+coef)%P
                terms={i:c for i,c in terms.items() if c}
                normalized.extend(struct.pack('<I',len(terms)))
                for i,c in sorted(terms.items()):normalized.extend(struct.pack('<I',i)+c.to_bytes(32,'little'))
            assert pos==len(body);body=normalized
        self.r.write(body);self.constraint_bytes+=len(body);self.constraints+=kernel.constraints
        self.rows.append({'kernel':kernel.name,'tag':tag,'new_wire_start':start,
                          'new_wire_count':len(fresh),'constraints_emitted':kernel.constraints})
        return mapping[1:1+kernel.nout]
    def finish(self):
        self.r.write(struct.pack('<IQ',3,8*self.next))
        for start in range(0,self.next,1_000_000):
            self.r.write(np.arange(start,min(self.next,start+1_000_000),dtype='<u8').tobytes())
        head=struct.pack('<I',32)+FIELD+struct.pack('<IIIIQI',self.next,2,2,self.private_count,self.next,self.constraints)
        self.r.seek(24);self.r.write(head);self.r.seek(92);self.r.write(struct.pack('<Q',self.constraint_bytes))
        self.w.seek(60);self.w.write(struct.pack('<I',self.next));self.w.seek(68);self.w.write(struct.pack('<Q',32*self.next))
        for f in [self.r,self.w]:f.flush();os.fsync(f.fileno());f.close()
        (self.root/'instances.json').write_text(json.dumps(self.rows,indent=2)+'\n')
        return {'wires':self.next,'constraints':self.constraints,'instances':len(self.rows),
                'r1cs_bytes':(self.root/'binding.r1cs').stat().st_size,
                'wtns_bytes':(self.root/'binding.wtns').stat().st_size,
                'r1cs_sha256':sha(self.root/'binding.r1cs'),'wtns_sha256':sha(self.root/'binding.wtns')}

def hashes(server,fixture,context,blind):
    seed=int.from_bytes(bytes.fromhex(fixture['helper_seed_hex']),'little')
    first=server.call('poseidon4',{'inputs':list(map(str,[seed,blind[0],*context]))})['out']
    acc=server.call('poseidon4',{'inputs':list(map(str,[fixture['bins'],blind[1],*context]))})['out']
    for start in range(0,fixture['bins'],15):
        values=fixture['leader'][start:start+15];values=values+['0']*(15-len(values))
        acc=server.call('poseidon16',{'inputs':[acc,*values]})['out']
    return int(first),int(acc)

def run(fixture,out):
    began=time.monotonic();n=fixture['bins'];seed=bytes.fromhex(fixture['helper_seed_hex'])
    context=[0x73687470632d7072696f,0x20261024]
    blind=[secrets.randbelow(P),secrets.randbelow(P)]
    kernels={x:Kernel(x) for x in ['keccak12','share_row','poseidon4','poseidon16']}
    witness_log=out.parent/(out.name+'-witness-server.log');server=Server(witness_log)
    circuit=None
    try:
        commitments=hashes(server,fixture,context,blind)
        circuit=Circuit(out,[*commitments,*context],n+132)
        private=out/'commitment-openings.private.json'
        private.write_text(json.dumps({'blinds':list(map(str,blind)),'fixture_kind':'fresh synthetic'},indent=2)+'\n');private.chmod(0o600)
        primary=circuit.value(fixture['primary']);seed_scalar=circuit.value(int.from_bytes(seed,'little'))
        seed_bits=[circuit.value((x>>i)&1) for x in seed for i in range(8)]
        blinds=[circuit.value(x) for x in blind];leaders=[circuit.value(int(x)) for x in fixture['leader']]
        zero=circuit.fixed(0)
        circuit.manual([(seed_scalar,1),*((w,-(1<<i)) for i,w in enumerate(seed_bits))],[(0,1)],[])
        msg=bytes([8,8,0,0,0,0,3,0,1])+seed+bytes([1])
        assert len(msg)==26
        block=bytearray(200);block[:26]=msg;block[26]=1;block[167]=128
        state=[(b>>i)&1 for b in block for i in range(8)]
        links=[(0 if value else zero) for value in state]
        links[9*8:25*8]=seed_bits
        stream_links=[];stream_bits=[];perms=(16*n+167)//168
        k=kernels['keccak12']
        for index in range(perms):
            result=server.call('keccak12',{'in':state})
            aliases={k.inputs[f'main.in[{i}]']:int(w) for i,w in enumerate(links)}
            output=circuit.instance(k,aliases,result,'squeeze-'+str(index))
            local=np.unpackbits(np.frombuffer(base64.b64decode(result['bits']),dtype=np.uint8),bitorder='little')[:k.wires]
            state=local[1:1601].tolist();links=output.tolist()
            stream_links.extend(links[:1344]);stream_bits.extend(state[:1344])
            if index%64==0 or index==perms-1:
                print(json.dumps({'phase':'sponge','bins':n,'completed':index+1,'total':perms,'constraints_written':circuit.constraints,'elapsed_s':time.monotonic()-began}),flush=True)
        native_fields=[]
        for j in range(n):native_fields.append(sum(stream_bits[128*j+i]<<i for i in range(128)))
        assert all(x<Q for x in native_fields),'OUTSIDE_REGISTERED_NO_REJECTION_BRANCH'
        assert all((int(a)+b)%Q==int(j==fixture['primary']) for j,(a,b) in enumerate(zip(fixture['leader'],native_fields))),'NATIVE_SHARD_BYTES_DO_NOT_MATCH_CIRCUIT_EXPANSION'
        selected=[];row=kernels['share_row']
        for j in range(n):
            bits=stream_bits[j*128:(j+1)*128];leader=int(fixture['leader'][j]);carry=(leader+native_fields[j]-int(j==fixture['primary']))//Q
            result=server.call('share_row',{'helper_bits':bits,'leader':str(leader),'primary':fixture['primary'],'position':j,'carry':carry})
            aliases={row.inputs[f'main.helper_bits[{i}]']:int(stream_links[128*j+i]) for i in range(128)}
            aliases.update({row.inputs['main.leader']:leaders[j],row.inputs['main.primary']:primary,
                            row.inputs['main.position']:circuit.fixed(j)})
            # O2 substitutes carry into its Boolean constraint. There is then
            # no carry witness wire to alias; the native integer relation is
            # still present in the retained rank-one constraints.
            if 'main.carry' in row.inputs:aliases[row.inputs['main.carry']]=circuit.value(carry)
            selected.extend(circuit.instance(row,aliases,result,'coordinate-'+str(j)).tolist())
        circuit.manual([*((i,1) for i in selected),(0,-1)],[(0,1)],[])
        h=kernels['poseidon4']
        for tag,values,ids,public in [('seed',[int.from_bytes(seed,'little'),blind[0],*context],[seed_scalar,blinds[0],3,4],1),
                                      ('vector-initial',[n,blind[1],*context],[circuit.fixed(n),blinds[1],3,4],None)]:
            result=server.call('poseidon4',{'inputs':list(map(str,values))})
            aliases={h.inputs[f'main.inputs[{i}]']:v for i,v in enumerate(ids)}
            produced=int(circuit.instance(h,aliases,result,tag)[0])
            if public:circuit.equal(produced,public)
            else:acc=produced;acc_value=result['out']
        fold=kernels['poseidon16']
        for start in range(0,n,15):
            values=fixture['leader'][start:start+15];ids=leaders[start:start+15]
            while len(values)<15:values.append('0');ids.append(zero)
            result=server.call('poseidon16',{'inputs':[acc_value,*values]})
            aliases={fold.inputs[f'main.inputs[{i}]']:v for i,v in enumerate([acc,*ids])}
            acc=int(circuit.instance(fold,aliases,result,'vector-fold-'+str(start))[0]);acc_value=result['out']
        circuit.equal(acc,2)
        result=circuit.finish()
        result.update(schema='shtpc.seeded-additive-share-binding.actual-r1cs/1',bins=n,primary=fixture['primary'],
                      relation='SeededShareBinding/no-rejection/1',elapsed_s=time.monotonic()-began,
                      actual_full_r1cs_materialized=True,global_cross_instance_optimization=False,
                      native_shard_equations_checked=n,keccak_instances=perms,
                      public_commitments=list(map(str,commitments)),public_context=context,
                      kernel_sha256={name:k.sha256 for name,k in kernels.items()},
                      main_wire_ids={'seed_digest':1,'leader_digest':2,'context_hi':3,'context_lo':4,'primary':primary,'seed_scalar':seed_scalar,'leader_first':leaders[0]})
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        return result
    except BaseException as e:
        if circuit:
            for f in [circuit.r,circuit.w]:
                if not f.closed:f.flush();f.close()
        out.mkdir(exist_ok=True)
        (out/'failure.json').write_text(json.dumps({'type':type(e).__name__,'error':str(e),'bins':n,'elapsed_s':time.monotonic()-began,'preserved_partial_outputs':True},indent=2)+'\n')
        raise
    finally:server.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--bins',type=int,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();assert args.bins in [8,101,1001,10001]
    if shutil.disk_usage(args.output.parent).free<40*1024**3:raise RuntimeError('LOCAL_DISK_RESERVE_REQUIRED')
    fixtures=[json.loads(s) for s in (HERE/'native-fixtures/raw.jsonl').read_text().splitlines()]
    fixture=next(x for x in fixtures if x['bins']==args.bins)
    print(json.dumps(run(fixture,args.output.resolve())),flush=True)

if __name__=='__main__':main()
