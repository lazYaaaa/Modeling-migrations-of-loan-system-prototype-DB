<?php
/**
 * Create demo data for testing
 */

require_once __DIR__ . '/api/config/database.php';

echo "=== Создание демо-данных ===\n\n";

try {
    $pdo->beginTransaction();
    
    // Проверка существующих данных
    $check_emp = $pdo->query("SELECT COUNT(*) as count FROM employees")->fetch();
    $check_cli = $pdo->query("SELECT COUNT(*) as count FROM clients")->fetch();
    
    if ($check_emp['count'] > 0 || $check_cli['count'] > 0) {
        echo "⚠ В системе уже присутствуют данные\n";
        echo "Текущие сотрудники: " . $check_emp['count'] . "\n";
        echo "Текущие клиенты: " . $check_cli['count'] . "\n";
        echo "\nДемо-данные загружены автоматически из all_data.json\n";
        exit(0);
    }
    
    // Создание сотрудников
    echo "1. Создание сотрудников...\n";
    
    $employees = [
        ['Варвара Валентиновна Соколова', 'Менеджер по кредитованию', 'user_1', 'Активен'],
        ['Логинов Никита Теймуразович', 'Менеджер по кредитованию', 'user_2', 'Активен'],
        ['Зуев Станимир Демидович', 'Специалист по кредитованию', 'user_3', 'Активен'],
        ['Таисия Аскольдовна Киселева', 'Специалист по кредитованию', 'user_4', 'Активен'],
        ['Панфил Гаврилович Гордеев', 'Менеджер по кредитованию', 'user_5', 'Активен'],
        ['Дорофеева Полина Валериевна', 'Руководитель по кредитованию', 'user_6', 'Активен'],
        ['Федосий Гордеевич Голубев', 'Специалист по кредитованию', 'user_7', 'Активен'],
        ['Кузьмин Гордей Чеславович', 'Специалист по кредитованию', 'user_8', 'Активен'],
        ['Денисов Кир Бенедиктович', 'Аналитик по кредитованию', 'user_9', 'Активен'],
        ['Мартын Антонович Большаков', 'Руководитель по кредитованию', 'user_10', 'Активен'],
    ];
    
    $emp_insert = $pdo->prepare("INSERT INTO employees (full_name, position, login, password_hash, status) VALUES (?, ?, ?, ?, ?)");
    
    foreach ($employees as $emp) {
        // For demo set password equal to login (user_1 -> password 'user_1')
        $passwordHash = password_hash($emp[2], PASSWORD_DEFAULT);
        $emp_insert->execute([$emp[0], $emp[1], $emp[2], $passwordHash, $emp[3]]);
        echo "  ✓ " . $emp[0] . " (" . $emp[2] . ") - password set to login (hashed)\n";
    }
    
    // Создание клиентов
    echo "\n2. Создание клиентов...\n";
    
    $clients = [
        ['Сорокина Анна Владимировна', '8694 973235', '+79391008512'],
        ['Парамонов Валерий Егорович', '5923 847261', '+79271345678'],
        ['Щукина Инна Тимофеевна', '4521 639847', '+79129876543'],
        ['Маслов Владимир Захарович', '7365 482917', '+79195467823'],
        ['Иванова Елена Сергеевна', '2846 719534', '+79081234567'],
    ];
    
    $cli_insert = $pdo->prepare("INSERT INTO clients (full_name, passport_number, phone_number) VALUES (?, ?, ?)");
    
    foreach ($clients as $cli) {
        $cli_insert->execute($cli);
        echo "  ✓ " . $cli[0] . "\n";
    }
    
    // Создание кредитных продуктов
    echo "\n3. Создание кредитных продуктов...\n";
    
    $products = [
        ['Потребительский кредит', 50000, 500000, 12, 60, 12.5],
        ['Ипотечный кредит', 500000, 10000000, 60, 300, 8.5],
        ['Автокредит', 200000, 3000000, 12, 84, 10.0],
        ['Бизнес-кредит', 100000, 5000000, 12, 120, 14.0],
    ];
    
    $prod_insert = $pdo->prepare("INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate) VALUES (?, ?, ?, ?, ?, ?)");
    
    foreach ($products as $prod) {
        $prod_insert->execute($prod);
        echo "  ✓ " . $prod[0] . "\n";
    }
    
    // Создание тестовых заявок
    echo "\n4. Создание тестовых заявок...\n";
    
    $test_apps = [
        [1, 1, 1, 150000, 'Новая'],
        [2, 2, 2, 1500000, 'Новая'],
        [3, 3, 3, 350000, 'Новая'],
        [4, 4, 4, 250000, 'В работе'],
        [5, 5, 1, 100000, 'Одобрена'],
    ];
    
    $app_insert = $pdo->prepare("INSERT INTO credit_applications (client_id, employee_id, product_id, requested_amount, status) VALUES (?, ?, ?, ?, ?)");
    
    foreach ($test_apps as $app) {
        $app_insert->execute($app);
        echo "  ✓ Заявка для клиента " . $app[0] . " на сумму " . number_format($app[3], 0) . " ₽\n";
    }
    
    $pdo->commit();
    
    echo "\n=== Данные созданы ===\n";
    echo "Сотрудников: " . count($employees) . "\n";
    echo "Клиентов: " . count($clients) . "\n";
    echo "Продуктов: " . count($products) . "\n";
    echo "Тестовых заявок: " . count($test_apps) . "\n";
    echo "\nДля входа используйте:\n";
    echo "  Логин: user_1 (или user_2, ..., user_10)\n";
    echo "  Пароль: любой\n";
    
} catch (Exception $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    echo "✗ Ошибка: " . $e->getMessage() . "\n";
    exit(1);
}
?>
