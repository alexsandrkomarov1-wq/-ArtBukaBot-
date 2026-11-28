# KOMAROVA_CORE — настройка независимого ИИ и каналов связи

**Контрольная метка:** `KOMAROVA_CORE`  
**Рабочая ветка:** `core-backend-foundation`  
**Дата проверки документации:** 2026-11-27

## Что подготовлено

- Формат команд и отчётов: `docs/AI_CONTROL_AND_TIME_ACCOUNTING.md`.
- Шаблон настроек без секретов: `config/ai-network.example.json`.
- Зарегистрирован KOMAROVA_CORE и зарезервировано второе изолированное пространство со статусом `unconfigured`.
- Все каналы и модель выключены по умолчанию.
- Секреты передаются только через переменные окружения/защищённое хранилище, никогда не коммитятся.

Это подготовленная конфигурация, не заявление о том, что облачные подключения уже работают.

## Windows shell standard (mandatory)

All Windows commands and troubleshooting instructions for KOMAROVA_CORE must target **PowerShell 7.7.0 (pwsh)**. Do not silently provide Windows PowerShell 5.1 syntax or CMD syntax. Label command blocks as PowerShell 7.7.0, provide complete copy-paste-ready commands, and prefer one-line commands when practical. Avoid multi-line here-strings and split blocks when the user's terminal paste flow has shown that they are being inserted in reverse or leaving the >> continuation prompt. Never include the interactive PS prompt inside a command block. If the prompt is >>, first instruct the user to press Ctrl+C to return to the normal PS> prompt, then provide one complete replacement command. Version check: $PSVersionTable.PSVersion.

## 1. Независимая модель

### Рекомендуемый тестовый вариант

Google Gemini Developer API, модель `gemini-3.1-flash-lite`, OpenAI-compatible endpoint:
`https://generativelanguage.googleapis.com/v1beta/openai/`

Официальная страница Google на дату проверки указывает бесплатный уровень для ряда моделей, включая Flash-Lite. Лимиты и доступность зависят от модели, региона и аккаунта и могут меняться. На бесплатном уровне Google может использовать предоставленный контент для улучшения продуктов.

**Ограничение данных:** до отдельной проверки условий и согласия владельца отправлять только общие технические задания и публичные материалы. Запрещены семейные оригиналы, приватные фотографии, документы, переписка, пароли, токены и персональные данные.

Hugging Face Inference Providers не выбран как гарантированно бесплатный production-провайдер: текущая документация указывает отсутствие ежемесячных кредитов для Free-пользователей. Gemma остаётся допустимой моделью, если появится реально бесплатный и проверенный runtime; наличие весов модели на Hugging Face не означает бесплатный API-инференс.

### Подключение модели

1. Владелец самостоятельно создаёт API key в Google AI Studio.
2. Ключ не отправляется в чат и не записывается в Git.
3. На Windows ключ задаётся в пользовательской переменной окружения `GEMINI_API_KEY`.
4. Включение модели разрешается только после теста нейтрального текста.
5. Платный тариф и автоматические платежи запрещены; при отсутствии бесплатной квоты агент останавливается.

Команда для локального сохранения ключа после его получения:
`[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "ВСТАВИТЬ_КЛЮЧ_ЛОКАЛЬНО", "User")`

Не вводить ключ в переписку ChatGPT, не коммитить его и не присылать скриншоты с ключом.

## 2. Telegram

Telegram Desktop — клиент пользователя. Для интеграции нужен отдельный Telegram Bot API bot.

1. В Telegram открыть `@BotFather`.
2. Выполнить `/newbot`, задать имя и username.
3. Сохранить выданный bot token локально как `TELEGRAM_BOT_TOKEN`.
4. Узнать числовой Telegram user ID владельца и задать `TELEGRAM_ALLOWED_USER_IDS`.
5. Не включать обработку сообщений, пока allowlist не настроен.
6. Для локального первого теста использовать Bot API long polling. Webhook понадобится при переносе на доступный HTTPS backend.
7. Проверить отправку тестового сообщения и получение команды с контрольной меткой `KOMAROVA_CORE`.

Токен бота — секрет полного управления ботом. Его нельзя отправлять в этот чат или коммитить.

## 3. WhatsApp

Ссылка `https://web.whatsapp.com/` — пользовательский веб-клиент, а не API для серверной интеграции.

Для автоматизации нужен официальный WhatsApp Business Platform Cloud API:
- Meta developer app и WhatsApp Business Account;
- тестовый или зарегистрированный номер;
- Phone Number ID и access token;
- публичный HTTPS webhook и verify token;
- подписка на события сообщений.

Переменные: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`.

До появления HTTPS backend и завершения настройки Meta канал остаётся выключенным. Не использовать неофициальную автоматизацию WhatsApp Web, эмуляцию браузера или хранение session cookies.

## 4. Почта

Для Gmail требуется отдельная OAuth-конфигурация и отдельное согласие на Gmail API scopes. Существующий Google Drive OAuth/token не является разрешением на чтение почты и автоматически не переиспользуется.

Первый этап — только чтение входящих сообщений с минимальным scope:
`https://www.googleapis.com/auth/gmail.readonly`

Отправка писем запрещена до отдельного согласия владельца и отдельного scope. OAuth secrets и refresh token хранятся локально вне Git.

Для Microsoft 365 потребуется отдельная регистрация приложения и минимальные Microsoft Graph Mail permissions.

## 5. Единый маршрутизатор

Все каналы вызывают одну функцию нормализации входящего события. Канальные адаптеры не назначают исполнителей напрямую.

Обязательные поля события:
- `control_tag = KOMAROVA_CORE`;
- `source_channel` (web/telegram/whatsapp/email);
- `source_message_id`, `received_at_utc`;
- `sender_id`, результат проверки allowlist/permissions;
- `project_id`, `task_id`, `message_type`;
- `payload_ref`, `privacy_classification`, `status`.

Правила: проверить отправителя; определить проект только по явной привязке; присвоить task ID и ключ идемпотентности; записать команду в очередь; передать координатору; проверить отчёт; только затем отвечать в исходный канал.

## 6. Командная шина и постоянное соединение

GitHub Pages — статический сайт, он не исполняет серверные фоновые процессы. Локальный JSONL spool пригоден для очереди на одном ПК, но сам по себе не является постоянно доступной облачной шиной.

Для постоянной шины необходим HTTPS backend с аутентификацией workers/channels, изоляцией по project_id, append-only командами/отчётами/событиями/time records, идемпотентностью, ограничением частоты и резервным копированием.

Новый хостинг или изменение существующего Supabase не выполняется без отдельного подтверждения владельца. Публичный GitHub-репозиторий не используется как очередь приватных команд.

ChatGPT в обычном чате не имеет постоянного фонового сокета к компьютеру. Для выдачи команд вне активного диалога потребуется отдельный утверждённый интеграционный endpoint/connector.

## 7. Статусы

| Компонент | Статус | Условие включения |
|---|---|---|
| Независимая модель | `CONFIGURED_DISABLED` | Локальный API key и нейтральный тест |
| Telegram | `WAITING_FOR_BOT_TOKEN` | BotFather token + owner user ID |
| WhatsApp | `WAITING_FOR_META_SETUP` | Meta Cloud API credentials + HTTPS webhook |
| Gmail | `WAITING_FOR_OAUTH_CONSENT` | Отдельный Gmail OAuth readonly scope |
| Web inbox | `LOCAL_ONLY` | Backend/queue adapter |
| Local command queue | `SPECIFIED_LOCAL_ONLY` | Worker и тесты |
| Remote command bus | `BLOCKED_HOSTING_DECISION` | Утверждённый HTTPS backend |
| PowerShell worker | `TEST_PENDING` | Успешный self-test и CI |

## 8. Порядок включения

1. Проверить PowerShell CLI self-test и CI.
2. Запустить независимую модель на обезличенном тесте.
3. Подключить Telegram bot с allowlist, только текстовые тесты.
4. Добавить Gmail readonly OAuth, не включая отправку.
5. Подготовить Meta Cloud API и HTTPS webhook.
6. Утвердить backend для постоянной шины; не использовать текущий Supabase без отдельного разрешения.
7. Подключить локальный worker к командам с read-only режимом.
8. Проверить раздельные журналы времени, проектов и исполнителей.
9. Включать специализированные роли по одной после end-to-end тестов.

Каждый канал считается рабочим только после end-to-end теста с сохранённым доказательством.
