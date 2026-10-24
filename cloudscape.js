/* The supplied Cloudscape shader, adapted to the existing buildless website. */
(() => {
  'use strict';
  const host=document.querySelector('.site-bg');if(!host)return;
  const canvas=document.createElement('canvas');canvas.setAttribute('aria-hidden','true');host.append(canvas);
  const gl=canvas.getContext('webgl',{antialias:false,alpha:false,powerPreference:'low-power'});if(!gl)return;
  const vertex=`attribute vec2 position;void main(){gl_Position=vec4(position,0.,1.);}`;
  const fragment=`precision highp float;
uniform vec2 u_resolution;uniform float u_time;uniform vec3 u_colorBottom;uniform vec3 u_colorMid;uniform vec3 u_colorTop;uniform float u_speed;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453123);}
float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);float a=hash(i);float b=hash(i+vec2(1.,0.));float c=hash(i+vec2(0.,1.));float d=hash(i+vec2(1.,1.));vec2 u=f*f*(3.-2.*f);return mix(a,b,u.x)+(c-a)*u.y*(1.-u.x)+(d-b)*u.x*u.y;}
float fbm(vec2 p,float t){float v=0.;float a=.5;float fi=0.;mat2 rot=mat2(.86,.51,-.51,.86);for(int i=0;i<6;i++){vec2 morph=vec2(sin(t*.5+fi),cos(t*.3-fi))*.05;v+=a*noise(p+morph);p=rot*p*2.;a*=.5;fi+=1.;}return v;}
void main(){vec2 uv=gl_FragCoord.xy/u_resolution;float t=u_time*u_speed;vec2 aspect=vec2(u_resolution.x/max(u_resolution.y,1.),1.);vec2 p=(uv-.5)*aspect;vec2 wind=vec2(t*.1,t*.02);float pattern=fbm(p*2.2-wind,t);float bandLow=smoothstep(.3,.65,pattern);float bandHigh=smoothstep(.7,.95,pattern);vec3 color=mix(u_colorBottom,u_colorMid,bandLow);color=mix(color,u_colorTop,bandHigh);gl_FragColor=vec4(color,1.);}`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){gl.deleteShader(s);return null;}return s;}
  const vs=shader(gl.VERTEX_SHADER,vertex),fs=shader(gl.FRAGMENT_SHADER,fragment);if(!vs||!fs)return;
  const program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))return;
  gl.useProgram(program);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);
  const position=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(position);gl.vertexAttribPointer(position,2,gl.FLOAT,false,0,0);
  const uniforms=Object.fromEntries(['resolution','time','colorBottom','colorMid','colorTop','speed'].map(k=>[k,gl.getUniformLocation(program,'u_'+k)]));
  const rgb=h=>h.match(/[a-f0-9]{2}/gi).map(x=>parseInt(x,16)/255);
  gl.uniform3fv(uniforms.colorBottom,rgb('#87ceeb'));gl.uniform3fv(uniforms.colorMid,rgb('#f8f8f8'));gl.uniform3fv(uniforms.colorTop,rgb('#ffffff'));gl.uniform1f(uniforms.speed,.45);
  let frame=0,last=0,elapsed=0,previous=0,lost=false;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  function draw(){gl.uniform1f(uniforms.time,elapsed);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);}
  function render(now){frame=0;if(document.hidden||reduced.matches||lost)return;if(now-last>=1000/24){if(previous)elapsed+=Math.min((now-previous)/1000,.1);previous=now;last=now;draw();}frame=requestAnimationFrame(render);}
  function start(){cancelAnimationFrame(frame);previous=0;if(!lost){draw();if(!document.hidden&&!reduced.matches)frame=requestAnimationFrame(render);}}
  function resize(){const dpr=Math.min(devicePixelRatio||1,1.25);canvas.width=Math.max(1,Math.round(host.clientWidth*dpr));canvas.height=Math.max(1,Math.round(host.clientHeight*dpr));gl.viewport(0,0,canvas.width,canvas.height);gl.uniform2f(uniforms.resolution,canvas.width,canvas.height);start();}
  const observer=new ResizeObserver(resize);observer.observe(host);reduced.addEventListener('change',start);document.addEventListener('visibilitychange',start);
  canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;cancelAnimationFrame(frame);canvas.style.visibility='hidden';});
  canvas.addEventListener('webglcontextrestored',()=>location.reload());
  window.addEventListener('pagehide',()=>{cancelAnimationFrame(frame);observer.disconnect();});window.addEventListener('pageshow',e=>{if(e.persisted){observer.observe(host);resize();}});
  resize();
})();
