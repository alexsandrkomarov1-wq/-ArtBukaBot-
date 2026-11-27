[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("init","start","pause","resume","stop","recover","event","status","ai","help")]
    [string]$Command = "help",

    [string]$Task,
    [string]$Category = "development",
    [string]$Description,
    [string]$Source = "manual",
    [string]$EventType = "project_note",
    [string]$Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# The script lives in <project>\tools. All logs remain local and are not uploaded.
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataRoot = Join-Path $ProjectRoot "data\project_time"
$SessionFile = Join-Path $DataRoot "active_session.json"
$EventsFile = Join-Path $DataRoot "events.jsonl"
$SessionsFile = Join-Path $DataRoot "sessions.jsonl"
$TimeZoneId = "Europe/Amsterdam"

function Ensure-Store {
    if (-not (Test-Path -LiteralPath $DataRoot)) {
        New-Item -ItemType Directory -Path $DataRoot -Force | Out-Null
    }
    foreach ($file in @($EventsFile, $SessionsFile)) {
        if (-not (Test-Path -LiteralPath $file)) {
            New-Item -ItemType File -Path $file -Force | Out-Null
        }
    }
}

function Get-UtcNow {
    return [DateTimeOffset]::UtcNow
}

function Format-LocalTime([DateTimeOffset]$Value) {
    try {
        $zone = [TimeZoneInfo]::FindSystemTimeZoneById($TimeZoneId)
        return [TimeZoneInfo]::ConvertTime($Value, $zone).ToString("yyyy-MM-dd HH:mm:ss zzz")
    }
    catch {
        return $Value.ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss zzz")
    }
}

function Write-JsonLine([string]$Path, [object]$Value) {
    $line = $Value | ConvertTo-Json -Depth 12 -Compress
    Add-Content -LiteralPath $Path -Value $line -Encoding utf8
}

function Write-ProjectEvent(
    [string]$Type,
    [string]$Text,
    [string]$EventSource = "manual",
    [string]$SessionId = ""
) {
    Ensure-Store
    $now = Get-UtcNow
    $entry = [ordered]@{
        event_id = [guid]::NewGuid().ToString()
        timestamp_utc = $now.ToString("o")
        timestamp_local = Format-LocalTime $now
        timezone = $TimeZoneId
        event_type = $Type
        description = $Text
        source = $EventSource
        session_id = $SessionId
        machine = $env:COMPUTERNAME
        user = $env:USERNAME
    }
    Write-JsonLine -Path $EventsFile -Value $entry
}

function Read-Session {
    if (-not (Test-Path -LiteralPath $SessionFile)) { return $null }
    return Get-Content -LiteralPath $SessionFile -Raw -Encoding utf8 | ConvertFrom-Json
}

function Save-Session([object]$Session) {
    $temp = "$SessionFile.tmp"
    $Session | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $temp -Encoding utf8
    Move-Item -LiteralPath $temp -Destination $SessionFile -Force
}

function Get-ActiveSeconds([object]$Session) {
    $seconds = [double]$Session.accumulated_active_seconds
    if (-not [bool]$Session.is_paused -and $Session.resumed_at_utc) {
        $resumed = [DateTimeOffset]::Parse([string]$Session.resumed_at_utc)
        $seconds += ((Get-UtcNow) - $resumed).TotalSeconds
    }
    return [long][Math]::Max(0, [Math]::Floor($seconds))
}

function Format-Duration([long]$Seconds) {
    [long]$hours = [Math]::Floor($Seconds / 3600)
    [long]$minutes = [Math]::Floor(($Seconds % 3600) / 60)
    [long]$rest = $Seconds % 60
    return ("{0:D2}:{1:D2}:{2:D2}" -f $hours, $minutes, $rest)
}

function Require-Session {
    $session = Read-Session
    if ($null -eq $session) {
        throw "Нет открытой сессии. Сначала выполните команду start."
    }
    return $session
}

switch ($Command) {
    "help" {
        @"
KOMAROVA_CORE command line
--------------------------
init                         создать локальную структуру журнала
start -Task "описание"       начать активную рабочую сессию
pause                        поставить сессию на паузу
resume                       продолжить сессию
stop                         закрыть сессию и записать итог
recover                      аварийно приостановить без учёта неизвестного времени
event -Description "..."     записать событие проекта
status                       показать текущую сессию и накопленные часы
ai -Prompt "..."             обратиться к отдельно настроенному ИИ

Неизвестное время после сбоя не засчитывается автоматически.
События и сессии хранятся локально в data\project_time.
ИИ не нужен для работы журнала и не получает журнал автоматически.
"@
    }

    "init" {
        Ensure-Store
        Write-ProjectEvent -Type "logger_initialized" -Text "Локальный журнал KOMAROVA_CORE инициализирован." -EventSource "powershell"
        Write-Host "Журнал создан: $DataRoot" -ForegroundColor Green
    }

    "start" {
        Ensure-Store
        if ([string]::IsNullOrWhiteSpace($Task)) { throw "Укажите задачу: start -Task 'Описание работы'." }
        if ($null -ne (Read-Session)) { throw "Уже существует открытая или приостановленная сессия. Выполните status, resume, stop или recover." }
        $now = Get-UtcNow
        $session = [ordered]@{
            session_id = [guid]::NewGuid().ToString()
            task = $Task
            category = $Category
            started_at_utc = $now.ToString("o")
            resumed_at_utc = $now.ToString("o")
            ended_at_utc = $null
            accumulated_active_seconds = 0
            is_paused = $false
            interrupted = $false
            timezone = $TimeZoneId
        }
        Save-Session $session
        Write-ProjectEvent -Type "work_session_started" -Text $Task -EventSource "powershell" -SessionId $session.session_id
        Write-Host "Сессия начата: $($session.session_id)" -ForegroundColor Green
        Write-Host "Задача: $Task"
    }

    "pause" {
        $session = Require-Session
        if ([bool]$session.is_paused) { throw "Сессия уже приостановлена." }
        $now = Get-UtcNow
        $resumed = [DateTimeOffset]::Parse([string]$session.resumed_at_utc)
        $session.accumulated_active_seconds = [long]$session.accumulated_active_seconds + [long][Math]::Floor(($now - $resumed).TotalSeconds)
        $session.is_paused = $true
        $session.resumed_at_utc = $null
        Save-Session $session
        Write-ProjectEvent -Type "work_session_paused" -Text "Рабочая сессия поставлена на паузу." -EventSource "powershell" -SessionId $session.session_id
        Write-Host ("Пауза. Учтено: " + (Format-Duration ([long]$session.accumulated_active_seconds))) -ForegroundColor Yellow
    }

    "resume" {
        $session = Require-Session
        if (-not [bool]$session.is_paused) { throw "Сессия уже активна." }
        $now = Get-UtcNow
        $session.is_paused = $false
        $session.resumed_at_utc = $now.ToString("o")
        Save-Session $session
        Write-ProjectEvent -Type "work_session_resumed" -Text "Рабочая сессия продолжена." -EventSource "powershell" -SessionId $session.session_id
        Write-Host "Сессия продолжена." -ForegroundColor Green
    }

    "stop" {
        $session = Require-Session
        $now = Get-UtcNow
        if (-not [bool]$session.is_paused -and $session.resumed_at_utc) {
            $resumed = [DateTimeOffset]::Parse([string]$session.resumed_at_utc)
            $session.accumulated_active_seconds = [long]$session.accumulated_active_seconds + [long][Math]::Floor(($now - $resumed).TotalSeconds)
        }
        $session.ended_at_utc = $now.ToString("o")
        $session.resumed_at_utc = $null
        $session.is_paused = $true
        Add-Member -InputObject $session -NotePropertyName duration_hms -NotePropertyValue (Format-Duration ([long]$session.accumulated_active_seconds)) -Force
        Add-Member -InputObject $session -NotePropertyName status -NotePropertyValue "closed" -Force

        $alreadySaved = $false
        if (Test-Path -LiteralPath $SessionsFile) {
            $alreadySaved = [bool](Select-String -LiteralPath $SessionsFile -SimpleMatch ([string]$session.session_id) -Quiet)
        }
        if (-not $alreadySaved) {
            Write-JsonLine -Path $SessionsFile -Value $session
        }
        Remove-Item -LiteralPath $SessionFile -Force
        Write-ProjectEvent -Type "work_session_closed" -Text ("Сессия закрыта. Активное время: " + $session.duration_hms) -EventSource "powershell" -SessionId $session.session_id
        Write-Host ("Сессия закрыта. Активное время: " + $session.duration_hms) -ForegroundColor Green
    }

    "recover" {
        $session = Require-Session
        $session.is_paused = $true
        $session.resumed_at_utc = $null
        $session.interrupted = $true
        $session.recovery_note = "Неизвестный интервал после последнего сохранённого состояния не засчитан."
        Save-Session $session
        Write-ProjectEvent -Type "work_session_interrupted_recovery" -Text "Сессия аварийно приостановлена. Неизвестный интервал не добавлен к рабочему времени." -EventSource "powershell" -SessionId $session.session_id
        Write-Host "Сессия безопасно приостановлена. Неизвестное время не засчитано." -ForegroundColor Yellow
    }

    "event" {
        if ([string]::IsNullOrWhiteSpace($Description)) { throw "Укажите описание: event -Description 'Что произошло'." }
        Write-ProjectEvent -Type $EventType -Text $Description -EventSource $Source
        Write-Host "Событие записано в локальный журнал." -ForegroundColor Green
    }

    "status" {
        Ensure-Store
        $session = Read-Session
        if ($null -eq $session) {
            Write-Host "Активной сессии нет."
        }
        else {
            $seconds = Get-ActiveSeconds $session
            Write-Host ("Сессия: " + $session.session_id)
            Write-Host ("Задача: " + $session.task)
            Write-Host ("Категория: " + $session.category)
            Write-Host ("Состояние: " + $(if ($session.is_paused) { "ПАУЗА" } else { "АКТИВНА" }))
            Write-Host ("Учтённое время: " + (Format-Duration $seconds))
            if ($session.interrupted) { Write-Host "Внимание: сессия восстановлена после прерывания." -ForegroundColor Yellow }
        }
        $count = 0
        $total = [long]0
        if (Test-Path -LiteralPath $SessionsFile) {
            foreach ($line in (Get-Content -LiteralPath $SessionsFile -Encoding utf8)) {
                if ([string]::IsNullOrWhiteSpace($line)) { continue }
                $item = $line | ConvertFrom-Json
                $total += [long]$item.accumulated_active_seconds
                $count++
            }
        }
        Write-Host ("Закрытых сессий: " + $count)
        Write-Host ("Сумма закрытых сессий: " + (Format-Duration $total))
        Write-Host ("Файлы журнала: " + $DataRoot)
    }

    "ai" {
        if ([string]::IsNullOrWhiteSpace($Prompt)) { throw "Укажите запрос: ai -Prompt 'Ваш вопрос'." }
        $baseUrl = $env:KOMAROVA_AI_BASE_URL
        $model = $env:KOMAROVA_AI_MODEL
        $apiKey = $env:KOMAROVA_AI_API_KEY

        if ([string]::IsNullOrWhiteSpace($baseUrl) -or [string]::IsNullOrWhiteSpace($model)) {
            throw @"
Автономный ИИ ещё не настроен.
Задайте KOMAROVA_AI_BASE_URL и KOMAROVA_AI_MODEL для локального Ollama
или другого совместимого сервера OpenAI API.
Ключ, если он требуется провайдеру, задаётся через KOMAROVA_AI_API_KEY.
Скрипт не использует ChatGPT и не отправляет журналы без явного включения их текста в запрос.
"@
        }

        $uri = $baseUrl.TrimEnd("/")
        if (-not $uri.EndsWith("/chat/completions")) {
            if (-not $uri.EndsWith("/v1")) { $uri += "/v1" }
            $uri += "/chat/completions"
        }
        $headers = @{}
        if (-not [string]::IsNullOrWhiteSpace($apiKey)) {
            $headers["Authorization"] = "Bearer $apiKey"
        }
        $body = @{
            model = $model
            temperature = 0.2
            messages = @(
                @{ role = "system"; content = "Ты автономный технический помощник проекта KOMAROVA_CORE. Отвечай по-русски. Не утверждай, что выполнял действия. Не проси и не раскрывай секреты. Не изменяй файлы и не запускай команды. Оригиналы семейных материалов должны оставаться неизменными." },
                @{ role = "user"; content = $Prompt }
            )
        } | ConvertTo-Json -Depth 8
        $response = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -ContentType "application/json; charset=utf-8" -Body $body -TimeoutSec 120
        $answer = $response.choices[0].message.content
        if ([string]::IsNullOrWhiteSpace([string]$answer)) { throw "ИИ-сервер ответил без текста. Проверьте совместимость API и выбранную модель." }
        Write-Output $answer
    }
}
