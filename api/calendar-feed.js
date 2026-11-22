// Read-only workout feed for the Life OS calendar engine (a Google Apps Script in Dylan's account).
// Auth: "Authorization: Bearer <CALENDAR_FEED_TOKEN>" (Vercel env var; never in this public repo).
// Dates follow the app exactly: day N falls on program.start + (N - 1) + (number of shifts <= N),
// so a "push it back a day" in the app moves every later workout in the calendar too.
// Only workout dates and completion flags leave the server; logs, notes, photos and the sync code do not.
const crypto=require('node:crypto');
const auth=require('../server/auth.cjs');
const schedule=require('../data/schedule.json');
const {exercises}=require('../data/exercises.json');

const NAMES=Object.fromEntries(exercises.map(e=>[e.id,e.name]));
const PHASES=Object.fromEntries(schedule.program.phases.map(p=>[p.id,p]));
const DAY_MS=86400000;

function tokenOK(req){
 const expected=process.env.CALENDAR_FEED_TOKEN||'';
 const header=req.headers.authorization||'';
 const given=header.startsWith('Bearer ')?header.slice(7).trim():'';
 if(expected.length<32||!given)return false;
 const a=crypto.createHash('sha256').update(given).digest(),b=crypto.createHash('sha256').update(expected).digest();
 return crypto.timingSafeEqual(a,b);
}
function addDays(iso,n){return new Date(Date.parse(iso+'T00:00:00Z')+n*DAY_MS).toISOString().slice(0,10);}
function dose(it){
 if(it.dose)return it.dose;
 const parts=[`${it.sets} × ${it.reps}`];
 if(it.load)parts.push(it.load);
 if(it.rest){const r=String(it.rest);parts.push(r.startsWith('→')?`then ${r.slice(1).trim()}`:`rest ${r}`);}
 return parts.join(' · ');
}
function buildFeed(state,from){
 const shifts=(Array.isArray(state.shifts)?state.shifts:[]).filter(Number.isInteger).sort((a,b)=>a-b);
 const done=state.done&&typeof state.done==='object'?state.done:{};
 const start=schedule.program.start;
 const all=schedule.days.map(d=>{
  const phase=PHASES[d.phase]||{};
  return {
   day:d.day,date:addDays(start,(d.day-1)+shifts.filter(s=>s<=d.day).length),done:!!done[d.day],
   element:d.element,focus:d.focus,title:d.title,formatName:d.formatName,location:d.location,
   minutes:d.minutes,contacts:d.contacts||0,phase:d.phase,phaseName:phase.name||d.phase,phaseNumeral:phase.numeral||'',
   summary:d.summary,
   blocks:d.blocks.map(b=>({kind:b.kind,title:b.title,where:b.where,minutes:b.minutes,
    items:b.items.map(it=>({tag:it.tag||'',name:NAMES[it.id]||it.id,dose:dose(it)}))})),
  };
 });
 const end=all[all.length-1].date,used=new Set(all.map(d=>d.date)),restDates=[];
 for(let i=0;addDays(start,i)<=end;i++){const iso=addDays(start,i);if(!used.has(iso)&&(!from||iso>=from))restDates.push(iso);}
 return {
  ok:true,generatedAt:new Date().toISOString(),
  program:{name:schedule.program.name,version:schedule.program.version,start,end,totalDays:schedule.program.totalDays,timeZone:'America/Los_Angeles',url:'https://white-lotus-training-arc.vercel.app/'},
  shifts,restDates,days:from?all.filter(d=>d.date>=from):all,
 };
}

module.exports=async(req,res)=>{
 if(req.method!=='GET')return auth.json(res,405,{error:'Method not allowed.'});
 if(!process.env.CALENDAR_FEED_TOKEN)return auth.json(res,503,{error:'Calendar feed is not configured.'});
 if(!tokenOK(req))return auth.json(res,401,{error:'Unauthorized.'});
 const fromParam=req.query&&typeof req.query.from==='string'?req.query.from:'';
 const from=/^\d{4}-\d{2}-\d{2}$/.test(fromParam)?fromParam:'';
 let state;
 try{
  const code=process.env.SHARED_SYNC_CODE;if(!code)throw new Error('Missing account');
  const row=await auth.convex('query','progress:get',{code});
  state=row&&row.state?JSON.parse(row.state):{};
 }catch{return auth.json(res,503,{error:'Cloud progress is temporarily unavailable.'});}
 return auth.json(res,200,buildFeed(state,from));
};
module.exports.buildFeed=buildFeed;
