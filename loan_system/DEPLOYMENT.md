# Руководство по развертыванию системы управления кредитованием

## Быстрый старт (за 5 минут)

### Шаг 1: Подготовка БД

```bash
# Подключитесь к PostgreSQL
psql -U postgres

# Создайте БД (если не создана)
CREATE DATABASE loan_system;

# Выйдите
\q

# Загрузите схему БД
psql -U postgres -d loan_system -f /path/to/main_migration_file.sql
```

### Шаг 2: Загрузка исходных данных

```bash
cd /path/to/loan_system

# Инициализируйте БД
php initialize.php

# Загрузите данные из JSON
php load_data.php
```

### Шаг 3: Запуск приложения

```bash
# Способ 1: Встроенный PHP сервер
cd frontend
php -S localhost:8000

# Способ 2: Apache (скопируйте в htdocs)
# Откройте http://localhost/loan_system/frontend
```

### Шаг 4: Вход в систему

- Логин: `user_1` (или любой из `user_2`, `user_3`, ..., `user_10`)
- Пароль: любой (не проверяется в демо)

---

## Подробное описание

### Требования

#### Обязательные
- PHP 7.4 или выше
- PostgreSQL 12 или выше
- Apache/Nginx (или php -S для разработки)

#### PHP модули
- pdo_pgsql
- json
- session

### Проверка окружения

```bash
# Проверка PHP
php --version

# Проверка расширений
php -m | grep pdo
php -m | grep pgsql

# Проверка PostgreSQL
psql --version
psql -U postgres -c "SELECT version();"
```

### Структура развертывания

```
/var/www/html/loan_system/          # Корневая папка
├── api/                             # Backend (PHP)
│   ├── config/
│   │   ├── database.php            # ВАЖНО: Отредактировать!
│   │   └── constants.php
│   ├── models/
│   ├── index.php
│   └── .htaccess
├── frontend/                        # Frontend (HTML/CSS/JS)
│   ├── assets/
│   ├── index.html
│   └── .htaccess
├── initialize.php
├── load_data.php
└── README.md
```

### Конфигурация Apache

Если используете Apache, добавьте в httpd.conf или .htaccess:

```apache
<Directory /var/www/html/loan_system>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
    
    # Включить mod_rewrite
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteBase /loan_system/
    </IfModule>
</Directory>
```

### Конфигурация Nginx

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /var/www/html/loan_system/frontend;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location ~ /api {
        rewrite ^/api/(.*)$ /api/index.php?request=$1 last;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
    }
}
```

---

## Постинсталляция

### 1. Проверка подключения к БД

```php
<?php
require_once 'api/config/database.php';

try {
    $result = $pdo->query("SELECT COUNT(*) FROM employees");
    echo "✓ Подключение успешно\n";
} catch (Exception $e) {
    echo "✗ Ошибка: " . $e->getMessage();
}
?>
```

### 2. Проверка таблиц

```sql
-- Проверить все таблицы
\dt

-- Проверить сотрудников
SELECT COUNT(*) FROM employees;

-- Проверить клиентов
SELECT COUNT(*) FROM clients;

-- Проверить заявки
SELECT COUNT(*) FROM credit_applications;
```

### 3. Создание тестовых данных

```sql
-- Если данных нет, создайте вручную
INSERT INTO employees (full_name, position, login, status)
VALUES ('Иван Иванов', 'Менеджер', 'ivan', 'Активен');

INSERT INTO clients (full_name, passport_number, phone_number)
VALUES ('Петр Петров', '1234 567890', '+79991234567');

INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate)
VALUES ('Потребительский кредит', 50000, 500000, 12, 60, 12.5);
```

---

## Безопасность

### Обязательно для продакшена

1. **Защита паролей**
```php
// Замените в models/Employee.php
public function authenticate($login, $password) {
    $sql = "SELECT * FROM employees WHERE login = ? AND status = 'Активен'";
    $stmt = $this->pdo->prepare($sql);
    $stmt->execute([$login]);
    $emp = $stmt->fetch();
    
    if ($emp && password_verify($password, $emp['password_hash'])) {
        return $emp;
    }
    return false;
}
```

2. **HTTPS**
```apache
# Принудительное HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

3. **CSRF токены**
```php
// Добавьте в api/index.php
session_start();
if (!isset($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
```

4. **Логирование**
```php
// api/config/logger.php
error_log("Action: User {$user_id} modified application {$app_id}", 3, 'logs/audit.log');
```

---

## Решение проблем

### Ошибка: "SQLSTATE[08006] could not connect to server"

```bash
# Проверьте статус PostgreSQL
sudo systemctl status postgresql

# Запустите PostgreSQL
sudo systemctl start postgresql

# Проверьте параметры подключения в api/config/database.php
# db_host, db_port, db_name, db_user, db_password
```

### Ошибка: "Class 'PDO' not found"

```bash
# Установите PHP PDO
# Ubuntu/Debian
sudo apt-get install php-pgsql

# CentOS/RHEL
sudo yum install php-pdo php-pgsql

# Перезагрузите Apache
sudo systemctl restart apache2
```

### Ошибка 404 при доступе к API

```bash
# Включите mod_rewrite
sudo a2enmod rewrite
sudo systemctl restart apache2

# Или отредактируйте URL в assets/js/app.js
// const API_URL = './api'; // Для относительного пути
const API_URL = 'http://localhost/loan_system/api'; // Для абсолютного
```

### Медленная загрузка приложения

```sql
-- Добавьте индексы
CREATE INDEX idx_applications_client ON credit_applications(client_id);
CREATE INDEX idx_applications_employee ON credit_applications(employee_id);
CREATE INDEX idx_applications_status ON credit_applications(status);
CREATE INDEX idx_locks_app_id ON application_locks(application_id);
```

---

## Обновление и поддержка

### Резервная копия БД

```bash
# Полная резервная копия
pg_dump -U postgres loan_system > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из резервной копии
psql -U postgres loan_system < backup_20231215_120000.sql
```

### Миграция на новую версию

```bash
# Убедитесь в наличии резервной копии
pg_dump -U postgres loan_system > backup_before_upgrade.sql

# Обновите файлы приложения
# Перезагрузите веб-сервер
sudo systemctl restart apache2
```

---

## Мониторинг

### Проверка логов

```bash
# Apache (Linux)
tail -f /var/log/apache2/error.log

# PHP-FPM
tail -f /var/log/php-fpm.log

# PostgreSQL
tail -f /var/log/postgresql/postgresql.log
```

### Статистика использования

```sql
-- Количество заявок по статусам
SELECT status, COUNT(*) FROM credit_applications GROUP BY status;

-- Активные блокировки
SELECT * FROM application_locks WHERE timeout_at > NOW();

-- Топ сотрудников по обработанным заявкам
SELECT e.full_name, COUNT(*) FROM credit_applications ca
JOIN employees e ON ca.employee_id = e.employee_id
GROUP BY e.employee_id ORDER BY COUNT(*) DESC;
```

---

## Контактная информация

При возникновении проблем обратитесь к администратору системы.

**Последнее обновление:** 2024-12-14
