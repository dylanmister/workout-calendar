/* A shared private account; only the server sees the password verifier and Convex key. */
window.WLTA_READY=(async()=>{
 const local=/^(localhost|127\.0\.0\.1)$/.test(location.hostname);
 let status;
 try{const response=await fetch('/api/session',{cache:'no-store'});if(!response.ok){if(local&&response.status===404)return;throw new Error('Sign-in is temporarily unavailable. Please reload to retry.');}status=await response.json();}
 catch(error){if(local)return;status={error:error.message};}
 window.WLTA_ACCOUNT=true;
 if(status.authenticated)return;
 const gate=document.createElement('div');gate.className='account-gate';gate.setAttribute('role','main');
 gate.innerHTML=`<section class="account-card"><svg class="account-lotus" aria-hidden="true"><use href="#lotus"/></svg><p class="eyebrow">The White Lotus Training Arc</p><h1>Welcome back.</h1><p class="muted">Sign in to continue your training arc.<br>Your progress follows you across devices.</p><form id="account-form"><label for="account-password">Password</label><input id="account-password" type="password" autocomplete="current-password" required maxlength="256"><button class="btn btn-primary" type="submit">Sign in</button><p id="account-error" role="alert"></p></form></section>`;
 document.body.append(gate);
 const underlying=[document.querySelector('.app-header'),document.querySelector('#view'),document.querySelector('.tabbar')];for(const el of underlying)el.hidden=true;
 if(status.error)gate.querySelector('#account-error').textContent=status.error;
 gate.querySelector('input').focus();
 await new Promise(resolve=>gate.querySelector('form').addEventListener('submit',async event=>{
  event.preventDefault();const button=gate.querySelector('button'),error=gate.querySelector('#account-error');button.disabled=true;error.textContent='';
  try{const response=await fetch('/api/session',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:gate.querySelector('input').value})});const result=await response.json();if(!response.ok)throw new Error(result.error||'Could not sign in.');gate.remove();for(const el of underlying)el.hidden=false;resolve();}
  catch(e){error.textContent=e.message;}finally{button.disabled=false;}
 }));
})();
window.WLTA_SIGN_OUT=async()=>{await fetch('/api/session',{method:'DELETE'});location.reload();};
