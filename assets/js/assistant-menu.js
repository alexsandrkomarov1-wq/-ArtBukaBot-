(function(){
  "use strict";
  function init(){
    const drawer=document.querySelector("[data-kc-menu-drawer]");
    const toggle=document.querySelector("[data-kc-menu-toggle]");
    const backdrop=document.querySelector("[data-kc-menu-backdrop]");
    const close=document.querySelector("[data-kc-menu-close]");
    const search=document.querySelector("[data-kc-menu-search]");
    const items=[...document.querySelectorAll("[data-kc-menu-item]")];
    const empty=document.querySelector("[data-kc-menu-empty]");
    if(!drawer||!toggle||!backdrop||!close||!search)return;
    let previousFocus=null;
    function open(){previousFocus=document.activeElement;drawer.classList.add("is-open");drawer.setAttribute("aria-hidden","false");backdrop.hidden=false;toggle.setAttribute("aria-expanded","true");document.body.classList.add("kc-menu-lock");search.focus();}
    function shut(){drawer.classList.remove("is-open");drawer.setAttribute("aria-hidden","true");backdrop.hidden=true;toggle.setAttribute("aria-expanded","false");document.body.classList.remove("kc-menu-lock");if(previousFocus&&previousFocus.focus)previousFocus.focus();}
    toggle.addEventListener("click",open);close.addEventListener("click",shut);backdrop.addEventListener("click",shut);
    document.addEventListener("keydown",function(e){if(e.key==="Escape"&&drawer.classList.contains("is-open"))shut();});
    search.addEventListener("input",function(){const q=search.value.trim().toLocaleLowerCase("ru");let visible=0;items.forEach(item=>{const match=(item.dataset.search||item.textContent).toLocaleLowerCase("ru").includes(q);item.hidden=!match;if(match)visible++;});empty.hidden=visible!==0;});
    drawer.addEventListener("keydown",function(e){if(e.key!=="Tab")return;const focusables=[...drawer.querySelectorAll('button:not([disabled]),input:not([disabled]),a[href]:not([aria-disabled="true"])')].filter(el=>!el.hidden);if(!focusables.length)return;const first=focusables[0],last=focusables[focusables.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}});
    drawer.querySelectorAll("a[href]").forEach(a=>a.addEventListener("click",function(){if(a.getAttribute("aria-disabled")==="true"){return;}shut();}));
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();