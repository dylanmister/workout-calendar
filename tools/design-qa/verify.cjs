const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),require('path').resolve('../codex training calendar')]}));
 const fs=require('fs'),assert=require('assert/strict');
const base='http://127.0.0.1:8010/?today=2026-10-20';
const copy=JSON.parse(fs.readFileSync('tools/design-baseline/copy.json','utf8'));
const text=()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),out=[];while(w.nextNode()){const n=w.currentNode;if(!n.parentElement.closest('script,style,svg')){const s=n.textContent.replace(/\s+/g,' ').trim();if(s)out.push(s)}}return out};
async function ready(page){await page.waitForSelector('.wrap');await page.waitForTimeout(180)}
async function photo(page,name){const height=await page.evaluate(()=>document.body.scrollHeight);for(let y=0;y<height;y+=650){await page.evaluate(y=>scrollTo(0,y),y);await page.waitForTimeout(80)}await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(650);await page.screenshot({path:`tools/design-qa/${name}.png`,fullPage:true});}
(async()=>{
 const integrity=JSON.parse(fs.readFileSync('tools/design-baseline/integrity.json','utf8'));
 for(const [file,hash] of Object.entries(integrity))assert.equal(require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),hash,`${file} unchanged`);
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.addInitScript(()=>localStorage.setItem('wlta-sync',JSON.stringify({off:true})));
 const errors=[],bad=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&!r.url().includes(':3210'))bad.push(r.url())});
 for(const route of Object.keys(copy)){
  await page.goto(base+'#/'+route);await ready(page);assert.deepEqual(await page.evaluate(text),copy[route],`Original copy on ${route}`);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${route} desktop overflow`);
  if(['today','calendar','progress','more','day/1','day/3','day/4'].includes(route))await photo(page,'after-desktop-'+route.replace('/','-'));
 }
 console.log('PASS: original app.js byte-for-byte unchanged; all rendered text preserved on eight routes.');
 for(const width of [390,768,320]){
  await page.setViewportSize({width,height:844});
  for(const route of ['today','calendar','progress','more','credits','day/3']){
   await page.goto(base+'#/'+route);await ready(page);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${route} overflow at ${width}`);
   if(route==='progress')assert.equal(await page.locator('.phase .t').evaluateAll(items=>items.every(e=>e.scrollWidth<=e.clientWidth)),true,`phase label clipping at ${width}`);
   if(width===390&&['today','calendar','progress','more'].includes(route))await photo(page,'after-phone-'+route);
  }
 }
 await page.setViewportSize({width:390,height:844});await page.goto(base+'#/today');await ready(page);
 await page.locator('[data-action="img"]').first().click();await page.locator('#lightbox:not([hidden])').waitFor();
  await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.closest('#lightbox')!==null),true,'dialog keyboard containment');
 if(await page.locator('[data-action="frame"][data-f="1"]').count()){await page.locator('[data-action="frame"][data-f="1"]').click();assert.equal(await page.locator('.f1').evaluate(e=>!e.classList.contains('hide')),true)}
 await page.keyboard.press('Escape');assert.equal(await page.locator('#lightbox').getAttribute('hidden')!==null,true);
 await page.locator('[data-action="log"]').first().click();await page.locator('.log input[data-f="w"]').first().fill('135');await page.locator('.log input[data-f="r"]').first().fill('8');await page.locator('textarea').fill('Design QA: session note.');await page.waitForTimeout(400);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'open log phone overflow');
 await page.reload();await ready(page);await page.locator('[data-action="log"]').first().click();assert.equal(await page.locator('.log input[data-f="w"]').first().inputValue(),'135');assert.equal(await page.locator('textarea').inputValue(),'Design QA: session note.');
 await page.locator('[data-action="push"]').click();await page.waitForTimeout(250);assert.match(await page.locator('#view').innerText(),/shifted|rest/i);
 await page.locator('[data-action="undo"]').first().click();await page.waitForTimeout(200);
 await page.goto(base+'#/day/2');await ready(page);
 const check=page.locator('[data-action="check"]');for(let i=0;i<await check.count();i++){await check.nth(i).click();}
 await page.locator('#celebrate:not([hidden])').waitFor();await page.locator('[data-action="close-celebrate"]').click();assert.match(await page.locator('#mastered').innerText(),/You have mastered Water today/);
 await page.goto(base+'#/calendar');await ready(page);await page.locator('a.cal-cell[href="#/day/3"]').click();await page.waitForSelector('#day-title');assert.equal(await page.locator('body').getAttribute('data-el'),'fire');
 await page.goto(base+'#/more');await ready(page);await page.locator('[data-action="unit"][data-u="kg"]').click();assert.equal(await page.locator('[data-u="kg"]').getAttribute('aria-pressed'),'true');
 const dl=page.waitForEvent('download');await page.locator('[data-action="export"]').click();const file=await dl;await file.saveAs('tools/design-qa/test-backup.json');const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('wlta-v1')));
 await page.locator('#import-file').setInputFiles('tools/design-qa/test-backup.json');await page.locator('[data-m="yes"]').click();await page.waitForTimeout(400);assert.deepEqual(await page.evaluate(()=>JSON.parse(localStorage.getItem('wlta-v1'))),saved);
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto(base+'#/today');await ready(page);assert.equal(await page.locator('.banner').evaluate(e=>getComputedStyle(e).opacity),'1');assert.equal(await page.locator('.banner').evaluate(e=>getComputedStyle(e).transitionDuration),'0s');
 assert.deepEqual(errors,[],'JavaScript errors');assert.deepEqual(bad,[],'HTTP errors');
 await browser.close();console.log('PASS: 320/390/768/1440 layouts; all routes; image lightbox/frames; logs/notes persistence; shift/undo; completion; units; export/import; reduced motion; no JS or HTTP errors.');
})().catch(e=>{console.error(e);process.exit(1)});
