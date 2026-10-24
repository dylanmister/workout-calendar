const auth=require('../server/auth.cjs');
module.exports=async(req,res)=>{
 if(!auth.authenticated(req))return auth.json(res,401,{error:'Please sign in again.'});
 try{
  const code=process.env.SHARED_SYNC_CODE;if(!code)throw new Error('Missing account');
  if(req.method==='GET')return auth.json(res,200,await auth.convex('query','progress:get',{code}));
  if(req.method!=='POST')return auth.json(res,405,{error:'Method not allowed.'});
  if(!auth.sameOrigin(req))return auth.json(res,403,{error:'Request origin not allowed.'});
  const {baseRev,state}=req.body||{};
  if(!Number.isInteger(baseRev)||baseRev<0||typeof state!=='string'||state.length>512*1024)return auth.json(res,400,{error:'Invalid saved progress.'});
  return auth.json(res,200,await auth.convex('mutation','progress:save',{code,baseRev,state}));
 }catch{return auth.json(res,503,{error:'Cloud progress is temporarily unavailable. Your changes remain saved on this device.'});}
};
