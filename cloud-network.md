---
layout: default
title: Облачная сеть
description: Единый каталог KOMAROVA_CORE и состояние подключения облачных хранилищ.
permalink: /cloud-network/
---
<style>
.cloud-console{--cn-line:rgba(127,174,197,.22);color:#eaf4fb;background:radial-gradient(circle at 85% 5%,rgba(38,121,151,.22),transparent 34%),linear-gradient(145deg,#101d2a,#172c3c 60%,#101b28);border:1px solid var(--cn-line);border-radius:24px;padding:clamp(20px,4vw,42px);margin:8px 0 34px;box-shadow:0 24px 70px rgba(0,0,0,.2)}
.cloud-console *{box-sizing:border-box}.cn-eyebrow{font-size:.72rem;letter-spacing:.18em;color:#8dc8dc;font-weight:700}.cloud-console h1{font-size:clamp(2rem,5vw,3.7rem);line-height:1.04;color:#f5fbff;margin:14px 0}.cloud-console h1 em{color:#8ed8e8;font-style:normal}.cn-lead{max-width:760px;color:#c0d0dc;font-size:1.04rem;line-height:1.7}.cn-state{display:inline-flex;gap:9px;align-items:center;border:1px solid rgba(241,190,103,.4);border-radius:999px;padding:8px 13px;color:#f6d69d;font-size:.78rem;letter-spacing:.06em;margin:12px 0 24px}.cn-dot{width:8px;height:8px;border-radius:50%;background:#e8b65f;box-shadow:0 0 12px #e8b65f}.cn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:13px;margin:24px 0}.cn-card{border:1px solid var(--cn-line);border-radius:16px;background:rgba(255,255,255,.045);padding:17px;min-height:145px}.cn-card-link{display:block;height:100%;color:inherit;text-decoration:none;cursor:pointer}.cn-card-link:focus-visible{outline:2px solid #8ed8e8;outline-offset:4px;border-radius:10px}.cn-open{display:inline-flex;margin-top:13px;padding:8px 12px;border:1px solid rgba(142,216,232,.48);border-radius:999px;color:#a9e3ef;font-size:.78rem;font-weight:700}.cn-card-link:hover .cn-open{background:rgba(142,216,232,.13)}.cn-provider-link{color:#f1f8fc;text-decoration:none;border-bottom:1px solid rgba(142,216,232,.55);transition:color .18s ease,border-color .18s ease}.cn-provider-link:hover,.cn-provider-link:focus-visible{color:#8ed8e8;border-color:#8ed8e8;outline:none}.cn-card strong{display:block;color:#f1f8fc;font-size:1rem;margin:5px 0 9px}.cn-card p{color:#b5c6d3;font-size:.88rem;line-height:1.55;margin:0}.cn-tag{font-size:.68rem;letter-spacing:.12em;color:#8dc8dc}.cn-tag.pending{color:#f0c77f}.cn-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;margin:18px 0 26px}.cn-step{border:1px solid var(--cn-line);border-radius:13px;padding:13px;background:rgba(5,14,24,.25)}.cn-step b{display:block;color:#9dd6e4;font-size:.74rem;letter-spacing:.1em;margin-bottom:7px}.cn-step span{font-size:.88rem;color:#dce8ef}.cn-note{border-left:3px solid #78c8d8;padding:12px 16px;background:rgba(91,167,188,.09);color:#d4e4ec;line-height:1.6;margin:22px 0}.cn-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}.cn-links a{color:#eafaff;border:1px solid rgba(142,216,232,.4);border-radius:999px;padding:10px 15px;text-decoration:none}.cn-links a:hover{background:rgba(142,216,232,.12)}.cn-foot{color:#91a9b8;font-size:.8rem;margin-top:22px}
</style>
<section class="cloud-console" aria-labelledby="cloud-title">
  <p class="cn-eyebrow">KOMAROVA_CORE / PRIVATE ARCHIVE INFRASTRUCTURE</p>
  <h1 id="cloud-title">Единая <em>облачная сеть</em></h1>
  <p class="cn-lead">Единая точка входа для загрузки, просмотра и скачивания семейных материалов. Файлы принимаются через архив KOMAROVA_CORE; дополнительные облака подключаются сервером только после авторизации и успешной проверки.</p>
  <div class="cn-state"><span class="cn-dot"></span> SUPABASE СХЕМА И ПРИВАТНЫЙ БАКЕТ СОЗДАНЫ · ПЕРВАЯ ЗАГРУЗКА ОЖИДАЕТ ВХОДА</div>
  <div class="cn-grid" aria-label="Состав облачной системы">
    <article class="cn-card"><a class="cn-card-link" href="/-ArtBukaBot-/account/" aria-label="Открыть единый каталог семейного архива"><span class="cn-tag">01 / REGISTRY</span><strong>Единый каталог ↗</strong><p>PERSON-ID, EVENT-ID, PLACE-ID и MATERIAL-ID связывают файлы с семейной историей. Оригиналы и производные версии учитываются отдельно.</p><span class="cn-open">Открыть каталог</span></a></article>
    <article class="cn-card"><a class="cn-card-link" href="#cn-providers" aria-label="Перейти к списку облачных хранилищ"><span class="cn-tag">02 / STORAGE</span><strong>Несколько хранилищ ↗</strong><p>Провайдеры подключаются отдельными серверными адаптерами. Сбой одного облака не должен останавливать остальные.</p><span class="cn-open">Показать провайдеров</span></a></article>
    <article class="cn-card"><a class="cn-card-link" href="/-ArtBukaBot-/status/" aria-label="Открыть состояние проекта и проверки"><span class="cn-tag">03 / INTEGRITY</span><strong>Проверка копий ↗</strong><p>Для каждой копии фиксируются удалённый ID, размер, SHA-256 и состояние. Успех подтверждается проверочным чтением.</p><span class="cn-open">Открыть состояние</span></a></article>
    <article class="cn-card"><a class="cn-card-link" href="/-ArtBukaBot-/media/" aria-label="Открыть AI MEDIA и работу с оригиналами"><span class="cn-tag">04 / SAFETY</span><strong>Защита оригинала ↗</strong><p>Оригинал не перезаписывается. Любая улучшенная или преобразованная версия получает собственный MATERIAL-ID.</p><span class="cn-open">Открыть AI MEDIA</span></a></article>
  </div>
  <h2 id="cn-providers">Семейные подключения облаков · STORAGE + AI API</h2>
  <p class="cn-lead">Каждый член семьи подключает собственную учётную запись каждого поддерживаемого провайдера. У одного провайдера может быть несколько независимых аккаунтов: по одному на каждого человека, а при необходимости несколько аккаунтов у одного человека. Доступы, OAuth-токены, квоты и история синхронизации разделены по владельцам. Google Drive входит в постоянный набор провайдеров. Два адреса ниже показывают два отдельных аккаунта; число семейных подключений не ограничено этими двумя карточками. Каждый аккаунт авторизуется отдельно.</p>
  <div class="cn-note"><strong>Модель подключения:</strong> семейный реестр хранит связь «член семьи → провайдер → аккаунт». Метка «ПОДКЛЮЧЕНИЕ · API / AI API» обозначает назначение коннектора, а не уже полученный токен. Реальный статус каждого аккаунта меняется на «Подключён» только после личной авторизации, проверки доступа, пробной записи и обратного чтения. Пароли и токены не вводятся на GitHub Pages и не хранятся в браузерном коде.</div>
  <div class="cn-grid" aria-label="Состояние облачных провайдеров">
    <article class="cn-card"><span class="cn-tag pending">ОСНОВНОЙ ПРОВАЙДЕР · ПОДКЛЮЧЕНИЕ НЕ ПРОВЕРЕНО</span><strong>Google Drive</strong><p>Несколько независимых семейных аккаунтов. Каждый кабинет открывается отдельно; серверная авторизация и тест записи/чтения выполняются независимо.</p><div class="cn-links"><a href="https://drive.google.com/drive/u/0/home" target="_blank" rel="noopener noreferrer">Открыть аккаунт u/0 ↗</a><a href="https://drive.google.com/drive/u/1/home" target="_blank" rel="noopener noreferrer">Открыть аккаунт u/1 ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР В КОДЕ · НУЖЕН OAUTH</span><strong>OneDrive</strong><p>Серверный адаптер Microsoft Graph. Требуется авторизация конкретного аккаунта и проверка записи с обратным чтением.</p><div class="cn-links"><a href="https://www.microsoft.com/nl-nl/microsoft-365/onedrive/online-cloud-storage" target="_blank" rel="noopener noreferrer">Открыть OneDrive ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР В КОДЕ · НУЖЕН OAUTH</span><strong>Яндекс Диск</strong><p>Серверный REST-адаптер. Требуется авторизация конкретного аккаунта и проверка записи с обратным чтением.</p><div class="cn-links"><a href="https://disk.yandex.ru/client/disk" target="_blank" rel="noopener noreferrer">Открыть Яндекс Диск ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР НЕ ПОДТВЕРЖДЁН</span><strong>MEGA</strong><p>Автоматическая передача не включена до реализации и проверки официального серверного API. Сохранена предоставленная тобой ссылка на блог MEGA.</p><div class="cn-links"><a href="https://blog.mega.io/?resilience=1" target="_blank" rel="noopener noreferrer">Открыть страницу MEGA ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР НЕ ПОДТВЕРЖДЁН</span><strong>pCloud</strong><p>Автоматическая передача не включена до реализации и проверки официального серверного API.</p><div class="cn-links"><a href="https://my.pcloud.com/#/filemanager" target="_blank" rel="noopener noreferrer">Открыть pCloud ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР НЕ ПОДТВЕРЖДЁН</span><strong>Dropbox</strong><p>Автоматическая передача не включена до реализации и проверки официального серверного API.</p><div class="cn-links"><a href="https://www.dropbox.com/home" target="_blank" rel="noopener noreferrer">Открыть Dropbox ↗</a></div></article>
    <article class="cn-card"><span class="cn-tag pending">АДАПТЕР НЕ ПОДТВЕРЖДЁН</span><strong>TeraBox</strong><p>Автоматическая передача не включена до реализации и проверки официального серверного API.</p><div class="cn-links"><a href="https://www.terabox.com/ai/index/russian" target="_blank" rel="noopener noreferrer">Открыть TeraBox AI ↗</a></div></article>
  </div>
  <section id="family-external-resources" data-resources-url="{{ '/assets/data/external-resources.json' | relative_url }}" aria-label="Семейные внешние ресурсы">
    <p class="cn-lead">Общий каталог из десяти пользовательских ссылок. Он загружается из единого JSON-файла, чтобы локальная и онлайн-версии показывали одинаковые адреса, подписи и категории.</p>
  </section>
  <script src="{{ '/assets/js/external-resources.js' | relative_url }}" defer></script>
  <div class="cn-links">
    <a href="{{ '/media/#archive-upload' | relative_url }}">Загрузить материалы в KOMAROVA_CORE ↗</a>
    <a href="{{ '/media/#archive-catalog' | relative_url }}">Открыть каталог и скачать файлы ↗</a>
  </div>
  <h2>Как материал проходит систему</h2>
  <div class="cn-flow" aria-label="Путь материала через облачную сеть">
    <div class="cn-step"><b>01 · INTAKE</b><span>Выбор и приём файла</span></div>
    <div class="cn-step"><b>02 · VERIFY</b><span>Проверка и SHA-256</span></div>
    <div class="cn-step"><b>03 · REGISTRY</b><span>MATERIAL-ID и связи</span></div>
    <div class="cn-step"><b>04 · REPLICATE</b><span>Копирование в облака</span></div>
    <div class="cn-step"><b>05 · CONFIRM</b><span>Чтение и сверка копии</span></div>
  </div>
  <div class="cn-note"><strong>Фактический статус:</strong> ссылки открывают личные кабинеты провайдеров; подключение ведётся отдельно для каждого члена семьи. Это пока переходы к веб-интерфейсам, а не работающие серверные коннекторы. AI MEDIA KOMAROVA_CORE должен получать файл через собственный защищённый backend, создавать отдельную улучшенную копию с новым MATERIAL-ID и сохранять её отдельно от оригинала. Ни один из семи провайдеров не объявляется подключённым к автоматической загрузке или AI-обработке до успешного теста авторизации, записи и обратного чтения. Google Drive поддерживает несколько независимых семейных аккаунтов; каждый подключается отдельно.</div>
  <div class="cn-links">
    <a href="{{ '/media/' | relative_url }}">Открыть AI MEDIA и архив ↗</a>
    <a href="{{ '/status/' | relative_url }}">Проверить состояние проекта ↗</a>
    <a href="{{ '/ai-control/' | relative_url }}">Открыть Центр управления ИИ ↗</a>
    <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/cloud-network-implementation.md">Технический план в GitHub ↗</a>
  </div>
  <p class="cn-foot">Рабочая ветка: core-backend-foundation · Публикация: GitHub Pages после успешной проверки сборки · main и настройки Supabase не затрагиваются.</p>
</section>


<style>
.plugin-registry-cloud{margin:34px 0 12px;padding:clamp(20px,4vw,38px);border:1px solid rgba(119,176,198,.28);border-radius:24px;background:linear-gradient(145deg,#101d2a,#1b3040);color:#eaf4fb}
.plugin-registry-cloud *{box-sizing:border-box}.plugin-registry-cloud .pr-eyebrow{font-size:.72rem;letter-spacing:.16em;color:#8dc8dc;font-weight:700}.plugin-registry-cloud h2{color:#f4fbff;font-size:clamp(1.7rem,4vw,2.5rem);margin:10px 0}.plugin-registry-cloud h3{color:#eaf4fb;margin-top:26px}.plugin-registry-cloud .pr-lead{max-width:900px;color:#c0d0dc;line-height:1.65}.plugin-registry-cloud .pr-status{display:inline-block;border:1px solid rgba(241,190,103,.4);border-radius:999px;padding:7px 12px;color:#f6d69d;font-size:.72rem;letter-spacing:.05em;margin:8px 0 18px}.plugin-registry-cloud .pr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(225px,1fr));gap:12px;margin:18px 0}.plugin-registry-cloud .pr-card{border:1px solid rgba(127,174,197,.22);border-radius:15px;background:rgba(255,255,255,.045);padding:16px}.plugin-registry-cloud .pr-card b{display:block;color:#f4fbff;margin:4px 0 8px}.plugin-registry-cloud .pr-card p{color:#bdced9;font-size:.88rem;line-height:1.55;margin:0}.plugin-registry-cloud .pr-kicker{font-size:.67rem;letter-spacing:.12em;color:#8dc8dc}.plugin-registry-cloud .pr-table-wrap{overflow-x:auto;margin:15px 0 24px}.plugin-registry-cloud table{width:100%;border-collapse:collapse;min-width:700px;font-size:.86rem}.plugin-registry-cloud th,.plugin-registry-cloud td{border-bottom:1px solid rgba(127,174,197,.2);padding:10px;text-align:left;vertical-align:top}.plugin-registry-cloud th{color:#9ed7e5}.plugin-registry-cloud td{color:#c6d5df}.plugin-registry-cloud .pr-callout{border-left:3px solid #78c8d8;padding:12px 16px;background:rgba(91,167,188,.09);color:#d4e4ec;line-height:1.6;margin:20px 0}.plugin-registry-cloud .pr-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.plugin-registry-cloud .pr-links a{color:#eafaff;border:1px solid rgba(142,216,232,.4);border-radius:999px;padding:10px 15px;text-decoration:none}
</style>
<section class="plugin-registry-cloud" aria-labelledby="plugin-registry-cloud-title">
  <p class="pr-eyebrow">PLUGIN SUPPORT REGISTRY · CLOUD COMPATIBILITY</p>
  <h2 id="plugin-registry-cloud-title">Реестр плагинов и <em>совместимость инфраструктуры</em></h2>
  <p class="pr-lead">Эта страница показывает не только облачные диски, но и то, как Photoshop, видео, ИИ, звук, карты и навигация будут связаны с главным порталом через единый каталог KOMAROVA_CORE.</p>
  <span class="pr-status">АРХИТЕКТУРА ОПИСАНА · PRODUCTION-ПОДКЛЮЧЕНИЯ НЕ ПОДТВЕРЖДЕНЫ</span>

  <h3>Редакторы, видео и конструкторы</h3>
  <div class="pr-grid">
    <article class="pr-card"><span class="pr-kicker">PHOTO / DESIGN</span><b>Photoshop и графика</b><p>Adobe Photoshop UXP/API, Lightroom, GIMP, Krita, Canva. Импорт и экспорт через рабочую копию; результат получает новый MATERIAL-ID.</p></article>
    <article class="pr-card"><span class="pr-kicker">VIDEO / PLAYER</span><b>Плееры и монтаж</b><p>HTML5, Video.js, VLC, FFmpeg/FFprobe, Shotcut, Kdenlive, DaVinci Resolve. Хранение оригинала отдельно от монтажного экспорта.</p></article>
    <article class="pr-card"><span class="pr-kicker">BUILDERS / 3D</span><b>Визуальные конструкторы</b><p>Canva, Figma, Three.js, MapLibre, Leaflet. Дизайн, 3D-порталы, карты и интерфейсные панели.</p></article>
  </div>

  <h3>ИИ-ассистенты, голос и ИИ-летописец</h3>
  <div class="pr-grid">
    <article class="pr-card"><span class="pr-kicker">AI ASSISTANT</span><b>Разговорный помощник</b><p>Текстовый и голосовой диалог, AI Router, Whisper/STT, Piper/TTS и WebRTC. Микрофон активируется только пользователем.</p></article>
    <article class="pr-card"><span class="pr-kicker">AI STORYTELLER</span><b>Рассказчик по видео</b><p>Извлечение аудио, распознавание речи, таймкоды, ключевые кадры и черновое описание сцен. ИИ не выдаёт догадки за факты.</p></article>
    <article class="pr-card"><span class="pr-kicker">WALK NARRATOR</span><b>Рассказчик туристической прогулки</b><p>GPX/KML/GeoJSON, GPS-точки, остановки, фотографии и заметки. Формирует маршрут и черновик истории после проверки географии человеком.</p></article>
    <article class="pr-card"><span class="pr-kicker">AUDIO</span><b>Звук и озвучивание</b><p>Очистка шума RNNoise/FFmpeg, синтез речи, субтитры и звуковая атмосфера. Каждый обработанный звук — отдельный материал.</p></article>
  </div>

  <h3>Карты и навигация</h3>
  <div class="pr-grid">
    <article class="pr-card"><span class="pr-kicker">MAP DATA</span><b>OpenStreetMap и Google Earth</b><p>Базовые геоданные, KML/KMZ, семейные места и экспорт маршрутов. Частные координаты не публикуются автоматически.</p></article>
    <article class="pr-card"><span class="pr-kicker">MAP UI</span><b>MapLibre и Leaflet</b><p>Интерактивная карта в главном портале, лёгкий режим для слабых устройств, слои PLACE-ID.</p></article>
    <article class="pr-card"><span class="pr-kicker">GEOCODING / ROUTING</span><b>Nominatim, OSRM, GraphHopper, Valhalla</b><p>Поиск мест и построение пеших/транспортных маршрутов после проверки API, лицензии, профиля маршрутизации и лимитов.</p></article>
  </div>

  <h3>Матрица облачных провайдеров</h3>
  <div class="pr-table-wrap"><table>
    <thead><tr><th>Провайдер</th><th>Интерфейс / API</th><th>Роль</th><th>Статус</th></tr></thead>
    <tbody>
      <tr><td>Google Drive</td><td>Drive API / OAuth 2.0</td><td>Отдельный аккаунт каждого члена семьи; два аккаунта уже представлены отдельными окнами, число подключений не ограничено двумя</td><td>Подключение аккаунта подтверждается персональной авторизацией и тестом чтения/записи</td></tr>
      <tr><td>MEGA</td><td>Официальный API / клиентская авторизация по условиям сервиса</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Отдельная запись подключения для каждого владельца; API-доступ подтверждается тестом</td></tr>
      <tr><td>pCloud</td><td>HTTP API / OAuth</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Отдельная OAuth-сессия и проверка доступа каждого аккаунта</td></tr>
      <tr><td>Яндекс Диск</td><td>REST API / OAuth / доступный аккаунту WebDAV</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Отдельная авторизация и проверка доступа каждого аккаунта</td></tr>
      <tr><td>OneDrive</td><td>Microsoft Graph / OAuth</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Отдельная Microsoft Graph авторизация и проверка разрешений каждого аккаунта</td></tr>
      <tr><td>Dropbox</td><td>Dropbox API / OAuth</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Отдельная OAuth-сессия и проверка квот/доступа каждого аккаунта</td></tr>
      <tr><td>TeraBox</td><td>Веб-доступ; серверная автоматизация только при подтверждённом официальном API</td><td>Индивидуальный аккаунт каждого члена семьи</td><td>Личный веб-доступ отделён от статуса серверного API-коннектора</td></tr>
    </tbody>ody>
  </table></div>

  <h3>Supabase — совместимость и назначение</h3>
  <p class="pr-lead">Существующий Supabase-проект KOMAROVA_CORE рассматривается как backend-компонент. Ссылка на Dashboard Explorer открывает административный инструмент анализа запросов и логов, а не пользовательский плагин сайта.</p>
  <div class="pr-table-wrap"><table>
    <thead><tr><th>Компонент</th><th>Возможное применение</th><th>Текущее состояние</th></tr></thead>
    <tbody>
      <tr><td>PostgreSQL</td><td>Метаданные PERSON/EVENT/PLACE/MATERIAL, связи и аудит</td><td>Таблица archive_items создана; RLS включён</td></tr>
      <tr><td>Auth</td><td>Пользователи, OAuth и сессии</td><td>Пока 0 пользователей; вход владельца ещё не проверен</td></tr>
      <tr><td>Storage</td><td>Приватные файлы и медиа</td><td>Приватный бакет создан; лимит 50 MiB/файл на Free; проверка загрузки ждёт первого пользователя</td></tr>
      <tr><td>RLS</td><td>Разграничение семейных данных</td><td>Две политики каталога и две Storage-политики созданы; Security Advisor без замечаний</td></tr>
      <tr><td>Edge Functions</td><td>Короткие API, webhook и интеграции</td><td>Не замена длительному AI/media worker</td></tr>
      <tr><td>Realtime</td><td>Статусы загрузок и синхронизации</td><td>Не настроен/не проверен</td></tr>
      <tr><td>PostGIS</td><td>Географические точки, расстояния и маршруты</td><td>Возможное расширение, не включено</td></tr>
      <tr><td>pgvector</td><td>Семантический поиск по текстам и описаниям</td><td>Возможное расширение, не включено</td></tr>
      <tr><td>Explorer / Notebooks</td><td>Исследование SQL и логов в Dashboard</td><td>Инструмент администрирования; не часть публичного интерфейса</td></tr>
    </tbody>
  </table></div>
  <div class="pr-callout"><strong>Неизменяемые ограничения:</strong> схема архива и приватный бакет уже созданы в Supabase KOMAROVA_CORE. Пользовательская загрузка ещё не проверена, поскольку Auth пока пуст. GitHub Pages не хранит секреты и семейные оригиналы. Активные сессии и серверные коннекторы проверяются отдельно для каждого семейного аккаунта. Оригинал никогда не перезаписывается; производный файл получает собственный MATERIAL-ID.</div>
  <div class="pr-links">
    <a href="{{ '/' | relative_url }}">Вернуться на главный портал ↗</a>
    <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/plugin-support-registry.md">Полный реестр и технические контракты ↗</a>
    <a href="https://colab.research.google.com/github/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/notebooks/KOMAROVA_CORE_Plugin_Support_Registry.ipynb">Открыть реестр в Google Colab ↗</a>
    <a href="https://supabase.com/dashboard/organizations?featurePreviewModal=preview-explorer">Supabase Dashboard Explorer ↗</a>
  </div>
</section>

