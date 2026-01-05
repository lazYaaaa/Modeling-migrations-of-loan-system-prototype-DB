<?php
/**
 * Database Initialization Script
 * Создает все необходимые таблицы и импортирует исходные данные
 */

require_once __DIR__ . '/api/config/database.php';


try {
    // Check if tables exist
    echo "1. Проверка существования таблиц...\n";
    
    $tables = [
        'employees', 'clients', 'loan_products', 'documents',
        'credit_history', 'credit_applications', 'application_documents',
        'accounts', 'credit_contracts', 'payment_schedule', 'payments'
    ];
    
    $result = $pdo->query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'");
    $existing_tables = $result->fetchAll(PDO::FETCH_COLUMN);
    
    $missing = array_diff($tables, $existing_tables);
    
    if (empty($missing)) {
        echo "✓ Все таблицы уже существуют\n\n";
    } else {
        echo "✗ Отсутствуют таблицы: " . implode(', ', $missing) . "\n";
        echo "Пожалуйста, запустите main_migration_file.sql\n";
        exit(1);
    }
    
    // Create locks table
    echo "2. Создание таблицы блокировок...\n";
    
    $create_locks = "
        CREATE TABLE IF NOT EXISTS application_locks (
            lock_id SERIAL PRIMARY KEY,
            application_id INTEGER NOT NULL UNIQUE,
            locked_by INTEGER NOT NULL,
            locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timeout_at TIMESTAMP NOT NULL,
            FOREIGN KEY (application_id) REFERENCES credit_applications(application_id) ON DELETE CASCADE,
            FOREIGN KEY (locked_by) REFERENCES employees(employee_id) ON DELETE CASCADE
        )
    ";
    
    $pdo->exec($create_locks);
    echo "✓ Таблица application_locks готова\n\n";
    
    // Create app_settings table
    echo "3. Создание таблицы параметров приложения...\n";
    
    $create_settings = "
        CREATE TABLE IF NOT EXISTS app_settings (
            key VARCHAR(100) PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ";
    
    $pdo->exec($create_settings);
    
    // Initialize locks_enabled setting if not exists
    $check_locks = $pdo->prepare("SELECT value FROM app_settings WHERE key = 'locks_enabled'");
    $check_locks->execute();
    if (!$check_locks->fetch()) {
        $init_locks = $pdo->prepare("INSERT INTO app_settings (key, value) VALUES (?, ?)");
        $init_locks->execute(['locks_enabled', 'true']);
    }
    echo "✓ Таблица app_settings готова\n\n";
    
    // Load sample data from all_data.json if tables are empty
    echo "4. Проверка исходных данных...\n";
    
    $check_employees = $pdo->query("SELECT COUNT(*) as count FROM employees")->fetch();
    $check_clients = $pdo->query("SELECT COUNT(*) as count FROM clients")->fetch();
    
    if ($check_employees['count'] == 0 || $check_clients['count'] == 0) {
        echo "Требуется загрузка исходных данных из all_data.json\n";
        echo "Используйте скрипт: php initialize_data.php\n\n";
    } else {
        echo "✓ Данные уже загружены\n";
        echo "  • Сотрудников: " . $check_employees['count'] . "\n";
        echo "  • Клиентов: " . $check_clients['count'] . "\n\n";
    }
    
    // Verify products
    echo "5. Проверка кредитных продуктов...\n";
    
    $check_products = $pdo->query("SELECT COUNT(*) as count FROM loan_products")->fetch();
    
    if ($check_products['count'] == 0) {
        echo "Создание стандартных кредитных продуктов...\n";
        
        $products = [
            ['Потребительский кредит', 50000, 500000, 12, 60, 12.5],
            ['Ипотечный кредит', 500000, 10000000, 60, 300, 8.5],
            ['Автокредит', 200000, 3000000, 12, 84, 10.0],
            ['Бизнес-кредит', 100000, 5000000, 12, 120, 14.0],
        ];
        
        $insert = "INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate) 
                  VALUES (?, ?, ?, ?, ?, ?)";
        $stmt = $pdo->prepare($insert);
        
        foreach ($products as $product) {
            $stmt->execute($product);
            echo "  ✓ " . $product[0] . "\n";
        }
        
        echo "\n";
    } else {
        echo "✓ Продукты уже существуют (" . $check_products['count'] . ")\n\n";
    }
    
    // Summary
    echo "=== Инициализация завершена ===\n";
    echo "\nПриложение готово к использованию!\n";
    echo "\nДля запуска используйте:\n";
    echo "  php -S localhost:8000 (из папки frontend)\n";
    echo "\nДля входа используйте логины из таблицы employees:\n";
    echo "  user_1, user_2, user_3, ..., user_10\n";
    echo "  Пароль: любой (не проверяется в демо)\n";
    
} catch (Exception $e) {
    echo "✗ Ошибка: " . $e->getMessage() . "\n";
    exit(1);
}
?>
