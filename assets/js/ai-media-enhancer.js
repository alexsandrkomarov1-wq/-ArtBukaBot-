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
  const qualityControl = root.querySelector("[data-ai-quality]");
  const qualityValue = root.querySelector("[data-ai-quality-value]");
  const zoomControl = root.querySelector("[data-ai-zoom]");
  const zoomValue = root.querySelector("[data-ai-zoom-value]");
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

  function applyZoom() {
    const zoom = Math.max(100, Math.min(300, Number(zoomControl && zoomControl.value) || 100));
    if (zoomValue) zoomValue.value = zoom + "%";
    [originalImage, resultImage].forEach(image => {
      if (!image) return;
      const frame = image.parentElement;
      if (frame) {
        frame.style.overflow = "auto";
        frame.style.maxHeight = "360px";
        frame.style.maxWidth = "100%";
      }
      image.style.display = "block";
      image.style.width = zoom + "%";
      image.style.maxWidth = "none";
      image.style.maxHeight = "none";
      image.style.height = "auto";
      image.style.flex = "0 0 auto";
      image.style.objectFit = "contain";
      image.style.imageRendering = "auto";
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
      mode.textContent = "ЛОКАЛЬНАЯ ПРОВЕРКА ОРИГИНАЛА";
    } else {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ЛОКАЛЬНАЯ ПРОВЕРКА ОРИГИНАЛА";
    }
    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + (file.type || "тип не определён");
    reset.disabled = false;
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
            resolve(new File([blob], file.name.replace(/\\.[^.]+$/, "") + "-enhanced." + ext,
              { type: blob.type || mime, lastModified: Date.now() }));
          }, mime, 0.94);
        } catch (error) { reject(error); }
      };
      image.onerror = () => { URL.revokeObjectURL(imageUrl); reject(new Error("Не удалось декодировать изображение.")); };
      image.src = imageUrl;
    });
  }

  async function runPrivateWorker() {
    // No browser-side credentials or manual backend connection. A deployed first-party worker will be invoked by the site service.
    return null;
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
        setStage("Ожидается AI video worker", "Real-ESRGAN x2 · FFmpeg · сохранение аудио");
        resultEmpty.textContent = "AI-обработка видео появится после установки внутреннего worker. Исходник не изменён, фиктивный ролик не создаётся.";
        resultEmpty.hidden = false;
        status.textContent = "Оригинал видео выбран. Локально проверены формат, размер и SHA-256; антивирусная проверка ClamAV не запускалась. Для улучшения требуется установить внутренний worker с Real-ESRGAN, FFmpeg и моделью.";
        mode.textContent = "AI VIDEO WORKER НЕ ПОДКЛЮЧЁН";
        return;
      }
      if (file.type.startsWith("image/")) {
        setStage("Локальная коррекция фотографии", "Цвет · контраст · умеренная резкость · без нейросетевой генерации");
        mode.textContent = "ЛОКАЛЬНАЯ ОБРАБОТКА";
        status.textContent = "Создаётся отдельная копия в браузере. Это облегчённый алгоритм, не Real-ESRGAN. Оригинал не изменяется.";
        const enhanced = await makeCanvasCopy(file, token, qualityControl ? qualityControl.value : 65);
        if (token !== generation) return;
        const sourceHashAfter = await sha256(file);
        if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
        await displayResult(enhanced, token, null);
        status.textContent = "Создана отдельная локальная копия (" + formatBytes(enhanced.size) + "). Оригинал не изменён. Это алгоритмическая коррекция, не нейросетевая реставрация; архивный MATERIAL-ID не присвоен.";
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

  if (qualityControl) {
    if (qualityValue) qualityValue.value = qualityControl.value + "%";
    qualityControl.addEventListener("change", () => {
      if (!sourceFile || !sourceFile.type.startsWith("image/")) return;
      if (qualityValue) qualityValue.value = qualityControl.value + "%";
      generation += 1;
      const token = generation;
      clearResult();
      setStage("Повторная обработка фотографии", "Применяется выбранная сила улучшения");
      void processSelected(sourceFile, token);
    });
  }
  if (zoomControl) {
    zoomControl.addEventListener("input", applyZoom);
    applyZoom();
  }

  exportButton.disabled = true;
  preview.hidden = true;
  mode.textContent = "AI-ДВИЖОК НЕ УСТАНОВЛЕН";
  setStage("Ожидается AI-движок", "Real-ESRGAN NCNN Vulkan · автоматическое улучшение x4");
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();