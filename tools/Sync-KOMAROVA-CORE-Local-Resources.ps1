# KOMAROVA_CORE: синхронизация общего каталога ссылок с локальной версией
# Требуется PowerShell 7.7.0. Скрипт не меняет .env, OAuth-файлы, базу данных и семейные материалы.
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion -lt [version]'7.7.0') { throw "Требуется PowerShell 7.7.0. Текущая версия: $($PSVersionTable.PSVersion)" }

$Root = Join-Path $env:USERPROFILE 'KOMAROVA_CORE'
$IndexPath = Join-Path $Root 'index.html'
if (-not (Test-Path -LiteralPath $IndexPath -PathType Leaf)) { throw "Не найден локальный файл: $IndexPath" }

$Base = 'https://raw.githubusercontent.com/alexsandrkomarov1-wq/-ArtBukaBot-/core-backend-foundation'
$Files = @(
    @{ Relative = 'assets/data/external-resources.json'; Url = "$Base/assets/data/external-resources.json" },
    @{ Relative = 'assets/js/external-resources.js'; Url = "$Base/assets/js/external-resources.js" }
)

foreach ($File in $Files) {
    $Destination = Join-Path $Root $File.Relative
    $Directory = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $Directory -Force | Out-Null
    $Temporary = "$Destination.download"
    Invoke-WebRequest -Uri $File.Url -OutFile $Temporary
    if ($File.Relative.EndsWith('.json')) {
        $Parsed = Get-Content -LiteralPath $Temporary -Raw -Encoding UTF8 | ConvertFrom-Json
        $Count = @($Parsed.groups | ForEach-Object { $_.items }).Count
        if ($Count -ne 10) { Remove-Item -LiteralPath $Temporary -Force; throw "Ожидалось 10 ссылок, получено $Count. Локальный файл не заменён." }
    }
    Move-Item -LiteralPath $Temporary -Destination $Destination -Force
    Write-Host "Синхронизирован: $($File.Relative)" -ForegroundColor Green
}

$Html = Get-Content -LiteralPath $IndexPath -Raw -Encoding UTF8
if ($Html -notmatch 'id=["'']family-external-resources["'']') {
    if ($Html -notmatch '</body>') { throw 'В index.html не найден закрывающий </body>. Файл не изменён.' }
    $Mount = @'
<section id="family-external-resources" data-resources-url="assets/data/external-resources.json" aria-label="Семейные внешние ресурсы">
  <h2>Семейные внешние ресурсы</h2>
  <p>Единый список ссылок KOMAROVA_CORE: облачные кабинеты, семейные источники и переписка.</p>
</section>
<script src="assets/js/external-resources.js" defer></script>
'@
    $Backup = "$IndexPath.before-resource-links-$(Get-Date -Format 'yyyyMMdd-HHmmss').bak"
    Copy-Item -LiteralPath $IndexPath -Destination $Backup
    $Html = $Html.Replace('</body>', $Mount + [Environment]::NewLine + '</body>')
    Set-Content -LiteralPath $IndexPath -Value $Html -Encoding UTF8
    Write-Host "Резервная копия index.html: $Backup" -ForegroundColor Yellow
} else {
    Write-Host 'Блок ссылок уже присутствует в index.html; повторная вставка не выполнялась.' -ForegroundColor Cyan
}

Write-Host 'Проверка каталога:' -ForegroundColor Cyan
$Registry = Get-Content -LiteralPath (Join-Path $Root 'assets/data/external-resources.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$Total = @($Registry.groups | ForEach-Object { $_.items }).Count
Write-Host "Ссылок в локальном каталоге: $Total"
Write-Host 'Локальная версия синхронизирована с общим каталогом ветки core-backend-foundation.' -ForegroundColor Green
Write-Host 'Перезагрузите http://127.0.0.1:8080 с Ctrl+F5. Сервер перезапускать не требуется.'