<?php
$host = 'localhost';
$port = '5432';
$dbname = 'student_labs'; 
$user = 'postgres';
$password = 'postgres';

$action = $_POST['action'] ?? '';

try {
    $conn = new PDO("pgsql:host=$host;port=$port;dbname=postgres", $user, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $stmt = $conn->query("SELECT 1 FROM pg_database WHERE datname = 'student_labs'");
    $dbExists = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$dbExists) {
        $conn->exec("CREATE DATABASE student_labs");
        echo "База данных 'student_labs' создана успешно<br>";
    } else {
        echo "База данных 'student_labs' уже существует<br>";
    }
    
    $conn = new PDO("pgsql:host=$host;port=$port;dbname=student_labs", $user, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    echo "<h3>Результат выполнения:</h3>";
    
    switch($action) {
        case 'create':
            if (!file_exists('create_tables.sql')) {
                echo "Файл create_tables.sql не найден";
                break;
            }
            $sql = file_get_contents('create_tables.sql');
            $conn->exec($sql);
            echo "Таблицы успешно созданы";
            break;
            
        case 'insert':
            if (!file_exists('insert_data.sql')) {
                echo "Файл insert_data.sql не найден";
                break;
            }
            $sql = file_get_contents('sql/2_insert_data.sql');
            $conn->exec($sql);
            echo "Данные успешно вставлены";
            break;
            
        case 'query1':
            $stmt = $conn->query("SELECT * FROM Student WHERE Year = 4");
            displayResults($stmt);
            break;
            
        case 'query2':
            $stmt = $conn->query("SELECT LabNum FROM Student, Plan, Work WHERE
                Plan.WorkNum = Work.Number AND
                Plan.StudentId = Student.Id AND
                Student.Name = 'Иванов И. И.' AND
                Work.Name = 'Изучение плазмы в открытом поле'");
            displayResults($stmt);
            break;
            
        case 'query3':
            $stmt = $conn->query("SELECT * FROM Student WHERE Year = 1");
            displayResults($stmt);
            break;
            
        case 'query4':
            $stmt = $conn->query("SELECT Student.Name FROM Student, Plan 
                WHERE WorkNum = 1 AND LabNum = 1 
                AND Plan.StudentId = Student.Id");
            displayResults($stmt);
            break;
            
        case 'query5':
            $stmt = $conn->query("SELECT Student.Name FROM Student, Plan, Work 
                WHERE LabNum = 1 AND
                Plan.WorkNum = Work.Number AND
                Plan.StudentId = Student.Id AND
                Work.Name = 'Изучение плазмы в магнитном поле'");
            displayResults($stmt);
            break;
            
        default:
            echo "Выберите действие";
    }
    
} catch(PDOException $e) {
    echo "Ошибка: " . $e->getMessage();
}

function displayResults($stmt) {
    if (!$stmt) {
        echo "Ошибка выполнения запроса";
        return;
    }
    
    echo "<table border='1' cellpadding='5'>";
    echo "<tr>";
    for ($i = 0; $i < $stmt->columnCount(); $i++) {
        $col = $stmt->getColumnMeta($i);
        echo "<th>" . htmlspecialchars($col['name']) . "</th>";
    }
    echo "</tr>";
    
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        echo "<tr>";
        foreach ($row as $value) {
            echo "<td>" . htmlspecialchars($value) . "</td>";
        }
        echo "</tr>";
    }
    echo "</table>";
}
?>