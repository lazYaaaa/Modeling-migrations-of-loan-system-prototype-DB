<?php
/**
 * Load data from all_data.json to database
 */

require_once __DIR__ . '/api/config/database.php';

echo "=== Загрузка исходных данных ===\n\n";

$json_file = __DIR__ . '/../all_data.json';

if (!file_exists($json_file)) {
    echo "✗ Файл all_data.json не найден\n";
    exit(1);
}

$json_data = json_decode(file_get_contents($json_file), true);

if (!$json_data) {
    echo "✗ Ошибка при чтении JSON файла\n";
    exit(1);
}

try {
    $pdo->beginTransaction();
    
    // Clear existing data
    echo "1. Очистка существующих данных...\n";
    $pdo->exec("TRUNCATE TABLE employees CASCADE");
    $pdo->exec("TRUNCATE TABLE clients CASCADE");
    
    $employees = [];
    $clients = [];
    
    // Parse JSON
    echo "2. Обработка данных из JSON...\n";
    
    foreach ($json_data as $item) {
        if ($item['source_table'] == 'employees') {
            $employees[] = $item;
        } elseif ($item['source_table'] == 'clients') {
            $clients[] = $item;
        }
    }
    
    // Insert employees
    echo "3. Загрузка сотрудников (" . count($employees) . ")...\n";
    
    $emp_insert = "INSERT INTO employees (employee_id, full_name, position, login, password_hash, status) 
                  VALUES (?, ?, ?, ?, ?, ?)";
    $emp_stmt = $pdo->prepare($emp_insert);
    
    foreach ($employees as $emp) {
        $passwordHash = password_hash($emp['unique_identifier'], PASSWORD_DEFAULT);
        $emp_stmt->execute([
            $emp['id'],
            $emp['name'],
            $emp['details'],
            $emp['unique_identifier'],
            $passwordHash,
            $emp['additional_info']
        ]);
        echo "  ✓ " . $emp['name'] . " (" . $emp['unique_identifier'] . ")\n";
    }
    
    // Insert clients
    echo "\n4. Загрузка клиентов (" . count($clients) . ")...\n";
    
    $cli_insert = "INSERT INTO clients (client_id, full_name, passport_number, phone_number) 
                  VALUES (?, ?, ?, ?)";
    $cli_stmt = $pdo->prepare($cli_insert);
    
    foreach ($clients as $client) {
        $phone = null;
        if (preg_match('/\+\d+/', $client['additional_info'], $matches)) {
            $phone = $matches[0];
        }
        
        $cli_stmt->execute([
            $client['id'],
            $client['name'],
            $client['unique_identifier'],
            $phone
        ]);
        echo "  ✓ " . $client['name'] . " (" . $client['unique_identifier'] . ")\n";
    }
    
    $pdo->commit();
    
    echo "\n=== Загрузка завершена ===\n";
    echo "✓ " . count($employees) . " сотрудников загружено\n";
    echo "✓ " . count($clients) . " клиентов загружено\n";
    
} catch (Exception $e) {
    $pdo->rollBack();
    echo "Ошибка: " . $e->getMessage() . "\n";
    exit(1);
}
?>
