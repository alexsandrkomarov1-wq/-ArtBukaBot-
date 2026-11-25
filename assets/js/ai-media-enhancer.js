(() => {
  "use strict";

  const root = document.querySelector("[data-ai-media-lab]");
  if (!root) return;

  const MAX_BYTES = 100 * 1024 * 1024;
  const input = root.querySelector("[data-ai-file-input]");
  const upload = root.querySelector("[data-ai-upload]");
  const view = root.querySelector("[data-ai-view]");
  const exportButton = root.querySelector("[data-ai-export]");
  const reset = root.querySelector("[data-ai-reset]");
  const info = root.querySelector("[data-ai-file-info]");
  const status = root.querySelector("[data-ai-status]");
  const mode = root.querySelector("[data-ai-mode]");
  const originalImage = root.querySelector("[data-ai-original-preview]");
  const originalVideo = root.querySelector("[data-ai-video-preview]");
  const originalEmpty = root.querySelector("[data-ai-original-empty]");
  const resultPreview = root.querySelector("[data-ai-result-preview]");
  const resultVideo = root.querySelector("[data-ai-result-video]");
  const resultEmpty = root.querySelector("[data-ai-result-empty]");

  let sourceFile = null;
  let sourceUrl = null;
  let resultFile = null;
  let resultUrl = null;

  function releaseUrl(url) {
    if (url) URL.revokeObjectURL(url);
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " Б";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " КБ";
    return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
  }

  function clearResult() {
    releaseUrl(resultUrl);
    resultUrl = null;
    resultFile = null;
    resultPreview.removeAttribute("src");
    resultPreview.hidden = true;
    resultVideo.pause();
    resultVideo.removeAttribute("src");
    resultVideo.load();
    resultVideo.hidden = true;
    resultEmpty.hidden = false;
  }

  function clearWorkspace() {
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
    view.disabled = true;
    reset.disabled = true;
    exportButton.disabled = true;
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    info.textContent = "Файл ещё не выбран. Выберите фотографию или видео для локального просмотра.";
    status.textContent = "Выберите изображение. Обработка выполняется локально в браузере, без отправки файла на сервер.";
  }

  function showFile(file) {
    releaseUrl(sourceUrl);
    sourceFile = file;
    sourceUrl = URL.createObjectURL(file);
    clearResult();
    originalEmpty.hidden = true;
    originalImage.hidden = true;
    originalVideo.hidden = true;
    exportButton.disabled = true;
    resultEmpty.hidden = false;
    resultPreview.hidden = true;
    resultPreview.removeAttribute("src");

    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      mode.textContent = "ФОТОГРАФИЯ ВЫБРАНА";
      status.textContent = "Оригинал открыт. Нажмите VIEW, чтобы создать отдельную улучшенную копию на этом устройстве.";
    } else if (file.type.startsWith("video/")) {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ВИДЕО ВЫБРАНО";
      status.textContent = "Видео открыто локально. Просмотр доступен, но полноценная обработка видео пока не реализована.";
    } else {
      clearWorkspace();
      status.textContent = "Браузер не распознал тип файла. Выберите изображение или видео.";
      return;
    }

    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + (file.type || "тип не определён");
    view.disabled = !file.type.startsWith("image/");
    reset.disabled = false;
  }


  upload.addEventListener("click", () => input.click());

  input.addEventListener("change", () => {
    const file = input.files && input.files[0];
    if (!file) return;
    if (!(file.type.startsWith("image/") || file.type.startsWith("video/"))) {
      status.textContent = "Формат не распознан как изображение или видео. Файл не принят.";
      input.value = "";
      return;
    }
    if (file.size === 0 || file.size > MAX_BYTES) {
      status.textContent = file.size === 0 ? "Файл пустой." : "Размер превышает 100 МБ. Выберите файл меньшего размера.";
      input.value = "";
      return;
    }
    showFile(file);
  });

  function enhanceImage(file) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      const imageUrl = URL.createObjectURL(file);
      image.onload = () => {
        URL.revokeObjectURL(imageUrl);
        try {
          if (image.naturalWidth * image.naturalHeight > 30000000) {
            throw new Error("Изображение превышает безопасный лимит 30 мегапикселей для обработки в браузере.");
          }
          const canvas = document.createElement("canvas");
          canvas.width = image.naturalWidth;
          canvas.height = image.naturalHeight;
          const context = canvas.getContext("2d", { willReadFrequently: true });
          if (!context) throw new Error("Браузер не предоставил Canvas 2D.");

          context.drawImage(image, 0, 0);
          const frame = context.getImageData(0, 0, canvas.width, canvas.height);
          const pixels = frame.data;

          // Локальная тоновая коррекция: умеренный контраст и насыщенность.
          for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i], g = pixels[i + 1], b = pixels[i + 2];
            const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
            const contrast = 1.08;
            const saturation = 1.06;
            pixels[i] = Math.max(0, Math.min(255, (luminance + (r - luminance) * saturation - 128) * contrast + 130));
            pixels[i + 1] = Math.max(0, Math.min(255, (luminance + (g - luminance) * saturation - 128) * contrast + 130));
            pixels[i + 2] = Math.max(0, Math.min(255, (luminance + (b - luminance) * saturation - 128) * contrast + 130));
          }
          context.putImageData(frame, 0, 0);

          // Мягкая резкость отдельным проходом с небольшим радиусом.
          const source = context.getImageData(0, 0, canvas.width, canvas.height);
          const inputPixels = source.data;
          const output = context.createImageData(canvas.width, canvas.height);
          const target = output.data;
          target.set(inputPixels);
          const w = canvas.width, h = canvas.height;
          for (let y = 1; y < h - 1; y++) {
            for (let x = 1; x < w - 1; x++) {
              const p = (y * w + x) * 4;
              for (let c = 0; c < 3; c++) {
                const center = inputPixels[p + c] * 1.35;
                const neighbours = (
                  inputPixels[p - 4 + c] + inputPixels[p + 4 + c] +
                  inputPixels[p - w * 4 + c] + inputPixels[p + w * 4 + c]
                ) * 0.0875;
                target[p + c] = Math.max(0, Math.min(255, center - neighbours));
              }
            }
          }
          context.putImageData(output, 0, 0);
          const mime = file.type === "image/png" ? "image/png" : "image/jpeg";
          canvas.toBlob(blob => {
            if (!blob) return reject(new Error("Не удалось сформировать файл-копию."));
            resolve(new File([blob], file.name.replace(/\.[^.]+$/, "") + "-enhanced." + (mime === "image/png" ? "png" : "jpg"), {
              type: mime,
              lastModified: Date.now()
            }));
          }, mime, 0.94);
        } catch (error) {
          reject(error);
        }
      };
      image.onerror = () => {
        URL.revokeObjectURL(imageUrl);
        reject(new Error("Не удалось декодировать изображение."));
      };
      image.src = imageUrl;
    });
  }

  view.addEventListener("click", async () => {
    if (!sourceFile) return;
    if (!sourceFile.type.startsWith("image/")) {
      status.textContent = "Для видео пока доступен только просмотр. Полноценный видеообработчик ещё не реализован.";
      return;
    }
    view.disabled = true;
    exportButton.disabled = true;
    status.textContent = "Выполняется локальная коррекция изображения. Оригинал не изменяется.";
    try {
      const enhanced = await enhanceImage(sourceFile);
      releaseUrl(resultUrl);
      resultFile = enhanced;
      resultUrl = URL.createObjectURL(enhanced);
      resultEmpty.hidden = true;
      resultVideo.hidden = true;
      resultVideo.pause();
      resultVideo.removeAttribute("src");
      resultPreview.src = resultUrl;
      resultPreview.hidden = false;
      mode.textContent = "КОПИЯ СОЗДАНА";
      exportButton.disabled = false;
      status.textContent = "Готово: создана отдельная улучшенная копия (" + formatBytes(enhanced.size) + "). Это локальная алгоритмическая коррекция, не AI-реставрация и не архивная регистрация.";
    } catch (error) {
      status.textContent = "Обработка не выполнена: " + error.message + ". Оригинал остался без изменений.";
    } finally {
      view.disabled = false;
    }
  });

  exportButton.addEventListener("click", () => {
    if (!resultFile || !resultUrl) return;
    const link = document.createElement("a");
    link.href = resultUrl;
    link.download = resultFile.name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    status.textContent = "Скачивание отдельной копии начато. Оригинал не изменён.";
  });

  reset.addEventListener("click", clearWorkspace);
  exportButton.disabled = true;
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();