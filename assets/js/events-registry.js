(() => {
  const root=document.querySelector("[data-events-app]");if(!root)return;
  const $=s=>root.querySelector(s),status=$("[data-status]");let events=[],people=[];
  const message=(text,kind="info")=>{status.textContent=text;status.dataset.kind=kind;};
  const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const fillOptions=(selector,items,idKey,labelFn)=>{
    const select=$(selector);select.replaceChildren();
    items.forEach(item=>{const option=document.createElement("option");option.value=item[idKey];option.textContent=labelFn(item);select.append(option);});
  };
  async function refresh(){
    [events,people]=await Promise.all([
      KomCoreRegistry.request("/api/v1/events?limit=100"),
      KomCoreRegistry.request("/api/v1/people?limit=100")
    ]);
    const list=$("[data-events-list]");list.replaceChildren();
    if(!events.length)list.append(node("div","registry-empty","В реестре пока нет событий."));
    events.forEach(item=>{
      const card=node("article","registry-card");card.append(node("h3","",item.title),node("span","registry-id",item.event_id));
      card.append(node("p","registry-muted",item.occurred_at?new Date(item.occurred_at).toLocaleString("ru-RU"):"Дата не указана"));
      if(item.description)card.append(node("p","",item.description));
      list.append(card);
    });
    fillOptions("[data-event-link-form] [name=event_id]",events,"event_id",item=>item.title+" · "+item.event_id);
    fillOptions("[data-event-link-form] [name=person_id]",people,"person_id",item=>item.display_name+" · "+item.person_id);
  }
  $("[data-connect-form]").addEventListener("submit",async event=>{
    event.preventDefault();const form=event.currentTarget,data=new FormData(form),button=form.querySelector("button");button.disabled=true;message("Подключаемся к API…");
    try{
      const user=await KomCoreRegistry.login(data.get("api"),data.get("username"),data.get("password"));
      form.elements.password.value="";$("[data-workspace]").classList.remove("registry-hidden");
      $("[data-user-label]").textContent="Вход выполнен как "+user.username+" · роль "+user.role;
      await refresh();message("Сервер подключён. Реестр загружен.","success");
    }catch(error){$("[data-workspace]").classList.add("registry-hidden");message(error.message,"error");}
    finally{button.disabled=false;}
  });
  $("[data-event-form]").addEventListener("submit",async event=>{
    event.preventDefault();const form=event.currentTarget,data=new FormData(form),payload={
      title:String(data.get("title")).trim(),description:String(data.get("description")).trim()||null,
      occurred_at:data.get("occurred_at")?new Date(data.get("occurred_at")).toISOString():null
    };
    const button=form.querySelector("button");button.disabled=true;
    try{
      const created=await KomCoreRegistry.request("/api/v1/events",{method:"POST",body:JSON.stringify(payload)});
      form.reset();message("Создано событие "+created.event_id,"success");await refresh();
    }catch(error){message(error.message,"error");}
    finally{button.disabled=false;}
  });
  $("[data-event-link-form]").addEventListener("submit",async event=>{
    event.preventDefault();const data=new FormData(event.currentTarget);
    const payload={source_type:"event",source_id:data.get("event_id"),target_type:"person",target_id:data.get("person_id"),relationship_type:data.get("relationship_type")};
    const button=event.currentTarget.querySelector("button");button.disabled=true;
    try{const link=await KomCoreRegistry.request("/api/v1/entities/links",{method:"POST",body:JSON.stringify(payload)});message("Связь сохранена: "+link.link_id,"success");}
    catch(error){message(error.message,"error");}finally{button.disabled=false;}
  });
  $("[data-refresh]").addEventListener("click",()=>refresh().then(()=>message("Реестр обновлён.","success")).catch(e=>message(e.message,"error")));
})();