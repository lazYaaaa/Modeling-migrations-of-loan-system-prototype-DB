-- Clean migration with UTF-8 encoding
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

CREATE TABLE IF NOT EXISTS app_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_account_balance_on_payment()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE accounts
    SET current_balance = current_balance + NEW.paid_amount
    WHERE account_id = NEW.account_id;
    
    INSERT INTO credit_history (client_id, event_type, description, source)
    SELECT 
        c.client_id,
        'Платеж получен',
        'Платеж в размере ' || NEW.paid_amount || ' рублей получен на счет ' || a.account_number,
        'Система'
    FROM accounts a
    JOIN clients c ON a.client_id = c.client_id
    WHERE a.account_id = NEW.account_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_received_trigger
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION update_account_balance_on_payment();

CREATE OR REPLACE FUNCTION update_payment_status_on_full_payment()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE payment_schedule
    SET status = 'Оплачена'
    WHERE schedule_id = NEW.schedule_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_status_update_trigger
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION update_payment_status_on_full_payment();

INSERT INTO employees (full_name, position, role, login, status) 
VALUES 
    ('Варвара Валентиновна Соколова', 'Менеджер по кредитам', 'manager', 'user_1', 'Активен'),
    ('Игорь Сергеевич Морозов', 'Администратор системы', 'admin', 'user_2', 'Активен'),
    ('Елена Петровна Новикова', 'Консультант', 'viewer', 'user_3', 'Активен'),
    ('Никита Игоревич Сидоров', 'Менеджер по кредитам', 'manager', 'nikita', 'Активен')
ON CONFLICT DO NOTHING;

INSERT INTO app_settings (key, value) 
VALUES ('locks_enabled', 'true')
ON CONFLICT (key) DO NOTHING;

INSERT INTO clients (full_name, passport_number, phone_number, address)
VALUES
    ('Иван Петрович Смирнов', '1234567890', '+79991112233', 'Москва, ул. Ленина, д. 1'),
    ('Мария Ивановна Сидорова', '0987654321', '+79992223344', 'Москва, пр. Ленинградский, д. 2'),
    ('Петр Алексеевич Петров', '1122334455', '+79993334455', 'Санкт-Петербург, ул. Невский, д. 3'),
    ('Елена Викторовна Волкова', '5544332211', '+79994445566', 'Казань, ул. Баумана, д. 4'),
    ('Сергей Сергеевич Сергеев', '9988776655', '+79995556677', 'Екатеринбург, ул. Малышева, д. 5')
ON CONFLICT DO NOTHING;

INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate)
VALUES
    ('Потребительский кредит', 50000, 500000, 6, 60, 10.5),
    ('Ипотека', 500000, 10000000, 120, 360, 6.5),
    ('Авто-кредит', 200000, 3000000, 24, 84, 8.5)
ON CONFLICT DO NOTHING;

INSERT INTO documents (client_id, document_type, series_number, issued_by, issue_date)
VALUES
    (1, 'Паспорт', '1234 567890', 'МВД России', '2015-05-10'),
    (2, 'Паспорт', '0987 654321', 'МВД России', '2012-03-15'),
    (3, 'Паспорт', '1122 334455', 'МВД России', '2018-07-20'),
    (4, 'Паспорт', '5544 332211', 'МВД России', '2016-11-25'),
    (5, 'Паспорт', '9988 776655', 'МВД России', '2014-02-28')
ON CONFLICT DO NOTHING;

INSERT INTO credit_applications (client_id, employee_id, product_id, requested_amount, status)
VALUES
    (1, 1, 1, 150000, 'На рассмотрении'),
    (2, 1, 1, 200000, 'На рассмотрении'),
    (3, 2, 2, 2000000, 'На рассмотрении'),
    (4, 2, 3, 800000, 'На рассмотрении'),
    (5, 1, 1, 100000, 'На рассмотрении')
ON CONFLICT DO NOTHING;
