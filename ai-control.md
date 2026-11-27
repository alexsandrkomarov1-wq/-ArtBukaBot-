---
layout: default
title: Центр управления ИИ
description: Единая панель управления ИИ-исполнителями и проверяемыми статусами проектов.
permalink: /ai-control/
---
<style>
.ai-control{color:#eaf4fb;background:linear-gradient(145deg,#101d2a,#172c3c 60%,#101b28);border:1px solid rgba(127,174,197,.22);border-radius:24px;padding:clamp(20px,4vw,42px);margin:8px 0 34px}
.ai-control *{box-sizing:border-box}.ai-control h1{font-size:clamp(2rem,5vw,3.5rem);color:#f5fbff}.ai-control h1 em{color:#8ed8e8;font-style:normal}.ac-lead{max-width:850px;color:#c0d0dc;line-height:1.7}.ac-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:13px;margin:20px 0}.ac-card{border:1px solid rgba(127,174,197,.22);border-radius:16px;background:rgba(255,255,255,.045);padding:17px}.ac-card h3{color:#f1f8fc}.ac-card p,.ac-card li{color:#bdced9;font-size:.9rem;line-height:1.6}.ac-tag{font-size:.67rem;letter-spacing:.12em;color:#8dc8dc}.ac-status{display:inline-block;border:1px solid rgba(241,190,103,.4);border-radius:999px;padding:5px 9px;color:#f2d18e;font-size:.68rem}.ac-off{border-color:rgba(220,130,130,.4);color:#efb0b0}.ac-ok{border-color:rgba(125,190,160,.4);color:#a9d8bd}.ac-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:18px 0}.ac-step{border:1px solid rgba(127,174,197,.22);border-radius:13px;padding:14px;background:rgba(5,14,24,.25)}.ac-step b{display:block;color:#9dd6e4;font-size:.74rem;margin-bottom:7px}.ac-step span{font-size:.88rem;color:#dce8ef}.ac-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}.ac-links a{color:#eafaff;border:1px solid rgba(142,216,232,.4);border-radius:999px;padding:9px 13px;text-decoration:none}.ac-note{border-left:3px solid #78c8d8;padding:12px 16px;background:rgba(91,167,188,.09);color:#d4e4ec;line-height:1.6;margin:20px 0}.ac-table{width:100%;border-collapse:collapse;margin:15px 0;font-size:.88rem}.ac-table th,.ac-table td{border-bottom:1px solid rgba(127,174,197,.22);padding:10px;text-align:left;vertical-align:top}.ac-table th{color:#9ed7e5}.ac-table td{color:#c6d5df}
</style>
<section class="ai-control" aria-labelledby="ac-title">
<p class="ac-tag">KOMAROVA_CORE / SHARED AI GOVERNANCE</p>
<h1 id="ac-title">Центр <em>управления ИИ</em></h1>
<p class="ac-lead">Единая модель управления для двух проектов. Владелец задаёт цели и разрешения; ChatGPT координирует и проверяет; независимые модели и локальные исполнители выполняют только назначенные задачи в пределах своих полномочий.</p>
<p><span class="ac-status">СПЕЦИФИКАЦИЯ ЕСТЬ</span> <span class="ac-status ac-off">ПОСТОЯННАЯ ШИНА НЕ ПОДКЛЮЧЕНА</span></p>
<h2>Иерархия управления</h2>
<div class="ac-flow">
<div class="ac-step"><b>01 · ВЛАДЕЛЕЦ</b><strong>Ты</strong><span>Высший уровень решений. Утверждаешь цели, доступы и рискованные действия.</span></div>
<div class="ac-step"><b>02 · ГЛАВНЫЙ КООРДИНАТОР</b><strong>ChatGPT</strong><span>Архитектура, распределение поручений, проверка доказательств и результатов.</span></div>
<div class="ac-step"><b>03 · НЕЗАВИСИМАЯ МОДЕЛЬ</b><strong>Подчинённый ИИ</strong><span>Работает по конкретному заданию и не меняет собственные права.</span></div>
<div class="ac-step"><b>04 · ИСПОЛНИТЕЛЬ</b><strong>PowerShell Worker / специализированные агенты</strong><span>Выполняют разрешённые команды и возвращают отчёты.</span></div>
</div>
<h2>Подтверждённое состояние компонентов</h2>
<div class="ac-grid">
<article class="ac-card"><span class="ac-tag">CONTROL / CHATGPT</span><h3>Главный координатор</h3><span class="ac-status ac-ok">ТЕКУЩАЯ СЕССИЯ ДОСТУПНА</span><p>Координация возможна в текущем диалоге. Постоянный фоновый канал ChatGPT к компьютеру не подключён.</p></article>
<article class="ac-card"><span class="ac-tag">MODEL / GEMINI CANDIDATE</span><h3>Независимая модель</h3><span class="ac-status ac-off">НЕ ПОДКЛЮЧЕНА</span><p>Gemini Flash-Lite описана как кандидат для отдельного теста. API-ключ не настроен; частные семейные материалы не передаются.</p></article>
<article class="ac-card"><span class="ac-tag">LOCAL / POWERSHELL</span><h3>Локальный исполнитель</h3><span class="ac-status">ЛОКАЛЬНЫЙ ТЕСТ ОЖИДАЕТСЯ</span><p>Скрипты присутствуют в рабочей ветке. Архив распакован во временную папку Windows; тестовый запуск ещё не подтверждён.</p></article>
<article class="ac-card"><span class="ac-tag">ROUTER / CHANNELS</span><h3>Единый маршрутизатор</h3><span class="ac-status ac-off">НЕ ПОДКЛЮЧЁН</span><p>Telegram Bot API, WhatsApp Cloud API и Gmail OAuth описаны. Рабочие авторизации и сквозные проверки отсутствуют.</p></article>
<article class="ac-card"><span class="ac-tag">COMMAND BUS</span><h3>Командная шина</h3><span class="ac-status ac-off">REMOTE BRIDGE ОТСУТСТВУЕТ</span><p>Формат очередей и локального журнала описан. Постоянная защищённая удалённая шина не развёрнута.</p></article>
<article class="ac-card"><span class="ac-tag">AUDIT / TIME</span><h3>Журналы и хронометраж</h3><span class="ac-status">СХЕМА ОПИСАНА</span><p>Предусмотрены отдельные записи владельца, агента, модели и CI, UTC + Europe/Amsterdam, доказательства и append-only журнал. Полная телеметрия не подключена.</p></article>
</div>
<h2>Два изолированных проекта · единый стандарт</h2>
<table class="ac-table"><thead><tr><th>Рабочее пространство</th><th>Регистрация</th><th>Правило</th></tr></thead><tbody>
<tr><td><strong>KOMAROVA_CORE</strong><br>Семейный архив</td><td><span class="ac-status ac-ok">ЗАРЕГИСТРИРОВАН</span></td><td>Рабочая ветка core-backend-foundation. Семейные оригиналы, секреты и облачные настройки защищены отдельными ограничениями.</td></tr>
<tr><td><strong>Проект №2</strong></td><td><span class="ac-status ac-off">НЕ ИДЕНТИФИЦИРОВАН</span></td><td>Имя, репозиторий и рабочая папка пока не внесены в реестр. Структура будет такой же, но данные и журналы останутся отдельными.</td></tr>
</tbody></table>
<h2>Очередь задач и отчётность</h2>
<div class="ac-grid">
<article class="ac-card"><span class="ac-tag">TASK BACKLOG</span><h3>Поручения</h3><p>Приоритеты, зависимости, READY / BLOCKED / APPROVAL_REQUIRED и критерии приёмки.</p><div class="ac-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/AGENT_TASK_BACKLOG.md">Открыть очередь задач ↗</a></div></article>
<article class="ac-card"><span class="ac-tag">CHANGE REGISTER</span><h3>Изменения и доказательства</h3><p>Исполнитель, задача, время, изменённые файлы, тесты и источник подтверждения.</p><div class="ac-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/AGENT_CHANGE_REGISTER.md">Открыть журнал изменений ↗</a></div></article>
<article class="ac-card"><span class="ac-tag">OPERATING CHARTER</span><h3>Полномочия и запреты</h3><p>Исполнитель не меняет регламент, не расширяет права, не затрагивает main и оригиналы.</p><div class="ac-links"><a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/AGENT_OPERATING_CHARTER.md">Открыть регламент ↗</a></div></article>
</div>
<div class="ac-note"><strong>Как читать статусы:</strong> «описано» означает наличие документа; «присутствует в ветке» означает наличие исходного файла; «подключено» требует успешной авторизации или соединения; «проверено» требует фактического теста и сохранённого доказательства. Цвет и надпись не заменяют проверку.</div>
<div class="ac-links"><a href="{{ '/cloud-network/' | relative_url }}">Облачная сеть ↗</a><a href="{{ '/status/' | relative_url }}">Состояние проекта ↗</a><a href="{{ '/' | relative_url }}">Главная KOMAROVA_CORE ↗</a></div>
<p class="ac-tag">Протокол управления: v1.0 · Europe/Amsterdam · Это снимок подтверждённых сведений, не потоковая телеметрия.</p>
</section>
