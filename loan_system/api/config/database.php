<?php
// Database Configuration
$db_host = 'localhost';
$db_port = 5432;
$db_name = 'loan_system';
$db_user = 'postgres';
$db_password = 'postgres';

// Connection string
$dsn = "pgsql:host=$db_host;port=$db_port;dbname=$db_name";

try {
    $pdo = new PDO($dsn, $db_user, $db_password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec("SET client_encoding = 'UTF8'");
} catch (PDOException $e) {
    die('Database connection failed: ' . $e->getMessage());
}
?>
