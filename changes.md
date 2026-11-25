---
layout: default
title: Журнал изменений
permalink: /changes/
description: Хронология проверенных изменений публичного сайта KOMAROVA_CORE
---
<div class="page-heading">
  <p class="eyebrow">KOMAROVA_CORE · ПРОЗРАЧНОСТЬ РАЗРАБОТКИ</p>
  <h1>Журнал <span>изменений.</span></h1>
  <p class="lead">Здесь фиксируются изменения публичного сайта, их GitHub-основание и фактический статус публикации. Коммит, объединение и работающая функция — разные вещи.</p>
</div>
<section class="status-summary">
  <h2>Последняя проверка: 25 ноября 2026</h2>
  <p>Опубликованные страницы главной, событий, семейной доски с картой, медиатеки и состояния проекта прочитаны напрямую с GitHub Pages. Это подтверждает доступность и содержимое страниц, но не заменяет проверку каждого действия нажатием в браузере.</p>
</section>
<section class="status-list" aria-label="История изменений">
  <article class="status-card">
    <div class="status-card-heading"><span class="status-pill status-green">ОПУБЛИКОВАНО</span><span class="status-index">25.11.2026</span></div>
    <h2>Навигация по разделам семейного архива</h2>
    <p>Карточки «События и хронология», «Места и путешествия» и «Фотографии и документы» ведут на соответствующие страницы. Добавлена отдельная страница событий, а для карты предусмотрен резервный режим.</p>
    <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/pull/19">PR #19</a> · merge commit <code>29fe9ae8</code></p>
  </article>
  <article class="status-card">
    <div class="status-card-heading"><span class="status-pill status-yellow">ЧАСТИЧНО</span><span class="status-index">25.11.2026</span></div>
    <h2>AI MEDIA ENHANCER</h2>
    <p>На главной опубликован демонстрационный интерфейс восстановления фото и видео. Настоящий ИИ-провайдер и AI-реставрация не подключены. Отдельная локальная диагностика загрузки разрабатывается в PR #18 и пока не входит в опубликованную версию.</p>
    <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/feature/ai-media-enhancer-homepage/docs/AI_MEDIA_ENHANCER.md">Спецификация редакции 1.0</a> · <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/pull/18">PR #18 · диагностика загрузки</a></p>
  </article>
  <article class="status-card">
    <div class="status-card-heading"><span class="status-pill status-yellow">ЛОКАЛЬНО</span><span class="status-index">25.11.2026</span></div>
    <h2>Портретные карточки</h2>
    <p>Добавлены четыре поля выбора фотографии с локальным предпросмотром. Файлы не отправляются на сервер, не привязаны к PERSON-ID и не сохраняются после обновления страницы.</p>
    <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/pull/16">PR #16</a></p>
  </article>
  <article class="status-card">
    <div class="status-card-heading"><span class="status-pill status-yellow">ЛОКАЛЬНЫЙ ПРОСМОТР</span><span class="status-index">24–25.11.2026</span></div>
    <h2>Фотографии и документы</h2>
    <p>Опубликован просмотр фотографий и видео, выбранных на текущем устройстве. На странице медиатеки указано, что API закрытого архива пока недоступен, а содержимое Google Drive в интерфейсе ещё не отображается.</p>
    <p class="status-links"><a href="https://alexsandrkomarov1-wq/-ArtBukaBot-/media/">Открыть медиатеку</a></p>
  </article>
  <article class="status-card">
    <div class="status-card-heading"><span class="status-pill status-green">ОПУБЛИКОВАНО</span><span class="status-index">23.11.2026</span></div>
    <h2>Первая публичная версия KOMAROVA_CORE</h2>
    <p>Создана Jekyll-витрина проекта с базовой структурой, стилями и разграничением публичных и закрытых семейных данных.</p>
    <p class="status-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/commit/a1b3c2ed">Начальный коммит сайта</a></p>
  </article>
</section>
<p class="status-note">Полный технический журнал и исходные основания изменений: <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/SITE_CHANGELOG.md">docs/SITE_CHANGELOG.md</a>. Фактическое рабочее время учитывается отдельно и не выводится из количества коммитов.</p>
<p><a href="{{ '/status/' | relative_url }}">← Состояние проекта</a> · <a href="{{ '/' | relative_url }}">Главная</a></p>
