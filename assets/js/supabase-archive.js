(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const form = $("supabase-connect-form");
  if (!form) return;

  const bucket = "komarova_core_private";
  const status = $("cloud-archive-status");
  const connection = $("cloud-connection-state");
  const auth = $("cloud-auth");
  const panel = $("cloud-private-panel");
  let projectUrl = "";
  let anonKey = "";
  let accessToken = "";
  let currentUser = null;
  let items = [];
  let filter = "all";
  let previewUrl = "";

  const setStatus = (message, error = false) => {
    status.textContent = message;
    status.dataset.state = error ? "error" : "ok";
  };
  const headers = (extra = {}) => ({
    apikey: anonKey,
    Authorization: "Bearer " + (accessToken || anonKey),
    ...extra
  });
  const api = (path) => projectUrl + path;
  const safeJson = async (response) => {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.msg || payload.message || payload.error_description || payload.error || payload.hint || ("HTTP " + response.status);
      throw new Error(String(detail));
    }
    return payload;
  };
  const kindOf = (file) => {
    if (file.type.startsWith("image/")) return "photo";
    if (file.type.startsWith("video/")) return "video";
    if (file.type.startsWith("audio/")) return "audio";
    return "document";
  };
  const makeMaterialId = () => "M-" + crypto.randomUUID().toUpperCase();
  const sha256 = async (file) => {
    const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  };
  const cleanName = (name) => name.normalize("NFKC").replace(/[^\p{L}\p{N}._ -]/gu, "_").slice(0, 180) || "file";
  const storagePath = (userId, materialId, filename) =>
    userId + "/" + materialId + "/" + encodeURIComponent(cleanName(filename));

  async function request(path, options = {}) {
    let response;
    try {
      response = await fetch(api(path), {
        ...options,
        headers: headers(options.headers || {}),
        cache: "no-store"
      });
    } catch (_) {
      throw new Error("Не удалось связаться с Supabase. Проверьте URL проекта и доступность сети.");
    }
    return safeJson(response);
  }

  async function connectProject(event) {
    event.preventDefault();
    const urlInput = $("supabase-project-url");
    const keyInput = $("supabase-anon-key");
    try {
      const parsed = new URL(urlInput.value.trim());
      if (parsed.protocol !== "https:" || !/\.supabase\.co$/.test(parsed.hostname)) {
        throw new Error("Укажите HTTPS Project URL вашего проекта Supabase.");
      }
      if (!keyInput.value.trim()) throw new Error("Введите публичный anon/publishable key. Service role key сюда вводить нельзя.");
      projectUrl = parsed.origin;
      anonKey = keyInput.value.trim();
      connection.textContent = "Проверка Supabase…";
      await request("/auth/v1/settings");
      connection.textContent = "Supabase доступен · проект отвечает. Войдите в семейный аккаунт.";
      $("supabase-project-state").textContent = "Подключение проверено для этой вкладки. URL и публичный ключ остаются только в памяти страницы.";
      $("supabase-login-email").focus();
    } catch (error) {
      projectUrl = "";
      anonKey = "";
      connection.textContent = "Supabase не подключён: " + error.message;
    }
  }

  async function login(event) {
    event.preventDefault();
    const email = $("cloud-username").value.trim();
    const passwordInput = $("cloud-password");
    const password = passwordInput.value;
    try {
      if (!projectUrl || !anonKey) throw new Error("Сначала проверьте подключение проекта Supabase.");
      const result = await request("/auth/v1/token?grant_type=password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      accessToken = result.access_token;
      currentUser = result.user;
      if (!accessToken || !currentUser?.id) throw new Error("Supabase не вернул подтверждённую пользовательскую сессию.");
      auth.hidden = true;
      panel.hidden = false;
      $("cloud-user-label").textContent = (currentUser.email || email) + " · защищённая сессия";
      connection.textContent = "Supabase Auth активен · Storage: приватный bucket";
      passwordInput.value = "";
      await loadArchive();
      await checkBucket();
    } catch (error) {
      accessToken = "";
      currentUser = null;
      passwordInput.value = "";
      connection.textContent = "Вход не выполнен: " + error.message;
    }
  }

  async function checkBucket() {
    try {
      await request("/storage/v1/bucket/" + bucket);
      $("cloud-storage-location").textContent = "Supabase Storage · " + bucket + " · private";
    } catch (_) {
      $("cloud-storage-location").textContent = "Supabase Storage · bucket не подтверждён. Выполните SQL-настройку ниже.";
    }
  }

  async function loadArchive() {
    const query = "?select=*&user_id=eq." + encodeURIComponent(currentUser.id) + "&order=created_at.desc&limit=200";
    items = await request("/rest/v1/archive_items" + query, {
      headers: { Accept: "application/json" }
    });
    renderArchive();
    setStatus("Записей в закрытом архиве: " + items.length + ". Отображаются только материалы текущей учётной записи.");
  }

  function renderArchive() {
    const list = $("cloud-archive-list");
    list.replaceChildren();
    const filtered = items.filter(item => filter === "all" || item.item_type === filter);
    if (!filtered.length) {
      const empty = document.createElement("p");
      empty.className = "media-list-empty";
      empty.textContent = "В этой категории пока нет файлов.";
      list.append(empty);
      return;
    }
    filtered.forEach(item => {
      const row = document.createElement("article");
      row.className = "media-item";
      const info = document.createElement("span");
      info.className = "media-item-info";
      const title = document.createElement("strong");
      title.textContent = item.title || item.original_filename;
      const meta = document.createElement("small");
      const date = item.created_at ? new Date(item.created_at).toLocaleString("ru-RU") : "дата не указана";
      meta.textContent = item.item_type + " · " + Math.ceil(item.size_bytes / 1024) + " КБ · " + date + " · " + item.material_id;
      info.append(title, meta);
      const actions = document.createElement("span");
      actions.className = "cloud-item-actions";
      if (["photo", "video"].includes(item.item_type)) {
        const view = document.createElement("button");
        view.type = "button";
        view.className = "media-button";
        view.textContent = "Просмотр";
        view.addEventListener("click", () => preview(item));
        actions.append(view);
      }
      const download = document.createElement("button");
      download.type = "button";
      download.className = "media-button";
      download.textContent = "Скачать";
      download.addEventListener("click", () => downloadItem(item));
      actions.append(download);
      row.append(info, actions);
      list.append(row);
    });
  }

  async function getFile(item) {
    const response = await fetch(api("/storage/v1/object/" + bucket + "/" + item.storage_path), {
      headers: headers(),
      cache: "no-store"
    });
    if (!response.ok) {
      const message = await response.text().catch(() => "");
      throw new Error("Файл не получен из Supabase Storage: HTTP " + response.status + (message ? " · " + message.slice(0, 180) : ""));
    }
    return response.blob();
  }

  async function preview(item) {
    try {
      const blob = await getFile(item);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      previewUrl = URL.createObjectURL(blob);
      $("cloud-preview").hidden = false;
      $("cloud-preview-name").textContent = item.title || item.original_filename;
      const video = item.item_type === "video";
      $("cloud-preview-image").hidden = video;
      $("cloud-preview-video").hidden = !video;
      if (video) {
        $("cloud-preview-video").src = previewUrl;
        $("cloud-preview-video").load();
      } else {
        $("cloud-preview-image").src = previewUrl;
        $("cloud-preview-image").alt = item.original_filename;
      }
      setStatus("Оригинал открыт из закрытого Supabase Storage. Файл не изменялся.");
    } catch (error) {
      setStatus(error.message, true);
    }
  }

  async function downloadItem(item) {
    try {
      const blob = await getFile(item);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = item.original_filename;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 30000);
      setStatus("Скачивание оригинала начато.");
    } catch (error) {
      setStatus(error.message, true);
    }
  }

  async function uploadFile(event) {
    event.preventDefault();
    const fileInput = $("cloud-upload-file");
    const file = fileInput.files?.[0];
    if (!file || !currentUser) return;
    const submit = $("cloud-upload-submit");
    submit.disabled = true;
    try {
      const materialId = makeMaterialId();
      const hash = await sha256(file);
      const path = storagePath(currentUser.id, materialId, file.name);
      const uploadResponse = await fetch(api("/storage/v1/object/" + bucket + "/" + path), {
        method: "POST",
        headers: headers({
          "Content-Type": file.type || "application/octet-stream",
          "x-upsert": "false",
          "cache-control": "3600"
        }),
        body: file,
        cache: "no-store"
      });
      if (!uploadResponse.ok) {
        const detail = await uploadResponse.text().catch(() => "");
        throw new Error("Supabase Storage отклонил загрузку: HTTP " + uploadResponse.status + (detail ? " · " + detail.slice(0, 220) : ""));
      }
      const record = {
        user_id: currentUser.id,
        material_id: materialId,
        storage_path: path,
        bucket_id: bucket,
        original_filename: file.name,
        title: $("cloud-upload-title").value.trim() || file.name,
        item_type: kindOf(file),
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        sha256: hash,
        person_id: $("cloud-person-id").value.trim() || null,
        event_id: $("cloud-event-id").value.trim() || null,
        place_id: $("cloud-place-id").value.trim() || null,
        record_status: "stored_original"
      };
      const inserted = await request("/rest/v1/archive_items", {
        method: "POST",
        headers: { "Content-Type": "application/json", Prefer: "return=representation" },
        body: JSON.stringify(record)
      });
      if (!Array.isArray(inserted) || !inserted.length) {
        throw new Error("Файл загружен, но реестр не подтвердил запись. Оригинал сохранён в Storage; не повторяйте загрузку, пока не проверите каталог.");
      }
      fileInput.value = "";
      $("cloud-upload-title").value = "";
      await loadArchive();
      setStatus("Оригинал сохранён в закрытом Supabase Storage. MATERIAL-ID: " + materialId + ". SHA-256 рассчитан; файл не обрабатывался и не перезаписывался.");
    } catch (error) {
      setStatus(error.message, true);
    } finally {
      submit.disabled = false;
    }
  }

  function logout() {
    accessToken = "";
    currentUser = null;
    items = [];
    panel.hidden = true;
    auth.hidden = false;
    $("cloud-password").value = "";
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = "";
    $("cloud-preview").hidden = true;
    $("cloud-archive-list").replaceChildren();
    connection.textContent = "Сессия завершена. Данные доступа очищены из памяти страницы.";
  }

  form.addEventListener("submit", connectProject);
  $("cloud-login-form").addEventListener("submit", login);
  $("cloud-upload-form").addEventListener("submit", uploadFile);
  $("cloud-logout").addEventListener("click", logout);
  $("cloud-preview-close").addEventListener("click", () => {
    $("cloud-preview-video").pause();
    $("cloud-preview").hidden = true;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = "";
  });
  document.querySelectorAll("[data-cloud-filter]").forEach(button => {
    button.addEventListener("click", () => {
      filter = button.dataset.cloudFilter;
      document.querySelectorAll("[data-cloud-filter]").forEach(other => {
        const active = other === button;
        other.classList.toggle("is-active", active);
        other.setAttribute("aria-pressed", String(active));
      });
      renderArchive();
    });
  });
  window.addEventListener("pagehide", () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    accessToken = "";
  });
})();