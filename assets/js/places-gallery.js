(() => {
  const root = document.querySelector("[data-places-gallery]");
  if (!root) return;
  const topics = [
    { query: 'filetype:bitmap "Hermitage Museum" Saint Petersburg', fallback: "Эрмитаж · Санкт-Петербург" },
    { query: 'filetype:bitmap Peterhof Palace Grand Cascade', fallback: "Петергоф · дворцы и парки" },
    { query: 'filetype:bitmap Lake Baikal landscape', fallback: "Байкал · природное наследие" }
  ];
  const collections = [[], [], []];
  const positions = [0, 0, 0];
  const clean = value => String(value || "").replace(/<[^>]*>/g, " ").replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
  const meta = (info, key) => info.extmetadata && info.extmetadata[key] ? clean(info.extmetadata[key].value) : "";
  async function loadTopic(topic, index) {
    const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&generator=search&gsrnamespace=6&gsrlimit=18&gsrsearch=" + encodeURIComponent(topic.query) + "&prop=imageinfo&iiprop=url%7Cextmetadata&iiurlwidth=1000";
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Wikimedia Commons HTTP " + response.status);
    const data = await response.json();
    const pages = Object.values(data.query && data.query.pages ? data.query.pages : {});
    return pages.map(page => {
      const info = page.imageinfo && page.imageinfo[0];
      if (!info || !info.thumburl || !info.descriptionurl || !info.mime || !info.mime.startsWith("image/")) return null;
      if (!info.thumburl.startsWith("https://upload.wikimedia.org/") || !info.descriptionurl.startsWith("https://commons.wikimedia.org/wiki/File:")) return null;
      const license = meta(info, "LicenseShortName");
      if (!license) return null;
      const artist = meta(info, "Artist") || meta(info, "Credit") || "Автор указан на странице файла";
      return { title: page.title.replace(/^File:/, "").replace(/_/g, " "), image: info.thumburl, page: info.descriptionurl, license, artist };
    }).filter(Boolean);
  }
  function show(index, advance) {
    const items = collections[index];
    if (!items.length) return;
    if (advance) positions[index] = (positions[index] + 1) % items.length;
    const item = items[positions[index]];
    const img = root.querySelector('[data-place-image="' + index + '"]');
    const link = root.querySelector('[data-place-link="' + index + '"]');
    const title = root.querySelector('[data-place-title="' + index + '"]');
    const credit = root.querySelector('[data-place-credit="' + index + '"]');
    img.classList.remove("is-loaded");
    img.onload = () => img.classList.add("is-loaded");
    img.onerror = () => { img.classList.remove("is-loaded"); credit.textContent = "Изображение временно недоступно"; };
    img.src = item.image;
    img.alt = item.title;
    link.href = item.page;
    title.textContent = item.title;
    credit.textContent = item.artist + " · " + item.license;
  }
  async function refresh() {
    const button = root.querySelector("[data-gallery-refresh]");
    button.disabled = true;
    button.textContent = "Обновляем…";
    await Promise.all(topics.map(async (topic, index) => {
      try {
        const items = await loadTopic(topic, index);
        if (items.length) {
          collections[index] = items;
          positions[index] = Math.floor(Math.random() * items.length);
          show(index, false);
        } else {
          root.querySelector('[data-place-credit="' + index + '"]').textContent = "В открытой медиатеке пока нет подходящего файла";
        }
      } catch (error) {
        root.querySelector('[data-place-credit="' + index + '"]').textContent = "Источник временно недоступен · Wikimedia Commons";
      }
    }));
    button.disabled = false;
    button.innerHTML = 'Обновить фотографии <span aria-hidden="true">↻</span>';
  }
  root.querySelector("[data-gallery-refresh]").addEventListener("click", refresh);
  refresh();
  window.setInterval(() => topics.forEach((_, index) => show(index, true)), 12000);
})();
