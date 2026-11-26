---
layout: default
title: Состояние проекта
permalink: /status/
description: Проверяемое состояние модулей KOMAROVA_CORE
---
<div class="page-heading">
<p class="eyebrow">КОНТРОЛЬ РАЗРАБОТКИ</p>
<h1>Состояние <span>проекта.</span></h1>
<p class="lead">Снимок состояния ветки <code>core-backend-foundation</code>. Цвет показывает подтверждённый статус реализации, а ссылки ведут к коду и проверкам.</p>
<p class="status-links"><a href="{{ '/changes/' | relative_url }}">Журнал изменений сайта ↗</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/SITE_CHANGELOG.md">Полный технический журнал</a></p>

</div>
<div class="status-legend">
  <span class="status-pill status-green">ЗЕЛЁНЫЙ · реализовано и проверено</span>
  <span class="status-pill status-yellow">ЖЁЛТЫЙ · частично реализовано или не проверено полностью</span>
  <span class="status-pill status-red">КРАСНЫЙ · реализация отсутствует</span>
</div>
<section class="status-list" aria-label="Статус модулей">
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">01</span></div>
  <h2>Единое файловое хранилище</h2>
  <p>В development backend есть приватный storage-слой, приём фото и видео, карантин, SHA-256, отдельные MATERIAL-ID и потоковая выдача проверенных файлов. Поддерживаются локальный приватный provider и S3-совместимый интерфейс.</p>
  <p class="status-evidence">Частный backend и постоянное хранилище ещё не развёрнуты. Публичная витрина не получает доступ к семейным файлам.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">02</span></div>
  <h2>Полный архив .kca</h2>
  <p>Реализован архив базы SQLite с манифестом, SHA-256, проверкой целостности и CLI. Оригинальные файлы, медиатека и их метаданные в архив не включаются.</p>
  <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/backend/app/archive.py">Код архива</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/backend/tests/test_archive.py">Тесты архива</a></p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-red">КРАСНЫЙ</span><span class="status-index">03</span></div>
  <h2>Шифрование и независимые копии</h2>
  <p>Шифрование архивов, независимые off-site копии, управление ключами восстановления и регулярные restore drills не реализованы.</p>
  <p class="status-evidence">Подтверждение: эти функции отсутствуют в текущем коде и не проходят отдельный цикл восстановления.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">04</span></div>
  <h2>PostgreSQL: миграция и восстановление</h2>
  <p>Миграции и тесты существуют, но полный проверенный цикл миграции, резервирования и восстановления PostgreSQL не подтверждён. Результаты SQLite не засчитываются как проверка PostgreSQL.</p>
  <p class="status-evidence">Подтверждение: отдельный PostgreSQL CI job и тест восстановления пока отсутствуют.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-red">КРАСНЫЙ</span><span class="status-index">05</span></div>
  <h2>Семейная почта и обратная связь</h2>
  <p>Провайдер-независимая архитектура Gmail/Yandex и границы приватности описаны. Подключение ящиков, чтение и поиск переписки, отправка через backend, форма обратной связи и почтовый интерфейс пока не реализованы.</p>
  <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/family-mail-architecture.md">Архитектура семейной почты</a></p>
</article>
</section>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-green">ЗЕЛЁНЫЙ</span><span class="status-index">06</span></div>
  <h2>Публичная главная страница</h2>
  <p>Публичная витрина KOMAROVA_CORE запущена. Главная содержит семейную портретную галерею с пустыми безопасными слотами, ссылки Internet Archive и NASA Mars. Внешние ссылки проверены на опубликованной странице.</p>
  <p class="status-evidence">Подтверждение: HTTP 200, четыре карточки портретов, внешние ссылки archive.org и science.nasa.gov/mars присутствуют в live HTML.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">07</span></div>
  <h2>Персональное управление портретом</h2>
  <p>На главной подготовлены места для портретов. Индивидуальная загрузка, выбор, замена и публикация фотографии из закрытого кабинета пока не реализованы: необходимы авторизация, защищённое хранилище, права доступа и отдельное согласие на публичный показ.</p>
  <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/site-architecture-and-navigation.md">Требования к портретам и публикации</a></p>
</article>

<p><a href="{{ '/' | relative_url }}">← На главную</a></p><section class="status-summary">
<h2>Последний подтверждённый запуск публичной витрины</h2>
<p>Публичная главная страница запущена на коммите <strong>abcb245d</strong>. Ветка <code>core-backend-foundation</code> прошла сборку сайта, проверку локальных ссылок, backend-тесты и публикацию GitHub Pages. Live-проверка подтвердила наличие четырёх портретных карточек, Internet Archive и NASA Mars.</p>
<ul>
<li>Ветка: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/tree/core-backend-foundation">core-backend-foundation</a></li>
<li>Коммит: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/commit/abcb245d9e93a3d0e037947aaf3cd52f8f6b30c9"><code>abcb245d</code></a></li>
<li>GitHub Pages build: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/actions/runs/45247644371">success</a></li>
<li>Backend tests: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/actions/runs/45247644556">success, 43 passed</a></li>
<li>Pages deployment: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/actions/runs/45247643872">success</a></li>
<li>Резервная контрольная точка: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/tree/backup/stable-2026-11-23">backup/stable-2026-11-23</a></li>
<li><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/release-and-rollback-policy.md">Правила выпусков и отката</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/requirements-register.md">Полный реестр требований</a></li>
</ul>
<p class="status-note">Публичная витрина считается запущенной и может улучшаться последующими проверяемыми выпусками. Закрытый семейный архив, редактирование портретов и другие приватные функции не считаются реализованными до фактического подключения backend и прохождения соответствующих тестов.</p>
</section>

<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-green">ЗЕЛЁНЫЙ</span><span class="status-index">06</span></div>
  <h2>Публичная главная страница</h2>
  <p>Публичная витрина KOMAROVA_CORE запущена. Главная содержит семейную портретную галерею с пустыми безопасными слотами, ссылки Internet Archive и NASA Mars. Внешние ссылки проверены на опубликованной странице.</p>
  <p class="status-evidence">Подтверждение: HTTP 200, четыре карточки портретов, внешние ссылки archive.org и science.nasa.gov/mars присутствуют в live HTML.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">07</span></div>
  <h2>Персональное управление портретом</h2>
  <p>На главной подготовлены места для портретов. Индивидуальная загрузка, выбор, замена и публикация фотографии из закрытого кабинета пока не реализованы: необходимы авторизация, защищённое хранилище, права доступа и отдельное согласие на публичный показ.</p>
  <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/site-architecture-and-navigation.md">Требования к портретам и публикации</a></p>
</article>

<p><a href="{{ '/' | relative_url }}">← На главную</a></p>


<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">08</span></div>
  <h2>Локальный просмотр фото и видео</h2>
  <p>В браузере реализован выбор файлов с устройства, просмотр изображений, воспроизведение видео поддерживаемых браузером форматов, переключение, слайдшоу фотографий, полноэкранный режим и скачивание выбранного файла. Файлы не отправляются на сервер и не сохраняются в семейном архиве.</p>
  <p class="status-evidence">Проверка: статический контракт интерфейса, синтаксис JavaScript и сборка GitHub Pages. Совместимость декодирования зависит от браузера и конкретного кодека.</p>
</article>


<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">09</span></div>
  <h2>Закрытый приём фото и видео</h2>
  <p>В development backend реализованы защищённые маршруты приёма файлов в карантин, проверка ClamAV, выдача только проверенных материалов, потоковое получение содержимого и создание отдельной производной копии. Реестр сохраняет ARCHIVE-ID, MATERIAL-ID, MIME по сигнатуре, размер, SHA-256 и связь с PERSON-ID. Дубликаты по точному SHA-256 не создают вторую запись.</p>
  <p>Маршруты и код worker существуют, но их работа зависит от установленного ClamAV, Real-ESRGAN NCNN Vulkan, файлов модели и частного storage. Частный backend не развёрнут и не подключён к публичному GitHub Pages. Поэтому живой AI MEDIA сейчас выполняет локальный предпросмотр и SHA-256, но не серверное сканирование или улучшение.</p>
  <p class="status-evidence">Подтверждение реализации: backend/app/cloud_archive_api.py, backend/app/ai_media_worker.py и тесты backend. Production-запуск и обработка реального семейного файла не подтверждены.</p>
</article>


<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">10</span></div>
  <h2>Ориентация и адаптация медиа</h2>
  <p>EXIF-aware подготовка изображений и видео-конвейер FFmpeg/FFprobe используются в development worker. AI-фото обрабатывается Real-ESRGAN x4, видео x2; производная версия сканируется и получает отдельный MATERIAL-ID со ссылкой на оригинал. Исходник не перезаписывается.</p>
  <p>Это серверная реализация в репозитории, а не доступная функция публичного сайта: частный worker, ClamAV и модели не развёрнуты. Локальный предпросмотр в браузере не считается AI-обработкой.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-green">РАБОТАЕТ</span><span class="status-index">11</span></div>
  <h2>Навигационные подсказки</h2>
  <p>На публичных страницах добавлен контекстный помощник с подсказками по текущему разделу и ссылками на существующие страницы. Он работает локально и не отправляет файлы или содержимое страниц во внешний ИИ. Live-проверка подтвердила помощника и первую всплывающую подсказку на главной, медиатеке и странице статуса.</p>
  <p>Neon AI Gateway включён на production-ветке, но на момент проверки все модели заблокированы ответом paid_plan_required. Публичный сайт проверяет состояние шлюза; вызов модели и защищённый media handler ещё не включены.</p>
</article>


<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">12</span></div>
  <h2>Neon AI Gateway</h2>
  <p>Neon AI Gateway включён на рабочей ветке <code>production</code>; на ветке существует credential с правом <code>ai_gateway:invoke</code>. Подключение проверено через Neon Function: запрос каталога <code>/v1/models</code> вернул HTTP 200.</p>
  <p>На момент проверки все доступные модели возвращают <code>enabled: false</code> и <code>paid_plan_required</code>. На бесплатном тарифе Neon для вызова моделей нужны платёжная карта и предоплаченные AI-кредиты. Ни одного inference-запроса и обработки семейного файла не выполнялось. Развёртывание прикладного обработчика, авторизация сайта и медиаархив остаются отдельными этапами.</p>
</article>
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">13</span></div>
  <h2>AI MEDIA ENHANCER · интерфейс и worker</h2>
  <p>На главной работают выбор фото/видео, локальный предпросмотр оригинала, проверка типа и размера, SHA-256, переключение природных сцен, музыкальные режимы, голосовые команды и экспорт только реального результата. Добавлено ручное подключение частного API с пустым полем пароля; токен хранится только в памяти страницы.</p>
  <p>ClamAV и Real-ESRGAN x4/x2 доступны в коде development backend, но на опубликованном сайте пока не запускаются: частный API/worker не развёрнут. Кнопка экспорта остаётся выключенной, пока сервер не вернёт настоящую проверенную копию.</p>
  <p class="status-evidence">Проверки: scripts/check_ai_media_lab.py, JavaScript syntax, backend tests и GitHub Pages build/deploy. Статус жёлтый до реального развёртывания и runtime-теста ClamAV/Real-ESRGAN.</p>
</article>



<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-yellow">ЖЁЛТЫЙ</span><span class="status-index">14</span></div>
  <h2>Supabase · закрытый архив фото и видео</h2>
  <p>В рабочую ветку добавлены клиент Supabase Auth/Storage, интерфейс подключения Project URL и публичного anon/publishable key, приватный bucket <code>komarova_core_private</code>, SQL-схема реестра <code>public.archive_items</code>, SHA-256 и связи-указатели PERSON-ID/EVENT-ID/PLACE-ID. Навигация архива разделена на загрузку, каталог, места хранения и локальный просмотр.</p>
  <p class="status-evidence">Проверка реального проекта ещё не завершена: URL и публичный ключ не внесены в конфигурацию страницы, SQL-скрипт не подтверждён запуском в Supabase, Auth login и тестовая загрузка/чтение не выполнялись. До этого Supabase не считается подключённым к сайту, а семейные файлы не следует загружать.</p>
  <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/backend/supabase/001_private_media_archive.sql">SQL-схема Supabase</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/assets/js/supabase-archive.js">Клиент архива</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/storage-provider-configuration.md">Границы интеграции и безопасности</a></p>
</article>
