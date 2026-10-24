const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),require('path').resolve('../codex training calendar')]}));
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>localStorage.setItem('wlta-sync',JSON.stringify({off:true})));
 const snapshots={};
 for(const route of ['today','calendar','progress','more','credits','day/1','day/3','day/4']){
  await page.goto('http://127.0.0.1:8010/?today=2026-10-20#/'+route);await page.waitForSelector('.wrap');await page.waitForTimeout(150);
  snapshots[route]=await page.locator('body').evaluate(b=>{const w=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);const out=[];while(w.nextNode()){const n=w.currentNode;if(!n.parentElement.closest('script,style,svg')){const s=n.textContent.replace(/\s+/g,' ').trim();if(s)out.push(s)}}return out});
  if(route==='today'){await page.screenshot({path:'tools/design-qa/before-desktop.png',fullPage:true});await page.setViewportSize({width:390,height:844});await page.screenshot({path:'tools/design-qa/before-phone.png',fullPage:true});await page.setViewportSize({width:1440,height:1000});}
 }
 fs.writeFileSync('tools/design-baseline/copy.json',JSON.stringify(snapshots,null,2));await browser.close();console.log('Captured original rendered wording for eight routes and baseline screenshots.');
})().catch(e=>{console.error(e);process.exit(1)});
