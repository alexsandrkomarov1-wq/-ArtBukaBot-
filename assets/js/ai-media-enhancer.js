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
  const motion = document.querySelector("[data-ai-motion]");
  const scanStage = motion && motion.querySelector("[data-ai-scan-stage]");
  const scanImage = motion && motion.querySelector("[data-ai-scan-image]");
  const scanState = motion && motion.querySelector("[data-ai-scan-state]");
  const scanNote = motion && motion.querySelector("[data-ai-scan-note]");
  const scanProgress = motion && motion.querySelector("[data-ai-scan-progress]");
  const defaultScanImage = scanImage ? scanImage.getAttribute("src") : "";

  let sourceFile = null;
  let sourceUrl = null;
  let scanTimer = null;

  function releaseUrl(url) {
    if (url) URL.revokeObjectURL(url);
  }

  function stopScan() {
    if (scanTimer) window.clearTimeout(scanTimer);
    scanTimer = null;
    if (motion) motion.classList.remove("is-scanning");
    if (scanStage) scanStage.classList.remove("is-scanning");
    if (scanProgress) scanProgress.style.width = "0";
    if (scanState) scanState.textContent = sourceFile ? "ФОТО ГОТОВО К СКАНИРОВАНИЮ" : "ОЖИДАЕТ ФОТОГРАФИЮ";
  }

  function clearWorkspace() {
    stopScan();
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
    resultImage.removeAttribute("src");
    resultImage.hidden = true;
    resultEmpty.hidden = false;
    if (scanImage && defaultScanImage) scanImage.src = defaultScanImage;
    view.disabled = true;
    exportButton.disabled = true;
    reset.disabled = true;
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    info.textContent = "Файл ещё не выбран. Нажмите «Выбрать фото или видео».";
    status.textContent = "Оригинал не изменяется. Сканирующая анимация не является AI-восстановлением.";
    if (scanNote) scanNote.textContent = "Это визуальная анимация сканера. Она не изменяет фотографию и не выдаёт себя за AI-восстановление.";
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " Б";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " КБ";
    return (bytes / (1024 * 1024)).toFixed(1) + " МБ";
  }

  function showFile(file) {
    stopScan();
    releaseUrl(sourceUrl);
    sourceFile = file;
    sourceUrl = URL.createObjectURL(file);
    originalEmpty.hidden = true;
    originalImage.hidden = true;
    originalVideo.hidden = true;
    resultImage.removeAttribute("src");
    resultImage.hidden = true;
    resultEmpty.hidden = false;
    exportButton.disabled = true;

    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl;
      originalImage.hidden = false;
      if (scanImage) scanImage.src = sourceUrl;
      mode.textContent = "ФОТО ВЫБРАНО";
      view.disabled = false;
      status.textContent = "Оригинал открыт локально. Нажмите VIEW, чтобы запустить сканирующий проход. AI-обработка пока не подключена.";
      if (scanState) scanState.textContent = "ФОТО ГОТОВО К СКАНИРОВАНИЮ";
    } else if (file.type.startsWith("video/")) {
      originalVideo.src = sourceUrl;
      originalVideo.hidden = false;
      if (scanImage && defaultScanImage) scanImage.src = defaultScanImage;
      mode.textContent = "ВИДЕО ВЫБРАНО";
      view.disabled = true;
      status.textContent = "Видео доступно для локального просмотра. Сканирование кадров, AI-улучшение и экспорт видео пока не реализованы.";
      if (scanState) scanState.textContent = "СКАНИРОВАНИЕ ВИДЕО НЕ ПОДКЛЮЧЕНО";
    } else {
      clearWorkspace();
      status.textContent = "Браузер не распознал тип файла. Выберите изображение или видео.";
      return;
    }

    info.textContent = file.name + " · " + formatBytes(file.size) + " · " + file.type;
    reset.disabled = false;
  }

  function runScanner() {
    if (!sourceFile || !sourceFile.type.startsWith("image/") || !motion || !scanStage) return;
    stopScan();
    motion.classList.add("is-scanning");
    scanStage.classList.add("is-scanning");
    if (scanState) scanState.textContent = "СКАНИРУЮЩИЙ ПРОХОД";
    if (scanNote) scanNote.textContent = "Сканирующая линия проходит по выбранному оригиналу. Это анимация интерфейса, а не вычисление нейросети.";
    if (scanProgress) {
      scanProgress.style.width = "0";
      window.requestAnimationFrame(() => { scanProgress.style.width = "100%"; });
    }
    mode.textContent = "СКАНИРОВАНИЕ";
    view.disabled = true;
    status.textContent = "Выполняется визуальный сканирующий проход по оригиналу. Файл не изменяется.";
    scanTimer = window.setTimeout(() => {
      motion.classList.remove("is-scanning");
      scanStage.classList.remove("is-scanning");
      scanTimer = null;
      if (scanState) scanState.textContent = "СКАНИРУЮЩИЙ ПРОХОД ЗАВЕРШЁН";
      if (scanNote) scanNote.textContent = "Проход завершён. Качество фотографии не менялось: AI-модель не подключена, улучшенная копия не создана.";
      mode.textContent = "ОЖИДАЕТ AI-МОДЕЛЬ";
      status.textContent = "Анимация сканера завершена. Настоящее AI-восстановление не выполнялось; оригинал остался неизменным, экспорт результата отключён.";
      view.disabled = false;
    }, 6200);
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

  view.addEventListener("click", runScanner);
  reset.addEventListener("click", clearWorkspace);
  window.addEventListener("pagehide", () => {
    if (scanTimer) window.clearTimeout(scanTimer);
    releaseUrl(sourceUrl);
  });

  clearWorkspace();
})();
