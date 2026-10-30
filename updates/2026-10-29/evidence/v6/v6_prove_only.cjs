'use strict';
const fs=require('fs'),path=require('path');
const M='/srv/waybill-workspace-v7/shtpc-g6-20261022/heatmap_split/verify/node_modules';
const snarkjs=require(path.join(M,'snarkjs'));
const run=path.resolve(process.argv[2]),name=process.argv[3],input=JSON.parse(fs.readFileSync(process.argv[4])),out=path.resolve(process.argv[5]);
const log=path.join(run,'crypto-events.jsonl');
const event=(x)=>fs.appendFileSync(log,JSON.stringify({...x,at:new Date().toISOString()})+'\n');
async function timed(label,fn){const t=performance.now();const cpu=process.cpuUsage();const r=await fn();event({label,wall_s:(performance.now()-t)/1000,cpu_us:process.cpuUsage(cpu),max_rss_kib:process.resourceUsage().maxRSS});return r;}
(async()=>{
 const zkey=path.join(run,name+'.DEVELOPMENT.zkey');
 const vkPath=path.join(run,name+'.vkey.json');
 let vk;
 if(fs.existsSync(vkPath)) vk=JSON.parse(fs.readFileSync(vkPath));
 else { vk=await timed(name+' export vkey',()=>snarkjs.zKey.exportVerificationKey(zkey)); fs.writeFileSync(vkPath,JSON.stringify(vk,null,2)+'\n',{flag:'wx'}); }
 const p=await timed(name+' prove',()=>snarkjs.groth16.fullProve(input,path.join(run,name+'_js',name+'.wasm'),zkey,undefined,{sanityCheck:true},{singleThread:true}));
 const verified=await timed(name+' verify',()=>snarkjs.groth16.verify(vk,p.publicSignals,p.proof));
 fs.writeFileSync(out,JSON.stringify({...p,verified,proof_json_bytes:Buffer.byteLength(JSON.stringify(p.proof)),scope:'DEVELOPMENT_LOCAL_COMPONENT'},null,2)+'\n',{flag:'wx'});
 event({label:name+' proof',verified,proof_json_bytes:Buffer.byteLength(JSON.stringify(p.proof)),public_signals:p.publicSignals.length});
 process.exit(verified?0:1);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
