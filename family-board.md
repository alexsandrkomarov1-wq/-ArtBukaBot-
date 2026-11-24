---
layout: default
title: Семейная интерактивная доска объявлений + карта семейных открытий
description: Демонстрационный интерфейс семейной доски и карты посещённых и желаемых мест KOMAROVA_CORE.
permalink: /family-board/
---
<section class="page-heading family-board-heading">
  <p class="eyebrow">KOMAROVA_CORE · СЕМЕЙНОЕ ПРОСТРАНСТВО</p>
  <h1>Семейная интерактивная доска объявлений <span>+</span> карта семейных открытий</h1>
  <p class="lead">Объявления, идеи совместных прогулок, места, где уже побывали разные участники семьи, и открытия, которые ещё впереди.</p>
</section>

<section class="fb-demo-notice" aria-label="Статус демонстрационной версии">
  <strong>Демонстрационный режим</strong>
  <p>Интерфейс уже интерактивен. Созданные здесь объявления и отметки мест сохраняются только в этом браузере на этом устройстве. Они не отправляются на сервер, не синхронизируются с семьёй и не являются записями главного реестра KOMAROVA_CORE. Не вводите личные сведения.</p>
</section>

<div class="fb-tabs" role="tablist" aria-label="Разделы семейного пространства">
  <button class="fb-tab is-active" type="button" role="tab" aria-selected="true" aria-controls="fb-board-panel" data-fb-tab="board">Доска объявлений</button>
  <button class="fb-tab" type="button" role="tab" aria-selected="false" aria-controls="fb-map-panel" data-fb-tab="map">Карта семейных открытий</button>
</div>

<section id="fb-board-panel" class="fb-panel" data-fb-panel="board">
  <div class="fb-section-head">
    <div><p class="eyebrow">СЕМЕЙНАЯ ЛЕНТА</p><h2>Что происходит в семье</h2><p>Предложения, вопросы, приглашения и заметки. В реальной версии записи будут связаны с PERSON-ID, EVENT-ID и PLACE-ID.</p></div>
    <span class="fb-counter" data-fb-post-count>0 записей</span>
  </div>
  <form class="fb-compose" data-fb-compose>
    <label for="fb-post-title">Заголовок объявления</label>
    <input id="fb-post-title" name="title" maxlength="100" placeholder="Например: прогулка в воскресенье" required>
    <label for="fb-post-body">Текст</label>
    <textarea id="fb-post-body" name="body" rows="3" maxlength="1200" placeholder="Расскажите, что предлагаете или хотите обсудить…" required></textarea>
    <div class="fb-compose-footer">
      <label class="fb-select-label" for="fb-post-kind">Тип записи
        <select id="fb-post-kind" name="kind">
          <option value="Объявление">Объявление</option>
          <option value="Предложение">Предложение</option>
          <option value="Вопрос">Вопрос</option>
          <option value="Приглашение">Приглашение</option>
          <option value="Рекомендация">Рекомендация</option>
        </select>
      </label>
      <button class="fb-button fb-button-primary" type="submit">Опубликовать в демо</button>
    </div>
    <p class="fb-form-note">Автор в демонстрации обозначается как «Участник 1». Публикация доступна только в локальном демо.</p>
  </form>
  <div class="fb-feed-tools">
    <label for="fb-filter">Показать
      <select id="fb-filter" data-fb-filter>
        <option value="all">Все записи</option>
        <option value="Предложение">Предложения</option>
        <option value="Вопрос">Вопросы</option>
        <option value="Приглашение">Приглашения</option>
        <option value="Объявление">Объявления</option>
        <option value="Рекомендация">Рекомендации</option>
      </select>
    </label>
    <span data-fb-storage-state>Локальное сохранение включено</span>
  </div>
  <div class="fb-feed" data-fb-feed aria-live="polite"></div>
</section>

<section id="fb-map-panel" class="fb-panel" data-fb-panel="map" hidden>
  <div class="fb-section-head">
    <div><p class="eyebrow">СЕМЕЙНАЯ ГЕОГРАФИЯ</p><h2>Где были и куда отправимся</h2><p>Посещение учитывается отдельно для каждого человека. Одно место может быть знакомо одному участнику и оставаться новым для другого.</p></div>
    <span class="fb-counter">PLACE-ID · демо</span>
  </div>
  <div class="fb-map-controls">
    <form class="fb-city-search" data-fb-city-search>
      <label for="fb-city">Город или район</label>
      <div class="fb-inline-controls"><input id="fb-city" name="city" value="Санкт-Петербург" placeholder="Введите город" required><button class="fb-button" type="submit">Найти город</button></div>
    </form>
    <label for="fb-person">Смотреть отметки участника
      <select id="fb-person" data-fb-person>
        <option value="PERSON-DEMO-01">Участник 1 · демонстрация</option>
        <option value="PERSON-DEMO-02">Участник 2 · демонстрация</option>
      </select>
    </label>
    <label for="fb-radius">Радиус поиска
      <select id="fb-radius" data-fb-radius>
        <option value="1500">1,5 км</option><option value="3000" selected>3 км</option><option value="5000">5 км</option><option value="10000">10 км</option>
      </select>
    </label>
  </div>
  <div class="fb-map-legend" aria-label="Обозначения карты">
    <span><i class="fb-dot fb-dot-visited"></i>Были</span>
    <span><i class="fb-dot fb-dot-wishlist"></i>Хотим посетить</span>
    <span><i class="fb-dot fb-dot-planned"></i>Предложено / запланировано</span>
    <span><i class="fb-dot fb-dot-new"></i>Ещё не отмечено</span>
  </div>
  <div class="fb-map-layout">
    <div id="fb-map" class="fb-map" role="application" aria-label="Интерактивная карта семейных мест"></div>
    <aside class="fb-place-side">
      <div class="fb-place-side-head"><div><span class="fb-kicker">МЕСТА В ОБЛАСТИ КАРТЫ</span><h3>Список открытий</h3></div><button type="button" class="fb-icon-button" data-fb-refresh aria-label="Найти места рядом" title="Найти места рядом">↻</button></div>
      <p class="fb-side-help" data-fb-map-status>Показаны демонстрационные места Санкт-Петербурга. Нажмите на маркер или выберите место из списка.</p>
      <div class="fb-place-list" data-fb-place-list></div>
    </aside>
  </div>
  <div class="fb-place-detail" data-fb-place-detail aria-live="polite">
    <p class="fb-kicker">КАРТОЧКА МЕСТА</p><h3>Выберите точку на карте</h3><p>Здесь появятся заметки, история посещений и действия для выбранного места.</p>
  </div>
  <p class="fb-map-footnote">Карта и поиск используют OpenStreetMap. Данные о местах загружаются по запросу из открытого OpenStreetMap Overpass API; доступность зависит от внешнего сервиса. Демонстрационные отметки не подтверждают реальные посещения. Закрытые адреса и постоянная геолокация не используются.</p>
</section>

<section class="fb-next-steps">
  <div><p class="eyebrow">СЛЕДУЮЩИЙ ЭТАП</p><h2>От демонстрации к семейной системе</h2><p>После подключения защищённого backend демо-механика будет заменена API KOMAROVA_CORE: авторизация, реальные PERSON-ID, POST-ID и PLACE-ID, права доступа, журнал изменений, резервирование и синхронизация устройств.</p></div>
  <a href="{{ '/status/' | relative_url }}">Состояние реализации ↗</a>
</section>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" defer></script>
<script src="{{ '/assets/js/family-board-map.js' | relative_url }}?v={{ site.time | date: '%Y%m%d%H%M' }}" defer></script>
