---
layout: default
title: Медиатека
permalink: /media/
description: Локальный просмотр фотографий и видео в KOMAROVA_CORE
---
<section class="media-heading">
  <p class="eyebrow">KOMAROVA_CORE · MEDIA</p>
  <h1>Семейная <em>медиатека.</em></h1>
  <p class="media-lead">Закрытый облачный архив подключается через защищённый backend и приватное хранилище Neon. Локальный просмотр не отправляет их на сервер; файлы из облачного кабинета передаются только после входа в закрытый архив. Браузер обычно учитывает EXIF-поворот поддерживаемых фотографий, но HEIC/HEIF и поворот видео зависят от декодера устройства.</p>
</section>

<section class="cloud-archive" aria-labelledby="cloud-archive-title">
  <div class="media-library-heading"><div><p class="eyebrow">ЗАКРЫТЫЙ КАБИНЕТ · NEON OBJECT STORAGE</p><h2 id="cloud-archive-title">Семейный облачный архив</h2></div><span id="cloud-connection-state" class="media-status">Проверка подключения…</span></div>
  <div id="cloud-auth">
    <form id="cloud-login-form" class="cloud-auth-form">
      <label>Логин<input id="cloud-username" name="username" autocomplete="username" required minlength="3"></label>
      <label>Пароль<input id="cloud-password" name="password" type="password" autocomplete="current-password" required></label>
      <button type="submit" class="media-open-button">Войти в семейный кабинет</button>
    </form>
    <details class="cloud-bootstrap">
      <summary>Первичная настройка владельца</summary>
      <form id="cloud-bootstrap-form" class="cloud-auth-form">
        <label>Одноразовый код настройки<input id="cloud-bootstrap-token" type="password" autocomplete="off" required></label>
        <label>Новый логин владельца<input id="cloud-owner-username" autocomplete="username" required minlength="3"></label>
        <label>Пароль владельца (не менее 12 символов)<input id="cloud-owner-password" type="password" autocomplete="new-password" required minlength="12"></label>
        <button type="submit" class="media-button">Создать учётную запись владельца</button>
      </form>
    </details>
  </div>
  <div id="cloud-private-panel" hidden>
    <div class="cloud-toolbar">
      <span id="cloud-user-label"></span>
      <button type="button" id="cloud-logout" class="media-button">Выйти</button>
    </div>
    <form id="cloud-upload-form" class="cloud-upload-form">
      <label>Фотография или видео<input id="cloud-upload-file" type="file" accept="image/jpeg,image/png,image/gif,image/webp,image/tiff,image/heic,image/heif,video/mp4,video/quicktime,video/webm,video/x-matroska" required></label>
      <label>Название (необязательно)<input id="cloud-upload-title" maxlength="300" placeholder="Например, семейная встреча"></label>
      <label>Связать с человеком / PERSON-ID<select id="cloud-person-id"><option value="">Без привязки к человеку</option></select></label>
      <button type="submit" class="media-open-button">Загрузить в закрытый архив</button>
    </form>
    <p id="cloud-archive-status" class="media-status" role="status" aria-live="polite">После входа здесь появятся файлы из приватного bucket uploads.</p>
    <div id="cloud-archive-list" class="media-list"><p class="media-list-empty">Архив ещё не загружен.</p></div>
    <div id="cloud-preview" class="cloud-preview" hidden>
      <div class="cloud-preview-head"><strong id="cloud-preview-name"></strong><button type="button" id="cloud-preview-close" class="media-button">Закрыть просмотр</button></div>
      <img id="cloud-preview-image" alt="" hidden>
      <video id="cloud-preview-video" controls playsinline hidden></video>
    </div>
  </div>
</section>
<section class="media-workspace" aria-label="Локальный просмотр фотографий и видео">
  <div class="media-toolbar">
    <label class="media-open-button" for="media-file-input">＋ Открыть фото и видео</label>
    <input id="media-file-input" class="media-file-input" type="file" accept="image/*,video/*" multiple>
    <div class="media-toolbar-actions">
      <button type="button" id="media-slideshow" class="media-button" disabled>▶ Слайдшоу</button>
      <button type="button" id="media-fullscreen" class="media-button" disabled>⛶ На весь экран</button>
    </div>
  </div>
  <p id="media-status" class="media-status" role="status" aria-live="polite">Файлы ещё не выбраны. Нажмите «Открыть фото и видео».</p>
  <div class="media-viewer" id="media-viewer">
    <div class="media-empty" id="media-empty">
      <span class="media-empty-symbol" aria-hidden="true">▧</span>
      <h2>Ваши фотографии и видео</h2>
      <p>Выберите один или несколько файлов на компьютере или телефоне. Фото откроются в просмотрщике, видео будут воспроизводиться здесь же.</p>
    </div>
    <div class="media-stage" id="media-stage" hidden>
      <img id="media-image" alt="" hidden>
      <video id="media-video" controls playsinline preload="metadata" hidden></video>
      <div class="media-caption">
        <div><strong id="media-current-name"></strong><span id="media-current-meta"></span></div>
        <a id="media-download" class="media-download" href="#" download>Скачать файл</a>
      </div>
    </div>
    <div class="media-controls">
      <button type="button" id="media-prev" class="media-button" disabled>← Назад</button>
      <span id="media-counter">0 / 0</span>
      <button type="button" id="media-next" class="media-button" disabled>Далее →</button>
    </div>
  </div>
  <div class="media-library-heading">
    <div><p class="eyebrow">ТЕКУЩИЙ СЕАНС</p><h2>Список файлов</h2></div>
    <div class="media-filters" role="group" aria-label="Фильтр файлов">
      <button type="button" class="media-filter is-active" data-filter="all" aria-pressed="true">Все</button>
      <button type="button" class="media-filter" data-filter="image" aria-pressed="false">Фото</button>
      <button type="button" class="media-filter" data-filter="video" aria-pressed="false">Видео</button>
    </div>
  </div>
  <div id="media-list" class="media-list" aria-live="polite">
    <p class="media-list-empty">Здесь появятся выбранные файлы.</p>
  </div>
</section>

<section class="media-limitations">
  <h2>Что работает сейчас, а что ещё впереди</h2>
  <ul>
    <li><strong>Работает в этой версии:</strong> локальный выбор фотографий и видео, просмотр изображений, встроенное воспроизведение видео, переключение файлов, слайдшоу фотографий, полноэкранный режим и скачивание выбранного файла.</li>
    <li><strong>Пока не реализовано:</strong> загрузка в постоянное семейное хранилище, общие альбомы между устройствами, учёт PERSON-ID/EVENT-ID/PLACE-ID, ИИ-описания, экспорт ZIP и синхронизация.</li>
    <li><strong>Ориентация:</strong> браузер применяет EXIF Orientation для поддерживаемых изображений. Для видео с метаданными поворота и HEIC/HEIF универсального браузерного решения нет. В закрытом архиве предусмотрен отдельный обработчик, который создаёт выровненную копию, не меняя оригинал; он пока не подключён к загрузке.</li>
    <li><strong>Совместимость:</strong> расширение не доказывает реальный формат и кодек. MP4/H.264 обычно поддерживается шире, чем MKV или HEVC. Ошибка декодирования будет показана отдельно, а не маскироваться под пустую фотографию.</li>
  </ul>
  <p>Не выбирайте файлы на чужом устройстве. До подключения закрытого кабинета медиатека не является семейным облачным архивом и не передаёт содержимое файлов на KOMAROVA_CORE.</p>
</section>
<script>window.KOMAROVA_API_BASE = "https://komarova-core-api.onrender.com";</script>
<script src="{{ '/assets/js/cloud-archive.js' | relative_url }}?v=1" defer></script>
<script src="{{ '/assets/js/media-library.js' | relative_url }}" defer></script>
