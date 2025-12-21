-- Clean migration with UTF-8 encoding - NO DROP SCHEMA!
-- Just truncate tables if they exist

-- Tables creation
CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'manager' CHECK (role IN ('admin', 'manager', 'viewer')),
    login VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'Активен'
);

CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    passport_number VARCHAR(50) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    address TEXT
);

CREATE TABLE IF NOT EXISTS loan_products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    min_amount NUMERIC(15, 2) NOT NULL CHECK (min_amount >= 0),
    max_amount NUMERIC(15, 2) NOT NULL CHECK (max_amount >= min_amount),
    min_term INTEGER NOT NULL CHECK (min_term > 0),
    max_term INTEGER NOT NULL CHECK (max_term >= min_term),
    base_interest_rate NUMERIC(5, 2) NOT NULL CHECK (base_interest_rate >= 0)
);

CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data insertion with explicit locks_enabled setting
INSERT INTO app_settings (key, value) 
VALUES ('locks_enabled', 'true')
ON CONFLICT (key) DO UPDATE SET value = 'true';

-- Employees data
INSERT INTO employees (full_name, position, role, login, status) 
VALUES 
    ('Варвара Валентиновна Соколова', 'Менеджер по кредитам', 'manager', 'user_1', 'Активен'),
    ('Игорь Сергеевич Морозов', 'Администратор системы', 'admin', 'user_2', 'Активен'),
    ('Елена Петровна Новикова', 'Консультант', 'viewer', 'user_3', 'Активен'),
    ('Никита Игоревич Сидоров', 'Менеджер по кредитам', 'manager', 'nikita', 'Активен')
ON CONFLICT (login) DO UPDATE SET full_name = EXCLUDED.full_name, position = EXCLUDED.position, role = EXCLUDED.role;

-- Clients data
INSERT INTO clients (full_name, passport_number, phone_number, address)
VALUES
    ('Иван Петрович Смирнов', '1234567890', '+79991112233', 'Москва, ул. Ленина, д. 1'),
    ('Мария Ивановна Сидорова', '0987654321', '+79992223344', 'Москва, пр. Ленинградский, д. 2'),
    ('Петр Алексеевич Петров', '1122334455', '+79993334455', 'Санкт-Петербург, ул. Невский, д. 3'),
    ('Елена Викторовна Волкова', '5544332211', '+79994445566', 'Казань, ул. Баумана, д. 4'),
    ('Сергей Сергеевич Сергеев', '9988776655', '+79995556677', 'Екатеринбург, ул. Малышева, д. 5')
ON CONFLICT (passport_number) DO UPDATE SET full_name = EXCLUDED.full_name;

-- Products data
INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate)
VALUES
    ('Потребительский кредит', 50000, 500000, 6, 60, 10.5),
    ('Ипотека', 500000, 10000000, 120, 360, 6.5),
    ('Авто-кредит', 200000, 3000000, 24, 84, 8.5)
ON CONFLICT DO NOTHING;
