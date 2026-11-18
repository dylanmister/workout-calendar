const auth=require('../server/auth.cjs');
const photo=require('../server/photos.cjs');
// GET ?date=YYYY-MM-DD&size=thumb|full&v=<version>: one progress photo, only for the signed-in account.
// Images are streamed through here so photos stay behind the password (storage URLs never reach the browser).
function fail(res,status){res.statusCode=status;res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.end();}
module.exports=async(req,res)=>{
 if(!auth.authenticated(req))return fail(res,401);
 if(req.method!=='GET'&&req.method!=='HEAD')return fail(res,405);
 const q=photo.params(req),date=q.get('date'),size=q.get('size')==='full'?'full':'thumb';
 if(!photo.validDate(date))return fail(res,400);
 try{
  const code=process.env.SHARED_SYNC_CODE;if(!code)throw new Error('Missing account');
  const file=await auth.convex('query','photos:file',{code,date,size});
  if(!file)return fail(res,404);
  const image=await fetch(file.url,{signal:AbortSignal.timeout(15000)});
  if(!image.ok)throw new Error('Storage read failed');
  const buf=Buffer.from(await image.arrayBuffer());
  res.statusCode=200;
  res.setHeader('Content-Type','image/jpeg');
  res.setHeader('Content-Length',String(buf.length));
  res.setHeader('X-Content-Type-Options','nosniff');
  // A versioned URL never changes content (a replaced photo gets a new version), so this device may keep it.
  res.setHeader('Cache-Control',q.get('v')===String(file.v)?'private, max-age=31536000, immutable':'private, no-cache');
  res.end(req.method==='HEAD'?undefined:buf);
 }catch{return fail(res,503);}
};
