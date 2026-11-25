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

  function makeCanvasCopy(file, token) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      const imageUrl = URL.createObjectURL(file);
      image.onload = () => {
        URL.revokeObjectURL(imageUrl);
        try {
          if (token !== generation) return reject(new Error("Выбран другой файл."));
          const width = image.naturalWidth;
          const height = image.naturalHeight;
          if (!width || !height || width * height > MAX_PIXELS) {
            throw new Error("Изображение превышает безопасный предел 30 мегапикселей.");
          }
          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const context = canvas.getContext("2d", { willReadFrequently: true });
          if (!context) throw new Error("Canvas 2D недоступен.");
          context.drawImage(image, 0, 0);

          const frame = context.getImageData(0, 0, width, height);
          const pixels = frame.data;
          for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i], g = pixels[i + 1], b = pixels[i + 2];
            const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
            const saturation = 1.045;
            const contrast = 1.055;
            pixels[i] = Math.max(0, Math.min(255, (luminance + (r - luminance) * saturation - 128) * contrast + 128));
            pixels[i + 1] = Math.max(0, Math.min(255, (luminance + (g - luminance) * saturation - 128) * contrast + 128));
            pixels[i + 2] = Math.max(0, Math.min(255, (luminance + (b - luminance) * saturation - 128) * contrast + 128));
          }
          context.putImageData(frame, 0, 0);

          // Restrained unsharp mask; it does not synthesize missing detail.
          const source = context.getImageData(0, 0, width, height).data;
          const sharpened = context.createImageData(width, height);
          const target = sharpened.data;
          target.set(source);
          for (let y = 1; y < height - 1; y++) {
            for (let x = 1; x < width - 1; x++) {
              const p = (y * width + x) * 4;
              for (let channel = 0; channel < 3; channel++) {
                const neighbours = source[p - 4 + channel] + source[p + 4 + channel] +
                  source[p - width * 4 + channel] + source[p + width * 4 + channel];
                target[p + channel] = Math.max(0, Math.min(255, source[p + channel] * 1.28 - neighbours * 0.07));
              }
            }
          }
          context.putImageData(sharpened, 0, 0);
          const requestedMime = file.type === "image/png" ? "image/png" : "image/webp";
          canvas.toBlob(blob => {
            if (!blob) return reject(new Error("Не удалось создать файл результата."));
            const extension = blob.type === "image/png" ? "png" : blob.type === "image/webp" ? "webp" : "jpg";
            const name = file.name.replace(/\.[^.]+$/, "") + "-enhanced." + extension;
            resolve(new File([blob], name, { type: blob.type || requestedMime, lastModified: Date.now() }));
          }, requestedMime, 0.94);
        } catch (error) {
          reject(error);
        }
      };
      image.onerror = () => {
        URL.revokeObjectURL(imageUrl);
        reject(new Error("Pillow-подобная подготовка в браузере: файл не удалось декодировать."));
      };
      image.src = imageUrl;
    });
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

    setStage("Обработка проверенного оригинала", "Pillow · OpenCV · scikit-image / FFmpeg · OpenCV");
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
    const result = new File([blob], file.name.replace(/\.[^.]+$/, "") + "-enhanced" + (file.type.startsWith("video/") ? ".mp4" : ".webp"), {
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
        setStage("Видеообработчик подготовлен", "FFmpeg + OpenCV · требуется подключение частного backend worker");
        status.textContent = "Оригинал видео открыт и проверен по типу и размеру. Автоматическая обработка FFmpeg + OpenCV подготовлена в backend, но публичный сайт пока не подключён к серверу. Фиктивный результат не создаётся.";
        mode.textContent = "ВИДЕО · ОЖИДАЕТ BACKEND";
        return;
      }
      setStage("Автоматическая обработка фотографии", "Коррекция цвета, контраста, шумов и резкости");
      status.textContent = "Создаётся отдельная локальная копия. Оригинал остаётся нетронутым.";
      const enhanced = await makeCanvasCopy(file, token);
      if (token !== generation) return;
      const sourceHashAfter = await sha256(file);
      if (sourceHashBefore !== sourceHashAfter) throw new Error("Контрольная сумма оригинала изменилась.");
      const bitmap = await createImageBitmap(enhanced);
      const originalBitmap = await createImageBitmap(file);
      const dimensionsValid = bitmap.width === originalBitmap.width && bitmap.height === originalBitmap.height;
      bitmap.close();
      originalBitmap.close();
      if (!dimensionsValid) throw new Error("Проверка размеров результата не пройдена.");
      await displayResult(enhanced, token, null);
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