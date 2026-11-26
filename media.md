---
layout: default
title: Архив фото и видео
permalink: /media/
description: Закрытый семейный архив фотографий, видео, аудио и документов KOMAROVA_CORE
---
<section class="media-heading">
  <p class="eyebrow">KOMAROVA_CORE · ЕДИНЫЙ СЕМЕЙНЫЙ АРХИВ</p>
  <h1>Архив <em>памяти.</em></h1>
  <p class="media-lead">Фотографии, видео, аудио и документы хранятся в закрытом Supabase Storage. PostgreSQL ведёт реестр материалов и связи с людьми, событиями и местами. Оригиналы загружаются отдельно, не перезаписываются и не публикуются на открытой витрине.</p>
  <nav class="media-entry-actions" aria-label="Навигация по архиву">
    <a class="media-button" href="#archive-upload">Загрузить материалы</a>
    <a class="media-button" href="#archive-catalog">Каталог архива</a>
    <a class="media-button" href="#archive-storage">Места хранения</a>
    <a class="media-button" href="{{ '/generations/' | relative_url }}">Поколения</a>
    <a class="media-button" href="{{ '/events/' | relative_url }}">События</a>
    <a class="media-button" href="{{ '/family-board/' | relative_url }}">География</a>
  </nav>
</section>

<section class="cloud-archive" id="archive-storage" aria-labelledby="archive-storage-title">
  <div class="media-library-heading">
    <div><p class="eyebrow">ФИЗИЧЕСКОЕ ХРАНЕНИЕ</p><h2 id="archive-storage-title">Подключение Supabase</h2></div>
    <span id="cloud-connection-state" class="media-status">Ожидается подключение проекта</span>
  </div>
  <p>Используется публичный anon/publishable key с обязательными RLS-политиками. Секретный service_role key сюда вводить запрещено. URL и публичный ключ остаются только в памяти открытой вкладки и не записываются в браузерное хранилище.</p>
  <form id="supabase-connect-form" class="cloud-auth-form">
    <label>Project URL
      <input id="supabase-project-url" type="url" inputmode="url" autocomplete="off" placeholder="https://ваш-проект.supabase.co" required>
    </label>
    <label>Публичный anon / publishable key
      <textarea id="supabase-anon-key" rows="2" autocomplete="off" spellcheck="false" placeholder="Вставьте публичный ключ из Settings → API" required></textarea>
    </label>
    <button type="submit" class="media-open-button">Проверить подключение Supabase</button>
  </form>
  <p id="supabase-project-state" class="media-status" role="status" aria-live="polite">Проект ещё не проверен. Не вводите service_role key.</p>
  <div class="storage-location-card">
    <strong>Место хранения файлов</strong>
    <span id="cloud-storage-location">Supabase Storage · приватный bucket: komarova_core_private · ожидается настройка</span>
    <small>Реестр: Supabase PostgreSQL · таблица public.archive_items. Доступ к объектам ограничивается идентификатором вошедшего пользователя.</small>
  </div>
  <details class="cloud-bootstrap">
    <summary>Первичная настройка структуры архива в Supabase</summary>
    <p>Откройте SQL Editor в проекте Supabase и выполните подготовленный SQL-файл. Он создаёт приватный bucket, таблицу реестра и политики Row Level Security. Скрипт не переносит и не удаляет существующие данные.</p>
    <p><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/backend/supabase/001_private_media_archive.sql">Открыть SQL-настройку KOMAROVA_CORE ↗</a></p>
    <p>Учётная запись требуется только для входа в закрытый семейный архив. В редакторе фотографий вход по почте не используется.</p>
  </details>
</section>

<section class="cloud-archive" id="archive-upload" aria-labelledby="archive-upload-title">
  <div class="media-library-heading">
    <div><p class="eyebrow">ЗАКРЫТЫЙ ДОСТУП</p><h2 id="archive-upload-title">Семейный кабинет</h2></div>
    <span class="media-status">Supabase Auth</span>
  </div>
  <div id="cloud-auth">
    <form id="cloud-login-form" class="cloud-auth-form">
      <label>Электронная почта
        <input id="cloud-username" name="email" type="email" autocomplete="username" required>
      </label>
      <label>Пароль
        <input id="cloud-password" name="password" type="password" autocomplete="off" required>
      </label>
      <button type="submit" class="media-open-button">Войти в семейный архив</button>
    </form>
  </div>
  <div id="cloud-private-panel" hidden>
    <div class="cloud-toolbar">
      <span id="cloud-user-label"></span>
      <button type="button" id="cloud-logout" class="media-button">Выйти</button>
    </div>
    <form id="cloud-upload-form" class="cloud-upload-form">
      <label>Фото, видео, аудио или документ
        <input id="cloud-upload-file" type="file" accept="image/*,video/*,audio/*,.pdf,.txt,.rtf,.doc,.docx,.odt,.xls,.xlsx,.ods,.ppt,.pptx,.odp" required>
      </label>
      <label>Название / подпись
        <input id="cloud-upload-title" maxlength="300" placeholder="Например, семейная встреча">
      </label>
      <label>Описание
        <textarea id="cloud-upload-description" rows="2" maxlength="2000" placeholder="Кто, что и при каких обстоятельствах изображено"></textarea>
      </label>
      <label>Дата съёмки / создания
        <input id="cloud-captured-at" type="date">
      </label>
      <button id="cloud-upload-submit" type="submit" class="media-open-button">Сохранить оригинал в архив</button>
    </form>
    <p id="cloud-archive-status" class="media-status" role="status" aria-live="polite">После входа здесь появятся ваши архивные материалы.</p>
  </div>
</section>

<section class="cloud-archive" id="archive-catalog" aria-labelledby="archive-catalog-title">
  <div class="media-library-heading">
    <div><p class="eyebrow">ЕДИНЫЙ РЕЕСТР · MATERIAL-ID</p><h2 id="archive-catalog-title">Каталог архива</h2></div>
    <span class="media-status">Закрытый список</span>
  </div>
  <div class="media-filters cloud-archive-filters" role="group" aria-label="Фильтр архива">
    <button type="button" class="media-filter is-active" data-cloud-filter="all" aria-pressed="true">Все материалы</button>
    <button type="button" class="media-filter" data-cloud-filter="photo" aria-pressed="false">Фото</button>
    <button type="button" class="media-filter" data-cloud-filter="video" aria-pressed="false">Видео</button>
    <button type="button" class="media-filter" data-cloud-filter="audio" aria-pressed="false">Аудио</button>
    <button type="button" class="media-filter" data-cloud-filter="document" aria-pressed="false">Документы</button>
  </div>
  <div id="cloud-archive-list" class="media-list"><p class="media-list-empty">Войдите в архив, чтобы загрузить каталог.</p></div>
  <div id="cloud-preview" class="cloud-preview" hidden>
    <div class="cloud-preview-head"><strong id="cloud-preview-name"></strong><button type="button" id="cloud-preview-close" class="media-button">Закрыть просмотр</button></div>
    <img id="cloud-preview-image" alt="" hidden>
    <video id="cloud-preview-video" controls playsinline hidden></video>
  </div>
</section>

<section class="media-workspace" id="local-media-workspace" aria-label="Локальный просмотр файлов">
  <div class="media-library-heading">
    <div><p class="eyebrow">БЕЗ ЗАГРУЗКИ В ОБЛАКО</p><h2>Быстрый просмотр с устройства</h2></div>
    <span class="media-status">Только текущий сеанс</span>
  </div>
  <div class="media-toolbar">
    <label class="media-open-button" for="media-file-input">＋ Открыть файлы на устройстве</label>
    <input id="media-file-input" class="media-file-input" type="file" accept="image/*,video/*,audio/*,.pdf,.txt,.rtf,.doc,.docx,.odt,.xls,.xlsx,.ods,.ppt,.pptx,.odp" multiple>
    <div class="media-toolbar-actions">
      <button type="button" id="media-slideshow" class="media-button" disabled>▶ Слайдшоу</button>
      <button type="button" id="media-fullscreen" class="media-button" disabled>⛶ На весь экран</button>
    </div>
  </div>
  <p id="media-status" class="media-status" role="status" aria-live="polite">Выберите файлы для локального просмотра. Этот режим не загружает их в архив.</p>
  <div class="media-viewer" id="media-viewer">
    <div class="media-empty" id="media-empty">
      <span class="media-empty-symbol" aria-hidden="true">▧</span>
      <h2>Предпросмотр материалов</h2>
      <p>Фото, видео и аудио открываются в браузере. Документы можно открыть в отдельной вкладке, если формат поддерживается.</p>
    </div>
    <div class="media-stage" id="media-stage" hidden>
      <img id="media-image" alt="" hidden>
      <video id="media-video" controls playsinline preload="metadata" hidden></video>
      <audio id="media-audio" controls preload="metadata" hidden></audio>
      <div id="media-document" class="media-document-preview" hidden><p>Предпросмотр документа</p><a id="media-document-open" target="_blank" rel="noopener noreferrer">Открыть документ в новой вкладке</a></div>
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
    <div><p class="eyebrow">ТЕКУЩИЙ СЕАНС</p><h2>Выбранные файлы</h2></div>
    <div class="media-filters" role="group" aria-label="Фильтр локальных файлов">
      <button type="button" class="media-filter is-active" data-filter="all" aria-pressed="true">Все</button>
      <button type="button" class="media-filter" data-filter="image" aria-pressed="false">Фото</button>
      <button type="button" class="media-filter" data-filter="video" aria-pressed="false">Видео</button>
      <button type="button" class="media-filter" data-filter="audio" aria-pressed="false">Аудио</button>
      <button type="button" class="media-filter" data-filter="document" aria-pressed="false">Документы</button>
    </div>
  </div>
  <div id="media-list" class="media-list" aria-live="polite"><p class="media-list-empty">Здесь появятся выбранные файлы.</p></div>
</section>

<section class="media-limitations">
  <h2>Правила хранения и защиты</h2>
  <ul>
    <li>Файлы находятся в приватном bucket Supabase Storage, а не в публичной папке сайта.</li>
    <li>Доступ ограничивается Supabase Auth и Row Level Security. На первом этапе пользователь видит только собственные записи и объекты.</li>
    <li>Оригинал загружается без преобразования. AI-результат в будущем будет отдельным объектом с новым MATERIAL-ID и ссылкой на оригинал.</li>
    <li>SHA-256 рассчитывается в браузере перед отправкой. Это контрольная сумма, а не антивирусная проверка.</li>
    <li>Автоматическое ClamAV-сканирование, AI-worker, совместные семейные права и полноценный резервный экспорт пока не подключены.</li>
    <li>Для бесплатного Supabase фактические ограничения размера файла и объёма Storage зависят от настроек и лимитов проекта. Большие видео следует проверять отдельно до массовой загрузки.</li>
  </ul>
</section>
<script src="{{ '/assets/js/supabase-archive.js' | relative_url }}?v=20261126-supabase-archive-1" defer></script>
<script src="{{ '/assets/js/media-library.js' | relative_url }}?v=20261126-archive-navigation-1" defer></script>
