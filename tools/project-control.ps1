[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("init","status","launch","register","event","task-start","task-pause","task-resume","task-stop","scan","help")]
    [string]$Command = "help",

    [string]$ProjectId = "KOMAROVA_CORE",
    [string]$Name,
    [string]$Path,
    [string]$Repo,
    [string]$Branch,
    [string]$SiteUrl,
    [string]$LocalUrl,
    [string]$Task,
    [string]$Description,
    [ValidateSet("human","assistant","agent","tinyfish","worker","ci","git-observer")]
    [string]$Actor = "human"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:TimeZoneId = "Europe/Amsterdam"
$script:StoreRoot = if ($env:KOMAROVA_CONTROL_HOME) {
    $env:KOMAROVA_CONTROL_HOME
} else {
    Join-Path $env:LOCALAPPDATA "KOMAROVA_CORE\ControlCenter"
}
$script:RegistryPath = Join-Path $script:StoreRoot "projects.json"

function Get-LocalStamp([DateTimeOffset]$Value) {
    try {
        $zone = [TimeZoneInfo]::FindSystemTimeZoneById($script:TimeZoneId)
        return [TimeZoneInfo]::ConvertTime($Value, $zone).ToString("yyyy-MM-dd HH:mm:ss zzz")
    } catch {
        return $Value.ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss zzz")
    }
}

function Ensure-Store {
    if (-not (Test-Path -LiteralPath $script:StoreRoot)) {
        New-Item -ItemType Directory -Path $script:StoreRoot -Force | Out-Null
    }
    if (-not (Test-Path -LiteralPath $script:RegistryPath)) {
        $defaultRoot = "C:\Users\KomarovA\KOMAROVA_CORE"
        $projects = @(
            [ordered]@{
                project_id = "KOMAROVA_CORE"
                name = "KOMAROVA_CORE"
                path = $defaultRoot
                repository = "alexsandrkomarov1-wq/-ArtBukaBot-"
                branch = "core-backend-foundation"
                site_url = "https://alexsandrkomarov1-wq.github.io/-ArtBukaBot-/"
                local_url = "http://127.0.0.1:8080/"
                configured = $true
            },
            [ordered]@{
                project_id = "PROJECT_2"
                name = "Второй проект (ожидает идентификации)"
                path = ""
                repository = ""
                branch = ""
                site_url = ""
                local_url = ""
                configured = $false
            }
        )
        Save-Registry $projects
    }
    foreach ($project in (Get-Projects)) {
        $dir = Get-ProjectDir ([string]$project.project_id)
        if (-not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        $log = Join-Path $dir "events.jsonl"
        if (-not (Test-Path -LiteralPath $log)) {
            New-Item -ItemType File -Path $log -Force | Out-Null
        }
    }
}

function Save-Registry([object[]]$Projects) {
    if (-not (Test-Path -LiteralPath $script:StoreRoot)) {
        New-Item -ItemType Directory -Path $script:StoreRoot -Force | Out-Null
    }
    $tmp = "$($script:RegistryPath).tmp"
    $json = ConvertTo-Json -InputObject @($Projects) -Depth 10
    [System.IO.File]::WriteAllText($tmp, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tmp -Destination $script:RegistryPath -Force
}

function Get-Projects {
    if (-not (Test-Path -LiteralPath $script:RegistryPath)) { return @() }
    $raw = Get-Content -LiteralPath $script:RegistryPath -Raw -Encoding utf8
    if ([string]::IsNullOrWhiteSpace($raw)) { return @() }
    return @($raw | ConvertFrom-Json)
}

function Get-ProjectDir([string]$Id) {
    $safe = $Id -replace '[^A-Za-z0-9_-]', '_'
    return Join-Path $script:StoreRoot $safe
}

function Get-Project([string]$Id) {
    $found = Get-Projects | Where-Object { $_.project_id -eq $Id } | Select-Object -First 1
    if ($null -eq $found) { throw "Проект '$Id' не зарегистрирован. Используйте register." }
    return $found
}

function Write-Event([string]$Id,[string]$Type,[string]$Text,[string]$EventActor,[hashtable]$Extra = @{}) {
    Ensure-Store
    $now = [DateTimeOffset]::UtcNow
    $entry = [ordered]@{
        event_id = [guid]::NewGuid().ToString()
        project_id = $Id
        timestamp_utc = $now.ToString("o")
        timestamp_local = Get-LocalStamp $now
        timezone = $script:TimeZoneId
        event_type = $Type
        actor = $EventActor
        description = $Text
        computer = $env:COMPUTERNAME
        user = $env:USERNAME
    }
    foreach ($key in $Extra.Keys) { $entry[$key] = $Extra[$key] }
    $line = ConvertTo-Json -InputObject $entry -Depth 12 -Compress
    $file = Join-Path (Get-ProjectDir $Id) "events.jsonl"
    [System.IO.File]::AppendAllText($file, $line + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

function Get-SessionPath([string]$Id) {
    return Join-Path (Get-ProjectDir $Id) "active_session.json"
}

function Get-ActiveSeconds([object]$Session) {
    $seconds = [long]$Session.accumulated_active_seconds
    if (-not [bool]$Session.is_paused -and $Session.resumed_at_utc) {
        $start = [DateTimeOffset]::Parse([string]$Session.resumed_at_utc)
        $seconds += [long][Math]::Max(0,[Math]::Floor(([DateTimeOffset]::UtcNow - $start).TotalSeconds))
    }
    return $seconds
}

function Format-Duration([long]$Seconds) {
    $h = [long][Math]::Floor($Seconds / 3600)
    $m = [long][Math]::Floor(($Seconds % 3600) / 60)
    $s = [long]($Seconds % 60)
    return "{0:00}:{1:00}:{2:00}" -f $h,$m,$s
}

function Get-GitSnapshot([object]$Project) {
    $path = [string]$Project.path
    if ([string]::IsNullOrWhiteSpace($path) -or -not (Test-Path -LiteralPath $path)) {
        return [ordered]@{ available=$false; reason="Локальная папка проекта не найдена или не настроена." }
    }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return [ordered]@{ available=$false; reason="Git не найден в PATH." }
    }
    $top = & git -C $path rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0) {
        return [ordered]@{ available=$false; reason="Папка не является Git-репозиторием." }
    }
    $branchName = (& git -C $path branch --show-current 2>$null | Select-Object -First 1)
    $head = (& git -C $path rev-parse HEAD 2>$null | Select-Object -First 1)
    $last = (& git -C $path log -1 '--format=%cI|%H|%s' 2>$null | Select-Object -First 1)
    $changes = @(& git -C $path status --short 2>$null)
    return [ordered]@{
        available = $true
        root = [string]$top
        branch = [string]$branchName
        head = [string]$head
        last_commit = [string]$last
        working_tree_changes = @($changes)
        protected_branch = ([string]$branchName -eq "main")
    }
}

function Show-Help {
@"
KOMAROVA_CORE · MULTI-PROJECT CONTROL
PowerShell 7.7.0

Команды:
  .\project-control.ps1 init
  .\project-control.ps1 status
  .\project-control.ps1 launch
  .\project-control.ps1 scan
  .\project-control.ps1 event -ProjectId KOMAROVA_CORE -Description "Описание"
  .\project-control.ps1 task-start -ProjectId KOMAROVA_CORE -Task "Задача" -Actor human
  .\project-control.ps1 task-pause -ProjectId KOMAROVA_CORE
  .\project-control.ps1 task-resume -ProjectId KOMAROVA_CORE
  .\project-control.ps1 task-stop -ProjectId KOMAROVA_CORE
  .\project-control.ps1 register -ProjectId PROJECT_2 -Name "Название" -Path "D:\Project" -Repo "owner/repo" -Branch "work" -SiteUrl "https://example.com/"

Данные и журналы:
  $($script:StoreRoot)
  Журналы раздельные по project_id, формат JSONL, только добавление.
  Локальные журналы не отправляются в облако автоматически.

Защита:
  - main никогда не используется для разработки.
  - scan только читает Git; он не изменяет файлы и не отправляет изменения.
  - launch только открывает настроенные URL.
  - оригиналы, секреты, OAuth и Supabase не затрагиваются.
  - PROJECT_2 не запускается, пока его адрес и репозиторий не зарегистрированы.
"@ | Write-Output
}

Ensure-Store

switch ($Command) {
    "help" { Show-Help }

    "init" {
        foreach ($p in (Get-Projects)) {
            Write-Event ([string]$p.project_id) "control_initialized" "Инициализирован журнал управления проектом." "worker"
        }
        Write-Host "Центр учёта создан: $script:StoreRoot" -ForegroundColor Green
        Write-Host "Проектов в реестре: $(@(Get-Projects).Count)"
    }

    "status" {
        $rows = foreach ($p in (Get-Projects)) {
            $configured = [bool]$p.configured
            $snapshot = Get-GitSnapshot $p
            $sessionPath = Get-SessionPath ([string]$p.project_id)
            $sessionState = "нет"
            $duration = "00:00:00"
            if (Test-Path -LiteralPath $sessionPath) {
                $session = Get-Content -LiteralPath $sessionPath -Raw -Encoding utf8 | ConvertFrom-Json
                $sessionState = if ($session.is_paused) { "пауза" } else { "активна" }
                $duration = Format-Duration (Get-ActiveSeconds $session)
            }
            [pscustomobject]@{
                Project = $p.name
                ID = $p.project_id
                Configured = $configured
                Branch = if ($snapshot.available) { $snapshot.branch } else { [string]$p.branch }
                Git = if ($snapshot.available) { "доступен" } else { "не проверен" }
                Session = $sessionState
                Time = $duration
                Site = [string]$p.site_url
            }
        }
        $rows | Format-Table -AutoSize
        Write-Host "Журналы: $script:StoreRoot"
    }

    "register" {
        if ([string]::IsNullOrWhiteSpace($ProjectId) -or [string]::IsNullOrWhiteSpace($Name)) {
            throw "Для register обязательны -ProjectId и -Name."
        }
        $all = @(Get-Projects)
        $existing = @($all | Where-Object { $_.project_id -eq $ProjectId })
        $item = [ordered]@{
            project_id = $ProjectId
            name = $Name
            path = if ($Path) { $Path } else { "" }
            repository = if ($Repo) { $Repo } else { "" }
            branch = if ($Branch) { $Branch } else { "" }
            site_url = if ($SiteUrl) { $SiteUrl } else { "" }
            local_url = if ($LocalUrl) { $LocalUrl } else { "" }
            configured = [bool]($Path -or $Repo -or $SiteUrl -or $LocalUrl)
        }
        if ($existing.Count -gt 0) {
            $all = @($all | Where-Object { $_.project_id -ne $ProjectId })
        }
        $all += [pscustomobject]$item
        Save-Registry $all
        $dir = Get-ProjectDir $ProjectId
        if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $log = Join-Path $dir "events.jsonl"
        if (-not (Test-Path -LiteralPath $log)) { New-Item -ItemType File -Path $log -Force | Out-Null }
        Write-Event $ProjectId "project_registered" "Обновлена регистрация проекта '$Name'." "owner" @{ repository=$Repo; branch=$Branch; site_url=$SiteUrl }
        Write-Host "Проект зарегистрирован: $ProjectId" -ForegroundColor Green
    }

    "launch" {
        $targets = if ($ProjectId -eq "ALL") { @(Get-Projects) } else { @((Get-Project $ProjectId)) }
        foreach ($p in $targets) {
            if (-not [bool]$p.configured) {
                Write-Host "Пропуск $($p.project_id): проект ещё не настроен." -ForegroundColor Yellow
                continue
            }
            foreach ($url in @([string]$p.site_url,[string]$p.local_url)) {
                if ([string]::IsNullOrWhiteSpace($url)) { continue }
                if ($url -notmatch '^https?://') {
                    Write-Host "Пропуск некорректного URL: $url" -ForegroundColor Yellow
                    continue
                }
                if ($url -eq [string]$p.local_url) {
                    try {
                        $probe = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 3 -SkipHttpErrorCheck
                        if ([int]$probe.StatusCode -lt 200 -or [int]$probe.StatusCode -ge 400) {
                            Write-Host "Локальный сервер не готов ($($probe.StatusCode)): $url" -ForegroundColor Yellow
                            Write-Event ([string]$p.project_id) "local_site_not_ready" "Локальный адрес не ответил успешно: $url (HTTP $($probe.StatusCode)). Сервер автоматически не запускался." "worker"
                            continue
                        }
                    } catch {
                        Write-Host "Локальный сервер недоступен: $url" -ForegroundColor Yellow
                        Write-Event ([string]$p.project_id) "local_site_not_ready" "Локальный адрес недоступен: $url. Сервер автоматически не запускался." "worker"
                        continue
                    }
                }
                Start-Process $url
                Write-Event ([string]$p.project_id) "browser_open_requested" "PowerShell передал URL браузеру: $url" "owner" @{ url=$url }
                Write-Host "Открыт запрос браузеру: $url" -ForegroundColor Green
            }
            if ($p.repository -and $p.branch) {
                $repoUrl = "https://github.com/$($p.repository)/tree/$($p.branch)"
                Start-Process $repoUrl
                Write-Event ([string]$p.project_id) "repository_open_requested" "Открыта рабочая ветка проекта в браузере: $repoUrl" "owner" @{ url=$repoUrl }
                Write-Host "Открыта рабочая ветка GitHub: $repoUrl" -ForegroundColor Green
            }
        }
    }

    "event" {
        if ([string]::IsNullOrWhiteSpace($Description)) { throw "Укажите -Description." }
        Write-Event $ProjectId "project_note" $Description $Actor
        Write-Host "Запись добавлена в журнал $ProjectId." -ForegroundColor Green
    }

    "task-start" {
        if ([string]::IsNullOrWhiteSpace($Task)) { throw "Укажите -Task." }
        $p = Get-Project $ProjectId
        $sessionPath = Get-SessionPath $ProjectId
        if (Test-Path -LiteralPath $sessionPath) { throw "Для $ProjectId уже есть активная сессия. Сначала pause или stop." }
        $now = [DateTimeOffset]::UtcNow
        $session = [ordered]@{
            session_id = [guid]::NewGuid().ToString()
            project_id = $ProjectId
            task = $Task
            actor = $Actor
            started_at_utc = $now.ToString("o")
            resumed_at_utc = $now.ToString("o")
            accumulated_active_seconds = 0
            is_paused = $false
        }
        [System.IO.File]::WriteAllText($sessionPath,(ConvertTo-Json $session -Depth 8),[System.Text.UTF8Encoding]::new($false))
        Write-Event $ProjectId "task_started" $Task $Actor @{ session_id=$session.session_id }
        Write-Host "Сессия начата: $($session.session_id)" -ForegroundColor Green
    }

    "task-pause" {
        $sessionPath = Get-SessionPath $ProjectId
        if (-not (Test-Path -LiteralPath $sessionPath)) { throw "Активная сессия не найдена." }
        $session = Get-Content -LiteralPath $sessionPath -Raw -Encoding utf8 | ConvertFrom-Json
        if ($session.is_paused) { throw "Сессия уже на паузе." }
        $session.accumulated_active_seconds = Get-ActiveSeconds $session
        $session.is_paused = $true
        $session.resumed_at_utc = $null
        [System.IO.File]::WriteAllText($sessionPath,(ConvertTo-Json $session -Depth 8),[System.Text.UTF8Encoding]::new($false))
        Write-Event $ProjectId "task_paused" "Учтённое время: $(Format-Duration $session.accumulated_active_seconds)" $Actor
        Write-Host "Пауза. Учтено: $(Format-Duration $session.accumulated_active_seconds)" -ForegroundColor Yellow
    }

    "task-resume" {
        $sessionPath = Get-SessionPath $ProjectId
        if (-not (Test-Path -LiteralPath $sessionPath)) { throw "Сессия не найдена." }
        $session = Get-Content -LiteralPath $sessionPath -Raw -Encoding utf8 | ConvertFrom-Json
        if (-not $session.is_paused) { throw "Сессия уже активна." }
        $session.is_paused = $false
        $session.resumed_at_utc = [DateTimeOffset]::UtcNow.ToString("o")
        [System.IO.File]::WriteAllText($sessionPath,(ConvertTo-Json $session -Depth 8),[System.Text.UTF8Encoding]::new($false))
        Write-Event $ProjectId "task_resumed" "Работа продолжена." $Actor
        Write-Host "Сессия продолжена." -ForegroundColor Green
    }

    "task-stop" {
        $sessionPath = Get-SessionPath $ProjectId
        if (-not (Test-Path -LiteralPath $sessionPath)) { throw "Сессия не найдена." }
        $session = Get-Content -LiteralPath $sessionPath -Raw -Encoding utf8 | ConvertFrom-Json
        $total = Get-ActiveSeconds $session
        $session.accumulated_active_seconds = $total
        $session.is_paused = $true
        Add-Member -InputObject $session -NotePropertyName ended_at_utc -NotePropertyValue ([DateTimeOffset]::UtcNow.ToString("o")) -Force
        Add-Member -InputObject $session -NotePropertyName duration_hms -NotePropertyValue (Format-Duration $total) -Force
        $sessionsFile = Join-Path (Get-ProjectDir $ProjectId) "sessions.jsonl"
        $line = ConvertTo-Json -InputObject $session -Depth 10 -Compress
        [System.IO.File]::AppendAllText($sessionsFile,$line + [Environment]::NewLine,[System.Text.UTF8Encoding]::new($false))
        Remove-Item -LiteralPath $sessionPath -Force
        Write-Event $ProjectId "task_stopped" "Сессия закрыта. Активное время: $($session.duration_hms)" $Actor @{ session_id=$session.session_id; active_seconds=$total }
        Write-Host "Сессия закрыта. Активное время: $($session.duration_hms)" -ForegroundColor Green
    }

    "scan" {
        $targets = if ($ProjectId -eq "ALL") { @(Get-Projects) } else { @((Get-Project $ProjectId)) }
        foreach ($p in $targets) {
            $snapshot = Get-GitSnapshot $p
            if (-not $snapshot.available) {
                Write-Host "$($p.project_id): $($snapshot.reason)" -ForegroundColor Yellow
                Write-Event ([string]$p.project_id) "git_scan_unavailable" $snapshot.reason "git-observer"
                continue
            }
            $snapshotPath = Join-Path (Get-ProjectDir ([string]$p.project_id)) "last_git_snapshot.json"
            $previousHead = ""
            if (Test-Path -LiteralPath $snapshotPath) {
                $previous = Get-Content -LiteralPath $snapshotPath -Raw -Encoding utf8 | ConvertFrom-Json
                $previousHead = [string]$previous.head
            }
            $json = ConvertTo-Json -InputObject $snapshot -Depth 10
            [System.IO.File]::WriteAllText($snapshotPath,$json,[System.Text.UTF8Encoding]::new($false))
            if ($snapshot.head -and $snapshot.head -ne $previousHead) {
                Write-Event ([string]$p.project_id) "git_commit_observed" "Обнаружен HEAD: $($snapshot.head). Ветка: $($snapshot.branch). Это наблюдение, не учёт активного времени." "git-observer" @{ head=$snapshot.head; branch=$snapshot.branch; commit=$snapshot.last_commit }
            }
            $status = if ($snapshot.protected_branch) { "ОШИБКА: локальная папка на main. Только чтение." } else { "ветка $($snapshot.branch)" }
            Write-Host "$($p.project_id): $status; HEAD $($snapshot.head); незакоммиченных изменений: $(@($snapshot.working_tree_changes).Count)"
            if ($snapshot.protected_branch) { Write-Event ([string]$p.project_id) "protected_branch_detected" "Обнаружена main. Скрипт ничего не менял." "git-observer" }
        }
    }
}
