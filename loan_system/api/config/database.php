<?php
// Database Configuration
// Use 'db' as host in Docker (via env), default to localhost for local dev/server
$db_host = getenv('DB_HOST') ?: 'localhost';
$db_port = getenv('DB_PORT') ?: 5432;
$db_name = getenv('DB_NAME') ?: 'loan_system';
$db_user = getenv('DB_USER') ?: 'postgres';
$db_password = getenv('DB_PASSWORD') ?: 'example';

// Connection string
$dsn = "pgsql:host=$db_host;port=$db_port;dbname=$db_name";

try {
    $pdo = new PDO($dsn, $db_user, $db_password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec("SET client_encoding = 'UTF8'");
} catch (PDOException $e) {
    // Return JSON error instead of dying with plain text
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(500);
    die(json_encode(['success' => false, 'error' => 'Database connection failed: ' . $e->getMessage()]));
}
?>
