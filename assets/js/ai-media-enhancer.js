(() => {
  "use strict";

  const root = document.querySelector("[data-ai-media-lab]");
  if (!root) return;

  const MAX_BYTES = 100 * 1024 * 1024;
  const MAX_PIXELS = 30000000;
  const input = root.querySelector("[data-ai-file-input]");
  const upload = root.querySelector("[data-ai-upload]");
  const viewStage = root.querySelector("[data-ai-view]");
  const exportButton = root.querySelector("[data-ai-export]");
  const reset = root.querySelector("[data-ai-reset]");
  const info = root.querySelector("[data-ai-file-info]");
  const status = root.querySelector("[data-ai-status]");
  const mode = root.querySelector("[data-ai-mode]");
  const preview = root.querySelector("[data-ai-preview]");
  const originalImage = root.querySelector("[data-ai-original-preview]");
  const originalVideo = root.querySelector("[data-ai-video-preview]");
  const resultImage = root.querySelector("[data-ai-result-preview]");
  const resultVideo = root.querySelector("[data-ai-result-video]");
  const originalEmpty = root.querySelector("[data-ai-original-empty]");
  const resultEmpty = root.querySelector("[data-ai-result-empty]");
  const viewTitle = viewStage.querySelector(".ai-media-action-title");
  const viewNote = viewStage.querySelector(".ai-media-action-note");

  let sourceFile = null;
  let sourceUrl = null;
  let resultFile = null;
  let resultUrl = null;
  let generation = 0;
  let archiveResult = null;

  function releaseUrl(url) {
    if (url) URL.revokeObjectURL(url);
  }

  function setStage(title, note) {
    viewTitle.textContent = title;
    viewNote.textContent = note;
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " Б";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " КБ";
    return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
  }

  async function sha256(blob) {
    if (!window.crypto || !crypto.subtle) throw new Error("Проверка SHA-256 недоступна в этом браузере.");
    const digest = await crypto.subtle.digest("SHA-256", await blob.arrayBuffer());
    return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  }

  function clearResult() {
    releaseUrl(resultUrl);
    resultUrl = null;
    resultFile = null;
    archiveResult = null;
    resultImage.removeAttribute("src");
    resultImage.hidden = true;
    resultVideo.pause();
    resultVideo.removeAttribute("src");
    resultVideo.load();
    resultVideo.hidden = true;
    resultEmpty.hidden = false;
    exportButton.disabled = true;
  }

  function clearWorkspace() {
    generation += 1;
    clearResult();
    releaseUrl(sourceUrl);
    sourceUrl = null;
    sourceFile = null;
    input.value = "";
    originalImage.removeAttribute("src");
    originalImage.hidden = true;
    originalVideo.pause();
    originalVideo.removeAttribute("src");
    originalVideo.load();
    originalVideo.hidden = true;
    originalEmpty.hidden = false;
    preview.hidden = true;
    reset.disabled = true;
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    setStage("Автоматическое улучшение", "Запускается сразу после проверки выбранного оригинала");
    info.textContent = "Файл ещё не выбран. Выберите фотографию или видео.";
    status.textContent = "Оригинал не изменяется. После выбора начнётся автоматическая проверка.";
  }

  function showOriginal(file) {
    releaseUrl(sourceUrl);
    sourceFile = file;
    sourceUrl = URL.createObjectURL(file);
    clearResult();
    preview.hidden = false;
    originalEmpty.hidden = true;
    originalImage.hidden = true;
    originalVideo.hidden = true;
    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      mode.textContent = "ОРИГИНАЛ ПРОВЕРЯЕТСЯ";
    } else {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ОРИГИНАЛ ПРОВЕРЯЕТСЯ";
    }
    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + (file.type || "тип не определён");
    reset.disabled = false;
  }

  async function runPrivateWorker(file, token) {
    const config = window.KOMAROVA_CORE_API;
    if (!config || !config.baseUrl || !config.accessToken) return null;
    const base = config.baseUrl.replace(/\/+$/, "");
    const headers = { Authorization: "Bearer " + config.accessToken };
    const form = new FormData();
    form.append("file", file, file.name);
    const uploadedResponse = await fetch(base + "/api/v1/archive/items", {
      method: "POST", headers, body: form, cache: "no-store"
    });
    if (!uploadedResponse.ok) throw new Error("Архив не принял оригинал: HTTP " + uploadedResponse.status);
    const original = await uploadedResponse.json();
    if (token !== generation) throw new Error("Выбран другой файл.");

    const scanResponse = await fetch(base + "/api/v1/archive/items/" + encodeURIComponent(original.archive_item_id) + "/scan", {
      method: "POST", headers, cache: "no-store"
    });
    if (!scanResponse.ok) throw new Error("Проверка безопасности не завершена: HTTP " + scanResponse.status);
    const scan = await scanResponse.json();
    if (scan.scan_status !== "clean") throw new Error("Оригинал не прошёл антивирусную проверку.");

    setStage("Обработка проверенного оригинала", "Real-ESRGAN NCNN Vulkan x4 · видео x2");
    status.textContent = "Оригинал проверен и сохранён. Запущена автоматическая обработка отдельной копии.";
    const enhancedResponse = await fetch(base + "/api/v1/archive/items/" + encodeURIComponent(original.archive_item_id) + "/enhance", {
      method: "POST", headers, cache: "no-store"
    });
    if (!enhancedResponse.ok) throw new Error("Обработка не завершилась: HTTP " + enhancedResponse.status);
    const derivative = await enhancedResponse.json();
    if (token !== generation) throw new Error("Выбран другой файл.");

    const contentResponse = await fetch(base + "/api/v1/archive/items/" + encodeURIComponent(derivative.archive_item_id) + "/content", {
      method: "GET", headers, cache: "no-store"
    });
    if (!contentResponse.ok) throw new Error("Не удалось получить проверенную копию: HTTP " + contentResponse.status);
    const blob = await contentResponse.blob();
    const result = new File([blob], file.name.replace(/\.[^.]+$/, "") + "-enhanced" + (file.type.startsWith("video/") ? ".mp4" : ".png"), {
      type: blob.type || (file.type.startsWith("video/") ? "video/mp4" : "image/webp"),
      lastModified: Date.now()
    });
    return { file: result, material: derivative };
  }

  async function displayResult(file, token, material) {
    if (token !== generation) return;
    resultFile = file;
    resultUrl = URL.createObjectURL(file);
    resultEmpty.hidden = true;
    if (file.type.startsWith("video/")) {
      resultVideo.src = resultUrl;
      resultVideo.hidden = false;
      resultImage.hidden = true;
    } else {
      resultImage.src = resultUrl;
      resultImage.hidden = false;
      resultVideo.hidden = true;
    }
    archiveResult = material || null;
    exportButton.disabled = false;
    mode.textContent = material ? "КОПИЯ СОХРАНЕНА В АРХИВЕ" : "ЛОКАЛЬНАЯ КОПИЯ ГОТОВА";
    setStage("Копия создана и проверена", material ? "MATERIAL-ID: " + material.material_id : "Локальный результат · постоянный MATERIAL-ID появится после подключения архива");
    status.textContent = material
      ? "Готово. MATERIAL-ID " + material.material_id + " связан с оригиналом " + material.original_material_id + ". Конвейер: " + material.engine + "."
      : "Готово. Создана отдельная локальная копия (" + formatBytes(file.size) + "). Оригинал не изменён. Постоянная архивная регистрация не выполнялась.";
  }

  async function processSelected(file, token) {
    setStage("Проверка исходного файла", "Проверка типа, размера и контрольной суммы");
    status.textContent = "Проверяется оригинал. Исходный файл не изменяется.";
    const sourceHashBefore = await sha256(file);
    try {
      const serverResult = await runPrivateWorker(file, token);
      if (serverResult) {
        const sourceHashAfter = await sha256(file);
        if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
        await displayResult(serverResult.file, token, serverResult.material);
        return;
      }
      if (file.type.startsWith("video/")) {
        setStage("Ожидается AI video worker", "Real-ESRGAN x2 · FFmpeg · сохранение аудио");
        resultEmpty.textContent = "AI-обработка видео появится после подключения частного worker. Исходник не изменён, фиктивный ролик не создаётся.";
        resultEmpty.hidden = false;
        status.textContent = "Оригинал видео выбран. Локально проверены формат, размер и SHA-256; антивирусная проверка ClamAV не запускалась. Для улучшения требуется частный backend с Real-ESRGAN, FFmpeg и моделью.";
        mode.textContent = "AI VIDEO WORKER НЕ ПОДКЛЮЧЁН";
        return;
      }
      setStage("Ожидается AI worker", "Real-ESRGAN NCNN Vulkan · суперразрешение x4");
      mode.textContent = "AI WORKER НЕ ПОДКЛЮЧЁН";
      resultEmpty.textContent = "Настоящее AI-улучшение появится после подключения частного worker. Сейчас здесь не показывается поддельная копия.";
      resultEmpty.hidden = false;
      const sourceHashAfter = await sha256(file);
      if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
      status.textContent = "Оригинал сохранён без изменений. Локально проверены формат, размер и SHA-256; ClamAV не запускался, поскольку публичный сайт не подключён к частному backend. Для AI-улучшения требуется Real-ESRGAN worker и файлы модели. Внешний EzEnhancer доступен отдельно по ссылке ниже.";
      exportButton.disabled = true;
    } catch (error) {
      if (token !== generation) return;
      setStage("Обработка остановлена", "Оригинал сохранён без изменений");
      mode.textContent = "ОШИБКА ОБРАБОТКИ";
      status.textContent = "Не удалось создать проверенную копию: " + error.message + ". Исходный файл не изменён.";
    }
  }

  upload.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    const file = input.files && input.files[0];
    if (!file) return;
    if (!(file.type.startsWith("image/") || file.type.startsWith("video/"))) {
      status.textContent = "Файл не распознан как фотография или видео. Он не принят.";
      input.value = "";
      return;
    }
    if (!file.size || file.size > MAX_BYTES) {
      status.textContent = !file.size ? "Файл пустой." : "Файл превышает лимит 100 МБ.";
      input.value = "";
      return;
    }
    generation += 1;
    const token = generation;
    showOriginal(file);
    void processSelected(file, token);
  });

  exportButton.addEventListener("click", () => {
    if (!resultFile || !resultUrl) return;
    const link = document.createElement("a");
    link.href = resultUrl;
    link.download = resultFile.name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    status.textContent = "Скачивание отдельной копии начато. Оригинал сохранён отдельно.";
  });

  reset.addEventListener("click", clearWorkspace);
  exportButton.disabled = true;
  preview.hidden = true;
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();