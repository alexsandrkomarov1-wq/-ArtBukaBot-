(() => {
  "use strict";

  const cards = Array.from(document.querySelectorAll("[data-portrait-card]"));
  if (!cards.length) return;

  const MAX_FILE_BYTES = 12 * 1024 * 1024;
  const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);
  const previews = new Map();

  function clearCard(card) {
    const input = card.querySelector(".portrait-upload-input");
    const image = card.querySelector(".portrait-preview");
    const silhouette = card.querySelector(".portrait-silhouette");
    const state = card.querySelector("[data-portrait-state]");
    const clearButton = card.querySelector("[data-portrait-clear]");
    const previousUrl = previews.get(card);
    if (previousUrl) URL.revokeObjectURL(previousUrl);
    previews.delete(card);
    image.removeAttribute("src");
    image.hidden = true;
    silhouette.hidden = false;
    state.textContent = "ФОТО ПОКА НЕ ДОБАВЛЕНО";
    clearButton.hidden = true;
    input.value = "";
  }

  cards.forEach((card) => {
    const input = card.querySelector(".portrait-upload-input");
    const image = card.querySelector(".portrait-preview");
    const silhouette = card.querySelector(".portrait-silhouette");
    const state = card.querySelector("[data-portrait-state]");
    const clearButton = card.querySelector("[data-portrait-clear]");

    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file) return;
      if (!ALLOWED_TYPES.has(file.type)) {
        state.textContent = "Формат не поддерживается. Выберите JPG, PNG, WEBP или GIF.";
        input.value = "";
        return;
      }
      if (file.size > MAX_FILE_BYTES) {
        state.textContent = "Файл больше 12 МБ. Выберите фотографию меньшего размера.";
        input.value = "";
        return;
      }
      const previousUrl = previews.get(card);
      if (previousUrl) URL.revokeObjectURL(previousUrl);
      const url = URL.createObjectURL(file);
      previews.set(card, url);
      image.src = url;
      image.hidden = false;
      silhouette.hidden = true;
      state.textContent = "ПРЕДПРОСМОТР · " + file.name;
      clearButton.hidden = false;
    });

    clearButton.addEventListener("click", () => clearCard(card));
  });

  window.addEventListener("pagehide", () => {
    previews.forEach((url) => URL.revokeObjectURL(url));
    previews.clear();
  });
})();
