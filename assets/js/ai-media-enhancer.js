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
  const resultInput = root.querySelector("[data-ai-result-input]");
  const resultSelect = root.querySelector("[data-ai-result-select]");

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
    resultInput.value = "";
    resultPreview.removeAttribute("src");
    resultPreview.hidden = true;
    resultVideo.pause();
    resultVideo.removeAttribute("src");
    resultVideo.load();
    resultVideo.hidden = true;
    resultEmpty.hidden = false;
    resultSelect.disabled = !sourceFile;
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
    resultSelect.disabled = true;
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    info.textContent = "Файл ещё не выбран. Выберите фотографию или видео для локального просмотра.";
    status.textContent = "Исходный файл остаётся в этом браузере. Серверная обработка ещё не запущена.";
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

    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      mode.textContent = "ФОТОГРАФИЯ ВЫБРАНА";
      status.textContent = "Фотография открыта локально. Файл не отправлен на сервер. Нажмите VIEW, чтобы проверить состояние ИИ.";
    } else if (file.type.startsWith("video/")) {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      mode.textContent = "ВИДЕО ВЫБРАНО";
      status.textContent = "Видео открыто в локальном проигрывателе. Файл не отправлен на сервер. Видеообработчик пока не развёрнут.";
    } else {
      clearWorkspace();
      status.textContent = "Браузер не распознал тип файла. Выберите изображение или видео.";
      return;
    }

    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + (file.type || "тип не определён");
    view.disabled = false;
    reset.disabled = false;
    resultSelect.disabled = false;
  }

  function showResultCopy(file) {
    if (!sourceFile) return;
    const sourceKind = sourceFile.type.startsWith("image/") ? "image" : "video";
    const resultKind = file.type.startsWith("image/") ? "image" : file.type.startsWith("video/") ? "video" : "";
    if (!resultKind || resultKind !== sourceKind) {
      status.textContent = "Тип копии должен совпадать с оригиналом: изображение к изображению или видео к видео.";
      resultInput.value = "";
      return;
    }
    if (file.size === 0 || file.size > MAX_BYTES) {
      status.textContent = file.size === 0 ? "Файл-копия пустой." : "Размер копии превышает 100 МБ.";
      resultInput.value = "";
      return;
    }
    if (file.name === sourceFile.name && file.size === sourceFile.size && file.lastModified === sourceFile.lastModified) {
      status.textContent = "Выбран тот же файл, что и оригинал. Для сравнения укажите отдельную копию.";
      resultInput.value = "";
      return;
    }
    clearResult();
    resultFile = file;
    resultUrl = URL.createObjectURL(file);
    resultEmpty.hidden = true;
    if (resultKind === "image") {
      resultPreview.src = resultUrl;
      resultPreview.hidden = false;
    } else {
      resultVideo.src = resultUrl;
      resultVideo.hidden = false;
    }
    status.textContent = "Показана отдельная локальная копия: " + file.name + ". Это ручной предпросмотр, не AI-обработка; серверная проверка и MATERIAL-ID не подтверждены.";
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

  resultSelect.addEventListener("click", () => resultInput.click());
  resultInput.addEventListener("change", () => {
    const file = resultInput.files && resultInput.files[0];
    if (file) showResultCopy(file);
  });

  view.addEventListener("click", () => {
    if (!sourceFile) return;
    status.textContent = "Серверная обработка пока не подключена. Файл остался в браузере и не отправлялся. Оригинал сохранён без изменений; экспорт недоступен.";
  });

  reset.addEventListener("click", clearWorkspace);
  exportButton.disabled = true;
  resultSelect.disabled = true;
  window.addEventListener("pagehide", () => {
    releaseUrl(sourceUrl);
    releaseUrl(resultUrl);
  });
})();