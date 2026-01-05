-- Database initialization for loan system
-- UTF-8 encoding

CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'manager' CHECK (role IN ('admin', 'manager', 'viewer')),
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

CREATE TABLE IF NOT EXISTS documents (
    document_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    series_number VARCHAR(100) NOT NULL,
    issued_by VARCHAR(255),
    issue_date DATE
);

CREATE TABLE IF NOT EXISTS credit_history (
    history_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    source VARCHAR(100) DEFAULT 'Внутренняя'
);

CREATE TABLE IF NOT EXISTS credit_applications (
    application_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
    product_id INTEGER NOT NULL REFERENCES loan_products(product_id) ON DELETE RESTRICT,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    requested_amount NUMERIC(15, 2) NOT NULL CHECK (requested_amount > 0),
    status VARCHAR(20) DEFAULT 'На рассмотрении'
);

CREATE TABLE IF NOT EXISTS application_documents (
    application_id INTEGER NOT NULL REFERENCES credit_applications(application_id) ON DELETE CASCADE,
    document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    PRIMARY KEY (application_id, document_id)
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
    account_number VARCHAR(34) NOT NULL UNIQUE,
    account_type VARCHAR(50) NOT NULL,
    current_balance NUMERIC(15, 2) DEFAULT 0
);

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
);

CREATE TABLE IF NOT EXISTS payment_schedule (
    schedule_id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES credit_contracts(contract_id) ON DELETE CASCADE,
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(15, 2) NOT NULL CHECK (payment_amount >= 0),
    status VARCHAR(20) DEFAULT 'Ожидает оплаты'
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES payment_schedule(schedule_id) ON DELETE SET NULL,
    account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
    operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_amount NUMERIC(15, 2) NOT NULL CHECK (paid_amount > 0),
    operation_type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS application_locks (
    lock_id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL UNIQUE,
    locked_by INTEGER NOT NULL,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timeout_at TIMESTAMP NOT NULL,
    FOREIGN KEY (application_id) REFERENCES credit_applications(application_id) ON DELETE CASCADE,
    FOREIGN KEY (locked_by) REFERENCES employees(employee_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO app_settings (key, value) VALUES ('locks_enabled', 'true') ON CONFLICT (key) DO NOTHING;

-- Insert demo employees with password hashes
-- Password for all users set to username value (user_1, user_2, etc.)
INSERT INTO employees (full_name, position, login, password_hash, role, status) VALUES
    ('Варвара Валентиновна Соколова', 'Менеджер по кредитам', 'user_1', '$2y$10$IMTC5Tk0gZ083VskXHb9weuOK9fWKrI4wzQhWaevZDaPUG4sy8VnW', 'manager', 'Активен'),
    ('Игорь Сергеевич Морозов', 'Администратор системы', 'user_2', '$2y$10$KNzBPMi7VSOOfbamaRlIieOl6mXv73PyrzcsjY9Q1GInllicXsJZq', 'admin', 'Активен'),
    ('Елена Петровна Новикова', 'Консультант', 'user_3', '$2y$10$WqiYbcuzT3bbOoqUyoS8fuCEoLC8oQdWxvWWmAa2/bS.hs.uxpVpO', 'viewer', 'Активен'),
    ('Никита Игоревич Сидоров', 'Менеджер по кредитам', 'nikita', '$2y$10$xQDAtOwIgPnvGkWWZnpBEeIVnNx5l65bjFfpTIwd4hjlU1uoIJ7Di', 'manager', 'Активен')
ON CONFLICT (login) DO NOTHING;

-- Insert sample clients
INSERT INTO clients (full_name, passport_number, phone_number, address) VALUES
    ('Александр Петрович Иванов', '7712345678', '+79991234567', 'Москва, ул. Ленина, 10'),
    ('Мария Сергеевна Петрова', '7712345679', '+79991234568', 'Москва, ул. Красная, 20'),
    ('Иван Федорович Сидоров', '7712345680', '+79991234569', 'Москва, ул. Советская, 30'),
    ('Анна Владимировна Козлова', '7712345681', '+79991234570', 'Москва, ул. Центральная, 40')
ON CONFLICT (passport_number) DO NOTHING;

-- Insert loan products
INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate) VALUES
    ('Потребительский кредит', 50000, 500000, 12, 60, 12.5),
    ('Ипотечный кредит', 500000, 10000000, 60, 300, 8.5),
    ('Автокредит', 200000, 3000000, 12, 84, 10.0),
    ('Бизнес-кредит', 100000, 5000000, 12, 120, 14.0)
ON CONFLICT DO NOTHING;
