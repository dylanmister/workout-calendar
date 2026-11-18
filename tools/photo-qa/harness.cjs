/* QA harness: serves the site plus the real Vercel API handlers against the Convex DEVELOPMENT deployment, with a throwaway
   password ('qa-test-password') and session secret, so tests never need the real password or touch production.
   Each run uses a new random account. Needs tools/.cache/cloud-secrets.json for the development server key.
   QA_STATIC=1 serves the site without the API (the signed-out, local-only mode). QA_PORT changes the port (default 8031). */
const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'../..');
const secrets=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/.cache/cloud-secrets.json'),'utf8'));
const salt=crypto.randomBytes(16).toString('hex');
process.env.PASSWORD_HASH=JSON.stringify({salt,hash:crypto.scryptSync('qa-test-password',salt,64).toString('hex')});
process.env.SESSION_SECRET=crypto.randomBytes(32).toString('hex');
process.env.PROGRESS_SERVER_KEY=secrets.PROGRESS_SERVER_KEY;
process.env.CONVEX_URL='https://nautical-crow-965.convex.cloud'; // DEV deployment only
process.env.SHARED_SYNC_CODE=process.env.QA_CODE||('lotus-'+[...crypto.randomBytes(16)].map(x=>'abcdefghijklmnopqrstuvwxyz234567'[x&31]).join('').match(/.{4}/g).join('-'));
if(!process.env.CONVEX_URL.includes('nautical-crow-965'))throw new Error('refusing: not dev');
const api=f=>require(path.join(ROOT,'api',f));
const routes=process.env.QA_STATIC?{}:{'/api/session':api('session.js'),'/api/progress':api('progress.js'),'/api/photos':api('photos.js'),'/api/photo':api('photo.js')};
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.webmanifest':'application/manifest+json'};
const PORT=Number(process.env.QA_PORT||8031);
http.createServer(async(req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(routes[url.pathname]){let body='';for await(const chunk of req){body+=chunk;if(body.length>4.5*1024*1024){res.writeHead(413);res.end();return;}}
  try{req.body=body?JSON.parse(body):{};}catch{res.writeHead(400);res.end();return;}
  res.status=code=>{res.statusCode=code;return res;};res.json=data=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data));};
  const t=Date.now();await routes[url.pathname](req,res);if(process.env.QA_LOG)console.log(req.method,url.pathname+url.search,res.statusCode,Date.now()-t+'ms');return;}
 const file=path.resolve(ROOT,'.'+(url.pathname==='/'?'/index.html':decodeURIComponent(url.pathname)));
 if(!file.startsWith(path.resolve(ROOT)+path.sep)||file.includes(path.sep+'.')){res.writeHead(403);res.end();return;}
 try{res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');res.setHeader('Cache-Control','no-cache');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}
}).listen(PORT,'127.0.0.1',()=>console.log(`QA harness http://127.0.0.1:${PORT} code=${process.env.SHARED_SYNC_CODE.slice(0,10)}…`));
