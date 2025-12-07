<!DOCTYPE html>
<html>
<head>
    <title>Лабораторная SQL - PostgreSQL</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { border: 1px solid #ccc; padding: 20px; margin: 10px 0; }
        button { padding: 10px; margin: 5px; }
        .result { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #e0e0e0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Лабораторная работа: Базы данных и SQL (PostgreSQL)</h1>
        
        <div class="section">
            <h2>Создание таблиц</h2>
            <button onclick="runSQL('create')">Создать таблицы</button>
        </div>
        
        <div class="section">
            <h2>Вставка данных</h2>
            <button onclick="runSQL('insert')">Вставить данные</button>
        </div>
        
        <div class="section">
            <h2>Выполнение запросов</h2>
            <button onclick="runSQL('query1')">Студенты 4 курса</button>
            <button onclick="runSQL('query2')">Лаборатория для Иванова</button>
            <button onclick="runSQL('query3')">Студенты 1 курса</button>
            <button onclick="runSQL('query4')">Работа в лаборатории 1</button>
            <button onclick="runSQL('query5')">Студенты с плазмой в маг. поле</button>
        </div>
        
        <div id="result" class="result"></div>
    </div>

    <script>
        async function runSQL(action) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Выполнение...';
            
            try {
                const response = await fetch('execute.php', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'action=' + action
                });
                const data = await response.text();
                resultDiv.innerHTML = data;
            } catch (error) {
                resultDiv.innerHTML = 'Ошибка: ' + error.message;
            }
        }
    </script>
</body>
</html>