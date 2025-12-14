<?php
/**
 * Database setup script
 * Создает все необходимые таблицы для системы управления кредитованием
 */

require_once __DIR__ . '/api/config/database.php';

echo "=== Setup базы данных ===\n\n";

try {
    // Проверка расширения
    echo "1. Проверка расширений PHP...\n";
    if (!extension_loaded('pdo_pgsql')) {
        echo "✗ Требуется расширение pdo_pgsql\n";
        exit(1);
    }
    echo "✓ PDO PostgreSQL загружен\n\n";
    
    // Тестирование подключения
    echo "2. Тестирование подключения к БД...\n";
    $test = $pdo->query("SELECT VERSION()");
    $version = $test->fetch();
    echo "✓ PostgreSQL: " . substr($version[0], 0, 50) . "...\n\n";
    
    // Создание таблиц
    echo "3. Создание/проверка таблиц...\n";
    
    $pdo->beginTransaction();
    
    // Таблица сотрудников
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS employees (
            employee_id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            position VARCHAR(100) NOT NULL,
            login VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255),
            status VARCHAR(20) DEFAULT 'Активен'
        )
    ");
    echo "  ✓ employees\n";

    // Ensure password_hash column exists for older installs
    $pdo->exec("ALTER TABLE employees ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)");
    
    // Таблица клиентов
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS clients (
            client_id SERIAL PRIMARY KEY,
            full_name VARCHAR(255) NOT NULL,
            passport_number VARCHAR(50) NOT NULL UNIQUE,
            phone_number VARCHAR(20),
            address TEXT
        )
    ");
    echo "  ✓ clients\n";
    
    // Таблица кредитных продуктов
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS loan_products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            min_amount NUMERIC(15, 2) NOT NULL CHECK (min_amount >= 0),
            max_amount NUMERIC(15, 2) NOT NULL CHECK (max_amount >= min_amount),
            min_term INTEGER NOT NULL CHECK (min_term > 0),
            max_term INTEGER NOT NULL CHECK (max_term >= min_term),
            base_interest_rate NUMERIC(5, 2) NOT NULL CHECK (base_interest_rate >= 0)
        )
    ");
    echo "  ✓ loan_products\n";
    
    // Таблица документов
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS documents (
            document_id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
            document_type VARCHAR(100) NOT NULL,
            series_number VARCHAR(100) NOT NULL,
            issued_by VARCHAR(255),
            issue_date DATE
        )
    ");
    echo "  ✓ documents\n";
    
    // Таблица кредитной истории
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS credit_history (
            history_id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
            event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            source VARCHAR(100) DEFAULT 'Внутренняя'
        )
    ");
    echo "  ✓ credit_history\n";
    
    // Таблица кредитных заявок
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS credit_applications (
            application_id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
            employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
            product_id INTEGER NOT NULL REFERENCES loan_products(product_id) ON DELETE RESTRICT,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            requested_amount NUMERIC(15, 2) NOT NULL CHECK (requested_amount > 0),
            status VARCHAR(20) DEFAULT 'Новая'
        )
    ");
    echo "  ✓ credit_applications\n";
    
    // Таблица документов для заявок
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS application_documents (
            application_id INTEGER NOT NULL REFERENCES credit_applications(application_id) ON DELETE CASCADE,
            document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
            PRIMARY KEY (application_id, document_id)
        )
    ");
    echo "  ✓ application_documents\n";
    
    // Таблица счетов
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS accounts (
            account_id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
            account_number VARCHAR(34) NOT NULL UNIQUE,
            account_type VARCHAR(50) NOT NULL,
            current_balance NUMERIC(15, 2) DEFAULT 0
        )
    ");
    echo "  ✓ accounts\n";
    
    // Таблица кредитных контрактов
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS credit_contracts (
            contract_id SERIAL PRIMARY KEY,
            application_id INTEGER NOT NULL UNIQUE REFERENCES credit_applications(application_id) ON DELETE RESTRICT,
            product_id INTEGER NOT NULL REFERENCES loan_products(product_id) ON DELETE RESTRICT,
            account_id INTEGER NOT NULL UNIQUE REFERENCES accounts(account_id) ON DELETE RESTRICT,
            contract_number VARCHAR(100) NOT NULL UNIQUE,
            signing_date DATE NOT NULL,
            loan_amount NUMERIC(15, 2) NOT NULL CHECK (loan_amount > 0),
            interest_rate NUMERIC(5, 2) NOT NULL CHECK (interest_rate >= 0),
            loan_term INTEGER NOT NULL CHECK (loan_term > 0)
        )
    ");
    echo "  ✓ credit_contracts\n";
    
    // Таблица графика платежей
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS payment_schedule (
            schedule_id SERIAL PRIMARY KEY,
            contract_id INTEGER NOT NULL REFERENCES credit_contracts(contract_id) ON DELETE CASCADE,
            payment_date DATE NOT NULL,
            payment_amount NUMERIC(15, 2) NOT NULL CHECK (payment_amount >= 0),
            status VARCHAR(20) DEFAULT 'Ожидает оплаты'
        )
    ");
    echo "  ✓ payment_schedule\n";
    
    // Таблица платежей
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS payments (
            payment_id SERIAL PRIMARY KEY,
            schedule_id INTEGER REFERENCES payment_schedule(schedule_id) ON DELETE SET NULL,
            account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
            operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_amount NUMERIC(15, 2) NOT NULL CHECK (paid_amount > 0),
            operation_type VARCHAR(50) NOT NULL
        )
    ");
    echo "  ✓ payments\n";
    
    // Таблица блокировок (специальная для системы)
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS application_locks (
            lock_id SERIAL PRIMARY KEY,
            application_id INTEGER NOT NULL UNIQUE,
            locked_by INTEGER NOT NULL,
            locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timeout_at TIMESTAMP NOT NULL,
            FOREIGN KEY (application_id) REFERENCES credit_applications(application_id) ON DELETE CASCADE,
            FOREIGN KEY (locked_by) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
    ");
    echo "  ✓ application_locks\n";
    
    $pdo->commit();
    
    echo "\n=== Успешно ===\n";
    echo "Все таблицы созданы!\n";
    echo "\nСледующий шаг: php load_data.php\n";
    
} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    echo "✗ Ошибка: " . $e->getMessage() . "\n";
    exit(1);
}
?>
