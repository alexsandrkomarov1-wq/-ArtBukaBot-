# KOMAROVA_CORE — снимок состояния проекта

**Дата снимка:** 2026-11-27  
**Рабочая ветка:** `core-backend-foundation`  
**Запрет:** `main` не изменять.

## Подтверждённая идентичность
- GitHub: `alexsandrkomarov1-wq/-ArtBukaBot-`
- Публичная Pages-страница: https://alexsandrkomarov1-wq.github.io/-ArtBukaBot-/
- Локальная папка пользователя ранее указана как `C:\Users\KomarovA\KOMAROVA_CORE`; актуальный размер на этом компьютере пока не измерен.

## Структура репозитория (верхний уровень, наблюдалась через GitHub API)
`.github/`, `_data/`, `_layouts/`, `assets/`, `backend/`, `config/`, `desktop/`, `docs/`, `neon/`, `notebooks/`, `ops/`, `scripts/`, `tools/`, а также файлы сайта и конфигурации в корне. Существующие каталоги не перемещать без утверждения владельца.

## Постоянная память
- `project-memory/` создана в рабочей ветке.
- `PROJECT_STATE.md` — актуальный снимок.
- `DECISIONS.md` — журнал решений.
- Правила: `docs/PROJECT_FOLDER_AND_MEMORY_POLICY.md`.

## Размер: пока неполные данные
- GitHub API на 2026-11-27 вернул размер репозитория **880 KB** (приблизительная серверная оценка метаданных GitHub).
- Это НЕ размер локальной папки, не размер всех файлов пользователя, не размер облачных оригиналов и не объём резервных копий.
- Точный локальный размер `C:\Users\KomarovA\KOMAROVA_CORE` ещё не измерен.
- Размеры облачных хранилищ и медиа-архива не подтверждены.
- Не объявлять общий размер проекта известным, пока эти источники не измерены раздельно.

## Текущие ограничения
- Google Drive — временное тестовое подключение, не утверждённый постоянный провайдер.
- Не менять существующий Supabase без отдельного разрешения.
- GitHub Pages — публичный интерфейс, не частное файловое хранилище.
- Оригиналы неизменяемы; обработанные копии — отдельные материалы.
- Второй проект пока не идентифицирован; его память/папку не создавать до получения точного имени и пути.

## Последние архитектурные направления
- Общая для двух проектов визуальная концепция 3D-Древа памяти описана в `docs/DUAL_PROJECT_3D_TREE_ARCHITECTURE.md`.
- Реализация 3D ожидает успешной проверки текущего CI baseline.
- Задача AG-020 имеет статус PROPOSED до начала реализации.


## Инвентаризация существующих проектов и хранилищ — 2026-11-28

### Supabase: уже существуют ровно два проекта в организации
- `KOMAROVA_CORE` — ref `bcotusztvddzbnwefnrq`, регион `eu-west-1`, статус `ACTIVE_HEALTHY`; назначение: backend семейного архива.
- `alexsandrkomarov1-wq's Project` — ref `dkwhhnzuqapqogknldyd`, регион `eu-west-1`, статус `ACTIVE_HEALTHY`; существующий второй проект, не создавать вместо него новый.
- В обоих проектах список таблиц схемы `public` пуст, миграций нет, 0 Storage buckets и 0 Auth users (подтверждено read-only SQL 2026-11-28).
- Запрещено создавать третий проект или удалять/переименовывать существующие. Панели dashboard открывались через браузерный помощник, но он не был авторизован в Supabase; read-only Supabase connector подтвердил метаданные проектов.

### GitHub и Google Drive: найденные существующие ресурсы
- В подключённом GitHub-аккаунте найден один репозиторий: `alexsandrkomarov1-wq/-ArtBukaBot-`; рабочая ветка `core-backend-foundation`. Второй GitHub-репозиторий в доступном списке не найден.
- В существующем Google Drive найден каталог `Мой диск / Colab Notebooks` (https://drive.google.com/drive/folders/1ANX9kXP8RVpGsvcEdMTH4aEj2Dkr87Ad) с двумя файлами Google Colab: `Untitled Google Colab` (367 КБ) и `OMIA Урал / OMIA Ural Google Colab` (278 КБ).
- Отдельная папка `KOMAROVA_CORE` в Google Drive и файл `Untitled1.ipynb` не найдены.
- `OMIA Урал` — кандидат на идентичность второго прикладного проекта, но его назначение пока не подтверждено владельцем. До подтверждения ничего в этих Colab-файлах не менять.
- Файл `Komarov.pdf` (34,4 МБ) обнаружен в корне Drive; не открывался и не изменялся.

### Синхронизация папок
- Онлайн-рабочая копия KOMAROVA_CORE обновляется только в `core-backend-foundation`.
- Локальная папка `C:\\Users\\KomarovA\\KOMAROVA_CORE` ранее измерена владельцем: 15 файлов / 0,16 МБ. Полная синхронизация с текущей веткой не подтверждена; локальные файлы не перезаписывались.
- Google Drive не синхронизировался и не изменялся: в нём нет одноимённой папки проекта. Существующие Colab-файлы оставлены нетронутыми.
- Не создавать дубликаты папок/репозиториев/ноутбуков. Перед синхронизацией второго проекта требуется однозначно привязать его к одному из существующих Colab-файлов или иному уже существующему ресурсу.


### Последняя проверка интерфейса и CI — 2026-11-28
- `/generations/`: TinyFish подтвердил отсутствие полей API, логина, пароля и кнопки подключения.
- `/media/`: TinyFish подтвердил отсутствие видимых Project URL/publishable key/формы подключения; email и пароль остались только в «Папка участника». Секретный service_role key не добавлен в публичный код. Publishable key остаётся в JS как публичный ключ браузерного клиента.
- Статус API: отвечает. Это не означает, что физическое хранилище готово: приватный bucket и таблица архива ещё не созданы.
- Кодовые проверки на commit `c34e5916830ae0289fd7340493d93c3adf377fc2`: Pages build/deploy success (run `46085362926`), backend tests success (run `46085362957`), PowerShell self-test success (run `46085363013`).
- Старые CI ошибки были связаны с устаревшими тестовыми контрактами, ожидавшими уже удалённую форму Supabase; контракты обновлены и прошли.
- Изменения выполнялись только в `core-backend-foundation`; `main` не затронута.


## Archive UI verification — 2026-11-28

- Published media page: `https://alexsandrkomarov1-wq.github.io/-ArtBukaBot-/media/`.
- Physical storage panel simplified to `Семья → Фамилия → Поколение → Участник → Год`; removed Project URL/key inputs, connection button, manual SQL link and setup instructions.
- Password field remains only in the participant folder section.
- Page now truthfully reports that the existing KOMAROVA_CORE Supabase project responds, but the private Storage bucket and archive registry table do not yet exist; uploads are unavailable.
- Live page was inspected after commit `e812376a6ebb6a73a03505f92a15665fbbe7d6c5` via TinyFish run `6a4431e7-edd7-42a4-8ee1-d075f627e31f`.
- CI for code commit `e812376a6ebb6a73a03505f92a15665fbbe7d6c5`: Pages build #490 success, backend tests #564 success, agent self-test #80 success. A docs-only follow-up commit `fe79a6ca7cafaf26d7ee7ec4b0e4ef74d9510a96` records this work.
- No Supabase schema or Storage changes were made. The prepared SQL remains unapplied pending explicit owner approval. No additional Supabase project, GitHub repository, or Drive folder was created.
