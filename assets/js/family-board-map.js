(() => {
  const root = document.querySelector(".family-board-heading");
  if (!root) return;
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  const STORAGE_KEY = "komarova-core-family-board-demo-v1";
  const demoPerson = "PERSON-DEMO-01";
  const now = () => new Date().toISOString();
  const makeId = prefix => prefix + "-" + (window.crypto && crypto.randomUUID ? crypto.randomUUID().slice(0, 8).toUpperCase() : Date.now().toString(36).toUpperCase());
  const seedPosts = [{
    id: "POST-SEED-001", title: "Идея для семейной прогулки", body: "Можно выбрать музей или парк на выходные. Отметьте интересные места на карте и обсудим общий маршрут.", kind: "Предложение", author: "Демо-участник", createdAt: "2026-11-24T10:00:00.000Z", pinned: true, votes: 2, comments: ["Пример комментария. В реальной версии ответ будет связан с участником семьи."]
  }];
  const seedPlaces = [
    { id:"PLACE-DEMO-001", osmType:"node", osmId:0, name:"Государственный Эрмитаж", category:"Музей", lat:59.9398, lon:30.3146, city:"Санкт-Петербург", demo:true },
    { id:"PLACE-DEMO-002", osmType:"node", osmId:0, name:"Петропавловская крепость", category:"Историческое место", lat:59.9500, lon:30.3165, city:"Санкт-Петербург", demo:true },
    { id:"PLACE-DEMO-003", osmType:"node", osmId:0, name:"Русский музей", category:"Музей", lat:59.9387, lon:30.3322, city:"Санкт-Петербург", demo:true },
    { id:"PLACE-DEMO-004", osmType:"node", osmId:0, name:"Летний сад", category:"Парк", lat:59.9443, lon:30.3360, city:"Санкт-Петербург", demo:true },
    { id:"PLACE-DEMO-005", osmType:"node", osmId:0, name:"Исаакиевский собор", category:"Архитектура", lat:59.9341, lon:30.3061, city:"Санкт-Петербург", demo:true }
  ];
  let state = { posts: [], placeStates: {}, places: seedPlaces.slice(), activePlace: null };
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (saved && Array.isArray(saved.posts) && saved.placeStates && typeof saved.placeStates === "object") {
      state.posts = saved.posts;
      state.placeStates = saved.placeStates;
    }
  } catch (_) {}
  const persist = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ posts: state.posts, placeStates: state.placeStates }));
      const label = $("[data-fb-storage-state]");
      if (label) label.textContent = "Сохранено в этом браузере";
    } catch (_) {
      const label = $("[data-fb-storage-state]");
      if (label) label.textContent = "Локальное сохранение недоступно";
    }
  };
  const safeText = value => String(value || "");
  const formatDate = value => new Intl.DateTimeFormat("ru-RU", { day:"2-digit", month:"long", hour:"2-digit", minute:"2-digit" }).format(new Date(value));
  const allPosts = () => [...state.posts, ...seedPosts].sort((a,b) => Number(Boolean(b.pinned))-Number(Boolean(a.pinned)) || new Date(b.createdAt)-new Date(a.createdAt));
  const renderPosts = () => {
    const feed = $("[data-fb-feed]");
    const filter = $("[data-fb-filter]").value;
    const posts = allPosts().filter(post => filter === "all" || post.kind === filter);
    $("[data-fb-post-count]").textContent = posts.length + " записей";
    feed.replaceChildren();
    if (!posts.length) {
      const empty = document.createElement("div"); empty.className = "fb-empty"; empty.textContent = "В этой категории пока нет записей."; feed.append(empty); return;
    }
    posts.forEach(post => {
      const article = document.createElement("article");
      article.className = "fb-post" + (post.pinned ? " is-pinned" : "");
      const top = document.createElement("div"); top.className = "fb-post-top";
      const kind = document.createElement("span"); kind.className = "fb-post-kind"; kind.textContent = post.kind + (post.id.startsWith("POST-DEMO") ? " · пример" : "");
      const date = document.createElement("time"); date.className = "fb-post-date"; date.dateTime = post.createdAt; date.textContent = formatDate(post.createdAt);
      top.append(kind,date);
      const title = document.createElement("h3"); title.textContent = post.title;
      const body = document.createElement("p"); body.className = "fb-post-body"; body.textContent = post.body;
      const meta = document.createElement("div"); meta.className = "fb-post-meta"; meta.textContent = "Автор: " + post.author + " · " + post.id;
      const actions = document.createElement("div"); actions.className = "fb-post-actions";
      const vote = document.createElement("button"); vote.type="button"; vote.className="fb-small-button"; vote.textContent="Поддержать · " + (post.votes || 0);
      vote.addEventListener("click", () => { if (!post.id.startsWith("POST-DEMO")) { post.votes=(post.votes||0)+1; persist(); renderPosts(); } else { vote.textContent="Пример голосования · " + ((post.votes||0)+1); } });
      actions.append(vote);
      if (!post.id.startsWith("POST-DEMO")) {
        const pin = document.createElement("button"); pin.type="button"; pin.className="fb-small-button"; pin.textContent=post.pinned?"Открепить":"Закрепить";
        pin.addEventListener("click",()=>{post.pinned=!post.pinned;persist();renderPosts();}); actions.append(pin);
        const remove = document.createElement("button"); remove.type="button"; remove.className="fb-small-button"; remove.textContent="Удалить";
        remove.addEventListener("click",()=>{state.posts=state.posts.filter(item=>item.id!==post.id);persist();renderPosts();}); actions.append(remove);
      }
      const comments = document.createElement("div"); comments.className="fb-comment-list";
      (post.comments||[]).forEach(comment=>{const item=document.createElement("div");item.className="fb-comment";item.textContent=comment;comments.append(item);});
      const commentForm=document.createElement("form");commentForm.className="fb-comment-form";
      const input=document.createElement("input");input.maxLength=300;input.placeholder="Добавить комментарий";input.setAttribute("aria-label","Комментарий");
      const submit=document.createElement("button");submit.type="submit";submit.className="fb-small-button";submit.textContent="Ответить";
      commentForm.append(input,submit);
      commentForm.addEventListener("submit",event=>{event.preventDefault();if(!input.value.trim())return;if(post.id.startsWith("POST-DEMO")){const note=document.createElement("div");note.className="fb-comment";note.textContent="Демо: комментарии к примеру не сохраняются.";comments.append(note);input.value="";return;}post.comments=post.comments||[];post.comments.push(input.value.trim());persist();renderPosts();});
      article.append(top,title,body,meta,actions,comments,commentForm);feed.append(article);
    });
  };
  $("[data-fb-compose]").addEventListener("submit", event => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const title = safeText(data.get("title")).trim(), body = safeText(data.get("body")).trim();
    if (!title || !body) return;
    state.posts.push({ id:makeId("POST-DEMO"), title, body, kind:safeText(data.get("kind")), author:"Участник 1 · демо", createdAt:now(), pinned:false, votes:0, comments:[] });
    persist(); form.reset(); renderPosts();
  });
  $("[data-fb-filter]").addEventListener("change",renderPosts);
  renderPosts();

  let map = null, markerLayer = null, selectedPlace = null;
  let fallbackCenter = { lat: 59.9343, lon: 30.3351 };
  const currentPerson = () => $("[data-fb-person]").value;
  const statusOf = place => state.placeStates[currentPerson() + "|" + place.id] || "new";
  const statusLabel = status => ({ visited:"Были", wishlist:"Хотим посетить", planned:"Предложено / запланировано", new:"Ещё не отмечено" }[status] || "Ещё не отмечено");
  const statusClass = status => ({visited:"fb-dot-visited",wishlist:"fb-dot-wishlist",planned:"fb-dot-planned",new:"fb-dot-new"}[status] || "fb-dot-new");
  const placeDistance = (a,b) => {
    const rad=x=>x*Math.PI/180, R=6371000;
    const dLat=rad(b.lat-a.lat), dLon=rad(b.lon-a.lon);
    const h=Math.sin(dLat/2)**2+Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(dLon/2)**2;
    return 2*R*Math.asin(Math.sqrt(h));
  };
  const mapCenter = () => { const c=map ? map.getCenter() : fallbackCenter; return {lat:c.lat,lon:map ? c.lng : c.lon}; };
  const renderMapFallback = (message) => {
    const box = $("#fb-map");
    if (!box) return;
    box.replaceChildren();
    const panel = document.createElement("div");
    panel.className = "fb-map-fallback";
    const heading = document.createElement("strong");
    heading.textContent = "Карта доступна в резервном режиме";
    const note = document.createElement("p");
    note.textContent = message || "Внешняя библиотека карты не загрузилась. Список мест и отметки остаются доступны справа.";
    const link = document.createElement("a");
    link.href = "https://www.openstreetmap.org/#map=13/" + fallbackCenter.lat + "/" + fallbackCenter.lon;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Открыть эту область в OpenStreetMap ↗";
    panel.append(heading, note, link);
    box.append(panel);
  };
  const renderPlaceList = () => {
    const list=$("[data-fb-place-list]"); list.replaceChildren();
    const center=mapCenter();
    const places=state.places.map(place=>({...place,distance:placeDistance(center,{lat:place.lat,lon:place.lon})})).sort((a,b)=>a.distance-b.distance);
    places.forEach(place=>{
      const button=document.createElement("button");button.type="button";button.className="fb-place-item"+(selectedPlace&&selectedPlace.id===place.id?" is-selected":"");
      const dot=document.createElement("i");dot.className="fb-dot "+statusClass(statusOf(place));
      const copy=document.createElement("span");const name=document.createElement("strong");name.textContent=place.name;
      const sub=document.createElement("small");sub.textContent=place.category+" · "+(place.distance<1000?Math.round(place.distance)+" м":(place.distance/1000).toFixed(1).replace(".",",")+" км")+" · "+statusLabel(statusOf(place));
      copy.append(name,sub);button.append(dot,copy);button.addEventListener("click",()=>selectPlace(place,true));list.append(button);
    });
  };
  const renderMarkers = () => {
    if(map&&markerLayer){
      markerLayer.clearLayers();
      state.places.forEach(place=>{
        const status=statusOf(place);
        const colors={visited:"#2f7655",wishlist:"#bd8750",planned:"#637d9c",new:"#9a9a90"};
        const marker=L.circleMarker([place.lat,place.lon],{radius:9,color:"#fff",weight:2,fillColor:colors[status]||colors.new,fillOpacity:.95});
        marker.bindTooltip(place.name,{direction:"top"});
        marker.on("click",()=>selectPlace(place,false));
        marker.addTo(markerLayer);
      });
    }
    renderPlaceList();
  };
  const selectPlace = (place, pan) => {
    selectedPlace=place;
    if(pan&&map)map.setView([place.lat,place.lon],Math.max(map.getZoom(),14));
    else if(pan) { fallbackCenter = {lat:place.lat,lon:place.lon}; renderMapFallback("Выбрано место: " + place.name + ". Список и отметки работают; интерактивная подложка временно недоступна."); }
    const box=$("[data-fb-place-detail]");box.replaceChildren();
    const kicker=document.createElement("p");kicker.className="fb-kicker";kicker.textContent="КАРТОЧКА МЕСТА · "+place.id;
    const title=document.createElement("h3");title.textContent=place.name;
    const info=document.createElement("p");info.textContent=place.category+" · "+(place.city||"место из открытой карты")+". "+(place.demo?"Демонстрационная точка.":"Найдено в OpenStreetMap.");
    const label=document.createElement("label");label.className="fb-status-label";label.textContent="Отметка для выбранного участника";
    const select=document.createElement("select");select.className="fb-status-select";
    [["new","Ещё не отмечено"],["visited","Были"],["wishlist","Хотим посетить"],["planned","Предложено / запланировано"]].forEach(([value,text])=>{const option=document.createElement("option");option.value=value;option.textContent=text;select.append(option);});
    select.value=statusOf(place);
    select.addEventListener("change",()=>{state.placeStates[currentPerson()+"|"+place.id]=select.value;persist();renderMarkers();selectPlace(place,false);});
    const actions=document.createElement("div");actions.className="fb-place-detail-actions";actions.append(select);
    const source=document.createElement("p");source.className="fb-map-footnote";source.textContent=place.demo?"Данные точки приведены для демонстрации интерфейса.":"Источник: OpenStreetMap contributors.";
    box.append(kicker,title,info,label,actions,source);
    renderPlaceList();
  };
  const setMapStatus = message => { $("[data-fb-map-status]").textContent=message; };
  const initMap = () => {
    if(!window.L){
      setMapStatus("Интерактивная подложка OpenStreetMap не загрузилась. Список мест и личные отметки доступны в резервном режиме.");
      renderMapFallback();
      renderMarkers();
      return;
    }
    map=L.map("fb-map",{scrollWheelZoom:false}).setView([fallbackCenter.lat,fallbackCenter.lon],13);
    const tiles=L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'});
    let tileErrors=0;
    tiles.on("tileerror",()=>{
      tileErrors+=1;
      if(tileErrors>=4&&map){
        map.remove();
        map=null;
        markerLayer=null;
        setMapStatus("Подложка OpenStreetMap временно недоступна. Список мест и отметки работают в резервном режиме.");
        renderMapFallback("Не удалось загрузить карту OpenStreetMap. Выберите место из списка справа или откройте область на внешней карте.");
        renderMarkers();
      }
    });
    tiles.addTo(map);
    markerLayer=L.layerGroup().addTo(map);
    renderMarkers();
    map.on("moveend",renderPlaceList);
  };
  const searchCity = async city => {
    setMapStatus("Ищем координаты города…");
    try{
      const url="https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q="+encodeURIComponent(city);
      const response=await fetch(url,{headers:{Accept:"application/json"}});
      if(!response.ok)throw new Error("Геопоиск временно недоступен");
      const results=await response.json();if(!results.length)throw new Error("Город не найден");
      const point=results[0];
      fallbackCenter={lat:Number(point.lat),lon:Number(point.lon)};
      if(map)map.setView([fallbackCenter.lat,fallbackCenter.lon],13);
      else renderMapFallback("Центр поиска: " + point.display_name + ". Нажмите «Найти места рядом», чтобы загрузить точки из OpenStreetMap.");
      setMapStatus("Центр карты: "+point.display_name+". Нажмите ↻, чтобы найти достопримечательности в выбранном радиусе.");
    }catch(error){setMapStatus(error.message||"Не удалось найти город.");}
  };
  const findNearby = async () => {
    const center=mapCenter(),radius=Number($("[data-fb-radius]").value);
    setMapStatus("Запрашиваем открытые данные OpenStreetMap в радиусе "+(radius/1000)+" км…");
    const query='[out:json][timeout:25];(node["tourism"~"museum|attraction|gallery|artwork|viewpoint"](around:'+radius+','+center.lat+','+center.lon+');way["tourism"~"museum|attraction|gallery|artwork|viewpoint"](around:'+radius+','+center.lat+','+center.lon+');node["historic"~"monument|memorial|castle"](around:'+radius+','+center.lat+','+center.lon+');way["historic"~"monument|memorial|castle"](around:'+radius+','+center.lat+','+center.lon+');node["leisure"="park"](around:'+radius+','+center.lat+','+center.lon+');way["leisure"="park"](around:'+radius+','+center.lat+','+center.lon+'););out center tags;';
    try{
      const response=await fetch("https://overpass-api.de/api/interpreter",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"},body:"data="+encodeURIComponent(query)});
      if(!response.ok)throw new Error("Сервис OpenStreetMap ответил HTTP "+response.status);
      const data=await response.json();
      const found=(data.elements||[]).map(item=>{
        const tags=item.tags||{},centerPoint=item.center||item;
        const lat=Number(centerPoint.lat),lon=Number(centerPoint.lon),name=tags.name||tags["name:ru"]||tags.tourism||tags.historic||"Место без названия";
        if(!Number.isFinite(lat)||!Number.isFinite(lon))return null;
        const kind=tags.tourism==="museum"?"Музей":tags.tourism==="gallery"?"Галерея":tags.leisure==="park"?"Парк":tags.historic?"Историческое место":"Достопримечательность";
        return {id:"PLACE-OSM-DEMO-"+item.type+"-"+item.id,osmType:item.type,osmId:item.id,name,category:kind,lat,lon,city:"Область выбранной карты",demo:false};
      }).filter(Boolean);
      const unique=Array.from(new Map(found.map(p=>[p.id,p])).values());
      if(!unique.length){setMapStatus("В этом радиусе открытые данные не вернули подходящих мест. Измените радиус или центр карты.");return;}
      state.places=unique;
      selectedPlace=null;
      renderMarkers();
      if(map)map.fitBounds(L.latLngBounds(unique.map(p=>[p.lat,p.lon])).pad(.15));
      else {
        const first=unique[0];
        fallbackCenter={lat:first.lat,lon:first.lon};
        renderMapFallback("Загружено мест: " + unique.length + ". Выберите место в списке справа, чтобы открыть карточку и поставить личную отметку.");
      }
      setMapStatus("Найдено мест: "+unique.length+". Это данные OpenStreetMap, а не подтверждённые часы работы или посещения.");
      $("[data-fb-place-detail]").innerHTML='<p class="fb-kicker">РЕЗУЛЬТАТ ПОИСКА</p><h3>Места рядом загружены</h3><p>Выберите точку, чтобы добавить личную отметку. Посещение не определяется автоматически.</p>';
    }catch(error){setMapStatus((error.message||"Поиск не выполнен")+". Можно продолжить с демонстрационными точками.");}
  };
  $("[data-fb-city-search]").addEventListener("submit",event=>{event.preventDefault();searchCity($("#fb-city").value.trim());});
  $("[data-fb-person]").addEventListener("change",()=>{renderMarkers();if(selectedPlace)selectPlace(selectedPlace,false);});
  $("[data-fb-radius]").addEventListener("change",()=>setMapStatus("Радиус изменён. Нажмите ↻ для нового поиска."));
  $("[data-fb-refresh]").addEventListener("click",findNearby);
  $$("[data-fb-tab]").forEach(button=>button.addEventListener("click",()=>{
    $$("[data-fb-tab]").forEach(tab=>{const active=tab===button;tab.classList.toggle("is-active",active);tab.setAttribute("aria-selected",String(active));});
    $$("[data-fb-panel]").forEach(panel=>{panel.hidden=panel.dataset.fbPanel!==button.dataset.fbTab;});
    if(button.dataset.fbTab==="map"&&map)setTimeout(()=>map.invalidateSize(),80);
  }));
  initMap();
  if(window.location.hash==="#fb-map-panel"){
    const mapTab=$("[data-fb-tab='map']");
    if(mapTab)mapTab.click();
  }
  persist();
})();