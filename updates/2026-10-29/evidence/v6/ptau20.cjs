'use strict';
const path=require('path'), fs=require('fs'), crypto=require('crypto');
const N=/srv/waybill-workspace-v7/shtpc-g6-20261022/heatmap_split/verify/node_modules;
const snarkjs=require(path.join(N,'snarkjs'));
const ff=require(path.join(N,'ffjavascript'));
const run=process.argv[2], exp=Number(process.argv[3]);
const pot0=path.join(run,`DEVELOPMENT-pot${exp}-initial.ptau`);
const pot1=path.join(run,`DEVELOPMENT-pot${exp}-contributed.ptau`);
const pot2=path.join(run,`DEVELOPMENT-pot${exp}-phase2.ptau`);
const log=path.join(run,'ptau-events.jsonl');
const event=(x)=>fs.appendFileSync(log,JSON.stringify({...x,at:new Date().toISOString()})+'\n');
async function timed(label,fn){const t=performance.now();const cpu=process.cpuUsage();const out=await fn();event({label,wall_s:(performance.now()-t)/1000,cpu_us:process.cpuUsage(cpu),max_rss_kib:process.resourceUsage().maxRSS});return out;}
(async()=>{
  if (process.argv[4] !== 'resume') {
    for (const f of [pot0,pot1,pot2]) if (fs.existsSync(f)) throw Error('REFUSED_OVERWRITE:'+f);
    const curve=await ff.buildBn128();
    await timed('phase1 new accumulator',()=>snarkjs.powersOfTau.newAccumulator(curve,exp,pot0));
    await timed('phase1 contribution',()=>snarkjs.powersOfTau.contribute(pot0,pot1,'G1 LOCAL DEVELOPMENT ONLY',crypto.randomBytes(64).toString('hex')));
  }
  await timed('prepare phase2',()=>snarkjs.powersOfTau.preparePhase2(pot1,pot2));
  const ok=await timed('phase1 verify',()=>snarkjs.powersOfTau.verify(pot2));
  event({label:'phase1 result',ok});
  if(!ok) process.exitCode=1;
  process.exit(ok?0:1);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
