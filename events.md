---
layout: default
title: События и хронология
permalink: /events/
description: Раздел событий и семейной хронологии KOMAROVA_CORE
---
<section class="page-heading events-heading">
  <p class="eyebrow">KOMAROVA_CORE · ВРЕМЯ И ПАМЯТЬ</p>
  <h1>События и <em>хронология.</em></h1>
  <p class="lead">Значимые даты, встречи, семейные события и исторический контекст. Здесь должна собираться проверяемая история, связанная с людьми, местами и архивными материалами.</p>
</section>

<section class="events-status" aria-live="polite">
  <span class="events-status-label">СОСТОЯНИЕ РАЗДЕЛА</span>
  <h2>Хронология открывается, но реестр событий ещё не подключён.</h2>
  <p>В текущей версии KOMAROVA_CORE пока нет подтверждённого API событий и таблицы главного реестра для EVENT-ID. Поэтому здесь не показываются вымышленные записи и не создаются локальные события, которые можно ошибочно принять за семейные данные.</p>
</section>

<section class="events-empty">
  <div class="events-empty-mark" aria-hidden="true">◷</div>
  <div>
    <p class="eyebrow">ЛЕНТА СОБЫТИЙ</p>
    <h2>Записи пока не загружены</h2>
    <p>После реализации реестра здесь будут отображаться события с датой или периодом, названием, описанием, участниками (PERSON-ID), местом (PLACE-ID), источниками и связанными фотографиями или документами.</p>
  </div>
</section>

<section class="events-structure" aria-label="Структура будущей хронологии">
  <h2>Что будет храниться в записи события</h2>
  <ul>
    <li><strong>EVENT-ID</strong><span>Постоянный идентификатор события.</span></li>
    <li><strong>Дата или период</strong><span>Точная дата, приблизительная дата либо временной интервал с указанием точности.</span></li>
    <li><strong>Участники</strong><span>Связи с существующими PERSON-ID, без создания дубликатов людей.</span></li>
    <li><strong>Место</strong><span>Связь с PLACE-ID, если место известно.</span></li>
    <li><strong>Источники и материалы</strong><span>Документы, фотографии, ссылки и отметка достоверности сведений.</span></li>
    <li><strong>История изменений</strong><span>Кто и когда добавил или исправил запись.</span></li>
  </ul>
</section>

<nav class="events-actions" aria-label="Переходы по семейному архиву">
  <a class="primary-link" href="{{ '/family-board/' | relative_url }}">Семейная доска и карта <span aria-hidden="true">↗</span></a>
  <a class="outline-link" href="{{ '/media/' | relative_url }}">Фотографии и документы <span aria-hidden="true">↗</span></a>
  <a class="text-link" href="{{ '/' | relative_url }}#archive-directions">Вернуться к направлениям архива ↑</a>
</nav>
