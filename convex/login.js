import { mutation } from './_generated/server';
import { ConvexError,v } from 'convex/values';
export const attempt=mutation({
 args:{serverKey:v.string(),key:v.string()},
 handler:async(ctx,{serverKey,key})=>{
  if(!process.env.PROGRESS_SERVER_KEY||serverKey!==process.env.PROGRESS_SERVER_KEY)throw new ConvexError('Unauthorized');
  const now=Date.now(),windowMs=15*60*1000;
  const row=await ctx.db.query('loginAttempts').withIndex('by_key',q=>q.eq('key',key)).unique();
  if(!row){await ctx.db.insert('loginAttempts',{key,count:1,startedAt:now});return true;}
  if(now-row.startedAt>windowMs){await ctx.db.patch(row._id,{count:1,startedAt:now});return true;}
  if(row.count>=10)return false;
  await ctx.db.patch(row._id,{count:row.count+1});return true;
 }
});
