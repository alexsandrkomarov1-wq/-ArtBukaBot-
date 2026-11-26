(() => {
  "use strict";

  const cards = Array.from(document.querySelectorAll("[data-portrait-card]"));
  if (!cards.length) return;

  const MAX_FILE_BYTES = 12 * 1024 * 1024;
  const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp", "image/gif"]);
  const previews = new Map();
  const selectedFiles = new Map();
  const note = document.getElementById("family-portraits-status");
  const DB_NAME = "komarova-core-family-portraits";
  const STORE_NAME = "portraits";
  const STORAGE_KEY = "four-slots";
  let saveQueue = Promise.resolve();
  let restoring = true;

  function setNote(message) {
    if (note) note.textContent = message;
  }

  function openDB() {
    return new Promise((resolve, reject) => {
      if (!("indexedDB" in window)) {
        reject(new Error("Локальное хранилище IndexedDB недоступно."));
        return;
      }
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: "key" });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Не удалось открыть локальное хранилище."));
    });
  }

  async function readSavedSlots() {
    const db = await openDB();
    try {
      return await new Promise((resolve, reject) => {
        const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(STORAGE_KEY);
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error || new Error("Не удалось прочитать сохранённые портреты."));
      });
    } finally {
      db.close();
    }
  }

  async function writeSavedSlots() {
    const db = await openDB();
    const slots = cards.map((card, index) => {
      const file = selectedFiles.get(card);
      return file ? {
        index,
        file,
        name: file.name,
        type: file.type,
        lastModified: file.lastModified
      } : null;
    });
    try {
      await new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        tx.objectStore(STORE_NAME).put({ key: STORAGE_KEY, slots, savedAt: new Date().toISOString() });
        tx.oncomplete = resolve;
        tx.onerror = () => reject(tx.error || new Error("Не удалось сохранить портреты."));
        tx.onabort = () => reject(tx.error || new Error("Сохранение портретов прервано."));
      });
    } finally {
      db.close();
    }
  }

  function queueSave() {
    saveQueue = saveQueue.then(writeSavedSlots);
    return saveQueue;
  }

  const previewGeneration = new Map();

  async function makePortraitPreview(file) {
    if (file.type === "image/gif" || typeof createImageBitmap !== "function") return file;
    let bitmap = null;
    try {
      bitmap = await createImageBitmap(file);
      const pixels = bitmap.width * bitmap.height;
      const scale = Math.min(1, Math.sqrt(8000000 / pixels));
      const width = Math.max(1, Math.round(bitmap.width * scale));
      const height = Math.max(1, Math.round(bitmap.height * scale));
      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const context = canvas.getContext("2d", { alpha: false });
      if (!context) return file;
      if ("filter" in context) {
        context.filter = "brightness(1.06) contrast(1.08) saturate(1.12)";
      }
      context.drawImage(bitmap, 0, 0, width, height);
      context.filter = "none";
      const blob = await new Promise((resolve, reject) => {
        canvas.toBlob(
          value => value ? resolve(value) : reject(new Error("Не удалось создать копию предпросмотра.")),
          "image/webp",
          0.94
        );
      });
      canvas.width = 1;
      canvas.height = 1;
      return new File(
        [blob],
        file.name.replace(/\\.[^.]+$/, "") + "-portrait-preview.webp",
        { type: "image/webp", lastModified: Date.now() }
      );
    } catch (_) {
      return file;
    } finally {
      if (bitmap) bitmap.close();
    }
  }

  async function showFile(card, file) {
    const input = card.querySelector(".portrait-upload-input");
    const image = card.querySelector(".portrait-preview");
    const frame = card.querySelector(".portrait-frame");
    const silhouette = card.querySelector(".portrait-silhouette");
    const state = card.querySelector("[data-portrait-state]");
    const clearButton = card.querySelector("[data-portrait-clear]");
    const token = (previewGeneration.get(card) || 0) + 1;
    previewGeneration.set(card, token);
    const previousUrl = previews.get(card);
    if (previousUrl) URL.revokeObjectURL(previousUrl);
    previews.delete(card);
    selectedFiles.set(card, file);
    input.value = "";
    state.textContent = "ОБРАБОТКА ПРЕДПРОСМОТРА…";
    clearButton.hidden = true;

    const previewFile = await makePortraitPreview(file);
    if (previewGeneration.get(card) !== token) return;
    const url = URL.createObjectURL(previewFile);
    previews.set(card, url);
    image.onload = () => {
      if (previewGeneration.get(card) !== token) return;
      frame.style.aspectRatio = image.naturalWidth + " / " + image.naturalHeight;
      frame.style.minHeight = "0";
      frame.style.maxHeight = "420px";
    };
    image.src = url;
    image.hidden = false;
    silhouette.hidden = true;
    state.textContent = previewFile === file
      ? "ПРЕДПРОСМОТР · " + file.name
      : "ПРЕДПРОСМОТР · СВЕТ, КОНТРАСТ И ЦВЕТ СКОРРЕКТИРОВАНЫ";
    clearButton.hidden = false;
  }

  function clearCard(card) {
    const input = card.querySelector(".portrait-upload-input");
    const image = card.querySelector(".portrait-preview");
    const frame = card.querySelector(".portrait-frame");
    const silhouette = card.querySelector(".portrait-silhouette");
    const state = card.querySelector("[data-portrait-state]");
    const clearButton = card.querySelector("[data-portrait-clear]");
    previewGeneration.set(card, (previewGeneration.get(card) || 0) + 1);
    const previousUrl = previews.get(card);
    if (previousUrl) URL.revokeObjectURL(previousUrl);
    previews.delete(card);
    selectedFiles.delete(card);
    image.removeAttribute("src");
    image.onload = null;
    image.hidden = true;
    frame.style.aspectRatio = "";
    frame.style.minHeight = "";
    frame.style.maxHeight = "";
    silhouette.hidden = false;
    state.textContent = "ФОТО ПОКА НЕ ДОБАВЛЕНО";
    clearButton.hidden = true;
    input.value = "";
  }

  function setControlsDisabled(disabled) {
    cards.forEach((card) => {
      card.querySelector(".portrait-upload-input").disabled = disabled;
      card.querySelector("[data-portrait-clear]").disabled = disabled;
    });
  }

  async function restoreSavedSlots() {
    setControlsDisabled(true);
    try {
      const saved = await readSavedSlots();
      if (saved && Array.isArray(saved.slots)) {
        for (const slot of saved.slots) {
          if (!slot || !Number.isInteger(slot.index) || !cards[slot.index] || !slot.file) continue;
          await showFile(cards[slot.index], slot.file);
        }
        const count = selectedFiles.size;
        if (count) {
          setNote("Восстановлено портретов: " + count + " из 4. Они сохранены только в памяти этого браузера на этом устройстве. Это ещё не семейный облачный архив.");
        }
      }
    } catch (error) {
      setNote("Не удалось восстановить портреты из памяти браузера: " + error.message + " Выбранные сейчас файлы можно просматривать, но постоянное облачное хранение пока не подключено.");
    } finally {
      restoring = false;
      setControlsDisabled(false);
    }
  }

  cards.forEach((card) => {
    const input = card.querySelector(".portrait-upload-input");
    const clearButton = card.querySelector("[data-portrait-clear]");

    input.addEventListener("change", async () => {
      if (restoring) return;
      const file = input.files && input.files[0];
      if (!file) return;
      if (!ALLOWED_TYPES.has(file.type)) {
        card.querySelector("[data-portrait-state]").textContent = "Формат не поддерживается. Выберите JPG, PNG, WEBP или GIF.";
        input.value = "";
        return;
      }
      if (file.size > MAX_FILE_BYTES) {
        card.querySelector("[data-portrait-state]").textContent = "Файл больше 12 МБ. Выберите фотографию меньшего размера.";
        input.value = "";
        return;
      }
      void showFile(card, file);
      setNote("Сохраняем оригинал портрета в локальной памяти браузера…");
      try {
        await queueSave();
        setNote("Портрет сохранён в памяти этого браузера. Он восстановится после повторного открытия сайта, пока данные сайта не очищены. В облачный архив файл пока не отправлен.");
      } catch (error) {
        setNote("Предпросмотр работает, но браузер не смог сохранить файл: " + error.message + " Скачайте оригинал отдельно. Облачное хранение портретов пока не подключено.");
      }
    });

    clearButton.addEventListener("click", async () => {
      if (restoring) return;
      clearCard(card);
      setNote("Обновляем локальное сохранение портретов…");
      try {
        await queueSave();
        setNote("Предпросмотр и его локальная запись удалены. Оригиналы остальных портретов сохранены.");
      } catch (error) {
        setNote("Окно очищено, но обновить локальное сохранение не удалось: " + error.message);
      }
    });
  });

  window.addEventListener("pagehide", () => {
    previews.forEach((url) => URL.revokeObjectURL(url));
    previews.clear();
  });

  void restoreSavedSlots();
})();