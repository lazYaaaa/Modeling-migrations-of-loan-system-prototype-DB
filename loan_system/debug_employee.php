<?php
require_once __DIR__ . '/api/config/database.php';

$login = $argv[1] ?? 'user_1';

echo "Checking employee: $login\n\n";

$stmt = $pdo->prepare('SELECT * FROM employees WHERE login = ?');
$stmt->execute([$login]);
$emp = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$emp) {
    echo "Employee not found.\n";
    exit(1);
}

echo "Row output:\n";
print_r($emp);

$hash = $emp['password_hash'] ?? null;
if (!$hash) {
    echo "\npassword_hash is empty or null.\n";
    exit(1);
}

echo "\nVerifying password '" . $login . "' against stored hash...\n";
if (password_verify($login, $hash)) {
    echo "Password verification OK\n";
    exit(0);
} else {
    echo "Password verification FAILED\n";
    exit(2);
}
