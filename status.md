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
</div>
<div class="status-legend">
  <span class="status-pill status-green">ЗЕЛЁНЫЙ · реализовано и проверено</span>
  <span class="status-pill status-yellow">ЖЁЛТЫЙ · частично реализовано или не проверено полностью</span>
  <span class="status-pill status-red">КРАСНЫЙ · реализация отсутствует</span>
</div>
<section class="status-list" aria-label="Статус модулей">
<article class="status-card">
  <div class="status-card-heading"><span class="status-pill status-red">КРАСНЫЙ</span><span class="status-index">01</span></div>
  <h2>Единое файловое хранилище</h2>
  <p>Фото, видео, документы и аудио. Отдельного хранилища оригиналов, загрузки и выдачи файлов пока нет.</p>
  <p class="status-evidence">Подтверждение: в текущем дереве backend нет модуля object/file storage.</p>
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
</section>
<section class="status-summary">
<h2>Последняя подтверждённая проверка backend</h2>
<p><strong>31 тест пройден</strong> в CI. Это тесты существующей backend-основы и архива SQLite, а не доказательство готовности четырёх модулей выше.</p>
<ul>
<li>Ветка: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/tree/core-backend-foundation">core-backend-foundation</a></li>
<li>Коммит: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/commit/54bba598b649697ce5122b593fc034170d815680"><code>54bba598</code></a></li>
<li>CI: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/actions/runs/45112035406">запуск 45112035406 · success</a></li>
<li><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/requirements-register.md">Полный реестр требований</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/long-term-preservation.md">План долгосрочного хранения</a></li>
</ul>
<p class="status-note">Статусы на этой странице являются зафиксированным снимком. Они не обновляются автоматически при каждом коммите. После изменения кода страницу и доказательства необходимо обновить.</p>
</section>
<p><a href="{{ '/' | relative_url }}">← На главную</a></p>
