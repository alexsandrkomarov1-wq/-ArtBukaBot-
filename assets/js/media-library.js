(() => {
  "use strict";

  const byId = (id) => document.getElementById(id);
  const input = byId("media-file-input");
  if (!input) return;

  const ui = {
    status: byId("media-status"),
    empty: byId("media-empty"),
    stage: byId("media-stage"),
    image: byId("media-image"),
    video: byId("media-video"),
    name: byId("media-current-name"),
    meta: byId("media-current-meta"),
    download: byId("media-download"),
    counter: byId("media-counter"),
    list: byId("media-list"),
    previous: byId("media-prev"),
    next: byId("media-next"),
    slideshow: byId("media-slideshow"),
    fullscreen: byId("media-fullscreen"),
    viewer: byId("media-viewer")
  };

  let files = [];
  let visible = [];
  let current = -1;
  let filter = "all";
  let slideshowTimer = null;

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " Б";
    const units = ["КБ", "МБ", "ГБ", "ТБ"];
    let size = bytes / 1024;
    let unit = 0;
    while (size >= 1024 && unit < units.length - 1) {
      size /= 1024;
      unit += 1;
    }
    return size.toFixed(size >= 10 ? 1 : 2) + " " + units[unit];
  };

  const kindOf = (file) => {
    if (file.type.startsWith("image/")) return "image";
    if (file.type.startsWith("video/")) return "video";
    const ext = file.name.split(".").pop().toLowerCase();
    if (/^(jpg|jpeg|png|gif|webp|bmp|avif|heic|heif|tif|tiff)$/.test(ext)) return "image";
    if (/^(mp4|m4v|webm|ogv|mov|mkv|avi|mpeg|mpg|3gp)$/.test(ext)) return "video";
    return null;
  };

  const stopSlideshow = () => {
    if (slideshowTimer !== null) window.clearInterval(slideshowTimer);
    slideshowTimer = null;
    ui.slideshow.textContent = "▶ Слайдшоу";
    ui.slideshow.setAttribute("aria-pressed", "false");
  };

  const revokeFiles = () => {
    files.forEach((item) => URL.revokeObjectURL(item.url));
    files = [];
    visible = [];
    current = -1;
  };

  const renderList = () => {
    ui.list.replaceChildren();
    if (!visible.length) {
      const empty = document.createElement("p");
      empty.className = "media-list-empty";
      empty.textContent = files.length ? "Нет файлов этого типа." : "Здесь появятся выбранные файлы.";
      ui.list.append(empty);
      return;
    }

    visible.forEach((item, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "media-item" + (index === current ? " is-current" : "");
      button.setAttribute("aria-pressed", index === current ? "true" : "false");
      const preview = document.createElement("span");
      preview.className = "media-item-preview";
      preview.textContent = item.kind === "video" ? "▶" : "▧";
      const info = document.createElement("span");
      info.className = "media-item-info";
      const name = document.createElement("strong");
      name.textContent = item.file.name;
      const meta = document.createElement("small");
      meta.textContent = (item.kind === "video" ? "Видео" : "Фото") + " · " + formatSize(item.file.size);
      info.append(name, meta);
      button.append(preview, info);
      button.addEventListener("click", () => show(index));
      ui.list.append(button);
    });
  };

  const applyFilter = () => {
    const selected = current >= 0 ? visible[current] : null;
    visible = files.filter((item) => filter === "all" || item.kind === filter);
    current = selected ? visible.indexOf(selected) : (visible.length ? 0 : -1);
    renderList();
    if (current >= 0) renderCurrent();
    else {
      ui.stage.hidden = true;
      ui.empty.hidden = false;
      ui.counter.textContent = "0 / 0";
      ui.previous.disabled = true;
      ui.next.disabled = true;
    }
  };

  const renderCurrent = () => {
    const item = visible[current];
    if (!item) return;
    ui.empty.hidden = true;
    ui.stage.hidden = false;
    ui.image.hidden = item.kind !== "image";
    ui.video.hidden = item.kind !== "video";
    ui.video.pause();
    ui.image.removeAttribute("src");
    ui.video.removeAttribute("src");
    if (item.kind === "image") {
      ui.image.src = item.url;
      ui.image.alt = item.file.name;
    } else {
      ui.video.src = item.url;
      ui.video.load();
    }
    ui.name.textContent = item.file.name;
    ui.meta.textContent = (item.kind === "video" ? "Видео" : "Фото") + " · " + formatSize(item.file.size) + " · " + item.file.type;
    ui.download.href = item.url;
    ui.download.download = item.file.name;
    ui.counter.textContent = (current + 1) + " / " + visible.length;
    ui.previous.disabled = visible.length < 2;
    ui.next.disabled = visible.length < 2;
    renderList();
  };

  const show = (index) => {
    if (!visible.length) return;
    current = (index + visible.length) % visible.length;
    renderCurrent();
  };

  const move = (step) => show(current + step);

  input.addEventListener("change", () => {
    stopSlideshow();
    revokeFiles();
    const accepted = Array.from(input.files || []).map((file) => {
      const kind = kindOf(file);
      return kind ? { file, kind, url: URL.createObjectURL(file) } : null;
    }).filter(Boolean);
    files = accepted;
    filter = "all";
    document.querySelectorAll(".media-filter").forEach((button) => {
      const active = button.dataset.filter === "all";
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", active ? "true" : "false");
    });
    ui.status.textContent = files.length
      ? "Выбрано файлов: " + files.length + ". Они открыты только в этом браузере и не загружены на сервер."
      : "Поддерживаемые фото и видео не найдены. Проверьте тип выбранных файлов.";
    ui.slideshow.disabled = !files.some((item) => item.kind === "image");
    ui.fullscreen.disabled = !files.length;
    applyFilter();
    input.value = "";
  });

  document.querySelectorAll(".media-filter").forEach((button) => {
    button.addEventListener("click", () => {
      filter = button.dataset.filter;
      document.querySelectorAll(".media-filter").forEach((item) => {
        const active = item === button;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", active ? "true" : "false");
      });
      applyFilter();
    });
  });

  ui.previous.addEventListener("click", () => move(-1));
  ui.next.addEventListener("click", () => move(1));
  ui.slideshow.addEventListener("click", () => {
    if (slideshowTimer !== null) {
      stopSlideshow();
      return;
    }
    const photos = visible.filter((item) => item.kind === "image");
    if (!photos.length) return;
    if (visible[current]?.kind !== "image") {
      const firstPhoto = visible.indexOf(photos[0]);
      show(firstPhoto);
    }
    ui.slideshow.textContent = "Ⅱ Остановить";
    ui.slideshow.setAttribute("aria-pressed", "true");
    slideshowTimer = window.setInterval(() => {
      let next = current;
      for (let i = 0; i < visible.length; i += 1) {
        next = (next + 1) % visible.length;
        if (visible[next].kind === "image") break;
      }
      show(next);
    }, 5000);
  });
  ui.fullscreen.addEventListener("click", async () => {
    try {
      if (!document.fullscreenElement) await ui.viewer.requestFullscreen();
      else await document.exitFullscreen();
    } catch (error) {
      ui.status.textContent = "Полноэкранный режим недоступен в этом браузере.";
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === "ArrowLeft" && visible.length > 1) move(-1);
    if (event.key === "ArrowRight" && visible.length > 1) move(1);
    if (event.key === "Escape") stopSlideshow();
  });
  window.addEventListener("beforeunload", () => {
    stopSlideshow();
    revokeFiles();
  });
})();
