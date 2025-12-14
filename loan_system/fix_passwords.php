<?php
require_once __DIR__ . '/api/config/database.php';

echo "=== Fixing empty employee password_hash fields ===\n\n";

$stmt = $pdo->query("SELECT employee_id, login, full_name, password_hash FROM employees");
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

$update = $pdo->prepare("UPDATE employees SET password_hash = ? WHERE employee_id = ?");
$count = 0;

foreach ($rows as $r) {
    if (empty($r['password_hash'])) {
        $newHash = password_hash($r['login'], PASSWORD_DEFAULT);
        $update->execute([$newHash, $r['employee_id']]);
        echo "Updated {$r['full_name']} ({$r['login']})\n";
        $count++;
    }
}

echo "\nDone. Password hashes updated for {$count} employees.\n";
