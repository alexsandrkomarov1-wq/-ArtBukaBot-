# KOMAROVA_CORE — открыть официальные сайты облачных хранилищ
# Требуемая среда: PowerShell 7.7.0
# Скрипт только открывает сайты в браузере. Он НЕ выполняет регистрацию,
# OAuth, вход в аккаунты, API-проверки, загрузку или синхронизацию файлов.

$ErrorActionPreference = 'Stop'
$RequiredPowerShellVersion = [version]'7.7.0'

if ($PSVersionTable.PSVersion -ne $RequiredPowerShellVersion) {
    throw "Требуется PowerShell 7.7.0. Текущая версия: $($PSVersionTable.PSVersion). Запустите через pwsh 7.7.0."
}

$Sites = [ordered]@{
    'Google Drive' = 'https://drive.google.com/'
    'MEGA'         = 'https://mega.io/'
    'pCloud'       = 'https://www.pcloud.com/'
    'Яндекс Диск'  = 'https://disk.yandex.ru/'
    'OneDrive'     = 'https://onedrive.live.com/'
    'Dropbox'      = 'https://www.dropbox.com/'
    'TeraBox'      = 'https://www.terabox.com/'
}

Write-Host 'KOMAROVA_CORE — открытие официальных сайтов' -ForegroundColor Cyan
Write-Host 'Будут открыты 7 адресов в браузере по умолчанию.' -ForegroundColor Gray

foreach ($Entry in $Sites.GetEnumerator()) {
    $Uri = [uri]$Entry.Value
    if (-not $Uri.IsAbsoluteUri -or $Uri.Scheme -ne 'https') {
        throw "Некорректный HTTPS-адрес для $($Entry.Key): $($Entry.Value)"
    }

    Start-Process -FilePath $Uri.AbsoluteUri
    Write-Host ("Открыт: {0} — {1}" -f $Entry.Key, $Uri.AbsoluteUri) -ForegroundColor Green
}

Write-Host 'Готово. Скрипт не подключает аккаунты и не меняет файлы архива.' -ForegroundColor Cyan
