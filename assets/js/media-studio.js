(() => {
  "use strict";

  const root = document.querySelector("[data-ai-media-lab]");
  if (!root) return;

  const fileInput = root.querySelector("[data-music-files]");
  const audio = root.querySelector("[data-music-audio]");
  const playlist = root.querySelector("[data-music-playlist]");
  const play = root.querySelector("[data-music-play]");
  const previous = root.querySelector("[data-music-previous]");
  const next = root.querySelector("[data-music-next]");
  const seek = root.querySelector("[data-music-seek]");
  const currentTime = root.querySelector("[data-music-current-time]");
  const duration = root.querySelector("[data-music-duration]");
  const volume = root.querySelector("[data-music-volume]");
  const musicStatus = root.querySelector("[data-music-status]");
  const radioSearch = root.querySelector("[data-radio-search]");
  const radioFind = root.querySelector("[data-radio-find]");
  const radioList = root.querySelector("[data-radio-list]");
  const radioAudio = root.querySelector("[data-radio-audio]");
  const radioUrl = root.querySelector("[data-radio-url]");
  const radioConnect = root.querySelector("[data-radio-connect]");
  const radioStatus = root.querySelector("[data-radio-status]");

  let tracks = [];
  let index = -1;
  let activeUrl = null;

  const time = value => {
    if (!Number.isFinite(value) || value < 0) return "0:00";
    const seconds = Math.floor(value);
    return Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");
  };

  function releaseTracks() {
    tracks.forEach(track => URL.revokeObjectURL(track.url));
    tracks = [];
    index = -1;
    activeUrl = null;
  }

  function renderPlaylist() {
    playlist.replaceChildren();
    if (!tracks.length) {
      const empty = document.createElement("p");
      empty.className = "media-player-empty";
      empty.textContent = "Добавьте MP3 или другой аудиофайл с устройства. Файлы остаются в этом браузере и не отправляются в архив.";
      playlist.append(empty);
      return;
    }
    tracks.forEach((track, i) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "media-track" + (i === index ? " is-active" : "");
      button.setAttribute("aria-current", i === index ? "true" : "false");
      button.textContent = String(i + 1).padStart(2, "0") + " · " + track.file.name;
      button.addEventListener("click", () => void loadTrack(i, true));
      playlist.append(button);
    });
  }

  async function loadTrack(nextIndex, autoplay) {
    if (!tracks.length || nextIndex < 0 || nextIndex >= tracks.length) return;
    index = nextIndex;
    const track = tracks[index];
    audio.src = track.url;
    audio.load();
    renderPlaylist();
    musicStatus.textContent = "Выбран трек: " + track.file.name;
    if (autoplay) {
      try {
        await audio.play();
        play.textContent = "Ⅱ Пауза";
      } catch (error) {
        musicStatus.textContent = "Браузер не запустил файл: " + (error.message || "формат не поддерживается");
      }
    } else {
      play.textContent = "▶ Воспроизвести";
    }
  }

  fileInput.addEventListener("change", () => {
    const files = Array.from(fileInput.files || []).filter(file => file.type.startsWith("audio/") || /\.(mp3|m4a|aac|wav|ogg|flac)$/i.test(file.name));
    if (!files.length) {
      musicStatus.textContent = "Не найден поддерживаемый аудиофайл.";
      return;
    }
    releaseTracks();
    tracks = files.map(file => ({ file, url: URL.createObjectURL(file) }));
    index = 0;
    renderPlaylist();
    void loadTrack(0, false);
    musicStatus.textContent = "Добавлено файлов: " + tracks.length + ". Это локальный список, не постоянная архивная запись.";
  });

  play.addEventListener("click", async () => {
    if (!tracks.length) {
      fileInput.click();
      return;
    }
    if (audio.paused) {
      try {
        if (audio.ended) audio.currentTime = 0;
        await audio.play();
        play.textContent = "Ⅱ Пауза";
      } catch (error) {
        musicStatus.textContent = "Не удалось воспроизвести файл: " + (error.message || "ошибка");
      }
    } else {
      audio.pause();
      play.textContent = "▶ Воспроизвести";
    }
  });

  previous.addEventListener("click", () => void loadTrack(Math.max(0, index - 1), true));
  next.addEventListener("click", () => void loadTrack((index + 1) % tracks.length, true));
  audio.addEventListener("play", () => { play.textContent = "Ⅱ Пауза"; });
  audio.addEventListener("pause", () => { play.textContent = "▶ Воспроизвести"; });
  audio.addEventListener("ended", () => {
    if (index + 1 < tracks.length) void loadTrack(index + 1, true);
    else play.textContent = "▶ Воспроизвести";
  });
  audio.addEventListener("loadedmetadata", () => {
    seek.max = String(Math.floor(audio.duration || 0));
    duration.textContent = time(audio.duration);
  });
  audio.addEventListener("timeupdate", () => {
    seek.value = String(Math.floor(audio.currentTime || 0));
    currentTime.textContent = time(audio.currentTime);
  });
  seek.addEventListener("input", () => {
    if (Number.isFinite(audio.duration)) audio.currentTime = Number(seek.value);
  });
  volume.addEventListener("input", () => { audio.volume = Number(volume.value) / 100; });
  audio.volume = Number(volume.value) / 100;

  async function findStations() {
    radioFind.disabled = true;
    radioStatus.textContent = "Ищем открытые интернет-радиостанции…";
    radioList.replaceChildren();
    const query = radioSearch.value.trim();
    const endpoint = new URL("https://de1.api.radio-browser.info/json/stations/search");
    endpoint.search = new URLSearchParams({
      limit: "15", order: "clickcount", reverse: "true", hidebroken: "true",
      ...(query ? { name: query } : { tag: "nature" })
    }).toString();
    try {
      const response = await fetch(endpoint.toString(), { headers: { "Accept": "application/json" } });
      if (!response.ok) throw new Error("Каталог радио ответил HTTP " + response.status);
      const stations = await response.json();
      if (!Array.isArray(stations) || !stations.length) {
        radioStatus.textContent = "Станции не найдены. Можно вставить прямую ссылку на поток вручную.";
        return;
      }
      stations.forEach(station => {
        if (!station.url_resolved) return;
        const button = document.createElement("button");
        button.type = "button";
        button.className = "radio-station";
        const bitrate = station.bitrate ? " · " + station.bitrate + " кбит/с" : "";
        button.textContent = (station.name || "Без названия") + bitrate;
        button.addEventListener("click", () => playStation(station.url_resolved, station.name || "Интернет-радио"));
        radioList.append(button);
      });
      radioStatus.textContent = "Найдено станций: " + radioList.children.length + ". Воспроизведение зависит от доступности потока и сети.";
    } catch (error) {
      radioStatus.textContent = "Каталог радио сейчас недоступен: " + error.message + ". Вставьте прямой URL потока ниже.";
    } finally {
      radioFind.disabled = false;
    }
  }

  async function playStation(url, name) {
    try {
      const parsed = new URL(url);
      if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("Допускаются только HTTP/HTTPS потоки.");
      audio.pause();
      radioAudio.src = parsed.href;
      radioAudio.load();
      await radioAudio.play();
      radioStatus.textContent = "Играет радио: " + name;
    } catch (error) {
      radioStatus.textContent = "Не удалось запустить станцию: " + error.message + ". Поток может быть недоступен или блокироваться сетью.";
    }
  }

  radioFind.addEventListener("click", () => void findStations());
  radioConnect.addEventListener("click", () => {
    const url = radioUrl.value.trim();
    if (!url) {
      radioStatus.textContent = "Сначала вставьте прямую ссылку на аудиопоток.";
      return;
    }
    void playStation(url, "Пользовательский поток");
  });
  radioAudio.addEventListener("error", () => {
    radioStatus.textContent = "Поток остановлен или формат не поддерживается браузером.";
  });
  window.addEventListener("pagehide", () => {
    releaseTracks();
    radioAudio.pause();
    audio.pause();
  });
})();