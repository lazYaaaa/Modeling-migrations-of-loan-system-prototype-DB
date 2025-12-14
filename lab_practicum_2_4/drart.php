<?php
header('Content-Type: text/html; charset=utf-8');


$host = "localhost";
$dbname = "pktest";
$user = "postgres";
$password = "postgres";

try {
    $db = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec("SET CLIENT_ENCODING TO 'UTF8'");
} catch (PDOException $e) {
    die("Ошибка подключения: " . $e->getMessage());
}

$stmt = $db->query("SELECT dept, summ FROM finansy ORDER BY idf");
$data = [];
$config_segments = [];

$i = 1;
while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
    $data[] = "data{$i}series1:" . $row['summ'];
    $config_segments[] = "segment{$i}:|" . $row['dept'];
    $i++;
}

file_put_contents('data5.txt', implode("\n", $data));

$config_content = "
<config>
    <width>400</width>
    <height>300</height>
    <graph_type>pie</graph_type>
    <background_color>#FFFFFF</background_color>
    <title>Финансы по отделам</title>
    
    " . implode("\n", $config_segments) . "
</config>";

file_put_contents('config5.txt', $config_content);
?>

<html>
<head>
    <title>Задание 6. Диаграммы</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .chart-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }
        .chart-box {
            width: 400px;
            padding: 15px;
            border: 1px solid #ccc;
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>Задание 6: Три диаграммы</h1>

    <div class="chart-container">
        <div class="chart-box">
            <h3>1. Круговая диаграмма (Chart.js)</h3>
            <canvas id="pieChart" width="400" height="300"></canvas>
        </div>

        <div class="chart-box">
            <h3>2. Столбчатая диаграмма (Chart.js)</h3>
            <canvas id="barChart" width="400" height="300"></canvas>
        </div>

        <div class="chart-box">
            <h3>3. Линейная диаграмма (Chart.js)</h3>
            <canvas id="lineChart" width="400" height="300"></canvas>
        </div>
    </div>

    <h3>Данные из таблицы Finansy:</h3>
    <?php
    $stmt = $db->query("SELECT * FROM finansy ORDER BY dept");
    echo "<table border='1' cellpadding='5'><tr><th>Отдел</th><th>Сумма</th></tr>";
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<tr><td>" . htmlspecialchars($row['dept']) . "</td><td>" . $row['summ'] . "</td></tr>";
    }
    echo "</table>";
    ?>

    <script>

        const departments = [<?php
            $stmt = $db->query("SELECT dept FROM finansy ORDER BY idf");
            $depts = [];
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $depts[] = "'" . $row['dept'] . "'";
            }
            echo implode(', ', $depts);
        ?>];
        
        const amounts = [<?php
            $stmt = $db->query("SELECT summ FROM finansy ORDER BY idf");
            $sums = [];
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $sums[] = $row['summ'];
            }
            echo implode(', ', $sums);
        ?>];

        const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];

        new Chart(document.getElementById('pieChart'), {
            type: 'pie',
            data: {
                labels: departments,
                datasets: [{
                    data: amounts,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    title: { display: true, text: 'Распределение по отделам' }
                }
            }
        });


        new Chart(document.getElementById('barChart'), {
            type: 'bar',
            data: {
                labels: departments,
                datasets: [{
                    label: 'Сумма',
                    data: amounts,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });


        new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels: departments,
                datasets: [{
                    label: 'Финансы',
                    data: amounts,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>

    <h3>Созданные файлы для библиотеки графиков:</h3>
    <p><strong>data5.txt:</strong></p>
    <pre><?= htmlspecialchars(implode("\n", $data)) ?></pre>
    
    <p><strong>config5.txt:</strong></p>
    <pre><?= htmlspecialchars($config_content) ?></pre>
</body>
</html>