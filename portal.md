---
layout: default
title: Семейный кабинет
permalink: /portal/
description: Закрытый интерфейс KOMAROVA_CORE для входа и работы с семейным реестром
---

<meta name="robots" content="noindex, nofollow">

<section class="portal-shell" data-core-portal data-api-base="{{ site.api_base_url | default: '' | escape }}">
  <div class="portal-heading">
    <p class="eyebrow">KOMAROVA_CORE · PRIVATE SPACE</p>
    <h1>Семейный кабинет<span>.</span></h1>
    <p>Закрытый доступ к семейному реестру. Данные загружаются из API только после авторизации.</p>
  </div>
  <p class="portal-notice" data-portal-notice role="status" aria-live="polite">Проверяем настройки подключения…</p>
  <section class="portal-card" data-login-panel>
    <h2>Вход в систему</h2>
    <form data-login-form>
      <label for="portal-username">Логин</label>
      <input id="portal-username" name="username" autocomplete="username" required minlength="3" maxlength="80">
      <label for="portal-password">Пароль</label>
      <input id="portal-password" name="password" type="password" autocomplete="current-password" required minlength="12" maxlength="128">
      <button type="submit">Войти</button>
    </form>
  </section>
  <section class="portal-card" data-private-panel hidden>
    <div class="portal-user-row">
      <div><p class="eyebrow">АВТОРИЗОВАННЫЙ ПОЛЬЗОВАТЕЛЬ</p><h2 data-user-name></h2><p data-user-role></p></div>
      <button type="button" class="portal-secondary" data-logout>Выйти</button>
    </div>
    <div class="portal-section-heading"><h2>Реестр людей</h2><button type="button" class="portal-secondary" data-refresh>Обновить</button></div>
    <form class="portal-create-form" data-person-form>
      <label for="portal-person-name">Добавить человека</label>
      <div class="portal-create-row">
        <input id="portal-person-name" name="display_name" required maxlength="200" placeholder="Имя и фамилия">
        <button type="submit">Добавить</button>
      </div>
    </form>
    <ul class="portal-people" data-people-list aria-live="polite"></ul>
  </section>
  <p class="portal-footnote">Сеанс хранится только в памяти вкладки браузера. Пароль не сохраняется. Для защиты данных используйте личное устройство и выходите из системы после работы.</p>
</section>

<style>
.portal-shell{max-width:860px;margin:3rem auto 5rem}.portal-heading{margin-bottom:2rem}.portal-heading h1{font-size:clamp(2.4rem,6vw,4rem);margin:.3rem 0 1rem}.portal-heading h1 span{color:#c38a4a}.portal-heading>p:last-child{max-width:650px;color:#607080;line-height:1.7}.portal-notice{padding:1rem 1.2rem;border:1px solid #d9e1e8;border-radius:12px;background:#f5f8fa;color:#243747}.portal-notice[data-kind="error"]{border-color:#e2b5b5;background:#fff5f5;color:#8b2d2d}.portal-card{margin:1.25rem 0;padding:clamp(1.2rem,3vw,2rem);border:1px solid #dce3e9;border-radius:16px;background:#fff;box-shadow:0 10px 35px #172b3a0c}.portal-card h2{margin-top:0}.portal-card form{display:grid;gap:.65rem;max-width:520px}.portal-card label{font-weight:600;color:#34495a}.portal-card input{width:100%;padding:.8rem .9rem;border:1px solid #bdc9d3;border-radius:8px;font:inherit}.portal-card button{padding:.8rem 1.2rem;border:0;border-radius:8px;background:#18364a;color:#fff;font:inherit;font-weight:650;cursor:pointer}.portal-card button:disabled{opacity:.55;cursor:wait}.portal-user-row,.portal-section-heading,.portal-create-row{display:flex;align-items:center;justify-content:space-between;gap:1rem}.portal-user-row{padding-bottom:1.2rem;border-bottom:1px solid #e4e9ed}.portal-user-row h2{margin:.2rem 0}.portal-user-row p:last-child{margin:.2rem 0;color:#687989}.portal-secondary{background:#edf2f5!important;color:#21384a!important}.portal-section-heading{margin:1.5rem 0}.portal-section-heading h2{margin:0}.portal-create-form{max-width:none!important;padding:1rem;background:#f6f8fa;border-radius:10px}.portal-create-row input{flex:1;min-width:0}.portal-people{list-style:none;padding:0;margin:1.2rem 0 0}.portal-people li{display:flex;justify-content:space-between;gap:1rem;padding:.9rem .2rem;border-bottom:1px solid #e7ecef}.portal-people strong{overflow-wrap:anywhere}.portal-people small{color:#6a7b88;white-space:nowrap}.portal-empty{color:#748391;padding:1rem 0}.portal-footnote{color:#71808d;font-size:.9rem;line-height:1.6;margin-top:1.5rem}@media(max-width:600px){.portal-user-row,.portal-section-heading,.portal-create-row{align-items:stretch;flex-direction:column}.portal-user-row .portal-secondary,.portal-create-row button{width:100%}.portal-people li{flex-direction:column;gap:.2rem}}
</style>
<script src="{{ '/assets/js/family-portal.js' | relative_url }}" defer></script>
