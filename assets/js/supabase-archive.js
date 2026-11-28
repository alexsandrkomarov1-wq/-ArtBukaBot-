(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  // Public client configuration for the existing KOMAROVA_CORE Supabase project.
  // Publishable keys are designed for browser use; never place service_role/secret keys here.
  const SUPABASE_PROJECT_URL = "https://bcotusztvddzbnwefnrq.supabase.co";
  const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_OOJ5nZYn0rT8yJvcBjuWww_rfz0c-Rp";
  const bucket = "komarova_core_private";
  const MAX_UPLOAD_BYTES = 50 * 1024 * 1024;
  const status = $("cloud-archive-status");
  const connection = $("cloud-connection-state");
  if (!connection) return;
  const auth = $("cloud-auth");
  const panel = $("cloud-private-panel");
  let projectUrl = SUPABASE_PROJECT_URL;
  let anonKey = SUPABASE_PUBLISHABLE_KEY;
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
    ...(accessToken ? { Authorization: "Bearer " + accessToken } : {}),
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
  const storagePath = (userId, capturedAt, materialId, filename) => {
    const year = capturedAt ? String(new Date(capturedAt).getUTCFullYear()) : "Без_даты";
    return userId + "/" + year + "/" + materialId + "/" + encodeURIComponent(cleanName(filename));
  };

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

  async function connectProject() {
    try {
      connection.textContent = "Проверяем существующий проект KOMAROVA_CORE…";
      await request("/auth/v1/settings");
      connection.textContent = "Supabase KOMAROVA_CORE отвечает · войдите, чтобы проверить личный архив.";
      $("supabase-project-state").textContent = "Подключение к Supabase подтверждено. Приватный бакет и каталог созданы; доступ к ним проверяется после входа."
    } catch (error) {
      connection.textContent = "Supabase сейчас недоступен: " + error.message;
      $("supabase-project-state").textContent = "Проверка не пройдена. Файлы не загружались.";
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
      connection.textContent = "Учётная запись подтверждена · проверяем приватный каталог и хранилище.";
      passwordInput.value = "";
      await loadArchive();
      await checkBucket();
    } catch (error) {
      accessToken = "";
      currentUser = null;
      passwordInput.value = "";
      panel.hidden = true;
      auth.hidden = false;
      $("cloud-archive-list").replaceChildren();
      connection.textContent = "Вход не выполнен: " + error.message;
    }
  }

  async function checkBucket() {
    const probe = await request("/storage/v1/object/list/" + bucket, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prefix: currentUser.id + "/", limit: 1, offset: 0, sortBy: { column: "name", order: "asc" } })
    });
    if (!Array.isArray(probe)) throw new Error("Supabase Storage не подтвердил доступ к личной папке.");
    $("cloud-storage-location").textContent = "KOMAROVA_CORE · приватный бакет · папка текущего участника";
    connection.textContent = "Вход подтверждён · каталог и приватное хранилище доступны.";
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
    const folders = new Map();
    filtered.forEach(item => {
      const pathYear = String(item.storage_path || "").match(/\/(19|20)\d{2}\//)?.[0]?.replaceAll("/", "");
      const year = item.captured_at
        ? String(new Date(item.captured_at).getUTCFullYear())
        : (pathYear || "Без даты");
      if (!folders.has(year)) folders.set(year, []);
      folders.get(year).push(item);
    });
    const years = [...folders.keys()].sort((a, b) => {
      if (a === "Без даты") return 1;
      if (b === "Без даты") return -1;
      return Number(b) - Number(a);
    });
    years.forEach(year => {
      const folder = document.createElement("details");
      folder.className = "archive-year-folder";
      folder.open = true;
      const summary = document.createElement("summary");
      const label = document.createElement("span");
      label.className = "archive-year-folder-label";
      label.textContent = year === "Без даты" ? "Без подтверждённой даты" : year;
      const count = document.createElement("small");
      count.textContent = folders.get(year).length + " материалов";
      summary.append(label, count);
      folder.append(summary);
      const contents = document.createElement("div");
      contents.className = "archive-year-folder-items";
      folders.get(year).forEach(item => {
        const row = document.createElement("article");
        row.className = "media-item";
        const info = document.createElement("span");
        info.className = "media-item-info";
        const title = document.createElement("strong");
        title.textContent = item.title || item.original_filename;
        const meta = document.createElement("small");
        const date = item.captured_at
          ? new Date(item.captured_at).toLocaleDateString("ru-RU")
          : (item.created_at ? "Добавлено " + new Date(item.created_at).toLocaleDateString("ru-RU") : "дата не указана");
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
        contents.append(row);
      });
      folder.append(contents);
      list.append(folder);
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
    if (file.size > MAX_UPLOAD_BYTES) {
      setStatus("Файл превышает лимит бесплатного Supabase: 50 MiB на один файл. Выберите файл меньшего размера.", true);
      return;
    }
    const submit = $("cloud-upload-submit");
    let storageUploaded = false;
    let uploadedPath = "";
    submit.disabled = true;
    try {
      const materialId = makeMaterialId();
      const hash = await sha256(file);
      const duplicate = items.find(item => item.sha256 === hash);
      if (duplicate) throw new Error("Файл с таким SHA-256 уже есть в архиве: " + duplicate.material_id + ". Повторная копия не загружена.");
      const capturedAt = $("cloud-captured-at").value ? new Date($("cloud-captured-at").value + "T12:00:00Z").toISOString() : null;
      const path = storagePath(currentUser.id, capturedAt, materialId, file.name);
      uploadedPath = path;
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
      storageUploaded = true;
      const remoteBlob = await getFile({ storage_path: path });
      const remoteHash = await sha256(remoteBlob);
      if (remoteBlob.size !== file.size || remoteHash !== hash) {
        throw new Error("Проверочное чтение не совпало с оригиналом: размер или SHA-256 отличается. Запись каталога не создана; не повторяйте загрузку, пока не проверите объект.");
      }
      const record = {
        user_id: currentUser.id,
        material_id: materialId,
        storage_path: path,
        bucket_id: bucket,
        original_filename: file.name,
        title: $("cloud-upload-title").value.trim() || file.name,
        description: $("cloud-upload-description").value.trim() || null,
        captured_at: capturedAt,
        item_type: kindOf(file),
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        sha256: hash,
        person_id: $("cloud-person-id")?.value.trim() || null,
        event_id: $("cloud-event-id")?.value.trim() || null,
        place_id: $("cloud-place-id")?.value.trim() || null,
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
      $("cloud-upload-description").value = "";
      $("cloud-captured-at").value = "";
      await loadArchive();
      setStatus("Оригинал сохранён в приватном Storage и проверен обратным чтением. Размер и SHA-256 совпали. MATERIAL-ID: " + materialId + ". Оригинал не изменялся.");
    } catch (error) {
      const message = storageUploaded
        ? error.message + " Файл уже находится в приватном Storage по пути " + uploadedPath + "; не повторяйте загрузку, пока не проверите реестр."
        : error.message;
      setStatus(message, true);
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

  // Проверяем существующий проект автоматически; форму подключения не показываем.
  connectProject();
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