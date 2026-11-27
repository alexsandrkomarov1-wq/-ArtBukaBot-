---
layout: default
title: Облачная сеть
description: Единый каталог KOMAROVA_CORE и состояние подключения облачных хранилищ.
permalink: /cloud-network/
---
<style>
.cloud-console{--cn-line:rgba(127,174,197,.22);color:#eaf4fb;background:radial-gradient(circle at 85% 5%,rgba(38,121,151,.22),transparent 34%),linear-gradient(145deg,#101d2a,#172c3c 60%,#101b28);border:1px solid var(--cn-line);border-radius:24px;padding:clamp(20px,4vw,42px);margin:8px 0 34px;box-shadow:0 24px 70px rgba(0,0,0,.2)}
.cloud-console *{box-sizing:border-box}.cn-eyebrow{font-size:.72rem;letter-spacing:.18em;color:#8dc8dc;font-weight:700}.cloud-console h1{font-size:clamp(2rem,5vw,3.7rem);line-height:1.04;color:#f5fbff;margin:14px 0}.cloud-console h1 em{color:#8ed8e8;font-style:normal}.cn-lead{max-width:760px;color:#c0d0dc;font-size:1.04rem;line-height:1.7}.cn-state{display:inline-flex;gap:9px;align-items:center;border:1px solid rgba(241,190,103,.4);border-radius:999px;padding:8px 13px;color:#f6d69d;font-size:.78rem;letter-spacing:.06em;margin:12px 0 24px}.cn-dot{width:8px;height:8px;border-radius:50%;background:#e8b65f;box-shadow:0 0 12px #e8b65f}.cn-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:13px;margin:24px 0}.cn-card{border:1px solid var(--cn-line);border-radius:16px;background:rgba(255,255,255,.045);padding:17px;min-height:145px}.cn-card strong{display:block;color:#f1f8fc;font-size:1rem;margin:5px 0 9px}.cn-card p{color:#b5c6d3;font-size:.88rem;line-height:1.55;margin:0}.cn-tag{font-size:.68rem;letter-spacing:.12em;color:#8dc8dc}.cn-tag.pending{color:#f0c77f}.cn-flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:10px;margin:18px 0 26px}.cn-step{border:1px solid var(--cn-line);border-radius:13px;padding:13px;background:rgba(5,14,24,.25)}.cn-step b{display:block;color:#9dd6e4;font-size:.74rem;letter-spacing:.1em;margin-bottom:7px}.cn-step span{font-size:.88rem;color:#dce8ef}.cn-note{border-left:3px solid #78c8d8;padding:12px 16px;background:rgba(91,167,188,.09);color:#d4e4ec;line-height:1.6;margin:22px 0}.cn-links{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}.cn-links a{color:#eafaff;border:1px solid rgba(142,216,232,.4);border-radius:999px;padding:10px 15px;text-decoration:none}.cn-links a:hover{background:rgba(142,216,232,.12)}.cn-foot{color:#91a9b8;font-size:.8rem;margin-top:22px}
</style>
<section class="cloud-console" aria-labelledby="cloud-title">
  <p class="cn-eyebrow">KOMAROVA_CORE / PRIVATE ARCHIVE INFRASTRUCTURE</p>
  <h1 id="cloud-title">Единая <em>облачная сеть</em></h1>
  <p class="cn-lead">Здесь будет единая панель хранения для главного портала и AI MEDIA: один каталог материалов, несколько независимых облачных копий и прозрачный контроль синхронизации.</p>
  <div class="cn-state"><span class="cn-dot"></span> РАЗРАБОТКА ИНТЕРФЕЙСА · ПОДКЛЮЧЕНИЯ ЕЩЁ НЕ АКТИВНЫ</div>
  <div class="cn-grid" aria-label="Состав облачной системы">
    <article class="cn-card"><span class="cn-tag">01 / REGISTRY</span><strong>Единый каталог</strong><p>PERSON-ID, EVENT-ID, PLACE-ID и MATERIAL-ID связывают файлы с семейной историей. Оригиналы и производные версии учитываются отдельно.</p></article>
    <article class="cn-card"><span class="cn-tag">02 / STORAGE</span><strong>Несколько хранилищ</strong><p>Провайдеры подключаются отдельными серверными адаптерами. Сбой одного облака не должен останавливать остальные.</p></article>
    <article class="cn-card"><span class="cn-tag">03 / INTEGRITY</span><strong>Проверка копий</strong><p>Для каждой копии фиксируются удалённый ID, размер, SHA-256 и состояние. Успех подтверждается проверочным чтением.</p></article>
    <article class="cn-card"><span class="cn-tag">04 / SAFETY</span><strong>Защита оригинала</strong><p>Оригинал не перезаписывается. Любая улучшенная или преобразованная версия получает собственный MATERIAL-ID.</p></article>
  </div>
  <h2>Семь облачных хранилищ KOMAROVA_CORE</h2>
  <p class="cn-lead">Все семь провайдеров входят в целевую сеть. Объёмы ниже показывают заявленные бесплатные квоты; фактическая квота зависит от аккаунта и условий провайдера.</p>
  <div class="cn-grid" aria-label="Семь облачных хранилищ и статусы подключения">
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>MEGA</strong><p><b>20 GB</b><br>Ожидает настройки официальной серверной интеграции и авторизации аккаунта.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН · ВРЕМЕННЫЙ ТЕСТ</span><strong>Google Drive</strong><p><b>15 GB</b><br>Есть локальная OAuth-настройка для теста. Постоянным провайдером пока не считается; сайт не подтверждал серверную запись.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>pCloud</strong><p><b>До 10 GB</b><br>Ожидает настройки официальной серверной интеграции и авторизации аккаунта.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>Яндекс Диск</strong><p><b>5 GB</b><br>Ожидает настройки OAuth/API и проверки доступа к файлам.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>OneDrive</strong><p><b>5 GB</b><br>Ожидает настройки Microsoft Graph и авторизации аккаунта.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>Dropbox</strong><p><b>2 GB</b><br>Ожидает настройки официального API и авторизации аккаунта.</p></article>
    <article class="cn-card"><span class="cn-tag pending">НЕ ПОДКЛЮЧЁН</span><strong>TeraBox</strong><p><b>1 TB</b><br>Подключение не планировать до подтверждения поддерживаемого официального API и безопасного серверного доступа.</p></article>
  </div>
  <h2>Как материал проходит систему</h2>
  <div class="cn-flow" aria-label="Путь материала через облачную сеть">
    <div class="cn-step"><b>01 · INTAKE</b><span>Выбор и приём файла</span></div>
    <div class="cn-step"><b>02 · VERIFY</b><span>Проверка и SHA-256</span></div>
    <div class="cn-step"><b>03 · REGISTRY</b><span>MATERIAL-ID и связи</span></div>
    <div class="cn-step"><b>04 · REPLICATE</b><span>Копирование в облака</span></div>
    <div class="cn-step"><b>05 · CONFIRM</b><span>Чтение и сверка копии</span></div>
  </div>
  <div class="cn-note"><strong>Важно:</strong> эта страница показывает архитектуру и этапы разработки, а не имитирует работающую синхронизацию. Сейчас здесь нет подтверждённого статуса записи/чтения облаков. Air Live Drive может быть удобен на Windows как клиент, но не заменяет серверные коннекторы сайта.</div>
  <div class="cn-links">
    <a href="{{ '/media/' | relative_url }}">Открыть AI MEDIA и архив ↗</a>
    <a href="{{ '/status/' | relative_url }}">Проверить состояние проекта ↗</a>
    <a href="https://github.com/alexsandrkomarov1-wq/-ArtBukaBot-/blob/core-backend-foundation/docs/cloud-network-implementation.md">Технический план в GitHub ↗</a>
  </div>
  <p class="cn-foot">Рабочая ветка: core-backend-foundation · Публикация: GitHub Pages после успешной проверки сборки · main и настройки Supabase не затрагиваются.</p>
</section>
