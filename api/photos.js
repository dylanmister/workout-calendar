const auth=require('../server/auth.cjs');
const photo=require('../server/photos.cjs');
// GET: the account's photo list. POST: save a day's photo (replacing any earlier one). DELETE ?date=: remove it.
module.exports=async(req,res)=>{
 if(!auth.authenticated(req))return auth.json(res,401,{error:'Please sign in again.'});
 try{
  const code=process.env.SHARED_SYNC_CODE;if(!code)throw new Error('Missing account');
  if(req.method==='GET')return auth.json(res,200,{photos:await auth.convex('query','photos:list',{code})});
  if(!auth.sameOrigin(req))return auth.json(res,403,{error:'Request origin not allowed.'});
  if(req.method==='DELETE'){
   const date=photo.params(req).get('date');
   if(!photo.validDate(date))return auth.json(res,400,{error:'Invalid date.'});
   await auth.convex('mutation','photos:remove',{code,date});
   return auth.json(res,200,{ok:true});
  }
  if(req.method!=='POST')return auth.json(res,405,{error:'Method not allowed.'});
  const {date,full,thumb,w,h}=req.body||{};
  const fullJPEG=photo.jpeg(full,photo.MAX_BYTES.full),thumbJPEG=photo.jpeg(thumb,photo.MAX_BYTES.thumb);
  if(!photo.validDate(date)||!fullJPEG||!thumbJPEG||!Number.isFinite(w)||!Number.isFinite(h)||w<1||h<1||w>10000||h>10000)return auth.json(res,400,{error:'That photo could not be read. Please try another one.'});
  const urls=await auth.convex('mutation','photos:uploadUrls',{code});
  const stored=await Promise.allSettled([photo.store(urls.full,fullJPEG),photo.store(urls.thumb,thumbJPEG)]);
  const ids=stored.filter(s=>s.status==='fulfilled').map(s=>s.value);
  try{
   if(ids.length<2)throw new Error('Upload failed');
   return auth.json(res,200,await auth.convex('mutation','photos:save',{code,date,full:ids[0],thumb:ids[1],w,h}));
  }catch(error){
   if(ids.length)await auth.convex('mutation','photos:discard',{code,ids}).catch(()=>{});
   throw error;
  }
 }catch{return auth.json(res,503,{error:'Photo storage is temporarily unavailable. Please try again.'});}
};
