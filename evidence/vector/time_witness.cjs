'use strict';
const fs=require('fs'),path=require('path');
const M=path.resolve(process.env.SNARKJS_NODE_MODULES || 'node_modules');
const snarkjs=require(path.join(M,'snarkjs'));
(async()=>{
 const wasm=path.resolve(process.argv[2]),input=JSON.parse(fs.readFileSync(process.argv[3])),label=process.argv[4];
 const t=performance.now(),cpu=process.cpuUsage();
 const w={type:'mem'};
 await snarkjs.wtns.calculate(input,wasm,w,{sanityCheck:true});
 console.log(JSON.stringify({label,wall_s:(performance.now()-t)/1000,cpu_us:process.cpuUsage(cpu),max_rss_kib:process.resourceUsage().maxRSS}));
 process.exit(0);
})().catch(e=>{console.error(e.stack||e);process.exitCode=1;});
