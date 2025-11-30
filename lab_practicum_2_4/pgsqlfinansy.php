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

if ($_POST['action'] ?? '' == 'add') {
    $dept = $_POST['Dept'] ?? '';
    $summ = $_POST['Summ'] ?? '';
    
    if (!empty($dept) && is_numeric($summ)) {
        try {
            $stmt = $db->prepare("INSERT INTO finansy (dept, summ) VALUES (?, ?)");
            $stmt->execute([$dept, floatval($summ)]);
        } catch (PDOException $e) {
            $error = "Ошибка при добавлении: " . $e->getMessage();
        }
    }
}
?>
<html>
<head>
    <title>Задание 4. Редактор таблицы PostgreSQL</title>
</head>
<body>
    <h2>Таблица Finansy</h2>
    
    <?php if (isset($error)): ?>
        <div style="color: red;"><?= $error ?></div>
    <?php endif; ?>

    <form method="post" style="margin-bottom: 20px;">
        <input type="text" name="Dept" placeholder="Отдел" required size="12">
        <input type="number" step="0.01" name="Summ" placeholder="Сумма" required size="8">
        <input type="hidden" name="action" value="add">
        <input type="submit" value="Добавить">
    </form>
    
    <?php
    try {
        $stmt = $db->query("SELECT * FROM finansy ORDER BY dept");
        echo "<table border='1' cellpadding='5'>";
        echo "<tr><th>ID</th><th>Отдел</th><th>Сумма</th></tr>";
        
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            echo "<tr>";
            echo "<td>" . $row['idf'] . "</td>";
            echo "<td>" . htmlspecialchars($row['dept']) . "</td>";
            echo "<td>" . $row['summ'] . "</td>";
            echo "</tr>";
        }
        echo "</table>";
        
    } catch (PDOException $e) {
        echo "Ошибка при чтении данных: " . $e->getMessage();
    }
    ?>
</body>
</html>