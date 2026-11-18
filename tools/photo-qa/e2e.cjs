/* End-to-end test of the daily progress photo feature against tools/photo-qa/harness.cjs (Convex DEV deployment):
   placement, upload, cloud persistence, EXIF rotation, camera capture + self-timer (Chromium's fake camera), camera release,
   replace, large/PNG/invalid files, gallery order, viewer, calendar, compare, remove, a second device, and a denied camera.
   Run: python tools/photo-qa/make-images.py; node tools/photo-qa/harness.cjs; node tools/photo-qa/e2e.cjs */
const path=require('path');const ROOT=path.resolve(__dirname,'../..');
const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),path.resolve(ROOT,'../codex training calendar')]}));
const assert=require('assert/strict'),IMG=path.join(ROOT,'tools/.cache/photo-qa/img')+path.sep;
const B='http://127.0.0.1:8031',TODAY='2026-11-18';
const step=(m)=>console.log('  ✓',m);
async function signIn(page){await page.goto(`${B}/?today=${TODAY}`);if(await page.locator('#account-password').count()){await page.fill('#account-password','qa-test-password');await page.click('#account-form button');}await page.waitForSelector('#view .wrap',{timeout:20000});}
const index=(page)=>page.evaluate(async()=>(await (await fetch('/api/photos')).json()).photos);
async function waitToast(page,re){await page.waitForFunction((src)=>new RegExp(src).test(document.querySelector('#toast').textContent),re.source,{timeout:30000});}
const clearToast=(page)=>page.evaluate(()=>{document.querySelector('#toast').textContent='';});
async function upload(page,file){await clearToast(page);const fc=page.waitForEvent('filechooser');await page.locator('.photo-card [data-action=photo-upload]').click();await (await fc).setFiles(IMG+file);}
(async()=>{
 const browser=await chromium.launch({args:['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']});
 const ctx=await browser.newContext({viewport:{width:1280,height:900}});
 // count camera streams so we can prove they are released when the camera closes
 await ctx.addInitScript(()=>{const real=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);window.__streams=[];window.__asks=[];navigator.mediaDevices.getUserMedia=async(c)=>{window.__asks.push(c);const s=await real(c);window.__streams.push(s);return s;};});
 const page=await ctx.newPage();
 const errors=[],bad=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});
 await signIn(page);
 // clean slate for this account
 for(const p of await index(page))await page.evaluate(d=>fetch('/api/photos?date='+d,{method:'DELETE'}),p.date);
 await page.goto(`${B}/?today=${TODAY}#/today`);await page.reload();await page.waitForSelector(".photo-card");
 await page.waitForFunction(()=>!document.querySelector('.photo-card [data-action=photo-take]').disabled);

 // 1. placement: immediately after the supplement checklist
 assert.equal(await page.evaluate(()=>document.querySelector('.supplements').nextElementSibling.classList.contains('photo-card')),true);
 assert.match(await page.locator('.photo-card h2').innerText(),/DAILY PROGRESS PHOTO/i);
 assert.match(await page.locator('[data-action=photo-take]').innerText(),/TAKE PHOTO/i);
 assert.match(await page.locator('[data-action=photo-upload]').innerText(),/UPLOAD PHOTO/i);
 assert.match(await page.locator('.photo-card .cap-date').innerText(),/Wed, Nov 18, 2026/);
 step('photo section sits right after supplements, with title, both buttons and a date label');

 // 2. upload a photo
 await upload(page,'portrait.jpg');await waitToast(page,/Photo saved/);
 let idx=await index(page);assert.deepEqual(idx.map(p=>p.date),['2026-11-18']);assert.equal(idx[0].w,1200);assert.equal(idx[0].h,1500);
 assert.equal(await page.locator('.photo-card .polaroid-img img').count(),1,'photo displayed in the frame');
 step('upload: kept at 1200×1500 (no upscaling), saved under the workout date, displayed in the frame');

 // 3. persists across reloads (served from cloud storage, not local memory)
 await page.reload();await page.waitForSelector('.photo-card img');
 const src=await page.locator('.photo-card .polaroid-img img').getAttribute('src');assert.match(src,/^\/api\/photo\?date=2026-11-18&size=full&v=\d+$/);
 await page.waitForFunction(()=>{const i=document.querySelector('.photo-card .polaroid-img img');return i.complete&&i.naturalWidth>0;});
 step('reload: photo comes back from the cloud ('+src.split('?')[0]+')');

 // 4. EXIF-rotated phone photo stays upright
 await page.goto(`${B}/?today=${TODAY}#/day/30`);await page.waitForSelector('.photo-card[data-iso="2026-11-17"]');
 await upload(page,'exif6.jpg');await waitToast(page,/Photo saved/);
 idx=await index(page);const ex=idx.find(p=>p.date==='2026-11-17');assert.ok(ex.w<ex.h,`EXIF orientation applied (${ex.w}x${ex.h})`);
 step(`EXIF-rotated photo saved upright (${ex.w}×${ex.h})`);

 // 5. take a photo with the camera
 await page.goto(`${B}/?today=${TODAY}#/day/29`);await page.waitForSelector('.photo-card[data-iso="2026-11-16"]');
 await page.locator('[data-action=photo-take]').click();
 await page.waitForSelector('#camera:not([hidden]) [data-action=cam-shutter]:not([disabled])',{timeout:15000});
 assert.equal(await page.evaluate(()=>document.querySelector('.cam-video').videoWidth>0),true,'live preview running');
 assert.deepEqual(await page.evaluate(()=>window.__asks[0].video.facingMode),{ideal:'environment'},'the camera starts on the rear lens');
 await page.locator('[data-action=cam-shutter]').click();
 await page.waitForSelector('[data-step=review]:not([hidden])');
 await page.locator('[data-action=cam-retake]').click();await page.waitForSelector('[data-step=live]:not([hidden])');
 // self-timer: 3 seconds
 await page.locator('[data-action=cam-timer]').click();assert.match(await page.locator('[data-action=cam-timer]').innerText(),/3s/i);
 await page.locator('[data-action=cam-shutter]').click();
 assert.equal(await page.locator('.cam-count').innerText(),'3');
 await page.waitForSelector('[data-step=review]:not([hidden])',{timeout:6000});
 await clearToast(page);await page.locator('[data-action=cam-use]').click();
 assert.equal(await page.locator('#camera').isHidden(),true,'camera closes after use');
 assert.equal(await page.evaluate(()=>window.__streams.every(s=>s.getTracks().every(t=>t.readyState==='ended'))),true,'camera released');
 await waitToast(page,/Photo saved/);
 idx=await index(page);assert.ok(idx.some(p=>p.date==='2026-11-16'),'camera photo saved');
 await page.waitForFunction(()=>document.activeElement&&document.activeElement.dataset.action==='photo-take',null,{timeout:5000});
 step('camera: live preview, capture, retake, 3s self-timer, use photo, saved; camera released; focus back on Take Photo');

 // 5b. switching cameras twice in quick succession must not leave a camera running
 await page.locator('[data-action=photo-take]').click();await page.waitForSelector('[data-action=cam-shutter]:not([disabled])');
 await page.evaluate(()=>{const f=document.querySelector('[data-action=cam-flip]');f.click();f.click();});
 await page.waitForSelector('[data-action=cam-shutter]:not([disabled])');await page.waitForTimeout(800);
 assert.equal(await page.evaluate(()=>window.__streams.filter(s=>s.getTracks().some(t=>t.readyState==='live')).length),1,'exactly one live camera');
 await page.locator('[data-action=cam-close]').click();
 assert.equal(await page.evaluate(()=>window.__streams.every(s=>s.getTracks().every(t=>t.readyState==='ended'))),true,'all cameras released');
 step('camera: rapid front/back switching leaves exactly one camera on, and none after closing');

 // 6. closing the camera without a photo also releases it; Escape closes
 await page.locator('[data-action=photo-take]').click();await page.waitForSelector('[data-action=cam-shutter]:not([disabled])');
 await page.keyboard.press('Escape');assert.equal(await page.locator('#camera').isHidden(),true);
 assert.equal(await page.evaluate(()=>window.__streams.every(s=>s.getTracks().every(t=>t.readyState==='ended'))),true);
 step('camera: Escape closes it and releases the camera');

 // 7. replace (asks first; cancel keeps the old one)
 await page.goto(`${B}/?today=${TODAY}#/today`);await page.waitForSelector('.photo-card img');
 const before=(await index(page)).find(p=>p.date===TODAY);
 await upload(page,'landscape.jpg');await page.waitForSelector('#modal:not([hidden])');assert.match(await page.locator('#modal-title').innerText(),/Replace this photo/);
 await page.locator('[data-m=no]').click();assert.equal((await index(page)).find(p=>p.date===TODAY).v,before.v,'cancel keeps the old photo');
 await upload(page,'landscape.jpg');await page.waitForSelector('#modal:not([hidden])');await page.locator('[data-m=yes]').click();await waitToast(page,/Photo saved/);
 const after=(await index(page)).find(p=>p.date===TODAY);assert.ok(after.v>before.v);assert.deepEqual([after.w,after.h],[1600,1000]);
 assert.equal((await index(page)).filter(p=>p.date===TODAY).length,1,'still one photo for the day');
 step('replace: asks first, cancel keeps the old photo, confirm swaps it (still one per day)');

 // 8. big 12MP phone photo + transparent PNG + non-image
 await page.goto(`${B}/?today=${TODAY}#/day/28`);await page.waitForSelector('.photo-card[data-iso="2026-11-15"]');
 await upload(page,'big.jpg');await waitToast(page,/Photo saved/);
 assert.deepEqual((({w,h})=>[w,h])((await index(page)).find(p=>p.date==='2026-11-15')),[1600,1200]);
 await page.goto(`${B}/?today=${TODAY}#/day/27`);await page.waitForSelector('.photo-card[data-iso="2026-11-14"]');
 await upload(page,'alpha.png');await waitToast(page,/Photo saved/);
 await page.goto(`${B}/?today=${TODAY}#/day/26`);await page.waitForSelector('.photo-card[data-iso="2026-11-13"]');
 await upload(page,'not-an-image.jpg');await waitToast(page,/can't open that photo|isn't a photo/);
 assert.equal((await index(page)).some(p=>p.date==='2026-11-13'),false);
 step('12 MP photo shrunk to 1600×1200; PNG accepted; a fake .jpg is rejected with a clear message');

 // 9. gallery timeline: date order, dates under photos
 await page.goto(`${B}/?today=${TODAY}#/photos`);await page.waitForSelector('.polaroid-tile');
 const tiles=await page.locator('.polaroid-tile').evaluateAll(els=>els.map(e=>e.dataset.iso));
 assert.deepEqual(tiles,[...tiles].sort(),'chronological');assert.equal(tiles.length,5);
 assert.deepEqual(await page.locator('.polaroid-tile .cap-date').allInnerTexts(),['Sat, Nov 14','Sun, Nov 15','Mon, Nov 16','Tue, Nov 17','Wed, Nov 18']);
 await page.waitForFunction(()=>[...document.querySelectorAll('.polaroid-tile img')].every(i=>i.complete&&i.naturalWidth>0));
 step('gallery: 5 photos in date order, each with its date underneath, thumbnails load');

 // 10. viewer: open, arrows, swipe-free nav, escape
 await page.locator('.polaroid-tile').nth(1).click();await page.waitForSelector('#lightbox .photo-viewer');
 assert.match(await page.locator('#lb-title').innerText(),/Sunday, November 15, 2026/);
 await page.keyboard.press('ArrowRight');assert.match(await page.locator('#lb-title').innerText(),/Monday, November 16/);
 await page.locator('[data-action=photo-prev]').click();assert.match(await page.locator('#lb-title').innerText(),/Sunday, November 15/);
 await page.waitForFunction(()=>{const i=document.querySelector('.pv-full');return i.complete&&i.naturalWidth===1600;});
 await page.keyboard.press('Escape');assert.equal(await page.locator('#lightbox').isHidden(),true);
 step('viewer: large photo with full date, arrow keys and buttons move between days, Escape closes');

 // 11. calendar view
 await page.goto(`${B}/?today=${TODAY}#/photos/calendar/2026-11`);await page.waitForSelector('.photo-cal');
 assert.equal(await page.locator('.pcal-cell.has-photo').count(),5);
 await page.locator('.pcal-cell.has-photo').first().click();await page.waitForSelector('#lightbox .photo-viewer');await page.keyboard.press('Escape');
 await page.locator('a.pcal-cell[href="#/date/2026-11-12"]').click();await page.waitForSelector('.photo-card[data-iso="2026-11-12"]');
 step('calendar view: thumbnails on their dates; empty days open that day to add one');

 // 12. compare: side by side, slider, change dates
 await page.goto(`${B}/?today=${TODAY}#/photos/compare`);await page.waitForSelector('.compare-side');
 assert.equal(await page.locator('[data-compare=a]').inputValue(),'2026-11-14');assert.equal(await page.locator('[data-compare=b]').inputValue(),TODAY);
 assert.match(await page.locator('.compare-gap').innerText(),/4\s*DAYS APART/i);
 await page.locator('[data-compare=a]').selectOption('2026-11-16');await page.waitForFunction(()=>location.hash==='#/photos/compare/2026-11-16/2026-11-18');
 assert.match(await page.locator('.compare-gap').innerText(),/2\s*DAYS/i);
 await page.locator('[data-action=compare-mode][data-mode=slider]').click();await page.waitForSelector('.compare-slider');
 await page.locator('.cs-stage').scrollIntoViewIfNeeded();const box=await page.locator('.cs-stage').boundingBox();await page.mouse.move(box.x+box.width*.25,box.y+box.height/2);await page.mouse.down();await page.mouse.move(box.x+box.width*.8,box.y+box.height/2,{steps:5});await page.mouse.up();
 const pos=await page.locator('.compare-slider').evaluate(e=>parseFloat(e.style.getPropertyValue('--pos')));assert.ok(pos>75&&pos<85,'drag moves the divider: '+pos);
 await page.locator('[data-compare-slider]').fill('30');assert.equal(await page.locator('.compare-slider').evaluate(e=>e.style.getPropertyValue('--pos')),'30%');
 await page.locator('[data-action=compare-mode][data-mode=side]').click();await page.waitForSelector('.compare-side');
 step('compare: defaults to first vs latest, dates selectable, side-by-side and drag slider');

 // 13. remove
 await page.goto(`${B}/?today=${TODAY}#/day/27`);await page.waitForSelector('.photo-card [data-action=photo-remove]');
 await clearToast(page);await page.locator('[data-action=photo-remove]').click();await page.locator('[data-m=yes]').click();await waitToast(page,/removed/);
 assert.equal((await index(page)).some(p=>p.date==='2026-11-14'),false);assert.equal(await page.locator('.photo-card .is-empty').count(),1);
 step('remove: confirmed, deleted from the cloud, frame back to empty');

 // 14. progress page summary
 await page.goto(`${B}/?today=${TODAY}#/progress`);await page.waitForSelector('.photos-summary .polaroid-mini');
 assert.equal(await page.locator('.photos-summary .polaroid-mini').count(),4);
 step('progress page: photo summary with recent prints and gallery links');

 // 15. a second device sees the photos (fresh browser profile, same account)
 const cookies=await ctx.cookies();const ctx2=await browser.newContext({viewport:{width:390,height:844}});await ctx2.addCookies(cookies);const p2=await ctx2.newPage();await signIn(p2);
 await p2.goto(`${B}/?today=${TODAY}#/today`);await p2.waitForSelector('.photo-card .polaroid-img img');
 await p2.waitForFunction(()=>{const i=document.querySelector('.photo-card .polaroid-img img');return i.complete&&i.naturalWidth>0;});
 step('second device (fresh profile, phone size) shows the same day\'s photo');
 await ctx2.close();

 assert.deepEqual(errors,[],'no JS errors');globalThis.cookies=cookies;
 assert.deepEqual(bad.filter(u=>!/photo\?date=2026-11-1[34]/.test(u)),[],'no unexpected HTTP errors');
 await browser.close();

 // 16. camera permission denied → clear guidance + upload fallback
 const b2=await chromium.launch({channel:'chromium',args:['--use-fake-device-for-media-stream','--deny-permission-prompts']});
 const c3=await b2.newContext({viewport:{width:390,height:844}});await c3.addCookies(globalThis.cookies);const p3=await c3.newPage();await signIn(p3);
 await p3.goto(`${B}/?today=${TODAY}#/today`);await p3.waitForFunction(()=>!document.querySelector('.photo-card [data-action=photo-take]').disabled);
 await p3.locator('[data-action=photo-take]').click();
 await p3.waitForSelector('.cam-msg.show [data-action=cam-upload]',{timeout:15000});
 assert.match(await p3.locator('.cam-msg p').innerText(),/Camera access is blocked.*allow camera access.*settings/);
 const fc=p3.waitForEvent('filechooser');await p3.locator('[data-action=cam-upload]').click();await fc;
 assert.equal(await p3.locator('#camera').isHidden(),true);
 step('camera blocked: explains how to allow it, and "Upload a photo instead" opens the picker');
 await b2.close();
 console.log('PASS: progress photo end-to-end');
})().catch(e=>{console.error('FAIL',e);process.exit(1)});
