const {createHash}=require('node:crypto');
const auth=require('../server/auth.cjs');
module.exports=async(req,res)=>{
 try{
  if(req.method==='GET')return auth.json(res,200,{account:true,authenticated:auth.authenticated(req)});
  if(!auth.sameOrigin(req))return auth.json(res,403,{error:'Request origin not allowed.'});
  if(req.method==='DELETE'){auth.clearSession(res);return auth.json(res,200,{ok:true});}
  if(req.method!=='POST')return auth.json(res,405,{error:'Method not allowed.'});
  const ip=(req.headers['x-vercel-forwarded-for']||req.headers['x-forwarded-for']||req.socket?.remoteAddress||'unknown').split(',')[0].trim();
  const key=createHash('sha256').update(process.env.SESSION_SECRET+ip).digest('hex');
  const allowed=await auth.convex('mutation','login:attempt',{key});
  if(!allowed)return auth.json(res,429,{error:'Too many attempts. Please try again in 15 minutes.'});
  if(!auth.passwordOK(req.body?.password))return auth.json(res,401,{error:'That password is not correct.'});
  auth.setSession(res);return auth.json(res,200,{ok:true});
 }catch{return auth.json(res,503,{error:'Sign-in is temporarily unavailable. Please try again shortly.'});}
};
