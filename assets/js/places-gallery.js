(() => {
  const root = document.querySelector("[data-places-gallery]");
  if (!root) return;

  const topics = [
    {
      query: "Hermitage Museum Saint Petersburg",
      nasaQuery: "Hermitage Museum Saint Petersburg",
      fallback: "Эрмитаж · Санкт-Петербург"
    },
    {
      query: "Peterhof Palace gardens fountains Russia",
      nasaQuery: "Peterhof Palace Russia",
      fallback: "Петергоф · дворцы и парки"
    },
    {
      query: "Lake Baikal Siberia landscape",
      nasaQuery: "Lake Baikal Siberia",
      fallback: "Байкал · природное наследие"
    }
  ];

  const collections = [[], [], []];
  const positions = [0, 0, 0];
  const sourceOrder = [
    ["openverse", "commons", "nasa"],
    ["commons", "openverse", "nasa"],
    ["nasa", "openverse", "commons"]
  ];
  const NASA_GUIDELINES = "https://www.nasa.gov/nasa-brand-center/images-and-media/";

  const safeHttps = value => {
    try {
      const url = new URL(value);
      return url.protocol === "https:" ? url.href : "";
    } catch (_) {
      return "";
    }
  };

  const clean = value => String(value || "")
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  const meta = (info, key) => info.extmetadata && info.extmetadata[key]
    ? clean(info.extmetadata[key].value)
    : "";

  async function loadOpenverse(topic) {
    const url = "https://api.openverse.org/v1/images/?q=" +
      encodeURIComponent(topic.query) + "&page_size=24&mature=false";
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Openverse HTTP " + response.status);
    const data = await response.json();

    return (data.results || []).map(item => {
      const image = safeHttps(item.thumbnail || item.url);
      const page = safeHttps(item.foreign_landing_url);
      const licenseUrl = safeHttps(item.license_url);
      if (!image || !page || !licenseUrl || !item.license) return null;
      return {
        title: clean(item.title) || topic.fallback,
        image,
        page,
        artist: clean(item.creator) || "Автор не указан в карточке источника",
        license: (String(item.license).toUpperCase() +
          (item.license_version ? " " + item.license_version : "")),
        licenseUrl,
        source: "Openverse · " + (item.provider || item.source || "каталог открытых изображений")
      };
    }).filter(Boolean);
  }

  async function loadCommons(topic) {
    const query = 'filetype:bitmap "' + topic.query + '"';
    const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*" +
      "&generator=search&gsrnamespace=6&gsrlimit=24&gsrsearch=" + encodeURIComponent(query) +
      "&prop=imageinfo&iiprop=url%7Cextmetadata&iiurlwidth=1000";
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Wikimedia Commons HTTP " + response.status);
    const data = await response.json();
    const pages = Object.values(data.query && data.query.pages ? data.query.pages : {});

    return pages.map(page => {
      const info = page.imageinfo && page.imageinfo[0];
      if (!info || !info.mime || !info.mime.startsWith("image/")) return null;
      const image = safeHttps(info.thumburl);
      const landing = safeHttps(info.descriptionurl);
      const licenseUrl = safeHttps(meta(info, "LicenseUrl"));
      const license = meta(info, "LicenseShortName");
      if (!image || !landing || !licenseUrl || !license) return null;
      return {
        title: page.title.replace(/^File:/, "").replace(/_/g, " "),
        image,
        page: landing,
        artist: meta(info, "Artist") || meta(info, "Credit") || "Автор указан на странице файла",
        license,
        licenseUrl,
        source: "Wikimedia Commons"
      };
    }).filter(Boolean);
  }

  async function loadNasa(topic) {
    const url = "https://images-api.nasa.gov/search?q=" +
      encodeURIComponent(topic.nasaQuery) + "&media_type=image&page_size=24";
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("NASA Images API HTTP " + response.status);
    const data = await response.json();
    const items = data.collection && data.collection.items ? data.collection.items : [];

    return items.map(entry => {
      const metadata = entry.data && entry.data[0] ? entry.data[0] : {};
      const preview = entry.links && entry.links.find(link => link.rel === "preview");
      const image = safeHttps(preview && preview.href);
      const nasaId = metadata.nasa_id;
      if (!image || !nasaId) return null;
      const page = "https://images.nasa.gov/details/" + encodeURIComponent(nasaId);
      const artist = clean(metadata.photographer || metadata.center || metadata.secondary_creator) ||
        "Авторство уточняется на странице NASA";
      const copyright = clean(metadata.copyright);
      return {
        title: clean(metadata.title) || topic.fallback,
        image,
        page,
        artist: copyright ? artist + " · " + copyright : artist,
        license: "Условия использования NASA",
        licenseUrl: NASA_GUIDELINES,
        source: "NASA Image and Video Library"
      };
    }).filter(Boolean);
  }

  const providers = {
    openverse: loadOpenverse,
    commons: loadCommons,
    nasa: loadNasa
  };

  async function loadTopic(topic, index) {
    const errors = [];
    for (const source of sourceOrder[index]) {
      try {
        const items = await providers[source](topic);
        if (items.length) return items;
      } catch (error) {
        errors.push(source);
      }
    }
    if (errors.length === sourceOrder[index].length) {
      throw new Error("Все внешние источники временно недоступны");
    }
    return [];
  }

  function addCreditLink(parent, label, href) {
    const link = document.createElement("a");
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = label;
    parent.appendChild(link);
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
    img.onerror = () => {
      img.classList.remove("is-loaded");
      credit.textContent = "Файл источника временно недоступен";
    };
    img.src = item.image;
    img.alt = item.title;
    link.href = item.page;
    title.textContent = item.title;

    credit.replaceChildren();
    credit.appendChild(document.createTextNode(item.artist + " · "));
    addCreditLink(credit, item.source, item.page);
    credit.appendChild(document.createTextNode(" · "));
    addCreditLink(credit, item.license, item.licenseUrl);
  }

  async function refresh() {
    const button = root.querySelector("[data-gallery-refresh]");
    button.disabled = true;
    button.textContent = "Обновляем…";

    await Promise.all(topics.map(async (topic, index) => {
      const credit = root.querySelector('[data-place-credit="' + index + '"]');
      try {
        const items = await loadTopic(topic, index);
        if (items.length) {
          collections[index] = items;
          positions[index] = Math.floor(Math.random() * items.length);
          show(index, false);
        } else {
          credit.textContent = "Подходящее изображение не найдено в Openverse, Wikimedia Commons или NASA";
        }
      } catch (_) {
        credit.textContent = "Openverse, Wikimedia Commons и NASA временно недоступны";
      }
    }));

    button.disabled = false;
    button.innerHTML = 'Обновить фотографии <span aria-hidden="true">↻</span>';
  }

  root.querySelector("[data-gallery-refresh]").addEventListener("click", refresh);
  refresh();
  window.setInterval(() => topics.forEach((_, index) => show(index, true)), 12000);
})();