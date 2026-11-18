/* The mobile menu drawer, the camera's rear default and front/back flip, and progress photos keeping their own shape,
   against tools/photo-qa/harness.cjs (Convex DEV deployment, throwaway account). Test photos are drawn in the browser.
   Run: node tools/photo-qa/harness.cjs; node tools/photo-qa/ui-check.cjs */
const path = require('path'); const ROOT = path.resolve(__dirname, '../..');
const {chromium} = require(require.resolve('playwright', {paths: [process.cwd(), path.resolve(ROOT, '../codex training calendar')]}));
const assert = require('assert/strict');
const B = 'http://127.0.0.1:8031', T = '2026-11-18';
const step = (m) => console.log('  ✓', m);
async function signIn(page, hash = 'today') {
  await page.goto(`${B}/?today=${T}#/${hash}`);
  if (await page.locator('#account-password').count()) { await page.fill('#account-password', 'qa-test-password'); await page.click('#account-form button'); }
  await page.waitForSelector('#view .wrap', {timeout: 20000});
}
const fresh = (page, hash) => page.goto(`${B}/?today=${T}&r=${Math.random().toString(36).slice(2)}#/${hash}`).then(() => page.waitForSelector('#view .wrap'));
(async () => {
  // two fake cameras, so the flip button has somewhere to go
  const browser = await chromium.launch({channel: 'chromium', args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream=device-count=2']});
  const ctx = await browser.newContext({viewport: {width: 390, height: 844}});
  await ctx.addInitScript(() => {
    const md = navigator.mediaDevices, real = md.getUserMedia.bind(md); window.__streams = []; window.__asks = [];
    md.getUserMedia = async (c) => { window.__asks.push(c); const s = await real(c); window.__streams.push(s); return s; };
  });
  const page = await ctx.newPage(); const errors = []; page.on('pageerror', (e) => errors.push(e.message));
  await signIn(page);

  // 1. mobile navigation: a Menu button and a slide-in drawer instead of the old bottom tab bar
  assert.equal(await page.locator('.tabbar').count(), 0, 'no bottom tab bar');
  assert.equal(await page.locator('.top-nav').isHidden(), true, 'top nav folded away on a phone');
  const menu = page.locator('#menu-btn');
  assert.equal(await menu.isVisible(), true); assert.equal(await menu.getAttribute('aria-expanded'), 'false');
  await menu.click(); await page.waitForSelector('#nav-drawer:not([hidden])');
  assert.equal(await menu.getAttribute('aria-expanded'), 'true');
  assert.equal(await page.evaluate(() => document.activeElement.closest('#nav-drawer') !== null && document.activeElement.getAttribute('aria-current')), 'page', 'focus starts on the current page');
  assert.deepEqual(await page.locator('#nav-drawer .drawer-nav a').allInnerTexts(), ['Today', 'Calendar', 'Progress', 'Photos', 'More'], 'all five destinations');
  for (let i = 0; i < 8; i++) { await page.keyboard.press('Tab'); assert.equal(await page.evaluate(() => !!document.activeElement.closest('#nav-drawer')), true, 'Tab stays inside the drawer'); }
  assert.equal(await page.evaluate(() => document.querySelector('#view').inert && document.querySelector('.app-header').inert), true, 'the page behind is inert');
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no sideways scroll with the drawer open');
  await page.keyboard.press('Escape'); await page.waitForSelector('#nav-drawer', {state: 'hidden'});
  assert.equal(await menu.getAttribute('aria-expanded'), 'false');
  await page.waitForFunction(() => document.activeElement && document.activeElement.id === 'menu-btn');
  step('drawer: opens from Menu, focus starts on the current page and stays inside, page behind is inert, Escape closes and returns focus');
  await menu.click(); await page.locator('#nav-drawer a[data-nav=calendar]').click();
  await page.waitForSelector('.cal-card'); assert.equal(await page.locator('#nav-drawer').isHidden(), true);
  assert.match(page.url(), /#\/calendar$/);
  await menu.click(); assert.equal(await page.locator('#nav-drawer a[aria-current=page]').getAttribute('data-nav'), 'calendar');
  await page.mouse.click(20, 400); await page.waitForSelector('#nav-drawer', {state: 'hidden'});
  await menu.click(); await page.locator('[data-action=menu-close]').click(); await page.waitForSelector('#nav-drawer', {state: 'hidden'});
  await menu.click(); await page.setViewportSize({width: 1280, height: 900}); await page.waitForSelector('#nav-drawer', {state: 'hidden'});
  assert.equal(await page.locator('.top-nav').isVisible(), true); assert.equal(await menu.isHidden(), true);
  assert.equal(await page.evaluate(() => getComputedStyle(document.body).overflow), 'visible', 'scrolling restored');
  await page.setViewportSize({width: 390, height: 844});
  step('drawer: choosing a page navigates and closes it; the current page is marked; tap outside, the close button and widening the window all close it');

  // 2. camera: rear camera first, unmirrored; the ↩ flip switches to the front camera (mirrored) and back
  await fresh(page, 'day/25'); await page.waitForSelector('[data-action=photo-take]:not([disabled])');
  assert.equal(await page.locator('#photo-capture').getAttribute('capture'), 'environment', 'phone camera-app fallback also opens the rear camera');
  await page.locator('[data-action=photo-take]').click(); await page.waitForSelector('[data-action=cam-shutter]:not([disabled])');
  const ask0 = await page.evaluate(() => window.__asks[0].video.facingMode);
  assert.deepEqual(ask0, {ideal: 'environment'}, 'first request asks for the rear camera');
  const flip = page.locator('[data-action=cam-flip]');
  assert.equal(await flip.isVisible(), true, 'flip button shown with two cameras');
  assert.equal(await page.locator('[data-action=cam-flip] use').getAttribute('href'), '#i-flip');
  assert.match(await flip.innerText(), /flip/i);
  const state = () => page.evaluate(() => { const v = document.querySelector('.cam-video'), t = v.srcObject && v.srcObject.getVideoTracks()[0];
    return {label: t && t.label, mirror: v.classList.contains('mirror'), aria: document.querySelector('[data-action=cam-flip]').getAttribute('aria-label'), live: window.__streams.filter((s) => s.getTracks().some((x) => x.readyState === 'live')).length}; });
  const s0 = await state(); assert.equal(s0.mirror, false, 'rear camera is not mirrored'); assert.equal(s0.aria, 'Switch to the front camera');
  await flip.click(); await page.waitForFunction((l) => { const v = document.querySelector('.cam-video'); return v.srcObject && v.srcObject.getVideoTracks()[0].label !== l && !document.querySelector('[data-action=cam-shutter]').disabled; }, s0.label);
  const s1 = await state(); assert.equal(s1.mirror, true, 'front camera preview is mirrored'); assert.equal(s1.aria, 'Switch to the rear camera'); assert.equal(s1.live, 1, 'exactly one camera on');
  await flip.click(); await page.waitForFunction((l) => { const v = document.querySelector('.cam-video'); return v.srcObject && v.srcObject.getVideoTracks()[0].label !== l && !document.querySelector('[data-action=cam-shutter]').disabled; }, s1.label);
  const s2 = await state(); assert.equal(s2.label, s0.label, 'back on the first camera'); assert.equal(s2.mirror, false); assert.equal(s2.live, 1);
  await page.locator('[data-action=cam-close]').click(); await page.locator('[data-action=photo-take]').click(); await page.waitForSelector('[data-action=cam-shutter]:not([disabled])');
  assert.equal((await state()).aria, 'Switch to the front camera', 'reopening starts on the rear camera again');
  await page.locator('[data-action=cam-close]').click();
  assert.equal(await page.evaluate(() => window.__streams.every((s) => s.getTracks().every((t) => t.readyState === 'ended'))), true, 'every camera released');
  step('camera: opens on the rear camera (unmirrored) every time; ↩ Flip switches to the front camera (mirrored) and back, one camera at a time');

  // 3. photos keep their own shape everywhere: tall phone, wide, square and portrait
  const shapes = {'2026-11-10': [1080, 1920], '2026-11-11': [1600, 900], '2026-11-12': [1200, 1200], '2026-11-13': [1200, 1500]};
  for (const [date, [w, h]] of Object.entries(shapes)) {
    const status = await page.evaluate(async ([date, w, h]) => {
      const c = new OffscreenCanvas(w, h), g = c.getContext('2d');
      g.fillStyle = '#fbf0d9'; g.fillRect(0, 0, w, h); g.lineWidth = w / 20; g.strokeStyle = '#ff3d8b'; g.strokeRect(0, 0, w, h);
      g.fillStyle = '#ffd23f'; g.beginPath(); g.arc(w / 2, h / 2, Math.min(w, h) / 4, 0, 7); g.fill();
      const blob = await c.convertToBlob({type: 'image/jpeg', quality: .8});
      const b64 = btoa(String.fromCharCode(...new Uint8Array(await blob.arrayBuffer())));
      return (await fetch('/api/photos', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date, full: b64, thumb: b64, w, h})})).status;
    }, [date, w, h]);
    assert.equal(status, 200, 'seed ' + date);
  }
  // the image's layout box (offset size: Polaroids are tilted, so their on-screen bounding boxes are bigger) must match the photo's own ratio
  const measure = (sel) => page.evaluate((sel) => [...document.querySelectorAll(sel)].map((img) => {
    const w = img.offsetWidth, h = img.offsetHeight, cs = getComputedStyle(img), nat = img.naturalWidth / img.naturalHeight, box = w / h;
    return {fit: cs.objectFit, nat: +nat.toFixed(3), box: +box.toFixed(3), w, h};
  }), sel);
  const loaded = (sel) => page.waitForFunction((sel) => { const a = [...document.querySelectorAll(sel)]; return a.length && a.every((i) => i.complete && i.naturalWidth); }, sel, {timeout: 20000});
  const ratioOf = (iso) => shapes[iso][0] / shapes[iso][1];
  for (const [iso] of Object.entries(shapes)) {
    await fresh(page, 'date/' + iso); await loaded('.photo-card .polaroid-img img');
    const [m] = await measure('.photo-card .polaroid-img img');
    assert.equal(m.fit, 'contain'); assert.ok(Math.abs(m.box - ratioOf(iso)) / ratioOf(iso) < 0.02, `day card ${iso}: ${m.w}x${m.h} keeps ${shapes[iso].join('x')}`);
    assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector('.photo-card .polaroid-img')).aspectRatio), 'auto', 'no forced frame shape');
  }
  step('day card (390px): tall 9:16, wide 16:9, square and 4:5 photos each shown at their own shape, uncropped');
  await fresh(page, 'photos'); await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 400) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 50)); } });
  await loaded('.polaroid-tile img');
  for (const m of await measure('.polaroid-tile img')) { assert.equal(m.fit, 'contain'); assert.ok(Math.abs(m.box - m.nat) / m.nat < 0.02, `gallery tile ${m.w}x${m.h} vs ${m.nat}`); }
  await page.locator('.polaroid-tile[data-iso="2026-11-10"]').click(); await page.waitForSelector('.photo-viewer'); await loaded('.pv-full');
  const pv = await page.evaluate(() => { const box = document.querySelector('.pv-media').getBoundingClientRect(), img = document.querySelector('.pv-full'); return {fit: getComputedStyle(img).objectFit, box: box.width / box.height, nat: img.naturalWidth / img.naturalHeight, fits: box.height <= innerHeight}; });
  assert.equal(pv.fit, 'contain'); assert.ok(pv.fits, 'viewer fits on screen');
  await page.keyboard.press('Escape');
  await fresh(page, 'photos/calendar/2026-11'); await loaded('.pcal-cell img');
  for (const m of await measure('.pcal-cell img')) assert.equal(m.fit, 'contain', 'calendar thumbnails are not cropped');
  await fresh(page, 'progress'); await page.locator('.photo-strip').scrollIntoViewIfNeeded(); await loaded('.photo-strip img');
  for (const m of await measure('.photo-strip img')) { assert.equal(m.fit, 'contain'); assert.ok(Math.abs(m.box - m.nat) / m.nat < 0.02, `progress strip ${m.w}x${m.h}`); }
  await fresh(page, 'photos/compare/2026-11-10/2026-11-11'); if (await page.locator('[data-mode=side][aria-pressed=false]').count()) await page.locator('[data-mode=side]').click();
  await loaded('.compare-shot img');
  for (const m of await measure('.compare-shot img')) { assert.equal(m.fit, 'contain'); assert.ok(Math.abs(m.box - m.nat) / m.nat < 0.02, `compare ${m.w}x${m.h}`); }
  await page.locator('[data-mode=slider]').click(); await loaded('.cs-img');
  const st = await page.evaluate(() => { const r = document.querySelector('.cs-stage').getBoundingClientRect(); return {box: r.width / r.height, fits: [...document.querySelectorAll('.cs-img')].every((i) => getComputedStyle(i).objectFit === 'contain'), solid: getComputedStyle(document.querySelector('.cs-before')).backgroundColor}; });
  assert.ok(Math.abs(st.box - 1600 / 900) / (1600 / 900) < 0.03, 'slider frame takes the after photo\'s shape'); assert.ok(st.fits); assert.notEqual(st.solid, 'rgba(0, 0, 0, 0)', 'before side has a solid backing');
  await page.locator('[data-mode=side]').click();
  step('gallery tiles, viewer, photo calendar, progress strip, side-by-side and slider compare: object-fit contain, own shape, nothing cropped or stretched');

  for (const date of Object.keys(shapes)) await page.evaluate((d) => fetch('/api/photos?date=' + d, {method: 'DELETE'}), date);
  assert.deepEqual(errors, [], 'no JavaScript errors');
  await browser.close();
  console.log('PASS: menu drawer, camera rear default + flip, photo shapes');
})().catch((e) => { console.error('FAIL', e); process.exit(1); });
