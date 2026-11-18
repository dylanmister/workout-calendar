/* API-level checks of the progress photo endpoints through tools/photo-qa/harness.cjs (Convex DEV deployment):
   sign-in required everywhere, same-origin required for changes, input validation, byte-exact round trips,
   cache headers, replace, date order, delete, and the cleanup of uploads whose save failed.
   Run: python tools/photo-qa/make-images.py; node tools/photo-qa/harness.cjs; node tools/photo-qa/api.cjs */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const ROOT=path.resolve(__dirname,'../..'),IMG=path.join(ROOT,'tools/.cache/photo-qa/img')+path.sep;
const B='http://127.0.0.1:8031',ORIGIN={Origin:B},DEV='https://nautical-crow-965.convex.cloud';
const step=(m)=>console.log('  ✓',m);
(async()=>{
 for(const u of ['/api/photos','/api/photo?date=2026-11-18&size=full']){const r=await fetch(B+u);assert.equal(r.status,401,u+' needs sign-in');}
 assert.equal((await fetch(B+'/api/photo?date=2026-11-18&size=full')).headers.get('cache-control'),'no-store');
 step('signed-out requests are refused (and not cached)');
 const login=await fetch(B+'/api/session',{method:'POST',headers:{'Content-Type':'application/json',...ORIGIN},body:JSON.stringify({password:'qa-test-password'})});
 assert.equal(login.status,200,'sign in');
 const H={Cookie:login.headers.get('set-cookie').split(';')[0]};
 const list=async()=>(await (await fetch(B+'/api/photos',{headers:H})).json()).photos;
 for(const p of await list())await fetch(B+'/api/photos?date='+p.date,{method:'DELETE',headers:{...H,...ORIGIN}});
 const big=fs.readFileSync(IMG+'portrait.jpg'),small=fs.readFileSync(IMG+'exif6.jpg');
 const post=(body,headers=ORIGIN)=>fetch(B+'/api/photos',{method:'POST',headers:{'Content-Type':'application/json',...H,...headers},body:JSON.stringify(body)});
 const good={date:'2026-11-18',full:big.toString('base64'),thumb:small.toString('base64'),w:1200,h:1500};
 assert.equal((await post(good,{})).status,403,'POST without Origin');
 assert.equal((await post(good,{Origin:'https://evil.example'})).status,403,'POST from another site');
 assert.equal((await post({...good,date:'2026-02-30'})).status,400,'impossible date');
 assert.equal((await post({...good,full:Buffer.from('not a jpeg '.repeat(40)).toString('base64')})).status,400,'non-JPEG');
 assert.equal((await post({...good,w:'wide'})).status,400,'bad size');
 assert.equal((await post({...good,thumb:Buffer.alloc(500*1024,0xff).toString('base64')})).status,400,'oversized thumbnail');
 step('changes need same-origin; bad dates, non-JPEGs, bad sizes and oversized files are rejected');
 const r1=await post(good);const j1=await r1.json();assert.equal(r1.status,200,JSON.stringify(j1));
 assert.deepEqual(await list(),[{date:'2026-11-18',v:j1.v,w:1200,h:1500}]);
 const full=await fetch(`${B}/api/photo?date=2026-11-18&size=full&v=${j1.v}`,{headers:H});
 assert.equal(full.headers.get('content-type'),'image/jpeg');assert.equal(full.headers.get('cache-control'),'private, max-age=31536000, immutable');
 assert.ok(Buffer.from(await full.arrayBuffer()).equals(big),'full image round-trips byte for byte');
 const thumb=await fetch(`${B}/api/photo?date=2026-11-18&size=thumb&v=old`,{headers:H});
 assert.equal(thumb.headers.get('cache-control'),'private, no-cache','an outdated version is not cached long-term');
 assert.ok(Buffer.from(await thumb.arrayBuffer()).equals(small));
 assert.equal((await fetch(`${B}/api/photo?date=2026-11-17&size=full`,{headers:H})).status,404);
 step('save, list, byte-exact full and thumbnail, private caching only for the current version, 404 for empty days');
 const r2=await post({...good,full:small.toString('base64'),w:900,h:1200});const j2=await r2.json();
 assert.ok(j2.v>j1.v);assert.equal((await list()).length,1,'one photo per day');
 assert.ok(Buffer.from(await (await fetch(`${B}/api/photo?date=2026-11-18&size=full&v=${j2.v}`,{headers:H})).arrayBuffer()).equals(small));
 assert.equal((await post({...good,date:'2026-10-19'})).status,200);
 assert.deepEqual((await list()).map(p=>p.date),['2026-10-19','2026-11-18'],'date order');
 step('replacing keeps one photo per day; list is in date order');
 assert.equal((await fetch(B+'/api/photos?date=2026-11-18',{method:'DELETE',headers:H})).status,403,'DELETE needs same origin');
 assert.equal((await fetch(B+'/api/photos?date=2026-11-18',{method:'DELETE',headers:{...H,...ORIGIN}})).status,200);
 assert.equal((await fetch(`${B}/api/photo?date=2026-11-18&size=full&v=${j2.v}`,{headers:H})).status,404,'deleted');
 await fetch(B+'/api/photos?date=2026-10-19',{method:'DELETE',headers:{...H,...ORIGIN}});
 assert.deepEqual(await list(),[]);
 step('delete needs same-origin and removes the photo');
 // cleanup of a failed save, straight against the development database
 const serverKey=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/.cache/cloud-secrets.json'),'utf8')).PROGRESS_SERVER_KEY;
 const code='lotus-'+[...require('crypto').randomBytes(16)].map(x=>'abcdefghijklmnopqrstuvwxyz234567'[x&31]).join('').match(/.{4}/g).join('-');
 const call=async(kind,fn,args)=>{const r=await (await fetch(`${DEV}/api/${kind}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:fn,args:{code,serverKey,...args},format:'json'})})).json();return r;};
 const urls=(await call('mutation','photos:uploadUrls',{})).value;
 const up=async(url,buf)=>(await (await fetch(url,{method:'POST',headers:{'Content-Type':'image/jpeg'},body:buf})).json()).storageId;
 const a=await up(urls.full,small),b=await up(urls.thumb,small);
 assert.equal((await call('mutation','photos:discard',{ids:[a,b]})).status,'success');
 const reuse=await call('mutation','photos:save',{date:'2026-11-18',full:a,thumb:b,w:900,h:1200});
 assert.equal(reuse.status,'error','discarded files are gone, so they cannot be saved');
 const wrongKey=await call('query','photos:list',{serverKey:'wrong'});
 assert.equal(wrongKey.status,'error','server key required');assert.match(JSON.stringify(wrongKey),/Unauthorized/);
 assert.equal((await call('query','photos:list',{})).status,'success','the same call with the right key works');
 step('uploads from a failed save are deleted; Convex functions refuse a wrong server key');
 console.log('PASS: photo API');
})().catch(e=>{console.error('FAIL',e);process.exit(1)});
