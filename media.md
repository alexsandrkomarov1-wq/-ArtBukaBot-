---
layout: default
title: Медиатека
permalink: /media/
description: Локальный просмотр фотографий и видео в KOMAROVA_CORE
---
<section class="media-heading">
  <p class="eyebrow">KOMAROVA_CORE · MEDIA</p>
  <h1>Семейная <em>медиатека.</em></h1>
  <p class="media-lead">Открывайте фотографии и видео прямо в браузере. Выбранные файлы остаются на вашем устройстве: эта первая версия не отправляет их на сервер и не сохраняет в семейном архиве.</p>
</section>

<section class="media-workspace" aria-label="Просмотр фотографий и видео">
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
    <li><strong>Совместимость:</strong> воспроизведение зависит от кодеков браузера и устройства. MP4/H.264 обычно поддерживается шире, чем MKV или HEVC. Само расширение файла не гарантирует декодирование.</li>
  </ul>
  <p>Не выбирайте файлы на чужом устройстве. До подключения закрытого кабинета медиатека не является семейным облачным архивом и не передаёт содержимое файлов на KOMAROVA_CORE.</p>
</section>
<script src="{{ '/assets/js/media-library.js' | relative_url }}" defer></script>
