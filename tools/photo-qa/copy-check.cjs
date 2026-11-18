/* Every string in tools/design-baseline/copy.json must still render, under the baseline's conditions:
   no account, sync off, fresh storage. Start the harness in static mode first:
   QA_STATIC=1 QA_PORT=8032 node tools/photo-qa/harness.cjs   (PowerShell: $env:QA_STATIC=1; $env:QA_PORT=8032; node ...) */
const path=require('path');const ROOT=path.resolve(__dirname,'../..');
const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),path.resolve(ROOT,'../codex training calendar')]}));
const fs=require('fs');
const copy=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/design-baseline/copy.json'),'utf8'));
const text=()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),out=[];while(w.nextNode()){const n=w.currentNode;if(!n.parentElement.closest('script,style,svg')){const s=n.textContent.replace(/\s+/g,' ').trim();if(s)out.push(s)}}return out};
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
 await p.addInitScript(()=>localStorage.setItem('wlta-sync',JSON.stringify({off:true})));
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 let missingTotal=0;const added={};
 for(const route of Object.keys(copy)){
  await p.goto('http://127.0.0.1:8032/?today=2026-10-20#/'+route);await p.waitForSelector('#view .wrap');await p.waitForTimeout(200);
  const now=await p.evaluate(text),bag=new Map();for(const s of now)bag.set(s,(bag.get(s)||0)+1);
  const missing=[];for(const s of copy[route]){if(bag.get(s))bag.set(s,bag.get(s)-1);else missing.push(s);}
  missingTotal+=missing.length;if(missing.length)console.log('MISSING on',route,missing);
  added[route]=[...bag].filter(([,c])=>c>0).map(([s,c])=>c>1?`${s} ×${c}`:s);
 }
 console.log('new text by route:',JSON.stringify(added,null,1));
 console.log(missingTotal?`FAIL: ${missingTotal} original strings missing`:'PASS: every original string still renders on all 8 baseline routes');
 if(errors.length)console.log('JS errors:',errors);
 await b.close();})();
