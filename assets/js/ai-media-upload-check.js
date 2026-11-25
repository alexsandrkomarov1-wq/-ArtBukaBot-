(() => {
  "use strict";

  const input = document.getElementById("ai-media-file");
  const status = document.getElementById("ai-media-check-status");
  const result = document.getElementById("ai-media-check-result");
  const details = document.getElementById("ai-media-check-details");
  if (!input || !status || !result || !details) return;

  const MAX_BYTES = 100 * 1024 * 1024;
  const IMAGE_EXT = new Set(["jpg", "jpeg", "png", "gif", "webp", "tif", "tiff", "bmp", "heic", "heif"]);
  const VIDEO_EXT = new Set(["mp4", "m4v", "mov", "avi", "mkv", "webm", "3gp"]);
  let generation = 0;

  const extensionOf = (name) => name.includes(".") ? name.split(".").pop().toLowerCase() : "";
  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " Б";
    const units = ["КБ", "МБ", "ГБ"];
    let value = bytes / 1024;
    let unit = 0;
    while (value >= 1024 && unit < units.length - 1) { value /= 1024; unit += 1; }
    return value.toFixed(value >= 10 ? 1 : 2) + " " + units[unit];
  };
  const addLine = (tag, text) => {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  };
  const setStatus = (message, state) => {
    status.textContent = message;
    status.dataset.state = state || "info";
  };
  const signatureOf = async (file) => {
    const bytes = new Uint8Array(await file.slice(0, 32).arrayBuffer());
    const starts = (...values) => values.every((value, index) => bytes[index] === value);
    if (starts(0xff, 0xd8, 0xff)) return "photo";
    if (starts(0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a)) return "photo";
    if (starts(0x47, 0x49, 0x46, 0x38, 0x37, 0x61) || starts(0x47, 0x49, 0x46, 0x38, 0x39, 0x61)) return "photo";
    if (starts(0x52, 0x49, 0x46, 0x46) && bytes[8] === 0x57 && bytes[9] === 0x45 && bytes[10] === 0x42 && bytes[11] === 0x50) return "photo";
    if (starts(0x49, 0x49, 0x2a, 0x00) || starts(0x4d, 0x4d, 0x00, 0x2a)) return "photo";
    if (starts(0x1a, 0x45, 0xdf, 0xa3)) return "video";
    if (starts(0x52, 0x49, 0x46, 0x46) && bytes[8] === 0x41 && bytes[9] === 0x56 && bytes[10] === 0x49) return "video";
    if (bytes.length >= 12 && bytes[4] === 0x66 && bytes[5] === 0x74 && bytes[6] === 0x79 && bytes[7] === 0x70) {
      const brand = String.fromCharCode(bytes[8], bytes[9], bytes[10], bytes[11]);
      if (["heic", "heix", "hevc", "hevx", "mif1", "msf1"].includes(brand)) return "photo";
      return "video";
    }
    return null;
  };

  const inspectImage = async (file, recommendations, facts) => {
    if (typeof createImageBitmap !== "function") {
      recommendations.push("Браузер не поддерживает локальный анализ изображения. Нужен серверный анализатор.");
      return;
    }
    let bitmap;
    try {
      bitmap = await createImageBitmap(file);
      const width = bitmap.width;
      const height = bitmap.height;
      facts.push("Размер изображения: " + width + " × " + height + " пикселей");
      facts.push("Разрешение: " + (width * height / 1000000).toFixed(2) + " Мп");
      if (width < 1920 || height < 1080) recommendations.push("Небольшое исходное разрешение. Можно рассмотреть увеличение до 2K; 4K имеет смысл только после оценки результата.");
      if (width * height < 1000000) recommendations.push("Меньше 1 Мп: увеличение разрешения может быть полезно, но новые детали будут предположительными.");
      const canvas = document.createElement("canvas");
      const scale = Math.min(128 / width, 128 / height);
      canvas.width = Math.max(1, Math.round(width * scale));
      canvas.height = Math.max(1, Math.round(height * scale));
      const context = canvas.getContext("2d", { willReadFrequently: true });
      if (!context) {
        recommendations.push("Не удалось получить пиксельные данные для предварительной оценки.");
        return;
      }
      context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
      const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
      const gray = new Float32Array(canvas.width * canvas.height);
      let sum = 0;
      for (let i = 0, p = 0; i < pixels.length; i += 4, p += 1) {
        const luminance = 0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2];
        gray[p] = luminance;
        sum += luminance;
      }
      const count = gray.length;
      const mean = sum / count;
      let variance = 0;
      for (let i = 0; i < count; i += 1) variance += (gray[i] - mean) ** 2;
      const contrast = Math.sqrt(variance / count);
      facts.push("Средняя яркость: " + Math.round(mean) + " / 255");
      facts.push("Контрастность кадра: " + Math.round(contrast) + " (ориентировочная оценка)");
      if (mean < 65) recommendations.push("Кадр выглядит тёмным по средней яркости. Возможна коррекция экспозиции и теней.");
      else if (mean > 210) recommendations.push("Кадр выглядит очень светлым. Стоит проверить пересветы и коррекцию экспозиции.");
      if (contrast < 35) recommendations.push("Низкий общий контраст. Можно проверить коррекцию уровней и контраста.");
      let lapSum = 0;
      let lapSquareSum = 0;
      let samples = 0;
      for (let y = 1; y < canvas.height - 1; y += 1) {
        for (let x = 1; x < canvas.width - 1; x += 1) {
          const at = y * canvas.width + x;
          const lap = 4 * gray[at] - gray[at - 1] - gray[at + 1] - gray[at - canvas.width] - gray[at + canvas.width];
          lapSum += lap;
          lapSquareSum += lap * lap;
          samples += 1;
        }
      }
      if (samples) {
        const lapVariance = Math.max(0, lapSquareSum / samples - (lapSum / samples) ** 2);
        facts.push("Локальная детализация: " + Math.round(lapVariance) + " (эвристическая оценка резкости)");
        if (lapVariance < 45) recommendations.push("Возможна мягкость или размытие. Рекомендуется отдельно проверить деликатное повышение резкости.");
      }
      if (!recommendations.length) recommendations.push("Явных проблем по базовым показателям не обнаружено. Можно оставить оригинал без изменений или выполнить экспертную проверку.");
      recommendations.push("Колоризацию, удаление царапин и генеративное восстановление выполнять только по отдельному выбору.");
    } catch (_) {
      facts.push("Размер изображения подтверждён по файлу, но браузер не смог декодировать пиксели.");
      recommendations.push("Для этого формата нужна серверная конвертация и проверка. Визуальная оценка качества не выполнена.");
    } finally {
      if (bitmap) bitmap.close();
    }
  };

  const inspectVideo = (file, recommendations, facts) => new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const video = document.createElement("video");
    video.preload = "metadata";
    const timeout = window.setTimeout(() => finish(new Error("Истекло время чтения видеометаданных.")), 15000);
    const finish = (error) => {
      window.clearTimeout(timeout);
      video.removeAttribute("src");
      video.load();
      URL.revokeObjectURL(url);
      if (error) reject(error);
      else resolve();
    };
    video.onloadedmetadata = () => {
      facts.push("Размер кадра: " + video.videoWidth + " × " + video.videoHeight + " пикселей");
      facts.push("Продолжительность: " + (Number.isFinite(video.duration) ? Math.round(video.duration) + " сек." : "не определена"));
      if (video.videoWidth < 1920 || video.videoHeight < 1080) recommendations.push("Исходное разрешение ниже Full HD. Можно оценить целесообразность увеличения разрешения.");
      recommendations.push("Стабилизацию, шумоподавление и синхронизацию звука нельзя надёжно оценить только по метаданным. Для этого нужен анализ кадров и аудиодорожки.");
      finish();
    };
    video.onerror = () => finish(new Error("Браузер не смог прочитать видеометаданные или контейнер."));
    video.src = url;
  });

  const renderResult = (file, kind, facts, recommendations) => {
    details.replaceChildren();
    const factsSection = document.createElement("section");
    factsSection.append(addLine("h4", "Техническая информация"));
    const factsList = document.createElement("ul");
    facts.forEach((fact) => factsList.append(addLine("li", fact)));
    factsSection.append(factsList);
    const suggestionsSection = document.createElement("section");
    suggestionsSection.append(addLine("h4", "Предложения по улучшению"));
    const suggestionsList = document.createElement("ul");
    recommendations.forEach((item) => suggestionsList.append(addLine("li", item)));
    suggestionsSection.append(suggestionsList);
    details.append(factsSection, suggestionsSection);
    result.hidden = false;
    setStatus("Проверка завершена: " + (kind === "photo" ? "фотография" : "видеозапись") + ". " + file.name + " · " + formatSize(file.size) + ". Файл проверен локально и не отправлялся на сервер.", "ok");
  };

  input.addEventListener("change", async () => {
    const run = ++generation;
    const file = input.files && input.files[0];
    result.hidden = true;
    details.replaceChildren();
    if (!file) return;
    setStatus("Проверяем файл…", "working");
    const extension = extensionOf(file.name);
    const kindByExtension = IMAGE_EXT.has(extension) ? "photo" : VIDEO_EXT.has(extension) ? "video" : null;
    try {
      if (file.size === 0) throw new Error("Файл пустой.");
      if (file.size > MAX_BYTES) throw new Error("Размер превышает допустимые 100 МиБ.");
      if (!kindByExtension) throw new Error("Формат файла не поддерживается.");
      const detectedKind = await signatureOf(file);
      if (run !== generation) return;
      if (detectedKind !== kindByExtension) throw new Error("Содержимое файла не соответствует расширению или файл повреждён.");
      const facts = ["Тип: " + (kindByExtension === "photo" ? "фотография" : "видеозапись"), "Формат: ." + extension, "Размер файла: " + formatSize(file.size), "Сигнатура файла соответствует поддерживаемому типу."];
      const recommendations = [];
      if (kindByExtension === "photo") await inspectImage(file, recommendations, facts);
      else {
        try {
          await inspectVideo(file, recommendations, facts);
        } catch (error) {
          facts.push("Формат и сигнатура файла проверены; браузер не смог прочитать видеометаданные.");
          recommendations.push("Для анализа разрешения, кадров, стабилизации и аудиосинхронизации нужен серверный медиапроцессор.");
        }
      }
      if (run !== generation) return;
      renderResult(file, kindByExtension, facts, recommendations);
    } catch (error) {
      if (run !== generation) return;
      setStatus("Проверка не пройдена: " + (error && error.message ? error.message : "неизвестная ошибка") + " Оригинал не изменён.", "error");
    }
  });
})();