(() => {
  "use strict";

  const root = document.querySelector("[data-ai-media-lab]");
  if (!root) return;

  const MAX_BYTES = 100 * 1024 * 1024;
  const MAX_PIXELS = 30000000;
  const input = root.querySelector("[data-ai-file-input]");
  const upload = root.querySelector("[data-ai-upload]");
  const videoUpload = root.querySelector("[data-ai-upload-video]");
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
  const qualityControl = root.querySelector("[data-ai-quality]");
  const qualityValue = root.querySelector("[data-ai-quality-value]");
  const zoomControl = root.querySelector("[data-ai-zoom]");
  const zoomValue = root.querySelector("[data-ai-zoom-value]");
  const trimStart = root.querySelector("[data-ai-trim-start]");
  const trimEnd = root.querySelector("[data-ai-trim-end]");
  const cropX = root.querySelector("[data-ai-crop-x]");
  const cropY = root.querySelector("[data-ai-crop-y]");
  const cropWidth = root.querySelector("[data-ai-crop-width]");
  const cropHeight = root.querySelector("[data-ai-crop-height]");
  const audioEnhance = root.querySelector("[data-ai-audio-enhance]");
  const videoSettings = root.querySelector("[data-ai-video-settings]");
  const videoEditor = root.querySelector("[data-ai-video-editor]");
  const openVideoEditor = root.querySelector("[data-ai-open-video-editor]");
  const closeVideoEditor = root.querySelector("[data-ai-close-video-editor]");
  const reprocessButton = root.querySelector("[data-ai-reprocess]");
  const privateApi = window.KOMAROVA_CORE_PRIVATE_API || null;
  const viewTitle = viewStage.querySelector(".ai-media-action-title");
  const viewNote = viewStage.querySelector(".ai-media-action-note");

  let sourceFile = null;
  let sourceUrl = null;
  let resultFile = null;
  let resultUrl = null;
  let generation = 0;
  let archiveResult = null;
  let archiveOriginal = null;
  const STORAGE_DB = "komarova-core-ai-media";
  const STORAGE_STORE = "workspace";
  const STORAGE_KEY = "current";

  function openWorkspaceDB() {
    return new Promise((resolve, reject) => {
      if (!("indexedDB" in window)) return reject(new Error("Локальное хранилище IndexedDB недоступно."));
      const request = indexedDB.open(STORAGE_DB, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORAGE_STORE)) db.createObjectStore(STORAGE_STORE);
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Не удалось открыть локальное хранилище."));
    });
  }

  async function writeWorkspace(record) {
    const db = await openWorkspaceDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORAGE_STORE, "readwrite");
      tx.objectStore(STORAGE_STORE).put(record, STORAGE_KEY);
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = tx.onabort = () => { const error = tx.error; db.close(); reject(error || new Error("Не удалось сохранить рабочую область.")); };
    });
  }

  async function readWorkspace() {
    const db = await openWorkspaceDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORAGE_STORE, "readonly");
      const request = tx.objectStore(STORAGE_STORE).get(STORAGE_KEY);
      request.onsuccess = () => { const value = request.result || null; db.close(); resolve(value); };
      request.onerror = () => { const error = request.error; db.close(); reject(error || new Error("Не удалось прочитать рабочую область.")); };
    });
  }

  async function deleteWorkspace() {
    const db = await openWorkspaceDB();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORAGE_STORE, "readwrite");
      tx.objectStore(STORAGE_STORE).delete(STORAGE_KEY);
      tx.oncomplete = () => { db.close(); resolve(); };
      tx.onerror = tx.onabort = () => { const error = tx.error; db.close(); reject(error || new Error("Не удалось очистить рабочую область.")); };
    });
  }

  async function persistWorkspace() {
    if (!sourceFile) return;
    const record = {
      version: 1,
      savedAt: Date.now(),
      original: sourceFile,
      originalName: sourceFile.name,
      originalType: sourceFile.type,
      originalLastModified: sourceFile.lastModified,
      result: resultFile || null,
      resultName: resultFile ? resultFile.name : "",
      resultType: resultFile ? resultFile.type : "",
      archiveOriginal: archiveOriginal || null,
      archiveResult: archiveResult || null,
      quality: qualityControl ? qualityControl.value : "65",
      zoom: zoomControl ? zoomControl.value : "100"
    };
    try {
      await writeWorkspace(record);
      if (info) info.textContent = (sourceFile.name || "Файл") + " · " + formatBytes(sourceFile.size) + " · сохранено в памяти этого браузера";
    } catch (error) {
      status.textContent = "Файл доступен в текущем сеансе, но браузер не смог сохранить его для следующего открытия: " + (error && error.message ? error.message : "недостаточно места или запрет хранилища") + ". Скачайте оригинал отдельно.";
    }
  }

  async function restoreWorkspace() {
    try {
      const saved = await readWorkspace();
      if (!saved || !saved.original) return;
      const original = saved.original instanceof File
        ? saved.original
        : new File([saved.original], saved.originalName || "saved-original", { type: saved.originalType || saved.original.type || "", lastModified: saved.originalLastModified || Date.now() });
      sourceFile = original;
      archiveOriginal = saved.archiveOriginal || null;
      archiveResult = saved.archiveResult || null;
      sourceUrl = URL.createObjectURL(original);
      preview.hidden = false;
      originalEmpty.hidden = true;
      originalImage.hidden = true;
      originalVideo.hidden = true;
      if (original.type.startsWith("image/")) {
        originalImage.src = sourceUrl;
        originalImage.hidden = false;
      } else if (original.type.startsWith("video/")) {
        originalVideo.src = sourceUrl;
        originalVideo.hidden = false;
      }
      if (saved.result) {
        const result = saved.result instanceof File
          ? saved.result
          : new File([saved.result], saved.resultName || "saved-result", { type: saved.resultType || saved.result.type || "", lastModified: Date.now() });
        resultFile = result;
        resultUrl = URL.createObjectURL(result);
        resultEmpty.hidden = true;
        if (result.type.startsWith("image/")) {
          resultImage.src = resultUrl;
          resultImage.hidden = false;
          resultVideo.hidden = true;
        } else if (result.type.startsWith("video/")) {
          resultVideo.src = resultUrl;
          resultVideo.hidden = false;
          resultImage.hidden = true;
        }
        exportButton.disabled = false;
        setStage("Сохранённая копия восстановлена", archiveResult ? "MATERIAL-ID: " + archiveResult.material_id : "Локальная копия · архивная запись не подтверждена");
        mode.textContent = archiveResult ? "КОПИЯ ЗАРЕГИСТРИРОВАНА В АРХИВЕ" : "ЛОКАЛЬНАЯ РАБОЧАЯ ОБЛАСТЬ";
      } else {
        setStage("Оригинал восстановлен", "Выберите обработку или замените исходный файл");
        mode.textContent = "ОРИГИНАЛ ВОССТАНОВЛЕН";
      }
      if (qualityControl && saved.quality) qualityControl.value = saved.quality;
      if (qualityValue && qualityControl) qualityValue.value = qualityControl.value + "%";
      if (zoomControl && saved.zoom) zoomControl.value = saved.zoom;
      applyZoom();
      info.textContent = original.name + " · " + formatBytes(original.size) + " · восстановлено из памяти этого браузера";
      status.textContent = archiveResult
        ? "Копия восстановлена. MATERIAL-ID " + archiveResult.material_id + " · оригинал " + archiveResult.original_material_id + ". Серверная запись остаётся в приватном архиве."
        : "Локальная рабочая область восстановлена. Это не заменяет постоянное хранение в приватном архиве.";
      reset.disabled = false;
    } catch (error) {
      status.textContent = "Не удалось восстановить локальную рабочую область. Возможно, браузер очистил данные или не поддерживает сохранение больших файлов.";
    }
  }

  function releaseUrl(url) {
    if (url) URL.revokeObjectURL(url);
  }

  function applyZoom() {
    const zoom = Math.max(100, Math.min(300, Number(zoomControl && zoomControl.value) || 100));
    if (zoomValue) zoomValue.value = zoom + "%";
    [originalImage, resultImage].forEach(image => {
      if (!image || image.hidden || !image.naturalWidth || !image.naturalHeight) return;
      const frame = image.parentElement;
      if (!frame) return;
      const availableWidth = Math.max(1, frame.clientWidth || frame.getBoundingClientRect().width);
      const fitScale = Math.min(availableWidth / image.naturalWidth, 360 / image.naturalHeight, 1);
      const displayWidth = Math.max(1, Math.round(image.naturalWidth * fitScale * zoom / 100));
      frame.style.display = "block";
      frame.style.width = "100%";
      frame.style.overflow = "auto";
      frame.style.maxHeight = "360px";
      image.style.display = "block";
      image.style.width = displayWidth + "px";
      image.style.maxWidth = "none";
      image.style.maxHeight = "none";
      image.style.height = "auto";
      image.style.marginInline = "auto";
      image.style.objectFit = "contain";
      image.style.imageRendering = "auto";
    });
    [originalVideo, resultVideo].forEach(video => {
      if (!video || video.hidden || !video.videoWidth || !video.videoHeight) return;
      const frame = video.parentElement;
      if (!frame) return;
      const availableWidth = Math.max(1, frame.clientWidth || frame.getBoundingClientRect().width);
      const fitScale = Math.min(availableWidth / video.videoWidth, 360 / video.videoHeight, 1);
      const displayWidth = Math.max(1, Math.round(video.videoWidth * fitScale * zoom / 100));
      frame.style.display = "block";
      frame.style.width = "100%";
      frame.style.overflow = "auto";
      frame.style.maxHeight = "360px";
      video.style.display = "block";
      video.style.width = displayWidth + "px";
      video.style.maxWidth = "none";
      video.style.maxHeight = "none";
      video.style.height = "auto";
      video.style.marginInline = "auto";
      video.style.objectFit = "contain";
    });
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
    archiveOriginal = null;
    if (videoSettings) videoSettings.hidden = true;
    if (videoEditor && videoEditor.open) videoEditor.close();
    if (openVideoEditor) openVideoEditor.disabled = true;
    if (reprocessButton) reprocessButton.disabled = true;
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
    mode.textContent = "AI-ДВИЖОК НЕ УСТАНОВЛЕН";
    setStage("Ожидается AI-движок", "Автоматическая проверка и Real-ESRGAN x4 будут запускаться внутри KOMAROVA_CORE");
    info.textContent = "Файл ещё не выбран. Выберите фотографию или видео.";
    status.textContent = "Оригинал не изменяется. После выбора выполняются локальные проверки. Серверный AI-движок пока не установлен.";
    void deleteWorkspace().catch(() => {});
  }

  function showOriginal(file) {
    releaseUrl(sourceUrl);
    sourceFile = file;
    archiveOriginal = null;
    const isVideo = file.type.startsWith("video/");
    if (videoSettings) videoSettings.hidden = !isVideo;
    if (openVideoEditor) openVideoEditor.disabled = !isVideo;
    if (reprocessButton) reprocessButton.disabled = !isVideo;
    sourceUrl = URL.createObjectURL(file);
    clearResult();
    preview.hidden = false;
    originalEmpty.hidden = true;
    originalImage.hidden = true;
    originalVideo.hidden = true;
    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      applyZoom();
      mode.textContent = "ЛОКАЛЬНАЯ ПРОВЕРКА ОРИГИНАЛА";
    } else {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ВИДЕО · ПРОСМОТР ОРИГИНАЛА";
    }
    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + (file.type || "тип не определён");
    reset.disabled = false;
    void persistWorkspace();
  }


  async function validateImageDimensions(file) {
    if (!file.type.startsWith("image/") || typeof createImageBitmap !== "function") return;
    let bitmap;
    try {
      bitmap = await createImageBitmap(file);
      if (bitmap.width * bitmap.height > MAX_PIXELS) {
        throw new Error("Изображение превышает безопасный предел 30 мегапикселей.");
      }
    } catch (error) {
      if (error instanceof Error && /30 мегапикселей/.test(error.message)) throw error;
      // Some browsers cannot decode HEIC/HEIF locally. The private worker performs authoritative decoding.
    } finally {
      if (bitmap) bitmap.close();
    }
  }

  // Lightweight browser fallback restored from the earlier implementation.
  // Deterministic correction only; this is not neural AI restoration.
  function makeCanvasCopy(file, token, quality) {
    const strength = Math.max(0, Math.min(100, Number(quality) || 0)) / 100;
    return new Promise((resolve, reject) => {
      const image = new Image();
      const imageUrl = URL.createObjectURL(file);
      image.onload = () => {
        URL.revokeObjectURL(imageUrl);
        try {
          if (token !== generation) return reject(new Error("Выбран другой файл."));
          const width = image.naturalWidth, height = image.naturalHeight;
          if (!width || !height || width * height > 12000000) {
            throw new Error("Для локальной обработки доступно до 12 мегапикселей. Большие файлы требуют серверного AI-worker.");
          }
          const canvas = document.createElement("canvas");
          canvas.width = width; canvas.height = height;
          const context = canvas.getContext("2d", { willReadFrequently: true });
          if (!context) throw new Error("Canvas 2D недоступен.");
          context.drawImage(image, 0, 0);
          const frame = context.getImageData(0, 0, width, height), pixels = frame.data;
          for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i], g = pixels[i + 1], b = pixels[i + 2];
            const l = 0.2126 * r + 0.7152 * g + 0.0722 * b;
            for (let c = 0; c < 3; c++) {
              const value = pixels[i + c];
              pixels[i + c] = Math.max(0, Math.min(255, (l + (value - l) * (1 + 0.10 * strength) - 128) * (1 + 0.12 * strength) + 128));
            }
          }
          context.putImageData(frame, 0, 0);
          const source = context.getImageData(0, 0, width, height).data;
          const sharpened = context.createImageData(width, height), target = sharpened.data;
          target.set(source);
          for (let y = 1; y < height - 1; y++) for (let x = 1; x < width - 1; x++) {
            const p = (y * width + x) * 4;
            for (let c = 0; c < 3; c++) {
              const n = source[p - 4 + c] + source[p + 4 + c] + source[p - width * 4 + c] + source[p + width * 4 + c];
              target[p + c] = Math.max(0, Math.min(255, source[p + c] * (1 + 0.30 * strength) - n * (0.075 * strength)));
            }
          }
          context.putImageData(sharpened, 0, 0);
          const mime = file.type === "image/png" ? "image/png" : "image/webp";
          canvas.toBlob(blob => {
            if (!blob) return reject(new Error("Не удалось создать файл результата."));
            const ext = blob.type === "image/png" ? "png" : blob.type === "image/webp" ? "webp" : "jpg";
            resolve(new File([blob], file.name.replace(/\.[^.]+$/, "") + "-enhanced." + ext,
              { type: blob.type || mime, lastModified: Date.now() }));
          }, mime, 0.94);
        } catch (error) { reject(error); }
      };
      image.onerror = () => { URL.revokeObjectURL(imageUrl); reject(new Error("Не удалось декодировать изображение.")); };
      image.src = imageUrl;
    });
  }

  async function privateApiRequest(path, options = {}) {
    if (!privateApi || typeof privateApi.request !== "function") {
      throw new Error("Приватный API и защищённая сессия не подключены к сайту.");
    }
    return privateApi.request(path, options);
  }

  async function runPrivateWorker(file, token) {
    if (!privateApi || typeof privateApi.request !== "function" || typeof privateApi.download !== "function") return null;
    if (!archiveOriginal) {
      const uploadForm = new FormData();
      uploadForm.append("file", file, file.name);
      uploadForm.append("title", file.name);
      setStage("Сохранение оригинала в архив", "Оригинал отправляется в приватное хранилище без преобразования");
      archiveOriginal = await privateApiRequest("/api/v1/archive/items", { method: "POST", body: uploadForm });
      await persistWorkspace();
    }
    if (archiveOriginal.record_status === "quarantined" || archiveOriginal.storage_state === "quarantined") {
      setStage("Антивирусная проверка", "Оригинал остаётся в карантине до подтверждения ClamAV");
      const scan = await privateApiRequest("/api/v1/archive/items/" + encodeURIComponent(archiveOriginal.archive_item_id) + "/scan", { method: "POST" });
      if (scan.scan_status !== "clean" || scan.record_status !== "available") {
        throw new Error("Оригинал не прошёл проверку ClamAV. Обработка не запускалась.");
      }
      archiveOriginal.record_status = scan.record_status;
      archiveOriginal.storage_state = scan.storage_state;
      await persistWorkspace();
    }
    if (archiveOriginal.record_status !== "available" || archiveOriginal.storage_state !== "verified") {
      throw new Error("Оригинал ещё не подтверждён сервером и не может быть обработан.");
    }

    const settings = new FormData();
    settings.append("strength", qualityControl ? qualityControl.value : "65");
    if (file.type.startsWith("video/")) {
      if (trimStart && trimStart.value !== "") settings.append("start_seconds", trimStart.value);
      if (trimEnd && trimEnd.value !== "") settings.append("end_seconds", trimEnd.value);
      const cropValues = [cropX, cropY, cropWidth, cropHeight];
      const filled = cropValues.filter(control => control && control.value !== "").length;
      if (filled !== 0 && filled !== 4) throw new Error("Для кадрирования заполните X, Y, ширину и высоту.");
      if (filled === 4) {
        settings.append("crop_x", cropX.value);
        settings.append("crop_y", cropY.value);
        settings.append("crop_width", cropWidth.value);
        settings.append("crop_height", cropHeight.value);
      }
      settings.append("enhance_audio", audioEnhance && audioEnhance.checked ? "true" : "false");
    }

    setStage("Серверная обработка", file.type.startsWith("video/") ? "Real-ESRGAN по кадрам · обрезка · обработка звука · новый MP4" : "Real-ESRGAN · коррекция выбранной силы · отдельный файл");
    const derivative = await privateApiRequest(
      "/api/v1/archive/items/" + encodeURIComponent(archiveOriginal.archive_item_id) + "/enhance",
      { method: "POST", body: settings }
    );
    const blob = await privateApi.download("/api/v1/archive/items/" + encodeURIComponent(derivative.archive_item_id) + "/content");
    const extension = file.type.startsWith("video/") ? "mp4" : "png";
    const name = file.name.replace(/\.[^.]+$/, "") + "-enhanced." + extension;
    return { file: new File([blob], name, { type: blob.type || (extension === "mp4" ? "video/mp4" : "image/png"), lastModified: Date.now() }), material: derivative };
  }

  async function displayResult(file, token, material) {
    if (token !== generation) return;
    resultFile = file;
    resultUrl = URL.createObjectURL(file);
    applyZoom();
    resultEmpty.hidden = true;
    if (file.type.startsWith("video/")) {
      resultVideo.src = resultUrl;
      resultVideo.hidden = false;
      resultImage.hidden = true;
    } else {
      resultImage.src = resultUrl;
      resultImage.hidden = false;
      resultVideo.hidden = true;
      applyZoom();
    }
    archiveResult = material || null;
    exportButton.disabled = false;
    mode.textContent = material ? "КОПИЯ СОХРАНЕНА В АРХИВЕ" : "ЛОКАЛЬНАЯ КОПИЯ ГОТОВА";
    setStage("Копия создана и проверена", material ? "MATERIAL-ID: " + material.material_id : "Локальный результат · постоянный MATERIAL-ID появится после подключения архива");
    status.textContent = material
      ? "Готово. MATERIAL-ID " + material.material_id + " связан с оригиналом " + material.original_material_id + ". Конвейер: " + material.engine + "."
      : "Готово. Создана отдельная локальная копия (" + formatBytes(file.size) + "). Оригинал не изменён. Постоянная архивная регистрация не выполнялась.";
    void persistWorkspace();
  }

  async function processSelected(file, token) {
    setStage("Проверка исходного файла", "Проверка типа, размера и контрольной суммы");
    status.textContent = "Проверяется оригинал. Исходный файл не изменяется.";
    const sourceHashBefore = await sha256(file);
    try {
      await validateImageDimensions(file);
      const serverResult = await runPrivateWorker(file, token);
      if (serverResult) {
        const sourceHashAfter = await sha256(file);
        if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
        await displayResult(serverResult.file, token, serverResult.material);
        return;
      }
      if (file.type.startsWith("video/")) {
        const sourceHashAfter = await sha256(file);
        if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
        setStage("Серверная студия не подключена", "Видео не будет имитировать обработку в окне предпросмотра");
        resultEmpty.textContent = "Для создания сохранённого MP4 требуется авторизация и доступный приватный backend. Оригинал не изменён.";
        resultEmpty.hidden = false;
        status.textContent = "Приватный API/защищённая сессия не подключены. ClamAV не запускалась; фиктивный ролик не создаётся. Обрезка, AI-обработка и экспорт начнут работать после подключения серверной среды.";
        mode.textContent = "ОЖИДАЕТСЯ ПРИВАТНЫЙ BACKEND";
        return;
      }
      if (file.type.startsWith("image/")) {
        setStage("Серверная студия не подключена", "Не создаём фиктивную копию предпросмотра");
        resultEmpty.textContent = "Для сохранённой производной копии требуется авторизация и доступный приватный backend.";
        resultEmpty.hidden = false;
        status.textContent = "Приватный API/защищённая сессия не подключены. Серверная обработка не запускалась, постоянная копия и MATERIAL-ID не создавались.";
        mode.textContent = "ОЖИДАЕТСЯ ПРИВАТНЫЙ BACKEND";
        return;
      }
      setStage("Ожидается установка AI-движка", "Real-ESRGAN NCNN Vulkan · суперразрешение x4");
      mode.textContent = "AI-ДВИЖОК НЕ УСТАНОВЛЕН";
      resultEmpty.textContent = "Настоящее AI-улучшение видео и нейросетевая реставрация появятся после установки внутреннего AI-worker.";
      resultEmpty.hidden = false;
      const sourceHashAfter = await sha256(file);
      if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
      status.textContent = "Оригинал сохранён без изменений. Внутренний AI-worker ещё не установлен; видеообработка не запускалась.";
      exportButton.disabled = true;
    } catch (error) {
      if (token !== generation) return;
      setStage("Обработка остановлена", "Оригинал сохранён без изменений");
      mode.textContent = "ОШИБКА ОБРАБОТКИ";
      status.textContent = "Не удалось создать проверенную копию: " + (error && error.message ? error.message : "неизвестная ошибка") + ". Исходный файл не изменён.";
    }
  }

  upload.addEventListener("click", () => {
    input.accept = "image/*";
    input.value = "";
    input.click();
  });
  if (videoUpload) videoUpload.addEventListener("click", () => {
    input.accept = "video/*";
    input.value = "";
    input.click();
  });
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

  if (openVideoEditor) openVideoEditor.addEventListener("click", () => {
    if (!sourceFile || !sourceFile.type.startsWith("video/") || !videoEditor) return;
    if (typeof videoEditor.showModal === "function") videoEditor.showModal();
    else {
      status.textContent = "Этот браузер не поддерживает отдельное окно редактора. Обновите браузер или используйте встроенный просмотр.";
    }
    status.textContent = "Редактор видео открыт. Параметры применятся только при доступном приватном backend и установленном FFmpeg/AI-worker.";
  });
  if (closeVideoEditor) closeVideoEditor.addEventListener("click", () => {
    if (videoEditor && videoEditor.open) videoEditor.close();
  });
  if (reprocessButton) reprocessButton.addEventListener("click", () => {
    if (!sourceFile) return;
    generation += 1;
    const token = generation;
    clearResult();
    void processSelected(sourceFile, token);
  });

  if (qualityControl) {
    if (qualityValue) qualityValue.value = qualityControl.value + "%";
    qualityControl.addEventListener("change", () => {
      if (!sourceFile) return;
      if (qualityValue) qualityValue.value = qualityControl.value + "%";
      generation += 1;
      const token = generation;
      clearResult();
      setStage("Повторная обработка", "Новая сила улучшения будет применена к отдельной серверной копии");
      void processSelected(sourceFile, token);
    });
  }
  originalImage.addEventListener("load", applyZoom);
  resultImage.addEventListener("load", applyZoom);
  originalVideo.addEventListener("loadedmetadata", applyZoom);
  resultVideo.addEventListener("loadedmetadata", applyZoom);
  if (zoomControl) {
    zoomControl.addEventListener("input", () => {
      applyZoom();
      void persistWorkspace();
    });
    applyZoom();
  }

  exportButton.disabled = true;
  preview.hidden = true;
  mode.textContent = "AI-ДВИЖОК НЕ УСТАНОВЛЕН";
  setStage("Ожидается серверная среда", "После подключения API ползунок будет менять параметры сохранённой копии");
  void restoreWorkspace();
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();