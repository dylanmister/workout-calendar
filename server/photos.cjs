// Shared checks for the progress photo endpoints. Photos arrive as JPEGs the browser already resized.
const DATE=/^\d{4}-\d{2}-\d{2}$/;
const MAX_BYTES={full:2.5*1024*1024,thumb:400*1024};
function validDate(date){if(typeof date!=='string'||!DATE.test(date))return false;const d=new Date(`${date}T00:00:00Z`);return !Number.isNaN(d.getTime())&&d.toISOString().slice(0,10)===date;}
function params(req){return new URL(req.url||'/','http://localhost').searchParams;}
// Base64 JPEG from the browser -> Buffer, or null if it isn't a reasonably sized JPEG.
function jpeg(b64,max){
 if(typeof b64!=='string'||b64.length>Math.ceil(max/3)*4+8)return null;
 const buf=Buffer.from(b64,'base64');
 return buf.length>=128&&buf.length<=max&&buf[0]===0xff&&buf[1]===0xd8&&buf[2]===0xff?buf:null;
}
async function store(url,buf){
 const res=await fetch(url,{method:'POST',headers:{'Content-Type':'image/jpeg'},body:buf,signal:AbortSignal.timeout(20000)});
 const data=await res.json().catch(()=>({}));
 if(!res.ok||typeof data.storageId!=='string')throw new Error('Upload failed');
 return data.storageId;
}
module.exports={MAX_BYTES,validDate,params,jpeg,store};
