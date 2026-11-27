[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$sourceScript = Join-Path $PSScriptRoot "komarova-core.ps1"
if (-not (Test-Path -LiteralPath $sourceScript)) {
    throw "Не найден tools/komarova-core.ps1"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("komarova-core-test-" + [guid]::NewGuid().ToString("N"))
$toolsDir = Join-Path $tempRoot "tools"
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
$testScript = Join-Path $toolsDir "komarova-core.ps1"
Copy-Item -LiteralPath $sourceScript -Destination $testScript

function Invoke-Logger([string]$Action, [string]$Task = "") {
    if ([string]::IsNullOrWhiteSpace($Task)) {
        $output = & $testScript $Action 2>&1
    }
    else {
        $output = & $testScript $Action -Task $Task 2>&1
    }
    return ($output -join [Environment]::NewLine)
}

try {
    $null = Invoke-Logger "init"
    $null = Invoke-Logger "start" "Автоматический изолированный тест"
    $status = Invoke-Logger "status"
    if ($status -notmatch "АКТИВНА") { throw "Статус не показывает активную сессию." }

    $null = Invoke-Logger "pause"
    $paused = Invoke-Logger "status"
    if ($paused -notmatch "ПАУЗА") { throw "Пауза не отражена в статусе." }

    $null = Invoke-Logger "resume"
    $null = Invoke-Logger "stop"

    $dataRoot = Join-Path $tempRoot "data\project_time"
    $sessionsFile = Join-Path $dataRoot "sessions.jsonl"
    $eventsFile = Join-Path $dataRoot "events.jsonl"
    if (-not (Test-Path -LiteralPath $sessionsFile)) { throw "Файл закрытых сессий не создан." }
    if (-not (Test-Path -LiteralPath $eventsFile)) { throw "Файл событий не создан." }

    $sessions = @(Get-Content -LiteralPath $sessionsFile -Encoding utf8 | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
    if ($sessions.Count -ne 1) { throw "Ожидалась ровно одна закрытая сессия; получено $($sessions.Count)." }
    if ($sessions[0].status -ne "closed") { throw "Сессия не закрыта корректно." }
    if ([long]$sessions[0].accumulated_active_seconds -lt 0) { throw "Отрицательная длительность сессии." }

    Write-Output "PASS: init/start/status/pause/resume/stop"
    Write-Output "PASS: JSONL events and sessions"
    Write-Output "PASS: isolated temporary directory; project data untouched"
}
finally {
    if (Test-Path -LiteralPath $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}
