[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "project-control.ps1"
if (-not (Test-Path -LiteralPath $scriptPath)) { throw "Не найден tools/project-control.ps1" }

$temp = Join-Path ([System.IO.Path]::GetTempPath()) ("komarova-control-test-" + [guid]::NewGuid().ToString("N"))
$env:KOMAROVA_CONTROL_HOME = $temp
try {
    & $scriptPath init
    & $scriptPath register -ProjectId TEST_PROJECT -Name "Тестовый проект" -Repo "test/example" -Branch "work" -SiteUrl "https://example.com/"
    & $scriptPath event -ProjectId TEST_PROJECT -Description "Проверка журнала" -Actor agent
    & $scriptPath task-start -ProjectId TEST_PROJECT -Task "Тестовая сессия" -Actor agent
    & $scriptPath task-pause -ProjectId TEST_PROJECT
    & $scriptPath task-resume -ProjectId TEST_PROJECT
    & $scriptPath task-stop -ProjectId TEST_PROJECT
    $events = Join-Path $temp "TEST_PROJECT\events.jsonl"
    $sessions = Join-Path $temp "TEST_PROJECT\sessions.jsonl"
    if (-not (Test-Path $events)) { throw "events.jsonl не создан." }
    if (-not (Test-Path $sessions)) { throw "sessions.jsonl не создан." }
    if ((Get-Content $events).Count -lt 5) { throw "Недостаточно событий в журнале." }
    if ((Get-Content $sessions).Count -ne 1) { throw "Закрытая сессия не записана ровно один раз." }
    Write-Host "PROJECT CONTROL SELF-TEST: PASS" -ForegroundColor Green
}
finally {
    Remove-Item Env:\KOMAROVA_CONTROL_HOME -ErrorAction SilentlyContinue
    if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
