---
layout: default
title: Главная
description: Цифровой семейный архив KOMAROVA_CORE. История, память и материалы для открытого доступа.
---
<section class="hero hero-archive ai-world-home" aria-labelledby="home-title">
  <div class="hero-copy">
    <p class="eyebrow"><span class="eyebrow-line"></span> ИНТЕРАКТИВНЫЙ МИР ИИ · KOMAROVA_CORE</p>
    <h1 id="home-title">Войдите в <em>цифровой мир.</em></h1>
    <p class="hero-lead">Единое пространство людей, поколений, событий, географии и семейных материалов. Выбирайте портал в 3D-мире или пользуйтесь обычной навигацией.</p>
    <div class="hero-actions">
      <a class="primary-link" href="#world-portals">Открыть проекты <span aria-hidden="true">↓</span></a>
      <a class="text-link" href="{{ '/status/' | relative_url }}">Проверить состояние системы ↗</a>
    </div>
  </div>
  <div class="hero-art" aria-label="Интерактивный трёхмерный мир KOMAROVA_CORE">
    <div class="world-interface">
      <div class="world-hud">
        <span class="world-hud-kicker">KOMAROVA_CORE / AI WORLD</span>
        <strong>ЦЕНТРАЛЬНОЕ ЯДРО</strong>
        <span class="world-render-status" data-world-render-status role="status" aria-live="polite">Проверка графического режима…</span>
      </div>
      <nav class="world-portals" id="world-portals" aria-label="Активные порталы проектов">
        <a class="world-portal" href="{{ '/generations/' | relative_url }}"><span class="world-portal-index">01 / PEOPLE</span><strong>Поколения</strong><small>Люди · PERSON-ID</small></a>
        <a class="world-portal" href="{{ '/events/' | relative_url }}"><span class="world-portal-index">02 / TIME</span><strong>События</strong><small>Хронология · EVENT-ID</small></a>
        <a class="world-portal" href="{{ '/family-board/#fb-map-panel' | relative_url }}"><span class="world-portal-index">03 / PLACES</span><strong>География</strong><small>Карта · посещения</small></a>
        <a class="world-portal" href="{{ '/media/' | relative_url }}"><span class="world-portal-index">04 / ARCHIVE</span><strong>Документы и медиа</strong><small>Фотографии · видео · файлы</small></a>
        <a class="world-portal" href="#ai-media-enhancer"><span class="world-portal-index">05 / AI MEDIA</span><strong>Восстановление</strong><small>Оригинал · производная копия</small></a>
        <button class="world-portal world-portal-button" type="button" data-world-open-guide><span class="world-portal-index">06 / AI GUIDE</span><strong>ИИ-помощник</strong><small>Подсказки и навигация</small></button>
        <a class="world-portal" href="{{ '/account/' | relative_url }}"><span class="world-portal-index">07 / PRIVATE</span><strong>Личный кабинет</strong><small>Защищённый доступ</small></a>
        <a class="world-portal" href="{{ '/status/' | relative_url }}"><span class="world-portal-index">08 / SYSTEM</span><strong>Состояние проекта</strong><small>Проверки · готовность</small></a>
      </nav>
      <div class="world-footer"><span>МЫШЬ · КЛАВИАТУРА · TOUCH</span><span>ПОРТАЛЫ ОТКРЫВАЮТ РЕАЛЬНЫЕ РАЗДЕЛЫ</span></div>
    </div>
  </div>
  <div class="hero-foot"><span>ЕДИНОЕ СЕМЕЙНОЕ ЯДРО</span><span class="hero-foot-rule"></span><span>ОДИН МИР · СВЯЗАННЫЕ ПРОЕКТЫ</span></div>
</section>
<section class="family-portraits" aria-labelledby="family-portraits-title">
  <div class="family-portraits-heading">
    <div>
      <p class="eyebrow">ЛИЦА И ПОКОЛЕНИЯ</p>
      <h2 id="family-portraits-title">Семья — <em>в центре истории.</em></h2>
      <p>Личные портреты участников семьи. Каждый выбирает фотографию сам, а на главной появляется только версия, разрешённая им для публикации.</p>
    </div>
    <span class="gallery-status">ПУБЛИЧНАЯ ГАЛЕРЕЯ · ПОДГОТОВЛЕНА</span>
  </div>
  <div class="family-portrait-grid" aria-label="Места для семейных портретов">
    <article class="family-portrait-card" data-portrait-card>
      <div class="portrait-frame"><span class="portrait-silhouette"></span><img class="portrait-preview" alt="Предварительный просмотр портрета 1" hidden><span class="portrait-index">01</span></div>
      <div class="portrait-meta"><span class="portrait-label">ПОРТРЕТ УЧАСТНИКА 01</span><strong>Место для фотографии</strong><span class="portrait-state" data-portrait-state aria-live="polite">ФОТО ПОКА НЕ ДОБАВЛЕНО</span><label class="portrait-select-button">Выбрать фотографию<input class="portrait-upload-input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" aria-label="Выбрать фотографию для портрета 1"></label><button class="portrait-clear-button" type="button" data-portrait-clear hidden>Убрать предварительный просмотр</button></div>
    </article>
    <article class="family-portrait-card" data-portrait-card>
      <div class="portrait-frame portrait-frame-alt"><span class="portrait-silhouette"></span><img class="portrait-preview" alt="Предварительный просмотр портрета 2" hidden><span class="portrait-index">02</span></div>
      <div class="portrait-meta"><span class="portrait-label">ПОРТРЕТ УЧАСТНИКА 02</span><strong>Место для фотографии</strong><span class="portrait-state" data-portrait-state aria-live="polite">ФОТО ПОКА НЕ ДОБАВЛЕНО</span><label class="portrait-select-button">Выбрать фотографию<input class="portrait-upload-input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" aria-label="Выбрать фотографию для портрета 2"></label><button class="portrait-clear-button" type="button" data-portrait-clear hidden>Убрать предварительный просмотр</button></div>
    </article>
    <article class="family-portrait-card" data-portrait-card>
      <div class="portrait-frame portrait-frame-warm"><span class="portrait-silhouette"></span><img class="portrait-preview" alt="Предварительный просмотр портрета 3" hidden><span class="portrait-index">03</span></div>
      <div class="portrait-meta"><span class="portrait-label">ПОРТРЕТ УЧАСТНИКА 03</span><strong>Место для фотографии</strong><span class="portrait-state" data-portrait-state aria-live="polite">ФОТО ПОКА НЕ ДОБАВЛЕНО</span><label class="portrait-select-button">Выбрать фотографию<input class="portrait-upload-input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" aria-label="Выбрать фотографию для портрета 3"></label><button class="portrait-clear-button" type="button" data-portrait-clear hidden>Убрать предварительный просмотр</button></div>
    </article>
    <article class="family-portrait-card" data-portrait-card>
      <div class="portrait-frame portrait-frame-dark"><span class="portrait-silhouette"></span><img class="portrait-preview" alt="Предварительный просмотр портрета 4" hidden><span class="portrait-index">04</span></div>
      <div class="portrait-meta"><span class="portrait-label">ПОРТРЕТ УЧАСТНИКА 04</span><strong>Место для фотографии</strong><span class="portrait-state" data-portrait-state aria-live="polite">ФОТО ПОКА НЕ ДОБАВЛЕНО</span><label class="portrait-select-button">Выбрать фотографию<input class="portrait-upload-input" type="file" accept="image/jpeg,image/png,image/webp,image/gif" aria-label="Выбрать фотографию для портрета 4"></label><button class="portrait-clear-button" type="button" data-portrait-clear hidden>Убрать предварительный просмотр</button></div>
    </article>
  </div>
  <p class="family-portraits-note" id="family-portraits-status" role="status" aria-live="polite">Выбор фотографии показывает её только в этом браузере. Файл не отправляется в интернет и не сохраняется в архиве. Для постоянного хранения требуется подключённый закрытый сервер.</p>
</section>

<section class="ai-media-lab" id="ai-media-enhancer" aria-labelledby="ai-media-title">
  <div class="ai-media-heading">
    <div>
      <p class="eyebrow">ВОССТАНОВЛЕНИЕ · СОХРАНЕНИЕ · ПОКОЛЕНИЯ</p>
      <h2 id="ai-media-title">AI MEDIA <em>ENHANCER</em></h2>
      <p class="ai-media-lead">Лаборатория восстановления KOMAROVA_CORE. Оригинал остаётся неизменным. Внутренний AI-движок KOMAROVA_CORE проверяет файл и создаёт отдельную улучшенную копию с восстановлением деталей и увеличением разрешения до 4×.</p>
    </div>
    <div class="ai-media-seal" aria-hidden="true"><span>KOMAROVA</span><strong>CORE</strong><small>MEDIA LAB</small></div>
  </div>

  <div class="ai-media-workspace" data-ai-media-lab>
    <div class="ai-media-workspace-heading">
      <div><span class="ai-media-kicker">РАБОЧАЯ ОБЛАСТЬ · AI SUPER-RESOLUTION</span><h3>Работа с вашим материалом</h3></div>
      <span class="ai-media-mode" data-ai-mode>ОЖИДАЕТ ФАЙЛ</span>
    </div>
    <div class="ai-media-engine-status" role="status" aria-live="polite"><strong>АВТОМАТИЧЕСКОЕ AI-УЛУЧШЕНИЕ · СЕРВЕРНОЕ СОХРАНЕНИЕ</strong><span>После подключения защищённой сессии оригинал загружается в приватный архив, проходит ClamAV, затем сервер создаёт отдельную производную копию. Ползунок меняет параметры именно сохраняемого файла.</span><small>Серверная среда пока не подключена к сайту. Без неё сохранённая AI-копия не создаётся.</small></div>

    <input class="ai-media-file-input" data-ai-file-input type="file" accept="image/*,video/*">
    <div class="ai-media-controls" aria-label="Этапы работы с материалом">
      <button class="ai-media-button ai-media-button-primary" type="button" data-ai-upload>
        <span class="ai-media-step">01 <span aria-hidden="true">/</span> PHOTO UPLOAD</span>
        <strong class="ai-media-action-title">Загрузить фотографию</strong>
        <small class="ai-media-action-note">Выберите фото для просмотра и доступной обработки · до 100 МБ</small>
      </button>
      <button class="ai-media-button" type="button" data-ai-upload-video>
        <span class="ai-media-step">01 <span aria-hidden="true">/</span> VIDEO UPLOAD</span>
        <strong class="ai-media-action-title">Загрузить видео</strong>
        <small class="ai-media-action-note">Видео появится в плеере слева. AI-конвейер видео пока не подключён · до 100 МБ</small>
      </button>
      <div class="ai-media-button ai-media-stage" data-ai-view role="status" aria-live="polite">
        <span class="ai-media-step">02 <span aria-hidden="true">/</span> VIEW</span>
        <strong class="ai-media-action-title">Автоматическое улучшение</strong>
        <small class="ai-media-action-note">Автоматический запуск после выбора фотографии или видео</small>
      </div>
      <button class="ai-media-button" type="button" data-ai-export disabled>
        <span class="ai-media-step">03 <span aria-hidden="true">/</span> EXPORT</span>
        <strong class="ai-media-action-title">Скачать улучшенную копию</strong>
        <small class="ai-media-action-note">Сохранение результата на компьютер после обработки</small>
      </button>
    </div>
    <div class="ai-media-file-info" data-ai-file-info role="status" aria-live="polite">Файл ещё не выбран. Выберите фотографию или видео для локального просмотра.</div>
    <p class="ai-media-storage-note">Оригинал и обработанная копия должны храниться в приватном архиве с отдельными MATERIAL-ID. Локальная память браузера используется только для временного предпросмотра и не заменяет архив.</p>
    <div class="ai-media-adjustments" data-ai-adjustments aria-label="Настройки фотографии">
      <label class="ai-media-range-control" for="ai-quality-range"><span><strong>Сила улучшения</strong><output data-ai-quality-value>65%</output></span>
        <input id="ai-quality-range" data-ai-quality type="range" min="0" max="100" step="5" value="65">
        <small>Меняет силу обработки в экспортируемом файле. После изменения ползунка сервер повторно создаёт отдельную копию; оригинал не перезаписывается.</small>
      </label>
      <button type="button" class="ai-media-button ai-video-editor-open" data-ai-open-video-editor disabled>Открыть отдельный редактор видео</button>
      <dialog class="ai-video-editor-dialog" data-ai-video-editor aria-labelledby="ai-video-editor-title"><div class="ai-media-video-settings" data-ai-video-settings aria-label="Монтаж видео" hidden>
        <strong id="ai-video-editor-title">МОНТАЖ ВИДЕО · ПРИМЕНЯЕТСЯ К ЭКСПОРТУ</strong>
        <div class="ai-media-video-grid">
          <label>Обрезать с, сек
            <input type="number" min="0" step="0.1" value="0" data-ai-trim-start>
          </label>
          <label>Обрезать до, сек
            <input type="number" min="0" step="0.1" placeholder="До конца видео" data-ai-trim-end>
          </label>
          <label>Кадрирование X, px
            <input type="number" min="0" step="2" data-ai-crop-x>
          </label>
          <label>Кадрирование Y, px
            <input type="number" min="0" step="2" data-ai-crop-y>
          </label>
          <label>Ширина кадра, px
            <input type="number" min="2" step="2" data-ai-crop-width>
          </label>
          <label>Высота кадра, px
            <input type="number" min="2" step="2" data-ai-crop-height>
          </label>
        </div>
        <label class="ai-media-audio-option"><input type="checkbox" data-ai-audio-enhance checked> Уменьшить шум и выровнять громкость звука при экспорте</label>
        <small>Обрезка и кадрирование применяются к новому MP4. При установленной модели RNNoise применяется нейросетевое шумоподавление; без неё используется фильтр FFmpeg afftdn. Это не восстановление утраченной речи.</small>
        <button type="button" class="ai-media-button" data-ai-reprocess disabled>Применить монтаж и создать новую копию</button>
        <button type="button" class="ai-media-button" data-ai-close-video-editor>Закрыть редактор</button>
      </div></dialog>
      <label class="ai-media-range-control" for="ai-zoom-range"><span><strong>Масштаб просмотра</strong><output data-ai-zoom-value>100%</output></span>
        <input id="ai-zoom-range" data-ai-zoom type="range" min="100" max="300" step="25" value="100">
        <small>Увеличивает обе фотографии для детального просмотра. Масштаб не меняет исходный файл и не влияет на экспорт.</small>
      </label>
    </div>
    <style>
      .ai-media-adjustments{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:16px 0;padding:18px;border:1px solid rgba(125,170,190,.28);border-radius:14px;background:rgba(12,28,43,.72);color:#eaf3f7}
      .ai-media-range-control{display:grid;gap:9px;min-width:0}
      .ai-media-range-control>span{display:flex;justify-content:space-between;gap:10px;align-items:center}
      .ai-media-range-control output{color:#86c8d8;font-variant-numeric:tabular-nums}
      .ai-media-range-control input{width:100%;accent-color:#76c7d5;cursor:pointer}
      .ai-media-range-control small{color:#a9becb;font-size:.78rem;line-height:1.5}
      .ai-media-live-frame{overflow:auto}
      .ai-media-live-frame img[data-ai-original-preview],.ai-media-live-frame img[data-ai-result-preview]{display:block;max-width:none;height:auto;margin-inline:auto}
      .ai-media-login{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:14px 0;padding:16px;border:1px solid rgba(125,170,190,.28);border-radius:12px;background:rgba(12,28,43,.72);color:#eaf3f7}
      .ai-media-login[hidden],.ai-media-video-settings[hidden]{display:none}
      .ai-media-login label,.ai-media-video-grid label{display:grid;gap:6px;font-size:.82rem}
      .ai-media-login input,.ai-media-video-grid input{width:100%;min-width:0;padding:10px;border:1px solid rgba(125,170,190,.35);border-radius:8px;background:#0b1b2a;color:#eaf3f7}
      .ai-media-login button{min-height:40px}
      .ai-media-login p{grid-column:1/-1;margin:0;color:#a9becb;font-size:.8rem}
      .ai-media-video-settings{display:grid;gap:12px;margin:16px 0;padding:18px;border:1px solid rgba(125,170,190,.28);border-radius:14px;background:rgba(12,28,43,.72);color:#eaf3f7}
      .ai-media-video-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
      .ai-media-audio-option{display:flex;align-items:center;gap:10px;color:#c8dbe4}
      .ai-media-audio-option input{accent-color:#76c7d5}
      .ai-media-video-settings small{color:#a9becb;font-size:.78rem;line-height:1.5}
      @media(max-width:650px){.ai-media-adjustments,.ai-media-login{grid-template-columns:1fr}.ai-media-video-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    </style>
    <div class="ai-media-live-preview" data-ai-preview hidden>
      <figure><figcaption>ИСХОДНЫЙ ФАЙЛ · ОРИГИНАЛ</figcaption><div class="ai-media-live-frame">
        <img data-ai-original-preview alt="Предпросмотр выбранного оригинала" hidden>
        <video data-ai-video-preview controls playsinline hidden></video>
        <span data-ai-original-empty>Оригинал появится после выбора файла</span>
      </div></figure>
      <figure><figcaption>РЕЗУЛЬТАТ · ОТДЕЛЬНАЯ КОПИЯ</figcaption><div class="ai-media-live-frame">
        <img data-ai-result-preview alt="Предпросмотр отдельной копии" hidden>
        <video data-ai-result-video controls playsinline hidden></video>
        <span data-ai-result-empty>Копия появится после автоматической обработки. Оригинал останется без изменений.</span>
      </div>
      <small class="ai-media-copy-note">Результат создаётся как отдельный файл. Исходник не изменяется.</small>
      </figure>
    </div>
    <p class="ai-media-live-status" data-ai-status role="status" aria-live="polite">Выберите фотографию. После автоматической проверки внутренний AI-движок создаст улучшенную копию.</p>
    <div class="ai-media-atmosphere" data-media-atmosphere>
      <div class="ai-media-nature-scene" data-nature-scene="forest" aria-hidden="true">
        <span class="nature-sun"></span><span class="nature-mountains"></span><span class="nature-hills"></span>
        <span class="nature-water"></span><span class="nature-trees"></span><span class="nature-fireflies"></span>
      </div>
      <div class="ai-media-atmosphere-content">
        <div><span class="ai-media-kicker">ЖИВАЯ АТМОСФЕРА · ПРИРОДА И ЗВУК</span><h3>Пусть архив оживает</h3><p data-atmosphere-status>Выберите настроение или произнесите команду. Музыка создаётся на устройстве, без платных музыкальных сервисов.</p></div>
        <div class="ai-media-atmosphere-controls">
          <div class="nature-scenes" aria-label="Смена природной сцены">
            <button type="button" data-scene-choice="forest" aria-pressed="true">Лес</button>
            <button type="button" data-scene-choice="lake" aria-pressed="false">Озеро</button>
            <button type="button" data-scene-choice="mountain" aria-pressed="false">Горы</button>
            <button type="button" data-scene-choice="sunset" aria-pressed="false">Закат</button>
          </div>
          <div class="music-moods" aria-label="Музыкальное настроение">
            <button type="button" data-mood-choice="romance" aria-pressed="true">Романтика</button>
            <button type="button" data-mood-choice="calm" aria-pressed="false">Спокойствие</button>
            <button type="button" data-mood-choice="focus" aria-pressed="false">Фокус</button>
            <button type="button" data-mood-choice="nature" aria-pressed="false">Природная мелодия</button>
          </div>
          <div class="assistant-controls">
            <button type="button" data-scene-auto aria-pressed="true">Автосмена пейзажа: включена</button>
            <button type="button" data-desktop-mode>Полноэкранная заставка</button>
            <button type="button" class="ai-media-sound-toggle" data-sound-toggle>▶ Включить музыку</button>
            <button type="button" data-voice-assistant>🎙 Голосовой помощник</button>
          </div>
          <span class="ai-media-assistant-hint">Команды: «включи романтику», «покажи лес», «включи спокойствие», «выключи музыку»</span>
        </div>
      </div>
    </div>

      <div class="media-playback-grid" aria-label="Музыкальная коллекция и интернет-радио">
        <section class="media-player-panel" aria-labelledby="music-archive-title">
          <span class="ai-media-kicker">ЛОКАЛЬНАЯ МУЗЫКАЛЬНАЯ КОЛЛЕКЦИЯ · ДО ПОДКЛЮЧЕНИЯ АРХИВА</span>
          <h4 id="music-archive-title">MP3-плеер и список воспроизведения</h4>
          <label class="media-file-picker">Добавить аудиофайлы с устройства
            <input type="file" data-music-files accept="audio/*,.mp3,.m4a,.aac,.wav,.ogg,.flac" multiple>
          </label>
          <div class="media-player-controls">
            <button type="button" data-music-previous aria-label="Предыдущий трек">⏮</button>
            <button type="button" data-music-play>▶ Воспроизвести</button>
            <button type="button" data-music-next aria-label="Следующий трек">⏭</button>
          </div>
          <div class="media-player-timeline"><span data-music-current-time>0:00</span><input type="range" data-music-seek min="0" max="0" value="0" aria-label="Позиция воспроизведения"><span data-music-duration>0:00</span></div>
          <label class="media-volume-control">Громкость <input type="range" data-music-volume min="0" max="100" value="75"></label>
          <audio data-music-audio preload="metadata"></audio>
          <div class="media-music-playlist" data-music-playlist aria-live="polite"><p class="media-player-empty">Добавьте MP3-файлы с устройства.</p></div>
          <p class="media-player-status" data-music-status role="status" aria-live="polite">Плеер готов. Локальные файлы не загружаются на сервер и не попадают в семейный архив.</p>
        </section>
        <section class="media-player-panel media-radio-panel" aria-labelledby="radio-title">
          <span class="ai-media-kicker">ИНТЕРНЕТ · РАДИО</span>
          <h4 id="radio-title">Радиоэфир</h4>
          <label>Найти станцию
            <input type="search" data-radio-search placeholder="Например: jazz, classical, nature">
          </label>
          <button type="button" data-radio-find>Найти интернет-радио</button>
          <div class="media-radio-list" data-radio-list aria-live="polite"></div>
          <label>Или вставить прямую ссылку на аудиопоток
            <input type="url" data-radio-url placeholder="https://…">
          </label>
          <button type="button" data-radio-connect>Подключить поток</button>
          <audio data-radio-audio controls preload="none"></audio>
          <p class="media-player-status" data-radio-status role="status" aria-live="polite">Нажмите «Найти интернет-радио», чтобы открыть каталог Radio Browser. Доступность потоков зависит от станции и сети.</p>
        </section>
      </div>
    <div class="ai-media-internal-engine" role="status" aria-live="polite"><strong>ВНУТРЕННИЙ AI-КОНВЕЙЕР KOMAROVA_CORE</strong><span>Файлы будут автоматически обрабатываться внутренним AI-движком KOMAROVA_CORE. Внешние сайты, ручная повторная загрузка, адрес API, логин и пароль не нужны. Сейчас движок ещё не установлен на сервере.</span></div>
    <button class="ai-media-reset" type="button" data-ai-reset disabled>Очистить рабочую область</button>
  </div>

  <div class="ai-media-tools">
    <article><span>PHOTO ENHANCEMENT · NEURAL AI</span><h3>Фотографии</h3><p>Pillow подготавливает оригинал; Real-ESRGAN NCNN Vulkan восстанавливает детали и увеличивает разрешение до 4×; OpenCV и scikit-image уточняют контраст, шум и резкость. Pillow завершает коррекцию яркости и цвета. Требуются частный backend и веса модели; без них сайт не показывает фальшивый результат.</p></article>
    <article><span>VIDEO ENHANCEMENT · NEURAL AI</span><h3>Видео</h3><p>Real-ESRGAN обрабатывает кадры с увеличением до 2×. FFmpeg применяет обрезку, кадрирование, коррекцию изображения, шумоподавление и нормализацию звука, затем собирает отдельный MP4. Нейросетевое улучшение звука пока не подключено.</p></article>
    <article><span>ARCHIVE PROTECTION · ОБЯЗАТЕЛЬНО</span><h3>Защита архива</h3><p>Каждый оригинал и результат получают отдельный MATERIAL-ID. Производная запись хранит ссылку на исходный MATERIAL-ID, контрольные суммы и сведения о применённом конвейере.</p></article>
  </div>

  <div class="ai-media-principle"><strong>Оригинал сохраняем. Результат проверяем. Производные версии учитываем отдельно.</strong><span>ОРИГИНАЛ ЗАЩИЩЁН · КОПИЯ УЧИТЫВАЕТСЯ ОТДЕЛЬНО</span></div>
  <p class="ai-media-footnote">Оригинал никогда не изменяется. Результат проходит проверку, получает отдельный MATERIAL-ID и связь с оригиналом. Приватный backend и AI-worker пока не подключены к опубликованному сайту. До подключения серверная обработка и постоянное сохранение недоступны.</p>
</section>

<section class="section-intro" id="archive-directions">
  <div><p class="eyebrow">СОДЕРЖАНИЕ АРХИВА</p><h2>Не просто страницы.<br><em>Связанные истории.</em></h2></div>
  <p>Каждый материал в будущем будет связан с людьми, датами, событиями, местами и источниками. Так отдельные документы складываются в общую картину.</p>
</section>
<section class="archive-grid" aria-label="Направления семейного архива">
  <a class="archive-card archive-card-link archive-card-feature" href="{{ '/generations/' | relative_url }}"><span class="card-kicker">01 / ПОКОЛЕНИЯ</span><div class="card-symbol symbol-tree" aria-hidden="true"><span></span><span></span><span></span><i></i></div><h3>История семьи</h3><p>Поколения, биографии, родственные связи и семейная хроника.</p><span class="card-state">ОТКРЫТЬ РЕЕСТР ↗</span></a>
  <a class="archive-card archive-card-link" href="{{ '/events/' | relative_url }}"><span class="card-kicker">02 / ВРЕМЯ</span><div class="card-symbol symbol-time" aria-hidden="true"><span></span><span></span><i></i></div><h3>События и хронология</h3><p>Значимые даты, встречи, семейные события и исторический контекст.</p><span class="card-state">ОТКРЫТЬ ХРОНОЛОГИЮ ↗</span></a>
  <a class="archive-card archive-card-link" href="{{ '/family-board/#fb-map-panel' | relative_url }}"><span class="card-kicker">03 / ГЕОГРАФИЯ</span><div class="card-symbol symbol-place" aria-hidden="true"><span></span><i></i></div><h3>Места и путешествия</h3><p>Города, маршруты, дома и места, связанные с семейной историей.</p><span class="card-state">ОТКРЫТЬ КАРТУ ↗</span></a>
  <a class="archive-card archive-card-link" href="{{ '/media/' | relative_url }}"><span class="card-kicker">04 / МЕДИАТЕКА</span><div class="card-symbol symbol-media" aria-hidden="true"><span></span><span></span><i></i></div><h3>Фотографии и документы</h3><p>Оригиналы, описания, источники и проверенные цифровые копии.</p><span class="card-state">ОТКРЫТЬ МЕДИАТЕКУ ↗</span></a>
</section>
<section class="places-gallery" aria-labelledby="places-gallery-title" data-places-gallery>
  <div class="places-gallery-heading">
    <div><p class="eyebrow">МИР ВОКРУГ НАС · МЕСТА И КУЛЬТУРА</p><h2 id="places-gallery-title">Места, которые <em>стоит увидеть.</em></h2><p>Музеи, архитектура, природные памятники и города. Фотографии загружаются из открытой медиатеки Wikimedia Commons с указанием источника и лицензии.</p></div>
    <button type="button" class="gallery-refresh" data-gallery-refresh>Обновить фотографии <span aria-hidden="true">↻</span></button>
  </div>
  <div class="places-gallery-grid">
    <article class="place-photo-card"><a data-place-link="0" href="https://commons.wikimedia.org/" target="_blank" rel="noopener noreferrer"><img data-place-image="0" alt="Эрмитаж и архитектура Санкт-Петербурга" loading="lazy"><span class="place-photo-overlay"></span></a><div class="place-photo-caption"><span>01 / МУЗЕИ И АРХИТЕКТУРА</span><h3 data-place-title="0">Эрмитаж · Санкт-Петербург</h3><small data-place-credit="0">Загрузка фотографии…</small></div></article>
    <article class="place-photo-card"><a data-place-link="1" href="https://commons.wikimedia.org/" target="_blank" rel="noopener noreferrer"><img data-place-image="1" alt="Дворцы и парки Петергофа" loading="lazy"><span class="place-photo-overlay"></span></a><div class="place-photo-caption"><span>02 / ИСТОРИЧЕСКИЕ МЕСТА</span><h3 data-place-title="1">Петергоф · дворцы и парки</h3><small data-place-credit="1">Загрузка фотографии…</small></div></article>
    <article class="place-photo-card"><a data-place-link="2" href="https://commons.wikimedia.org/" target="_blank" rel="noopener noreferrer"><img data-place-image="2" alt="Природные ландшафты Байкала" loading="lazy"><span class="place-photo-overlay"></span></a><div class="place-photo-caption"><span>03 / ПРИРОДА И ПУТЕШЕСТВИЯ</span><h3 data-place-title="2">Байкал · природное наследие</h3><small data-place-credit="2">Загрузка фотографии…</small></div></article>
  </div>
  <p class="places-gallery-note">Изображения сменяются автоматически. Каждая фотография ведёт на страницу оригинала с условиями использования. Доступность внешнего источника зависит от соединения с интернетом.</p>
</section>
<section class="sharing-panel">
  <div class="sharing-copy">
    <p class="eyebrow">ОТКРЫТЫЕ КОЛЛЕКЦИИ</p><h2>Семейная память<br><em>может быть доступна миру.</em></h2>
    <p>Материалы, которые разрешено публиковать, можно будет распространять через KOMAROVA_CORE и внешние цифровые библиотеки, включая Internet Archive. Для каждой публикации будут указаны авторство, источник и условия использования.</p>
    <a class="outline-link" href="https://archive.org/" target="_blank" rel="noopener noreferrer">Перейти на Internet Archive <span aria-hidden="true">↗</span></a>
    <p class="sharing-note">Внешняя площадка для будущих публикаций. Семейная коллекция KOMAROVA_CORE там пока не создана.</p>
  </div>
  <div class="sharing-seal" aria-hidden="true"><span>OPEN</span><strong>MEMORY</strong><span>SHARED WITH CARE</span></div>
</section>
<section class="mars-feature" aria-labelledby="mars-title">
  <div class="mars-art" role="img" aria-label="Стилизованное изображение планеты Марс"><span class="mars-orbit"></span><span class="mars-planet"></span><span class="mars-star mars-star-one"></span><span class="mars-star mars-star-two"></span></div>
  <div class="mars-copy">
    <p class="eyebrow">КОСМОС · ИССЛЕДОВАНИЯ · БУДУЩЕЕ</p>
    <h2 id="mars-title">Следующая остановка — <em>Марс.</em></h2>
    <p>Исследование Красной планеты, марсоходы, орбитальные миссии и новые открытия NASA. Отдельное направление для любознательных и тех, кто смотрит дальше горизонта.</p>
    <a class="outline-link" href="https://science.nasa.gov/mars/" target="_blank" rel="noopener noreferrer">Исследовать Марс · NASA <span aria-hidden="true">↗</span></a>
    <p class="mars-note">Официальный научный портал NASA. Открывается на сайте NASA, вне KOMAROVA_CORE.</p>
  </div>
</section>
<section class="privacy-strip"><span class="privacy-icon" aria-hidden="true">✳</span><div><h2>Открытость без потери приватности</h2><p>Публичная витрина содержит только одобренные материалы. Личные документы, адреса, переписки и оригиналы закрытого архива останутся в отдельной защищённой системе.</p></div><a href="{{ '/about/' | relative_url }}" aria-label="Подробнее о принципах проекта">↗</a></section>
<section class="status-teaser"><div><p class="eyebrow">ПРОЗРАЧНОСТЬ И ДОВЕРИЕ</p><h2>Разработка без выдуманных функций</h2><p>Показываем, что уже реализовано, что проверено и что ещё находится в планах.</p></div><a class="primary-link" href="{{ '/status/' | relative_url }}">Состояние проекта <span aria-hidden="true">↗</span></a></section>

<script defer src="{{ '/assets/js/ai-media-enhancer.js' | relative_url }}?v=20261126-video-dialog-1"></script>
<script defer src="{{ '/assets/js/media-atmosphere.js' | relative_url }}?v=20261126-atmosphere-controls-2"></script>

<script defer src="{{ '/assets/js/media-studio.js' | relative_url }}?v=20261126-media-studio-1"></script>

<script defer src="{{ '/assets/js/site-3d.js' | relative_url }}?v=20261125-gpu-recovery-2"></script>
<script defer src="{{ '/assets/js/ai-world-navigation.js' | relative_url }}?v=20261125-world-1"></script>
