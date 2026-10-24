/* Local integration harness for the actual Vercel handlers, using the dev database. */
const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
Object.assign(process.env,JSON.parse(fs.readFileSync('tools/.cache/cloud-secrets.json','utf8')));
process.env.CONVEX_URL='https://nautical-crow-965.convex.cloud';
process.env.SHARED_SYNC_CODE='lotus-'+[...crypto.randomBytes(16)].map(x=>'abcdefghijklmnopqrstuvwxyz234567'[x&31]).join('').match(/.{4}/g).join('-');
const routes={'/api/session':require('../api/session.js'),'/api/progress':require('../api/progress.js')};
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png'};
http.createServer(async(req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(routes[url.pathname]){let body='';for await(const chunk of req){body+=chunk;if(body.length>600000){res.writeHead(413);res.end();return;}}
 try{req.body=body?JSON.parse(body):{};}catch{res.writeHead(400);res.end();return;}
 res.status=code=>{res.statusCode=code;return res;};res.json=data=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(data));};return routes[url.pathname](req,res);}
 const file=path.resolve('.','.'+(url.pathname==='/'?'/index.html':decodeURIComponent(url.pathname)));
 if(!file.startsWith(process.cwd()+path.sep)||file.includes(path.sep+'.')){res.writeHead(403);res.end();return;}
 try{res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}
}).listen(8020,'127.0.0.1',()=>console.log('Integration server: http://localhost:8020 (Convex development database)'));
