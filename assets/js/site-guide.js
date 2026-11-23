(() => {
  "use strict";
  const root=document.getElementById("site-guide"); if(!root)return;
  const button=root.querySelector("[data-guide-toggle]"), panel=root.querySelector("[data-guide-panel]");
  const title=root.querySelector("[data-guide-title]"), body=root.querySelector("[data-guide-body]");
  const links=root.querySelector("[data-guide-links]"), close=root.querySelector("[data-guide-close]");
  const path=window.location.pathname, base=document.documentElement.dataset.baseurl||"";
  const routes={
    media:{title:"Медиатека",body:"Здесь можно открыть фото и видео с текущего устройства. Сейчас просмотр локальный: файлы не попадают в закрытый архив. Для HEIC, HEVC и видео с поворотом может потребоваться обработанная совместимая копия.",links:[["Открыть медиатеку","/media/"],["Состояние проекта","/status/"]]},
    account:{title:"Личный кабинет",body:"Это страница быстрых внешних ссылок и инструментов. Она не является закрытым семейным кабинетом и не запрашивает пароли сторонних сервисов.",links:[["Главная","/"],["Состояние проекта","/status/"]]},
    status:{title:"Состояние проекта",body:"Здесь показано, что реализовано, что проверено и что ожидает частного размещения. Зелёный CI не означает, что частный сервис уже работает.",links:[["Медиатека","/media/"],["Главная","/"]]},
    home:{title:"Главная",body:"Это публичная витрина семейного проекта. Здесь размещаются только материалы, разрешённые для публикации. Частные семейные данные хранятся отдельно.",links:[["Медиатека","/media/"],["Личный кабинет","/account/"]]},
    default:{title:"Навигация по KOMAROVA_CORE",body:"Можно перейти в медиатеку, открыть быстрые инструменты или проверить фактическое состояние проекта. Подсказки работают локально и не отправляют содержимое страниц или файлов внешнему ИИ-сервису.",links:[["Медиатека","/media/"],["Личный кабинет","/account/"],["Состояние проекта","/status/"]]}
  };
  let key="default";
  if(path.includes("/media/"))key="media";else if(path.includes("/account/"))key="account";else if(path.includes("/status/"))key="status";else if(path===base+"/"||path===base||path==="/")key="home";
  const data=routes[key];title.textContent=data.title;body.textContent=data.body;
  data.links.forEach(([label,route])=>{const a=document.createElement("a");a.href=base+route;a.textContent=label;links.append(a);});
  const setOpen=(open)=>{panel.hidden=!open;button.setAttribute("aria-expanded",open?"true":"false");if(open)close.focus();else button.focus();};
  button.addEventListener("click",()=>setOpen(panel.hidden));close.addEventListener("click",()=>setOpen(false));
  document.addEventListener("keydown",event=>{if(event.key==="Escape"&&!panel.hidden)setOpen(false);});
  try {
    if(!window.sessionStorage.getItem("komarova-guide-seen")) {
      button.classList.add("has-hint");
      window.sessionStorage.setItem("komarova-guide-seen","1");
    }
  } catch (_) { /* Private browsing may disable session storage; navigation still works. */ }
})();
