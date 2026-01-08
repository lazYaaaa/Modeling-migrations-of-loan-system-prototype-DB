# ========== ВАЖНОЕ ДОБАВЛЕНИЕ ==========
# Включение всех протоколов безопасности и игнорирование SSL ошибок
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls11 -bor [System.Net.SecurityProtocolType]::Tls
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
# =======================================

Write-Host "🚀 Проверка существующих групп (ID 1-34)..." -ForegroundColor Red

$createdEvents = @()
$token = "e1696c58c1fc6fdbdedd027887a6920c280cd45e"
$csrfToken = "4wG9bkx8p4vMY5qMgtPu9BBp1nhrPYDH5BLGM0sY9HTchbWXbHFms1xiHiQr1bli"

# Увеличиваем лимит на количество одновременных подключений
[System.Net.ServicePointManager]::DefaultConnectionLimit = 100

# Проверка доступности сервера перед началом
Write-Host "🔍 Проверка доступности сервера..." -ForegroundColor Yellow
try {
    $pingTest = Test-Connection -ComputerName 185.17.141.230 -Count 1 -Quiet
    if ($pingTest) {
        Write-Host "✅ Сервер доступен по ping" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Сервер недоступен по ping, но пробуем продолжить..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Ping тест не удался: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Создаем кодировку UTF-8 без BOM (один раз, перед циклом)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

$successCount = 0
$errorCount = 0
$groupIds = 1..34  # Только группы с 1 по 34

Write-Host "🎯 Проверяем группы: $groupIds" -ForegroundColor Cyan

foreach ($groupId in $groupIds) {
    # Данные для создания события
    $eventData = @{
        name = "test"
        component = 1
        starts = "2025-11-22T11:30:00Z"
        finishes = "2025-11-22T13:05:00Z"
        interval = 2400
        for_group = $true
        blocks_next = $true
        group = $groupId
        meta = @{
            knowledge_base = 783
            confirm_evidence = $true
            conflict_resolving = 2
            inference_direction = 2
            goal_selecting = 3
        }
    }
    
    $jsonData = $eventData | ConvertTo-Json -Depth 5 -Compress
    $url = "http://185.17.141.230:8080/api/events/"

    try {
        # Создаем HTTP запрос
        $request = [System.Net.HttpWebRequest]::Create($url)
        $request.Method = "POST"
        $request.ContentType = "application/json"
        $request.Headers.Add("Authorization", "Token $token")
        $request.Headers.Add("X-CSRFToken", $csrfToken)
        $request.Headers.Add("Cookie", "csrftoken=$csrfToken")
        $request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        $request.Timeout = 10000
        $request.KeepAlive = $false
        $request.Proxy = $null  # Отключаем прокси
        
        # Пишем данные
        $requestStream = $request.GetRequestStream()
        $writer = New-Object System.IO.StreamWriter($requestStream, $utf8NoBom)
        $writer.Write($jsonData)
        $writer.Flush()
        $writer.Close()
        $requestStream.Close()
        
        # Получаем ответ
        $response = $request.GetResponse()
        $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
        $content = $reader.ReadToEnd()
        $reader.Close()
        $response.Close()
        
        # Парсим JSON
        $createdEvent = $content | ConvertFrom-Json
        
        Write-Host "✅ УСПЕХ! Создано событие для группы ID $groupId" -ForegroundColor Green
        Write-Host "   ID события: $($createdEvent.id)" -ForegroundColor Cyan
        
        $createdEvents += [PSCustomObject]@{
            GroupID = $groupId
            EventID = $createdEvent.id
            EventName = $createdEvent.name
            Status = "Успешно"
        }
        
        $successCount++
        
        # Пауза между успешными запросами
        Start-Sleep -Milliseconds 300
        
    }
    catch [System.Net.WebException] {
        $errorCount++
        
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            
            # Получаем тело ошибки
            $errorStream = $_.Exception.Response.GetResponseStream()
            $errorReader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $errorReader.ReadToEnd()
            $errorReader.Close()
            $errorStream.Close()
            
            if ($statusCode -eq 400 -or $statusCode -eq 403 -or $statusCode -eq 404) {
                $errorPreview = $errorBody.Substring(0, [Math]::Min(80, $errorBody.Length))
                
                if ($errorBody -like "*object does not exist*" -or $errorBody -like "*Invalid pk*") {
                    Write-Host ("❌ ID {0} - группа не существует: {1}" -f $groupId, $errorPreview) -ForegroundColor DarkGray
                    $createdEvents += [PSCustomObject]@{
                        GroupID = $groupId
                        EventID = "N/A"
                        EventName = "N/A"
                        Status = "Группа не существует"
                    }
                } else {
                    Write-Host ("⚠️  ID {0} - ошибка {1}: {2}" -f $groupId, $statusCode, $errorPreview) -ForegroundColor Yellow
                    $createdEvents += [PSCustomObject]@{
                        GroupID = $groupId
                        EventID = "N/A"
                        EventName = "N/A"
                        Status = "Ошибка $statusCode"
                    }
                }
            } else {
                Write-Host ("❌ ID {0} - HTTP ошибка: {1}" -f $groupId, $statusCode) -ForegroundColor Red
                $createdEvents += [PSCustomObject]@{
                    GroupID = $groupId
                    EventID = "N/A"
                    EventName = "N/A"
                    Status = "Ошибка соединения"
                }
            }
        } else {
            Write-Host ("❌ ID {0} - ошибка соединения: {1}" -f $groupId, $_.Exception.Message) -ForegroundColor Red
            $createdEvents += [PSCustomObject]@{
                GroupID = $groupId
                EventID = "N/A"
                EventName = "N/A"
                Status = "Ошибка соединения"
            }
        }
        
        # Пауза после ошибки
        Start-Sleep -Milliseconds 200
    }
    catch {
        $errorCount++
        Write-Host ("⚠️  ID {0} - общая ошибка: {1}" -f $groupId, $_.Exception.Message) -ForegroundColor Yellow
        $createdEvents += [PSCustomObject]@{
            GroupID = $groupId
            EventID = "N/A"
            EventName = "N/A"
            Status = "Общая ошибка"
        }
        
        Start-Sleep -Milliseconds 200
    }
    
    # Промежуточная статистика
    if ($groupId % 5 -eq 0) {
        Write-Host "📊 Прогресс: $groupId/34 | Успешно: $successCount | Ошибок: $errorCount" -ForegroundColor Cyan
    }
}

# Результаты
Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ ГРУПП 1-34:" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

if ($createdEvents.Count -gt 0) {
    Write-Host "📋 Все группы:" -ForegroundColor Green
    $createdEvents | Format-Table GroupID, EventID, EventName, Status -AutoSize
    
    $successGroups = $createdEvents | Where-Object { $_.Status -eq "Успешно" }
    Write-Host "🎯 Найдено рабочих групп: $($successGroups.Count)" -ForegroundColor Cyan
    
    if ($successGroups.Count -gt 0) {
        Write-Host "✅ Рабочие ID групп: $($successGroups.GroupID -join ', ')" -ForegroundColor Green
    }
    
    # Сохраняем результаты
    $createdEvents | Export-Csv -Path "groups_check_results.csv" -NoTypeInformation -Encoding UTF8
    Write-Host "💾 Результаты сохранены в groups_check_results.csv" -ForegroundColor Green
} else {
    Write-Host "❌ Не найдено рабочих групп в диапазоне 1-34" -ForegroundColor Red
    Write-Host "📊 Статистика: Всего ошибок: $errorCount" -ForegroundColor Yellow
}

# Итоговая статистика
Write-Host "`n📈 ИТОГО:" -ForegroundColor Cyan
Write-Host "   Всего проверено: 34" -ForegroundColor Gray
Write-Host "   Успешно: $successCount" -ForegroundColor Green
Write-Host "   Ошибок: $errorCount" -ForegroundColor Red
if ($successCount -gt 0) {
    Write-Host "   Успешность: $([math]::Round(($successCount/34)*100, 1))%" -ForegroundColor Cyan
}