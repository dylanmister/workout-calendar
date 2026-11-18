/* Regression of the existing app (signed in, against tools/photo-qa/harness.cjs): reset, checklists and completion, set logs,
   notes, supplements, push/undo, calendar, exercise lightbox, units, backup export/import, cloud sync, layouts at five widths,
   reduced motion, and the before/after-arc screens. Run with the harness started: node tools/photo-qa/regression.cjs */
const path=require('path');const ROOT=path.resolve(__dirname,'../..');
const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),path.resolve(ROOT,'../codex training calendar')]}));
const fs=require('fs'),assert=require('assert/strict');
const B='http://127.0.0.1:8031',T='2026-10-20';
const step=(m)=>console.log('  ✓',m);
async function ready(page){await page.waitForSelector('#view .wrap');await page.waitForTimeout(250);}
(async()=>{
 const browser=await chromium.launch();
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await ctx.newPage();
 const errors=[],bad=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});
 await page.goto(`${B}/?today=${T}`);
 if(await page.locator('#account-password').count()){await page.fill('#account-password','qa-test-password');await page.click('#account-form button');}
 await ready(page);
 // start from a clean shared state for this test account, using the app's own reset
 await page.goto(`${B}/?today=${T}#/more`);await ready(page);
 await page.locator('[data-action=reset]').click();await page.locator('[data-m=yes]').click();await page.waitForTimeout(400);
 assert.deepEqual(await page.evaluate(()=>[Object.keys(WLTA.state.checks).length,Object.keys(WLTA.state.notes).length,WLTA.state.shifts.length]),[0,0,0]);
 step('reset shared progress clears checks, notes and shifts');

 // 2. checklist, progress bar, completion celebration, mastered stamp (Day 2 = Water)
 await page.goto(`${B}/?today=${T}#/day/2`);await ready(page);
 const checks=page.locator('[data-action="check"]'),n=await checks.count();
 await checks.first().click();assert.match(await page.locator('#day-progress').innerText(),new RegExp(`1 / ${n}`));
 for(let i=1;i<n;i++)await checks.nth(i).click();
 await page.locator('#celebrate:not([hidden])').waitFor();assert.match(await page.locator('#cel-title').innerText(),/You have mastered Water today/);
 await page.locator('[data-action="close-celebrate"]').click();
 assert.match(await page.locator('#mastered').innerText(),/You have mastered Water today/i);
 await checks.first().click();assert.equal(await page.locator('#mastered').innerText(),'','unchecking clears mastery');await checks.first().click();await page.locator('#celebrate:not([hidden])').waitFor();await page.locator('[data-action="close-celebrate"]').click();
 step(`checklist: ${n} items, progress bar, celebration, mastered stamp, uncheck clears it`);

 // 3. set logs + notes + supplements persist across reloads
 await page.goto(`${B}/?today=${T}#/day/1`);await ready(page);
 await page.locator('[data-action="log"]').first().click();
 await page.locator('.log input[data-f="w"]').first().fill('135');await page.locator('.log input[data-f="r"]').first().fill('8');
 await page.locator('textarea[data-action=notes]').fill('Regression: session note.');
 await page.locator('[data-action=supps]').click();assert.equal(await page.locator('[data-action=supps]').getAttribute('aria-pressed'),'true');
 assert.match(await page.locator('.log-summary').first().innerText(),/Logged: 135×8 lb/);
 await page.waitForTimeout(600);await page.reload();await ready(page);
 await page.locator('[data-action="log"]').first().click();
 assert.equal(await page.locator('.log input[data-f="w"]').first().inputValue(),'135');
 assert.equal(await page.locator('textarea[data-action=notes]').inputValue(),'Regression: session note.');
 assert.equal(await page.locator('[data-action=supps]').getAttribute('aria-pressed'),'true');
 assert.equal(await page.locator('.supp-state').innerText(),'YES');
 step('set log (135×8), session notes and supplement check survive a reload');
 // "copy last time" on a later day of the same exercise uses the log
 // 4. push back a day and undo (Day 3: today's Day 2 is already mastered, and mastered days can't be pushed)
 await page.goto(`${B}/?today=2026-10-21#/today`);await ready(page);
 const before=await page.evaluate(()=>WLTA.endDate());
 await page.locator('[data-action="push"]').click();await page.waitForTimeout(300);
 assert.match(await page.locator('#view').innerText(),/Rest stop/);assert.notEqual(await page.evaluate(()=>WLTA.endDate()),before);
 assert.equal(await page.locator('.photo-card').count(),1,'rest stop also has the photo section');
 await page.locator('#view [data-action="undo"]').first().click();await page.waitForTimeout(300);
 assert.equal(await page.evaluate(()=>WLTA.endDate()),before);
 step('push back a day → rest stop (with supplements + photo section), undo restores the end date');

 // 5. calendar navigation and month switching
 await page.goto(`${B}/?today=${T}#/calendar`);await ready(page);
 await page.locator('a.cal-cell[href="#/day/3"]').click();await page.waitForSelector('#day-title');
 assert.equal(await page.locator('body').getAttribute('data-el'),'fire');
 await page.goto(`${B}/?today=${T}#/calendar/2026-11`);await ready(page);assert.match(await page.locator('.cal-head h1').innerText(),/November 2026/);
 await page.locator('.cal-head a[aria-label="Previous month"]').click();await ready(page);assert.match(await page.locator('.cal-head h1').innerText(),/October 2026/);
 step('calendar: day cells open workouts, month arrows work');

 // 6. exercise image lightbox with start/finish frames and keyboard containment
 await page.goto(`${B}/?today=${T}#/day/1`);await ready(page);
 await page.locator('[data-action="img"]').first().click();await page.locator('#lightbox:not([hidden])').waitFor();
 await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>!!document.activeElement.closest('#lightbox')),true,'focus stays in dialog');
 if(await page.locator('[data-action="frame"][data-f="1"]').count()){await page.locator('[data-action="frame"][data-f="1"]').click();assert.equal(await page.locator('.f1').evaluate(e=>!e.classList.contains('hide')),true);}
 await page.keyboard.press('Escape');assert.equal(await page.locator('#lightbox').isHidden(),true);
 step('exercise lightbox: opens, frames switch, focus contained, Escape closes');

 // 7. units, export, import
 await page.goto(`${B}/?today=${T}#/more`);await ready(page);
 await page.locator('[data-action="unit"][data-u="kg"]').click();assert.equal(await page.locator('[data-u="kg"]').getAttribute('aria-pressed'),'true');
 await page.locator('[data-action="unit"][data-u="lb"]').click();
 const dl=page.waitForEvent('download');await page.locator('[data-action="export"]').click();const file=await dl;const saved=path.join(ROOT,'tools/.cache/photo-qa/regression-backup.json');fs.mkdirSync(path.dirname(saved),{recursive:true});await file.saveAs(saved);
 const backup=JSON.parse(fs.readFileSync(saved,'utf8'));assert.equal(backup.app,'white-lotus-training-arc');assert.equal(backup.data.notes['1'],'Regression: session note.');
 await page.locator('#import-file').setInputFiles(saved);await page.locator('[data-m="yes"]').click();await page.waitForTimeout(400);
 assert.equal(await page.evaluate(()=>WLTA.state.notes['1']),'Regression: session note.');
 step('units toggle; export backup contains the data; import restores it');

 // 8. cloud sync: what this device did is on the server
 await page.evaluate(()=>WLTA.syncNow());await page.waitForFunction(()=>WLTA.sync.status==='synced'&&!WLTA.sync.dirty,null,{timeout:20000});
 const cloud=JSON.parse((await page.evaluate(async()=>(await (await fetch('/api/progress')).json()))).state);
 assert.equal(cloud.notes['1'],'Regression: session note.');assert.ok(cloud.supps['2026-10-19'],'supplements synced');assert.ok(cloud.done['2'],'mastery synced');
 step('cloud sync: notes, supplements and completed days reach the server');

 // 9. layout: no sideways scrolling at any width on any route, incl. new ones and open dialogs
 const routes=['today','calendar','progress','more','credits','day/3','day/4','photos','photos/calendar','photos/compare','date/2026-10-01','date/2027-05-01'];
 for(const w of [320,390,768,1024,1440]){
  await page.setViewportSize({width:w,height:w<700?740:900});
  for(const r of routes){await page.goto(`${B}/?today=${T}#/${r}`);await ready(page);
   const over=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);assert.ok(over<=0,`${r} overflows by ${over}px at ${w}`);}
 }
 step('no horizontal overflow on 12 routes at 320/390/768/1024/1440');

 // 10. reduced motion: content visible immediately, no transitions
 await page.emulateMedia({reducedMotion:'reduce'});await page.goto(`${B}/?today=${T}#/today`);await ready(page);
 assert.equal(await page.locator('.banner').evaluate(e=>getComputedStyle(e).opacity),'1');
 assert.equal(await page.locator('.banner').evaluate(e=>getComputedStyle(e).transitionDuration),'0s');
 step('reduced motion respected');

 // 11. before the arc and after it
 for(const [d,re] of [['2026-10-10',/The arc approaches/],['2027-06-01',/The arc is complete/]]){await page.goto(`${B}/?today=${d}#/today`);await ready(page);assert.match(await page.locator('#view').innerText(),re);}
 step('before-start and after-end screens');

 assert.deepEqual(errors,[],'no JS errors');assert.deepEqual(bad,[],'no HTTP errors');
 await browser.close();console.log('PASS: regression');
})().catch(e=>{console.error('FAIL',e);process.exit(1)});
