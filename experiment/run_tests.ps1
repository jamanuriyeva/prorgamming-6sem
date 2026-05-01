# run_tests.ps1
# Последовательное тестирование всех фреймворков при 50, 100, 200 пользователях

$ErrorActionPreference = "Stop"

# Параметры тестирования (из задания)
$USERS = @(50, 100, 200)
$SPAWN_RATE = 10
$RUN_TIME = "3m"
$LOCUST_FILE = "locustfile.py"

# Папки для результатов
New-Item -ItemType Directory -Force -Path "report\csv" | Out-Null
New-Item -ItemType Directory -Force -Path "report\html" | Out-Null

Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ REST API ФРЕЙМВОРКОВ" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# ------------------------------------------------------------
function Test-Framework {
    param(
        [string]$Name,
        [string]$HostUrl,
        [string]$ServerScript
    )
    
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Yellow
    Write-Host "  ТЕСТИРОВАНИЕ: $Name" -ForegroundColor Yellow
    Write-Host "  Хост: $HostUrl" -ForegroundColor Yellow
    Write-Host "=" * 70 -ForegroundColor Yellow
    
    foreach ($users in $USERS) {
        Write-Host "`n>>> $Name | Пользователей: $users | Время: $RUN_TIME <<<" -ForegroundColor Green
        
        $htmlFile = "report/html/${Name}_users${users}.html"
        $csvPrefix = "report/csv/${Name}_users${users}"
        
        # Запуск Locust в headless-режиме
        locust -f $LOCUST_FILE `
            --host=$HostUrl `
            --headless `
            --users $users `
            --spawn-rate $SPAWN_RATE `
            --run-time $RUN_TIME `
            --html $htmlFile `
            --csv $csvPrefix
        
        Write-Host ">>> Завершено: $Name с $users пользователями" -ForegroundColor Green
        
        # Пауза между тестами (чтобы сервер "отдохнул")
        Start-Sleep -Seconds 3
    }
    
    Write-Host "`n$Name - ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ" -ForegroundColor Green
}

# ============================================================
# ЗАПУСК ТЕСТОВ
# ============================================================

Write-Host "`n!!! ВАЖНО: Убедитесь, что сервер запущен в другом терминале !!!" -ForegroundColor Red
Write-Host "Нажмите Enter для продолжения..."
Read-Host

# --- Flask ---
Write-Host "`n>>> Запустите Flask в другом терминале: python app_flask.py" -ForegroundColor Magenta
Write-Host ">>> После запуска нажмите Enter..." -ForegroundColor Magenta
Read-Host
Test-Framework -Name "flask" -HostUrl "http://127.0.0.1:5000" -ServerScript "app_flask.py"

# --- Sanic ---
Write-Host "`n>>> Запустите Sanic в другом терминале: python app_sanic.py" -ForegroundColor Magenta
Write-Host ">>> После запуска нажмите Enter..." -ForegroundColor Magenta
Read-Host
Test-Framework -Name "sanic" -HostUrl "http://127.0.0.1:8000" -ServerScript "app_sanic.py"

# --- aiohttp ---
Write-Host "`n>>> Запустите aiohttp в другом терминале: python app_aiohttp.py" -ForegroundColor Magenta
Write-Host ">>> После запуска нажмите Enter..." -ForegroundColor Magenta
Read-Host
Test-Framework -Name "aiohttp" -HostUrl "http://127.0.0.1:8080" -ServerScript "app_aiohttp.py"

# ============================================================
# ИТОГИ
# ============================================================
Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "`nРезультаты:" -ForegroundColor White
Write-Host "  HTML-отчёты: report/html/" -ForegroundColor Gray
Write-Host "  CSV-метрики:  report/csv/" -ForegroundColor Gray
Write-Host "`nПросмотр метрик:" -ForegroundColor White
Write-Host "  Get-Content report/csv/flask_users50_stats.csv | ConvertFrom-Csv | Format-Table" -ForegroundColor Gray
