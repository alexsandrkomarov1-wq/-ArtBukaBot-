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
  const resultImage = root.querySelector("[data-ai-result-preview]");
  const originalEmpty = root.querySelector("[data-ai-original-empty]");
  const resultEmpty = root.querySelector("[data-ai-result-empty]");

  let sourceFile = null;
  let sourceUrl = null;
  let resultUrl = null;
  let resultBlob = null;

  function releaseUrl(url) {
    if (url) URL.revokeObjectURL(url);
  }

  function clearResult() {
    releaseUrl(resultUrl);
    resultUrl = null;
    resultBlob = null;
    resultImage.removeAttribute("src");
    resultImage.hidden = true;
    resultEmpty.hidden = false;
    exportButton.disabled = true;
  }

  function clearWorkspace() {
    releaseUrl(sourceUrl);
    sourceUrl = null;
    sourceFile = null;
    clearResult();
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
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    info.textContent = "Файл ещё не выбран. Нажмите «Выбрать фото или видео».";
    status.textContent = "Локальный режим готов. Выбранный файл останется в этом браузере и пока не отправляется в Google Drive.";
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " Б";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " КБ";
    return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
  }

  function showFile(file) {
    releaseUrl(sourceUrl);
    clearResult();
    sourceFile = file;
    sourceUrl = URL.createObjectURL(file);
    originalEmpty.hidden = true;
    originalImage.hidden = true;
    originalVideo.hidden = true;

    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      mode.textContent = "ФОТОГРАФИЯ ВЫБРАНА";
      status.textContent = "Фотография проверена по типу и размеру. Нажмите VIEW для просмотра и создания локальной демонстрационной копии.";
    } else if (file.type.startsWith("video/")) {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ВИДЕО ВЫБРАНО";
      status.textContent = "Видеофайл выбран и доступен для просмотра. ИИ-обработка видео и экспорт улучшенной версии пока не подключены.";
    } else {
      clearWorkspace();
      status.textContent = "Браузер не распознал тип файла. Выберите изображение или видео.";
      return;
    }

    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + file.type;
    view.disabled = false;
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

  view.addEventListener("click", async () => {
    if (!sourceFile) return;
    if (sourceFile.type.startsWith("video/")) {
      status.textContent = "Видео открыто в локальном проигрывателе. Стабилизация, шумоподавление и ИИ-улучшение станут доступны после подключения видеообработчика.";
      return;
    }

    status.textContent = "Подготавливается локальная демонстрационная копия…";
    view.disabled = true;
    try {
      const bitmap = await createImageBitmap(sourceFile);
      const canvas = document.createElement("canvas");
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      const context = canvas.getContext("2d");
      if (!context) throw new Error("Canvas недоступен");
      context.filter = "contrast(1.06) saturate(1.06) brightness(1.02)";
      context.drawImage(bitmap, 0, 0);
      bitmap.close();
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.94));
      if (!blob) throw new Error("Не удалось создать копию");
      clearResult();
      resultBlob = blob;
      resultUrl = URL.createObjectURL(blob);
      resultImage.src = resultUrl;
      resultImage.hidden = false;
      resultEmpty.hidden = true;
      exportButton.disabled = false;
      status.textContent = "Готова локальная демонстрационная копия с лёгкой коррекцией контраста и цвета. Это НЕ ИИ-реставрация. Оригинал не изменён.";
    } catch (error) {
      status.textContent = "Не удалось подготовить копию в этом браузере: " + error.message;
    } finally {
      view.disabled = false;
    }
  });

  exportButton.addEventListener("click", () => {
    if (!resultBlob || !sourceFile) return;
    const link = document.createElement("a");
    const baseName = sourceFile.name.replace(/\.[^.]+$/, "") || "media";
    link.href = resultUrl;
    link.download = baseName + "-local-demo-copy.jpg";
    document.body.appendChild(link);
    link.click();
    link.remove();
    status.textContent = "Копия скачана на устройство. Она не загружена в Google Drive и не зарегистрирована в архивном реестре.";
  });

  reset.addEventListener("click", clearWorkspace);
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();