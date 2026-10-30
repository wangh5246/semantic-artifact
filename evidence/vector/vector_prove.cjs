'use strict';
const fs=require('fs'), path=require('path'), crypto=require('crypto');
const N=path.resolve(process.env.SNARKJS_NODE_MODULES || 'node_modules');
const snarkjs=require(path.join(N,'snarkjs'));
const P=21888242871839275222246405745257275088548364400416034343698204186575808495617n;
const run=path.resolve(process.argv[2]);
const mode=process.argv[3];
const log=path.join(run,'crypto-events.jsonl');
const event=(x)=>{fs.appendFileSync(log,JSON.stringify({...x,at:new Date().toISOString()})+'\n');console.log(JSON.stringify(x));};
async function timed(label,fn){const t=performance.now();const cpu=process.cpuUsage();const out=await fn();event({label,wall_s:(performance.now()-t)/1000,cpu_us:process.cpuUsage(cpu),max_rss_kib:process.resourceUsage().maxRSS});return out;}
function canonical(x){if(Array.isArray(x))return x.every(canonical);if(x&&typeof x==='object')return Object.values(x).every(canonical);return typeof x==='string'&&/^(0|[1-9][0-9]*)$/.test(x)&&BigInt(x)<P;}
(async()=>{
 if(mode==='zkey'){
  const r1cs=path.resolve(process.argv[4]),ptau=path.resolve(process.argv[5]),name=process.argv[6];
  const init=path.join(run,name+'.initial.zkey'),zkey=path.join(run,name+'.DEVELOPMENT.zkey');
  for(const f of [init,zkey])if(fs.existsSync(f))throw Error('REFUSED_OVERWRITE:'+f);
  await timed(name+' new zkey',()=>snarkjs.zKey.newZKey(r1cs,ptau,init));
  await timed(name+' contribution',()=>snarkjs.zKey.contribute(init,zkey,'G1 LOCAL DEVELOPMENT ONLY',crypto.randomBytes(64).toString('hex')));
  const ok=await timed(name+' zkey verify',()=>snarkjs.zKey.verifyFromR1cs(r1cs,ptau,zkey));
  if(!ok)throw Error('ZKEY_VERIFY_FAILED');
  const vkey=await snarkjs.zKey.exportVerificationKey(zkey);
  fs.writeFileSync(path.join(run,name+'.vkey.json'),JSON.stringify(vkey,null,2)+'\n',{flag:'wx'});
  event({label:name+' zkey result',ok});
 }else if(mode==='prove'){
  const name=process.argv[4],input=JSON.parse(fs.readFileSync(process.argv[5]));
  if(!canonical(input))throw Error('NONCANONICAL_INPUT_FIELD');
  const out=await timed(name+' prove',()=>snarkjs.groth16.fullProve(input,path.join(run,name+'_js',name+'.wasm'),path.join(run,name+'.DEVELOPMENT.zkey'),undefined,{sanityCheck:true},{singleThread:true}));
  const vk=JSON.parse(fs.readFileSync(path.join(run,name+'.vkey.json')));
  const verified=await timed(name+' verify',()=>snarkjs.groth16.verify(vk,out.publicSignals,out.proof));
  if(!verified)throw Error('PROOF_VERIFY_FAILED');
  const proof_json_bytes=Buffer.byteLength(JSON.stringify(out.proof));
  fs.writeFileSync(process.argv[6],JSON.stringify({...out,verified,proof_json_bytes,scope:'DEVELOPMENT_LOCAL_COMPONENT'},null,2)+'\n',{flag:'wx'});
  event({label:name+' proof',verified,proof_json_bytes,public_signals:out.publicSignals.length});
 }else if(mode==='verify'){
  const vk=JSON.parse(fs.readFileSync(process.argv[4])),o=JSON.parse(fs.readFileSync(process.argv[5]));
  const ok=await snarkjs.groth16.verify(vk,o.publicSignals,o.proof);
  console.log(JSON.stringify({verified:ok}));if(!ok)process.exitCode=1;
 }else throw Error('unknown mode');
 process.exit(0);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
