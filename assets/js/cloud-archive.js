(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const apiBase = String(window.KOMAROVA_API_BASE || "").replace(/\/$/, "");
  if (!apiBase) return;
  const tokenKey = "komarova_core_session";
  let token = sessionStorage.getItem(tokenKey) || "";
  let previewUrl = "";
  let sessionRole = "";
  let archiveItems = [];
  let archiveFilter = "all";
  const auth = $("cloud-auth");
  const panel = $("cloud-private-panel");
  const status = $("cloud-archive-status");
  const connection = $("cloud-connection-state");
  const headers = () => token ? { Authorization: "Bearer " + token } : {};
  const setStatus = (message, error = false) => {
    status.textContent = message;
    status.dataset.state = error ? "error" : "ok";
  };
  async function request(path, options = {}) {
    const response = await fetch(apiBase + path, {
      ...options,
      headers: { ...headers(), ...(options.headers || {}) }
    });
    const type = response.headers.get("content-type") || "";
    const body = type.includes("application/json") ? await response.json() : await response.text();
    if (!response.ok) throw new Error(body.detail?.message || body.detail || body.error || ("HTTP " + response.status));
    return body;
  }
  function showSession(user) {
    auth.hidden = true;
    panel.hidden = false;
    sessionRole = user.role;
    $("cloud-user-label").textContent = user.username + " · " + user.role;
    connection.textContent = "Закрытая сессия активна · проверяем хранилище";
  }
  async function checkStorage() {
    try {
      const result = await request("/api/v1/archive/storage/health");
      const label = result.backend === "local-private"
        ? "локальное приватное хранилище"
        : "S3-совместимое объектное хранилище";
      connection.textContent = "API доступен · " + label + " проверено";
    } catch (_) {
      connection.textContent = "API доступен · хранилище не подтверждено";
    }
  }
  function clearSession() {
    token = "";
    sessionRole = "";
    sessionStorage.removeItem(tokenKey);
    auth.hidden = false;
    panel.hidden = true;
    connection.textContent = "Не выполнен вход";
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = "";
  }
  async function loadPeople() {
    const people = await request("/api/v1/people?limit=100");
    const select = $("cloud-person-id");
    select.replaceChildren(new Option("Без привязки к человеку", ""));
    people.forEach(person => {
      const option = new Option(person.display_name + " · " + person.person_id, person.person_id);
      select.add(option);
    });
  }
  function renderArchive() {
    const list = $("cloud-archive-list");
    list.replaceChildren();
    const items = archiveItems.filter(item => {
      if (archiveFilter === "original") return !item.original_material_id;
      if (archiveFilter === "derivative") return Boolean(item.original_material_id);
      if (archiveFilter === "photo") return item.item_type === "photo";
      if (archiveFilter === "video") return item.item_type === "video";
      return true;
    });
    if (!items.length) {
      const empty = document.createElement("p");
      empty.className = "media-list-empty";
      empty.textContent = "В облачном архиве пока нет файлов.";
      list.append(empty);
    }
    for (const item of items) {
      const row = document.createElement("div");
      row.className = "media-item";
      const info = document.createElement("span");
      info.className = "media-item-info";
      const name = document.createElement("strong");
      name.textContent = item.title || item.original_filename;
      const meta = document.createElement("small");
      meta.textContent = (item.item_type === "photo" ? "Фото" : "Видео") + " · " + Math.round(item.size_bytes / 1024) + " КБ · MATERIAL-ID: " + item.material_id + (item.original_material_id ? " · производная от " + item.original_material_id : " · оригинал") + " · ARCHIVE-ID: " + item.archive_item_id;
      info.append(name, meta);
      const actions = document.createElement("span");
      actions.className = "cloud-item-actions";
      const view = document.createElement("button");
      view.type = "button";
      view.className = "media-button";
      if (item.record_status === "available" && item.storage_state === "verified") {
        view.textContent = "Просмотр";
        view.addEventListener("click", () => preview(item));
      } else {
        view.textContent = "На проверке";
        view.disabled = true;
        view.title = "Оригинал нельзя открыть до антивирусной проверки";
      }
      actions.append(view);
      if (sessionRole === "owner" || sessionRole === "moderator") {
        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "media-button";
        remove.textContent = "Удалить";
        remove.addEventListener("click", () => removeItem(item));
        actions.append(remove);
      }
      row.append(info, actions);
      list.append(row);
    }
    setStatus("Записей: " + items.length + ". Новые материалы остаются в карантине до антивирусной проверки.");
  }
  async function loadArchive() {
    archiveItems = await request("/api/v1/archive/items?limit=100");
    renderArchive();
    setStatus("Материалов в архиве: " + archiveItems.length + ". MATERIAL-ID отображается из ответа API; оригиналы и производные версии разделены.");
  }
  document.querySelectorAll("[data-cloud-filter]").forEach(button => button.addEventListener("click", () => {
    archiveFilter = button.dataset.cloudFilter;
    document.querySelectorAll("[data-cloud-filter]").forEach(item => {
      const active = item === button;
      item.classList.toggle("is-active", active);
      item.setAttribute("aria-pressed", String(active));
    });
    renderArchive();
  }));
  async function preview(item) {
    try {
      const response = await fetch(apiBase + "/api/v1/archive/items/" + encodeURIComponent(item.archive_item_id) + "/content", { headers: headers() });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const blob = await response.blob();
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      previewUrl = URL.createObjectURL(blob);
      $("cloud-preview").hidden = false;
      $("cloud-preview-name").textContent = item.title || item.original_filename;
      const isVideo = item.item_type === "video";
      $("cloud-preview-image").hidden = isVideo;
      $("cloud-preview-video").hidden = !isVideo;
      if (isVideo) {
        $("cloud-preview-video").src = previewUrl;
        $("cloud-preview-video").load();
      } else {
        $("cloud-preview-image").src = previewUrl;
        $("cloud-preview-image").alt = item.original_filename;
      }
      setStatus("Файл получен из приватного uploads и открыт в просмотрщике.");
    } catch (error) { setStatus("Не удалось открыть файл: " + error.message, true); }
  }
  async function removeItem(item) {
    if (!window.confirm("Удалить файл из закрытого облачного архива? Операция удалит объект из uploads.")) return;
    try {
      await request("/api/v1/archive/items/" + encodeURIComponent(item.archive_item_id), { method: "DELETE" });
      if (!$("cloud-preview").hidden && $("cloud-preview-name").textContent === (item.title || item.original_filename)) {
        $("cloud-preview").hidden = true;
      }
      await loadArchive();
    } catch (error) { setStatus("Удаление не выполнено: " + error.message, true); }
  }
  $("cloud-login-form").addEventListener("submit", async event => {
    event.preventDefault();
    try {
      const result = await request("/api/v1/auth/login", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: $("cloud-username").value, password: $("cloud-password").value })
      });
      token = result.access_token;
      sessionStorage.setItem(tokenKey, token);
      showSession(result.user);
      await checkStorage();
      await loadPeople(); await loadArchive();
      $("cloud-password").value = "";
    } catch (error) { connection.textContent = "Ошибка входа: " + error.message; }
  });
  $("cloud-bootstrap-form").addEventListener("submit", async event => {
    event.preventDefault();
    try {
      const bootstrapToken = $("cloud-bootstrap-token").value;
      const user = await fetch(apiBase + "/api/v1/auth/bootstrap", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Core-Bootstrap-Token": bootstrapToken },
        body: JSON.stringify({ username: $("cloud-owner-username").value, password: $("cloud-owner-password").value })
      });
      const body = await user.json();
      if (!user.ok) throw new Error(body.detail || ("HTTP " + user.status));
      $("cloud-bootstrap-token").value = "";
      $("cloud-owner-password").value = "";
      connection.textContent = "Владелец создан. Теперь войдите под новым логином.";
      $("cloud-username").value = body.username;
      $("cloud-password").focus();
    } catch (error) { connection.textContent = "Настройка не выполнена: " + error.message; }
  });
  $("cloud-upload-form").addEventListener("submit", async event => {
    event.preventDefault();
    const file = $("cloud-upload-file").files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    form.append("title", $("cloud-upload-title").value);
    if ($("cloud-person-id").value) form.append("person_id", $("cloud-person-id").value);
    try {
      setStatus("Загружаю файл в закрытое хранилище…");
      await request("/api/v1/archive/items", { method: "POST", body: form });
      $("cloud-upload-form").reset();
      await loadArchive();
      setStatus("Загрузка завершена. Материал сохранён в карантине; просмотр станет доступен после проверки.");
    } catch (error) { setStatus("Загрузка не выполнена: " + error.message, true); }
  });
  $("cloud-logout").addEventListener("click", async () => {
    try { await request("/api/v1/auth/logout", { method: "POST" }); } catch (_) {}
    clearSession();
  });
  $("cloud-preview-close").addEventListener("click", () => {
    $("cloud-preview").hidden = true;
    $("cloud-preview-video").pause();
    $("cloud-preview-video").removeAttribute("src");
    $("cloud-preview-image").removeAttribute("src");
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = "";
  });
  fetch(apiBase + "/health").then(r => r.ok ? r.json() : Promise.reject()).then(() => {
    connection.textContent = "API доступен · войдите для проверки хранилища";
  }).catch(() => { connection.textContent = "API пока недоступен"; });
  if (token) {
    request("/api/v1/auth/me").then(async user => {
      showSession(user); await checkStorage(); await loadPeople(); await loadArchive();
    }).catch(clearSession);
  }
})();