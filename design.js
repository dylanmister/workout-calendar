/* Progressive visual enhancement. Training data, routing and storage stay in app.js. */
(() => {
  'use strict';
  const view = document.getElementById('view');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let observer;
  function reveal(entries) {
    for (const entry of entries) if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  }
  if ('IntersectionObserver' in window) observer = new IntersectionObserver(reveal, {rootMargin:'0px 0px 35px 0px', threshold:0.03});
  function enhance() {
    const layout=view.querySelector('.day-layout');
    if(layout&&!layout.dataset.designed) {
      layout.dataset.designed='true';
      const side=layout.querySelector('.day-side');
      const masthead=document.createElement('div');masthead.className='day-masthead';
      // Same content, same reading order; only its layout container changes.
      masthead.append(side.querySelector('.banner'),side.querySelector('.day-actions'));
      layout.prepend(masthead);
    }
    let sequence=0;
    for(const target of view.querySelectorAll('.banner,.scroll,.summary,.block,.wrap.narrow > .card,.notes')) {
      if(target.dataset.reveal)continue;
      target.dataset.reveal='true';
      target.style.setProperty('--reveal-delay',`${(sequence++%3)*55}ms`);
      if(observer&&!motion.matches){target.classList.add('reveal');observer.observe(target);}
    }
  }
  // Observe only the app view: enhancement never reads or changes saved progress.
  const mutations=new MutationObserver(enhance);
  mutations.observe(view,{childList:true,subtree:true});
  enhance();
  motion.addEventListener('change',()=>{
    if(motion.matches)for(const target of view.querySelectorAll('.reveal')){target.classList.add('is-visible');observer?.unobserve(target);}
  });
  // Keep keyboard users inside an open dialog and return them to their trigger.
  const overlays=[...document.querySelectorAll('.overlay')];
  const background=[view,document.querySelector('.app-header'),document.querySelector('.tabbar')];
  let lastOutside=null,wasOpen=false;
  document.addEventListener('focusin',event=>{
    if(!event.target.closest('.overlay'))lastOutside=event.target;
  });
  function syncDialogs(){
    const open=overlays.find(el=>!el.hidden);
    for(const el of background)el.inert=Boolean(open);
    if(wasOpen&&!open&&lastOutside?.isConnected)lastOutside.focus({preventScroll:true});
    wasOpen=Boolean(open);
  }
  const dialogObserver=new MutationObserver(syncDialogs);
  for(const overlay of overlays)dialogObserver.observe(overlay,{attributes:true,attributeFilter:['hidden']});
  document.addEventListener('keydown',event=>{
    if(event.key!=='Tab')return;
    const open=overlays.find(el=>!el.hidden);if(!open)return;
    const focusable=[...open.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),textarea,[tabindex="0"]')].filter(el=>el.getClientRects().length);
    if(!focusable.length)return;
    const first=focusable[0],last=focusable.at(-1);
    if(event.shiftKey&&(document.activeElement===first||!open.contains(document.activeElement))){event.preventDefault();last.focus();}
    else if(!event.shiftKey&&(document.activeElement===last||!open.contains(document.activeElement))){event.preventDefault();first.focus();}
  });
})();
