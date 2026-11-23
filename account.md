---
layout: default
title: Личный кабинет
permalink: /account/
description: Быстрый доступ к семейным сервисам связи, почте и карте мира KOMAROVA_CORE
---

<section class="account-heading" aria-labelledby="account-title">
  <p class="eyebrow"><span class="eyebrow-line"></span> KOMAROVA_CORE · ЦЕНТР СВЯЗИ</p>
  <h1 id="account-title">Личный кабинет<span>.</span></h1>
  <p class="account-lead">Единая точка доступа к привычным сервисам общения, электронной почте и географии. Выберите нужный инструмент, чтобы продолжить работу на его официальной площадке.</p>
  <div class="account-meta"><span>ВНЕШНИЕ СЕРВИСЫ</span><i></i><span>БЫСТРЫЙ ДОСТУП</span><i></i><span>БЕЗ ПЕРЕДАЧИ ПАРОЛЕЙ</span></div>
</section>

<section class="account-section" aria-labelledby="communication-title">
  <div class="account-section-heading">
    <div><p class="eyebrow">01 / КОММУНИКАЦИИ</p><h2 id="communication-title">Оставаться на связи.</h2></div>
    <p>Мессенджеры открываются отдельно. Вход и авторизация происходят только на стороне соответствующего сервиса.</p>
  </div>
  <div class="account-grid">
    <article class="account-card">
      <div class="account-card-top"><span class="account-icon whatsapp-icon" aria-hidden="true">◉</span><span class="account-card-index">01</span></div>
      <p class="account-card-kicker">МЕССЕНДЖЕР</p>
      <h3>WhatsApp</h3>
      <p>Личные и групповые сообщения, аудио- и видеосвязь в поддерживаемых версиях сервиса.</p>
      <a class="account-action" href="https://web.whatsapp.com/login/" target="_blank" rel="noopener noreferrer">Открыть WhatsApp Web <span aria-hidden="true">↗</span></a>
    </article>
    <article class="account-card">
      <div class="account-card-top"><span class="account-icon telegram-icon" aria-hidden="true">➤</span><span class="account-card-index">02</span></div>
      <p class="account-card-kicker">МЕССЕНДЖЕР</p>
      <h3>Telegram</h3>
      <p>Открыть чаты, каналы и сообщения в веб-версии Telegram.</p>
      <a class="account-action" href="https://web.telegram.org/#/im." target="_blank" rel="noopener noreferrer">Открыть Telegram Web <span aria-hidden="true">↗</span></a>
    </article>
    <article class="account-card">
      <div class="account-card-top"><span class="account-icon outlook-icon" aria-hidden="true">✉</span><span class="account-card-index">03</span></div>
      <p class="account-card-kicker">ЭЛЕКТРОННАЯ ПОЧТА</p>
      <h3>Outlook</h3>
      <p>Переход непосредственно во входящие сообщения Outlook.</p>
      <a class="account-action" href="https://outlook.live.com/mail/0/inbox" target="_blank" rel="noopener noreferrer">Открыть входящие <span aria-hidden="true">↗</span></a>
    </article>
  </div>
</section>

<section class="account-contact" aria-labelledby="contact-title">
  <div class="account-contact-copy">
    <p class="eyebrow">02 / ПРЯМОЙ КОНТАКТ</p>
    <h2 id="contact-title">Написать или позвонить.</h2>
    <p>Письмо откроется в почтовой программе, настроенной на вашем устройстве. Для звонка нужен подтверждённый номер телефона: он пока не задан, поэтому сайт не будет подставлять случайный номер и изображать работающий вызов.</p>
  </div>
  <div class="account-contact-actions">
    <a class="account-action account-action-light" href="mailto:"> <span aria-hidden="true">✉</span> Написать письмо <span aria-hidden="true">↗</span></a>
    <div class="account-call-state" aria-label="Звонок пока не настроен">
      <span aria-hidden="true">☎</span><span><strong>Позвонить</strong><small>Номер телефона не настроен</small></span><span class="account-lock" aria-hidden="true">○</span>
    </div>
  </div>
</section>

<section class="account-map" aria-labelledby="map-title">
  <div class="account-map-copy">
    <p class="eyebrow">03 / ГЕОГРАФИЯ И ПУТЕШЕСТВИЯ</p>
    <h2 id="map-title">Мир становится ближе.</h2>
    <p>Выберите точку на планете: определите своё местоположение или найдите любой город, адрес и координаты вручную. Затем откройте выбранное место в Google Earth.</p>
    <form class="account-map-form" id="earth-place-form">
      <label for="earth-place-input">Место или координаты</label>
      <div class="account-map-search-row">
        <input id="earth-place-input" name="place" type="search" autocomplete="off" placeholder="Например, Хоругвино или 56.0697, 37.0757" required>
        <button type="submit" class="account-map-button">Найти место</button>
      </div>
      <button type="button" class="account-map-location" id="earth-geolocate">◎ Определить моё местоположение</button>
      <p class="account-map-status" id="earth-map-status" role="status" aria-live="polite">Пример выбран: Хоругвино, Московская область.</p>
    </form>
    <div class="account-map-result" aria-live="polite">
      <span class="account-map-result-label">ВЫБРАННОЕ МЕСТО</span>
      <strong id="earth-place-name">Хоругвино · Московская область</strong>
      <span class="account-map-coordinates" id="earth-place-coordinates">56°04′11″N · 37°04′33″E</span>
      <a class="account-action" id="earth-open-link" href="https://earth.google.com/web/@56.06970397,37.07571186,1500a,25000d,35y,0h,0t,0r" target="_blank" rel="noopener noreferrer">Открыть Google Earth <span aria-hidden="true">↗</span></a>
    </div>
    <p class="account-map-attribution">Поиск мест выполняется через OpenStreetMap Nominatim. При поиске или обратном определении адреса координаты передаются этому сервису. Геолокация запрашивается только после нажатия кнопки и с разрешения браузера. <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">Условия и атрибуция OpenStreetMap</a>.</p>
  </div>
  <div class="account-map-art" aria-label="Стилизованная карта мира">
    <div class="map-grid-lines"></div><div class="map-globe"><span class="map-latitude"></span><span class="map-longitude"></span><span class="map-marker"></span></div>
    <span class="map-caption" id="earth-map-caption">56°04′11″N · 37°04′33″E<br>ХОРУГВИНО · МОСКОВСКАЯ ОБЛАСТЬ</span>
  </div>
</section>

<aside class="account-privacy">
  <span class="account-privacy-mark" aria-hidden="true">✳</span>
  <div><h2>Ваши учётные записи остаются вашими.</h2><p>KOMAROVA_CORE не запрашивает пароли, коды подтверждения, cookies или токены WhatsApp, Telegram и Outlook. Эта страница содержит только ссылки на внешние сервисы и не подключена к их аккаунтам.</p></div>
</aside>

<script>
(function () {
  const form = document.getElementById('earth-place-form');
  if (!form) return;
  const input = document.getElementById('earth-place-input');
  const status = document.getElementById('earth-map-status');
  const nameNode = document.getElementById('earth-place-name');
  const coordinatesNode = document.getElementById('earth-place-coordinates');
  const caption = document.getElementById('earth-map-caption');
  const earthLink = document.getElementById('earth-open-link');
  const geoButton = document.getElementById('earth-geolocate');

  function dms(value, positive, negative) {
    const direction = value < 0 ? negative : positive;
    const absolute = Math.abs(value);
    const degrees = Math.floor(absolute);
    const minutesFloat = (absolute - degrees) * 60;
    const minutes = Math.floor(minutesFloat);
    const seconds = Math.round((minutesFloat - minutes) * 60);
    return degrees + '°' + String(minutes).padStart(2, '0') + '′' + String(seconds).padStart(2, '0') + '″' + direction;
  }

  function parseCoordinates(value) {
    const decimal = value.trim().match(/^(-?\d+(?:[.,]\d+)?)\s*[,; ]+\s*(-?\d+(?:[.,]\d+)?)$/);
    if (decimal) {
      const lat = Number(decimal[1].replace(',', '.'));
      const lon = Number(decimal[2].replace(',', '.'));
      if (Number.isFinite(lat) && Number.isFinite(lon) && Math.abs(lat) <= 90 && Math.abs(lon) <= 180) return { lat, lon };
    }
    const matches = [...value.matchAll(/(-?\d+(?:[.,]\d+)?)\s*°\s*(\d+(?:[.,]\d+)?)?\s*[′']?\s*(\d+(?:[.,]\d+)?)?\s*[″"]?\s*([NSEW])/gi)];
    if (matches.length === 2) {
      const values = matches.map(match => {
        const degrees = Number(match[1].replace(',', '.'));
        const minutes = Number((match[2] || '0').replace(',', '.'));
        const seconds = Number((match[3] || '0').replace(',', '.'));
        const direction = match[4].toUpperCase();
        return (degrees < 0 ? -1 : 1) * (Math.abs(degrees) + minutes / 60 + seconds / 3600) * (direction === 'S' || direction === 'W' ? -1 : 1);
      });
      if (Math.abs(values[0]) <= 90 && Math.abs(values[1]) <= 180) return { lat: values[0], lon: values[1] };
    }
    return null;
  }

  async function reverseName(lat, lon) {
    const url = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon);
    const response = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!response.ok) throw new Error('Сервис поиска мест временно недоступен.');
    const data = await response.json();
    return data.display_name || 'Выбранные координаты';
  }

  function selectPlace(lat, lon, label) {
    const latText = dms(lat, 'N', 'S');
    const lonText = dms(lon, 'E', 'W');
    const coords = latText + ' · ' + lonText;
    nameNode.textContent = label;
    coordinatesNode.textContent = coords;
    caption.textContent = coords + ' / ' + label.toLocaleUpperCase('ru-RU');
    earthLink.href = 'https://earth.google.com/web/@' + lat + ',' + lon + ',1500a,25000d,35y,0h,0t,0r';
    earthLink.setAttribute('aria-label', 'Открыть Google Earth: ' + label + ', ' + coords);
    const marker = document.querySelector('.map-marker');
    if (marker) marker.style.transform = 'translate(' + ((lon + 180) / 360 * 80 - 40) + 'px,' + ((90 - lat) / 180 * 80 - 40) + 'px)';
  }

  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    const query = input.value.trim();
    if (!query) return;
    status.textContent = 'Ищем место…';
    try {
      const coords = parseCoordinates(query);
      if (coords) {
        let label = 'Выбранные координаты';
        try { label = await reverseName(coords.lat, coords.lon); } catch (_) {}
        selectPlace(coords.lat, coords.lon, label);
        status.textContent = 'Координаты найдены. Можно открыть выбранную точку в Google Earth.';
        return;
      }
      const url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=' + encodeURIComponent(query);
      const response = await fetch(url, { headers: { 'Accept': 'application/json' } });
      if (!response.ok) throw new Error('Сервис поиска мест временно недоступен.');
      const results = await response.json();
      if (!results.length) throw new Error('Место не найдено. Уточните название или введите координаты.');
      const place = results[0];
      selectPlace(Number(place.lat), Number(place.lon), place.display_name);
      status.textContent = 'Место найдено. Координаты определены по OpenStreetMap.';
    } catch (error) {
      status.textContent = error.message || 'Не удалось найти место. Проверьте соединение и попробуйте ещё раз.';
    }
  });

  geoButton.addEventListener('click', function () {
    if (!navigator.geolocation) {
      status.textContent = 'Этот браузер не поддерживает геолокацию.';
      return;
    }
    status.textContent = 'Запрашиваем разрешение браузера на геолокацию…';
    navigator.geolocation.getCurrentPosition(async function (position) {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      status.textContent = 'Местоположение определено. Получаем название места…';
      let label = 'Моё местоположение';
      try { label = await reverseName(lat, lon); } catch (_) {}
      selectPlace(lat, lon, label);
      status.textContent = 'Текущие координаты определены браузером. Точность зависит от устройства и разрешения геолокации.';
    }, function (error) {
      const messages = {
        1: 'Доступ к геолокации запрещён. Разрешите его в настройках браузера или введите место вручную.',
        2: 'Не удалось определить местоположение устройства.',
        3: 'Время ожидания геолокации истекло. Попробуйте ещё раз или введите место вручную.'
      };
      status.textContent = messages[error.code] || 'Не удалось определить местоположение.';
    }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
  });
})();
</script>

<p class="account-back"><a href="{{ '/' | relative_url }}">← Вернуться на главную</a></p>
