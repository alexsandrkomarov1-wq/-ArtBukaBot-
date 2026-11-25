---
layout: default
title: События и семейная хронология
permalink: /events/
description: Серверный реестр событий KOMAROVA_CORE с постоянными EVENT-ID.
---
<section class="page-heading events-heading">
  <p class="eyebrow">KOMAROVA_CORE · ВРЕМЯ И ПАМЯТЬ</p>
  <h1>События и <em>хронология.</em></h1>
  <p class="lead">События получают постоянный EVENT-ID и связываются с участниками, местами и материалами через единый граф сущностей.</p>
</section>
<section class="registry-shell" data-events-app>
  <div class="registry-panel">
    <h2>Подключение к семейному серверу</h2>
    <p class="registry-muted">Используется защищённый API. До размещения backend реестр остаётся недоступен. Локальные демонстрационные события не создаются.</p>
    <form class="registry-connect" data-connect-form>
      <label>Адрес API<input name="api" type="url" placeholder="https://адрес-вашего-api" required></label>
      <label>Логин<input name="username" autocomplete="username" required></label>
      <label>Пароль<input name="password" type="password" autocomplete="off" required></label>
      <button class="registry-button" type="submit">Подключиться</button>
    </form>
    <p class="registry-status" data-status role="status" aria-live="polite">Сервер не подключён. События не подменяются примерами.</p>
  </div>
  <div class="registry-panel registry-hidden" data-workspace>
    <div class="registry-toolbar"><div><h2>Лента событий</h2><p class="registry-muted" data-user-label></p></div><button class="registry-button" type="button" data-refresh>Обновить</button></div>
    <form class="registry-form" data-event-form>
      <label>Название события<input name="title" maxlength="240" required placeholder="Например: семейная встреча"></label>
      <label>Дата и время<input name="occurred_at" type="datetime-local"></label>
      <label class="wide">Описание<textarea name="description" maxlength="10000" placeholder="Контекст, участники, источники…"></textarea></label>
      <button class="registry-button" type="submit">Создать событие и EVENT-ID</button>
    </form>
    <div class="registry-grid" data-events-list><div class="registry-empty">События ещё не загружены.</div></div>
    <div class="registry-panel">
      <h3>Связать событие с человеком</h3>
      <form class="registry-form" data-event-link-form>
        <label>Событие<select name="event_id" required></select></label>
        <label>Участник<select name="person_id" required></select></label>
        <label>Тип связи<input name="relationship_type" value="participant" maxlength="48" required></label>
        <button class="registry-button" type="submit">Сохранить связь</button>
      </form>
      <p class="registry-muted">Для связи с местами и материалами используется тот же API графа сущностей. Этот экран пока предлагает связь с участником.</p>
    </div>
  </div>
</section>
<link rel="stylesheet" href="{{ '/assets/css/registry.css' | relative_url }}?v=20261125-private-api-errors-2">
<script src="{{ '/assets/js/registry-client.js' | relative_url }}?v=20261125-private-api-errors-2" defer></script>
<script src="{{ '/assets/js/events-registry.js' | relative_url }}?v=20261125-private-api-errors-2" defer></script>
