---
layout: default
title: Поколения и семейное дерево
permalink: /generations/
description: Семейное дерево KOMAROVA_CORE на основе защищённого реестра PERSON-ID.
---
<section class="page-heading">
  <p class="eyebrow">KOMAROVA_CORE · РЕЕСТР ЛЮДЕЙ</p>
  <h1>Поколения и <em>семейные связи.</em></h1>
  <p class="lead">Единый список людей с постоянными PERSON-ID и связями между ними. Записи загружаются только из авторизованного серверного реестра.</p>
</section>
<section class="registry-shell" data-generation-app>
  <div class="registry-panel">
    <h2>Подключение к семейному серверу</h2>
    <p class="registry-muted">Сервер KOMAROVA_CORE пока не размещён в публичной инфраструктуре. Укажите адрес API только после его отдельной настройки. Пароль и токен не сохраняются в браузере; токен действует только до перезагрузки этой страницы.</p>
    <form class="registry-connect" data-connect-form>
      <label>Адрес API<input name="api" type="url" placeholder="https://адрес-вашего-api" required></label>
      <label>Логин<input name="username" autocomplete="username" required></label>
      <label>Пароль<input name="password" type="password" autocomplete="off" required></label>
      <button class="registry-button" type="submit">Подключиться</button>
    </form>
    <p class="registry-status" data-status role="status" aria-live="polite">Сервер не подключён. Демонстрационные люди не подставляются.</p>
  </div>
  <div class="registry-panel registry-hidden" data-workspace>
    <div class="registry-toolbar"><div><h2>Реестр людей</h2><p class="registry-muted" data-user-label></p></div><button class="registry-button" type="button" data-refresh>Обновить реестр</button></div>
    <form class="registry-form" data-person-form>
      <label>Имя человека<input name="display_name" maxlength="200" required placeholder="Имя и фамилия"></label>
      <button class="registry-button" type="submit">Создать запись и PERSON-ID</button>
    </form>
    <div class="registry-grid" data-people-list><div class="registry-empty">Записи ещё не загружены.</div></div>
  </div>
  <div class="registry-panel registry-hidden" data-links-panel>
    <h2>Связи между людьми</h2>
    <form class="registry-form" data-link-form>
      <label>От кого<select name="from_person_id" required></select></label>
      <label>К кому<select name="to_person_id" required></select></label>
      <label>Тип связи<input name="relationship_type" maxlength="60" placeholder="например: parent, child, sibling" required></label>
      <button class="registry-button" type="submit">Сохранить связь</button>
    </form>
    <p class="registry-muted">Связи записываются на сервер. Одна и та же связь не должна дублироваться; двунаправленность при необходимости задаётся отдельной записью.</p>
  </div>
</section>
<link rel="stylesheet" href="{{ '/assets/css/registry.css' | relative_url }}?v=20261125-private-api-errors-2">
<script src="{{ '/assets/js/registry-client.js' | relative_url }}?v=20261125-private-api-errors-2" defer></script>
<script src="{{ '/assets/js/generations.js' | relative_url }}?v=20261125-private-api-errors-2" defer></script>
