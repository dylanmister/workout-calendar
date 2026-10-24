const {chromium}=require(require.resolve('playwright',{paths:[process.cwd(),require('path').resolve('../codex training calendar')]}));
const assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:390,height:844}});
 await page.addInitScript(()=>localStorage.setItem('wlta-sync',JSON.stringify({off:true})));
 await page.goto('http://127.0.0.1:8010/?today=2026-10-20#/today');await page.waitForSelector('.banner.is-visible');await page.waitForTimeout(750);
 assert.equal(await page.locator('.banner').evaluate(e=>getComputedStyle(e).opacity),'1');
 assert.equal(await page.locator('.scroll').evaluate(e=>e.style.getPropertyValue('--reveal-delay')),'55ms');
 await page.emulateMedia({reducedMotion:'reduce'});assert.equal(await page.locator('.scroll').evaluate(e=>getComputedStyle(e).transitionDuration),'0s');
 assert.equal(await page.locator('.scroll').evaluate(e=>getComputedStyle(e).opacity),'1');
 await browser.close();console.log('PASS: final staggered reveal and live reduced-motion changes.');
})().catch(e=>{console.error(e);process.exit(1)});
