# ========== ВАЖНОЕ ДОБАВЛЕНИЕ ==========
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12 -bor [System.Net.SecurityProtocolType]::Tls11 -bor [System.Net.SecurityProtocolType]::Tls
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
# =======================================

Write-Host "🚀 Перебор всех вариантов параметров для групп 1-34..." -ForegroundColor Red

$token = "e1696c58c1fc6fdbdedd027887a6920c280cd45e"
$csrfToken = "4wG9bkx8p4vMY5qMgtPu9BBp1nhrPYDH5BLGM0sY9HTchbWXbHFms1xiHiQr1bli"
[System.Net.ServicePointManager]::DefaultConnectionLimit = 100

# Создаем кодировку UTF-8 без BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# Массив для результатов
$results = @()
$totalAttempts = 0
$successCount = 0
$errorCount = 0

# Все варианты параметров
$confirmEvidenceValues = @($true, $false)
$conflictResolvingValues = 1..3
$goalSelectingValues = 1..3

# Только существующие группы
$groupIds = 1..34

Write-Host "🎯 Всего комбинаций: $($confirmEvidenceValues.Count * $conflictResolvingValues.Count * $goalSelectingValues.Count * $groupIds.Count)" -ForegroundColor Cyan

# Основной цикл по группам
foreach ($groupId in $groupIds) {
    Write-Host "`n📊 Проверка группы ID: $groupId" -ForegroundColor Yellow
    
    # Вложенные циклы по параметрам
    foreach ($confirmEvidence in $confirmEvidenceValues) {
        foreach ($conflictResolving in $conflictResolvingValues) {
            foreach ($goalSelecting in $goalSelectingValues) {
                $totalAttempts++
                
                # Данные для создания события
                $eventData = @{
                    name = "993_obratny"
                    component = 1
                    starts = "2025-11-13T11:30:00Z"
                    finishes = "2025-11-13T13:05:00Z"
                    interval = 2400
                    for_group = $true
                    blocks_next = $true
                    group = $groupId
                    meta = @{
                        knowledge_base = 993
                        confirm_evidence = $confirmEvidence
                        conflict_resolving = $conflictResolving
                        inference_direction = 2
                        goal_selecting = $goalSelecting
                    }
                }
                
                $jsonData = $eventData | ConvertTo-Json -Depth 5 -Compress
                $url = "http://185.17.141.230:8080/api/events/"
                
                $comboString = "Гр:$groupId, Подт:$confirmEvidence, Конф:$conflictResolving, Цель:$goalSelecting"
                
                try {
                    # Создаем HTTP запрос
                    $request = [System.Net.HttpWebRequest]::Create($url)
                    $request.Method = "POST"
                    $request.ContentType = "application/json"
                    $request.Headers.Add("Authorization", "Token $token")
                    $request.Headers.Add("X-CSRFToken", $csrfToken)
                    $request.Headers.Add("Cookie", "csrftoken=$csrfToken")
                    $request.UserAgent = "Mozilla/5.0"
                    $request.Timeout = 8000
                    $request.KeepAlive = $false
                    $request.Proxy = $null
                    
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
                    
                    Write-Host "✅ УСПЕХ! $comboString" -ForegroundColor Green
                    Write-Host "   ID события: $($createdEvent.id)" -ForegroundColor Cyan
                    
                    $results += [PSCustomObject]@{
                        GroupID = $groupId
                        EventID = $createdEvent.id
                        EventName = $createdEvent.name
                        ConfirmEvidence = $confirmEvidence
                        ConflictResolving = $conflictResolving
                        GoalSelecting = $goalSelecting
                        Status = "Успешно"
                        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                    
                    $successCount++
                    
                    # Краткая пауза
                    Start-Sleep -Milliseconds 100
                    
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
                        
                        $results += [PSCustomObject]@{
                            GroupID = $groupId
                            EventID = "N/A"
                            EventName = "N/A"
                            ConfirmEvidence = $confirmEvidence
                            ConflictResolving = $conflictResolving
                            GoalSelecting = $goalSelecting
                            Status = "Ошибка $statusCode"
                            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                        }
                        
                        # Только периодически выводим ошибки
                        if ($totalAttempts % 10 -eq 0) {
                            Write-Host "⚠️  $comboString - ошибка $statusCode" -ForegroundColor DarkYellow
                        }
                    } else {
                        $results += [PSCustomObject]@{
                            GroupID = $groupId
                            EventID = "N/A"
                            EventName = "N/A"
                            ConfirmEvidence = $confirmEvidence
                            ConflictResolving = $conflictResolving
                            GoalSelecting = $goalSelecting
                            Status = "Ошибка соединения"
                            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                        }
                    }
                    
                    Start-Sleep -Milliseconds 50
                }
                catch {
                    $errorCount++
                    $results += [PSCustomObject]@{
                        GroupID = $groupId
                        EventID = "N/A"
                        EventName = "N/A"
                        ConfirmEvidence = $confirmEvidence
                        ConflictResolving = $conflictResolving
                        GoalSelecting = $goalSelecting
                        Status = "Общая ошибка"
                        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                    
                    Start-Sleep -Milliseconds 50
                }
                
                # Промежуточная статистика
                if ($totalAttempts % 50 -eq 0) {
                    Write-Host "📈 Пройдено: $totalAttempts | Успешно: $successCount | Ошибок: $errorCount" -ForegroundColor Cyan
                }
            }
        }
    }
}

# Результаты
Write-Host "`n" + "="*70 -ForegroundColor Green
Write-Host "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ПЕРЕБОРА ВСЕХ ВАРИАНТОВ" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

if ($successCount -gt 0) {
    Write-Host "✅ УСПЕШНЫЕ КОМБИНАЦИИ:" -ForegroundColor Green
    
    $successResults = $results | Where-Object { $_.Status -eq "Успешно" } | Select-Object GroupID, ConfirmEvidence, ConflictResolving, GoalSelecting, EventID
    
    # Группируем по ID группы для удобства
    $groupedResults = $successResults | Group-Object GroupID
    
    foreach ($group in $groupedResults) {
        Write-Host "`n🎯 Группа ID $($group.Name):" -ForegroundColor Yellow
        $group.Group | Format-Table -Property @{
            Name="Подтверждение"; Expression={$_.ConfirmEvidence}
        }, @{
            Name="Конфликт"; Expression={$_.ConflictResolving}
        }, @{
            Name="Цель"; Expression={$_.GoalSelecting}
        }, @{
            Name="ID события"; Expression={$_.EventID}
        } -AutoSize
    }
    
    # Сохраняем все результаты
    $results | Export-Csv -Path "all_combinations_results.csv" -NoTypeInformation -Encoding UTF8
    Write-Host "💾 Все результаты сохранены в all_combinations_results.csv" -ForegroundColor Green
    
    # Сохраняем только успешные
    $successResults | Export-Csv -Path "successful_combinations.csv" -NoTypeInformation -Encoding UTF8
    Write-Host "💾 Успешные комбинации сохранены в successful_combinations.csv" -ForegroundColor Green
} else {
    Write-Host "❌ Не найдено ни одной успешной комбинации" -ForegroundColor Red
}

# Итоговая статистика
Write-Host "`n" + "="*50 -ForegroundColor Cyan
Write-Host "📈 ИТОГОВАЯ СТАТИСТИКА:" -ForegroundColor Cyan
Write-Host "="*50 -ForegroundColor Cyan
Write-Host "   Всего попыток: $totalAttempts" -ForegroundColor Gray
Write-Host "   Успешно: $successCount" -ForegroundColor Green
Write-Host "   Ошибок: $errorCount" -ForegroundColor Red
if ($totalAttempts -gt 0) {
    $successRate = [math]::Round(($successCount/$totalAttempts)*100, 2)
    Write-Host "   Успешность: ${successRate}%" -ForegroundColor Cyan
}

# Краткая сводка по группам
if ($successCount -gt 0) {
    Write-Host "`n🎯 ГРУППЫ С РАБОЧИМИ КОМБИНАЦИЯМИ:" -ForegroundColor Cyan
    $successGroups = ($results | Where-Object { $_.Status -eq "Успешно" } | Select-Object -Unique GroupID).GroupID
    Write-Host "   ID групп: $($successGroups -join ', ')" -ForegroundColor Green
}