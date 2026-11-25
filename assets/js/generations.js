(() => {
  const root=document.querySelector("[data-generation-app]");
  if(!root)return;
  const $=s=>root.querySelector(s);
  const status=$("[data-status]");
  const workspace=$("[data-workspace]");
  const linksPanel=$("[data-links-panel]");
  let people=[];
  const message=(text,kind="info")=>{status.textContent=text;status.dataset.kind=kind;};
  const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
  const fillSelects=()=>{
    const from=$("[data-link-form] [name=from_person_id]");
    const to=$("[data-link-form] [name=to_person_id]");
    [from,to].forEach(select=>{select.replaceChildren();people.forEach(person=>{const option=document.createElement("option");option.value=person.person_id;option.textContent=person.display_name+" · "+person.person_id;select.append(option);});});
  };
  async function loadPeople(){
    const records=await KomCoreRegistry.request("/api/v1/people?limit=100");
    people=records;
    const list=$("[data-people-list]");list.replaceChildren();
    if(!people.length){list.append(node("div","registry-empty","В серверном реестре пока нет людей."));}
    for(const person of people){
      const card=node("article","registry-card");
      card.append(node("h3","",person.display_name),node("span","registry-id",person.person_id),node("span","registry-tag",person.status==="active"?"Активная запись":"Архивная запись"));
      const relationList=node("div","registry-muted","Загружаем связи…");card.append(relationList);list.append(card);
      try{
        const relations=await KomCoreRegistry.request("/api/v1/people/"+encodeURIComponent(person.person_id)+"/relationships");
        relationList.replaceChildren();
        if(!relations.length)relationList.textContent="Связей пока нет.";
        relations.forEach(rel=>{
          const otherId=rel.from_person_id===person.person_id?rel.to_person_id:rel.from_person_id;
          const other=people.find(p=>p.person_id===otherId);
          relationList.append(node("p","",rel.relationship_type+" → "+(other?other.display_name:otherId)));
        });
      }catch(error){relationList.textContent="Не удалось загрузить связи: "+error.message;}
    }
    fillSelects();
    linksPanel.classList.toggle("registry-hidden",people.length<2);
  }
  $("[data-connect-form]").addEventListener("submit",async event=>{
    event.preventDefault();const form=event.currentTarget;const data=new FormData(form);
    const button=form.querySelector("button");button.disabled=true;message("Проверяем адрес API и выполняем вход…");
    try{
      const user=await KomCoreRegistry.login(data.get("api"),data.get("username"),data.get("password"));
      workspace.classList.remove("registry-hidden");message("Подключено: "+user.username+" · роль "+user.role,"success");
      $("[data-user-label]").textContent="Вход выполнен как "+user.username+". Токен хранится только в памяти страницы.";
      form.elements.password.value="";
      await loadPeople();
    }catch(error){form.elements.password.value="";workspace.classList.add("registry-hidden");message(error.message,"error");}
    finally{button.disabled=false;}
  });
  $("[data-person-form]").addEventListener("submit",async event=>{
    event.preventDefault();const form=event.currentTarget;const button=form.querySelector("button");button.disabled=true;
    try{
      const display_name=new FormData(form).get("display_name").trim();
      const person=await KomCoreRegistry.request("/api/v1/people",{method:"POST",body:JSON.stringify({display_name})});
      form.reset();message("Создана запись "+person.person_id,"success");await loadPeople();
    }catch(error){message(error.message,"error");}
    finally{button.disabled=false;}
  });
  $("[data-link-form]").addEventListener("submit",async event=>{
    event.preventDefault();const form=event.currentTarget;const data=Object.fromEntries(new FormData(form).entries());const button=form.querySelector("button");button.disabled=true;
    try{
      const result=await KomCoreRegistry.request("/api/v1/relationships",{method:"POST",body:JSON.stringify(data)});
      message("Связь сохранена: "+result.relationship_id,"success");form.reset();await loadPeople();
    }catch(error){message(error.message,"error");}
    finally{button.disabled=false;}
  });
  $("[data-refresh]").addEventListener("click",()=>loadPeople().then(()=>message("Реестр обновлён.","success")).catch(e=>message(e.message,"error")));
})();