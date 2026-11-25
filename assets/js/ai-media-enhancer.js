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
  let sourceUrl = null;
  let sourceFile = null;
  function release(url) { if (url) URL.revokeObjectURL(url); }
  function clear() {
    release(sourceUrl); sourceUrl = null; sourceFile = null; input.value = "";
    originalImage.removeAttribute("src"); originalImage.hidden = true;
    originalVideo.pause(); originalVideo.removeAttribute("src"); originalVideo.load(); originalVideo.hidden = true;
    resultImage.removeAttribute("src"); resultImage.hidden = true;
    originalEmpty.hidden = false; resultEmpty.hidden = false;
    view.disabled = true; exportButton.disabled = true; reset.disabled = true;
    mode.textContent = "ОЖИДАЕТ ФАЙЛ";
    info.textContent = "Файл ещё не выбран.";
    status.textContent = "Доступен только локальный предпросмотр. Серверная AI-обработка пока не подключена.";
  }
  function show(file) {
    release(sourceUrl); sourceUrl = URL.createObjectURL(file); sourceFile = file;
    originalImage.hidden = true; originalVideo.hidden = true; originalEmpty.hidden = true;
    if (file.type.startsWith("image/")) {
      originalImage.src = sourceUrl; originalImage.hidden = false; mode.textContent = "ФОТО ВЫБРАНО";
    } else if (file.type.startsWith("video/")) {
      originalVideo.src = sourceUrl; originalVideo.hidden = false; mode.textContent = "ВИДЕО ВЫБРАНО";
    } else { clear(); status.textContent = "Неподдерживаемый тип файла."; return; }
    info.textContent = file.name + " · " + (file.size / 1048576).toFixed(2) + " МБ · " + file.type;
    view.disabled = false; reset.disabled = false;
    status.textContent = "Файл открыт только в этом браузере. Он не загружен на сервер и не сохранён в архиве.";
  }
  upload.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    const file = input.files && input.files[0]; if (!file) return;
    if (!(file.type.startsWith("image/") || file.type.startsWith("video/"))) {
      status.textContent = "Выберите изображение или видео."; input.value = ""; return;
    }
    if (!file.size || file.size > MAX_BYTES) {
      status.textContent = file.size ? "Размер файла превышает 100 МБ." : "Файл пустой.";
      input.value = ""; return;
    }
    show(file);
  });
  view.addEventListener("click", () => {
    if (!sourceFile) return;
    status.textContent = "Предпросмотр подтверждён. Реальная обработка заблокирована до подключения защищённого backend, сканера и AI-модели. Никакая копия не создана.";
  });
  exportButton.disabled = true;
  reset.addEventListener("click", clear);
  window.addEventListener("pagehide", () => release(sourceUrl));
  clear();
})();