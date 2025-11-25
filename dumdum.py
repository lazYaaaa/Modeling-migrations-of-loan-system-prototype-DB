import psycopg2
import random
from datetime import datetime, timedelta
from faker import Faker
import sys

# Устанавливаем кодировку для вывода
sys.stdout.reconfigure(encoding='utf-8')

# Инициализация Faker для генерации тестовых данных
fake = Faker('ru_RU')

class CreditDatabase:
    def __init__(self):
        self.conn = None
        self.connect()
        
    def connect(self):
        """Подключение к базе данных"""
        try:
            self.conn = psycopg2.connect(
                dbname="loan_system",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            # Устанавливаем кодировку для соединения
            self.conn.set_client_encoding('UTF8')
            print("Успешное подключение к базе данных")
        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
    
    def create_tables(self):
        """Создание таблиц"""
        if not self.conn:
            print("Нет подключения к базе данных")
            return
            
        try:
            with self.conn.cursor() as cur:
                # Удаляем существующие таблицы (для чистоты)
                tables = [
                    'payments', 'payment_schedule', 'credit_contracts', 
                    'application_documents', 'credit_applications', 
                    'credit_history', 'documents', 'accounts', 
                    'clients', 'employees', 'loan_products'
                ]
                
                for table in tables:
                    try:
                        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                    except:
                        pass
                
                # Таблица сотрудников
                cur.execute("""
                    CREATE TABLE employees (
                        employee_id SERIAL PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        position VARCHAR(100) NOT NULL,
                        login VARCHAR(50) UNIQUE NOT NULL,
                        status VARCHAR(20) DEFAULT 'Активен'
                    )
                """)
                
                # Таблица клиентов
                cur.execute("""
                    CREATE TABLE clients (
                        client_id SERIAL PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        passport_number VARCHAR(50) NOT NULL UNIQUE,
                        phone_number VARCHAR(20),
                        address TEXT,
                        status VARCHAR(20) DEFAULT 'active'
                    )
                """)
                
                # Таблица кредитных продуктов
                cur.execute("""
                    CREATE TABLE loan_products (
                        product_id SERIAL PRIMARY KEY,
                        product_name VARCHAR(255) NOT NULL,
                        min_amount NUMERIC(15, 2) NOT NULL CHECK (min_amount >= 0),
                        max_amount NUMERIC(15, 2) NOT NULL CHECK (max_amount >= min_amount),
                        min_term INTEGER NOT NULL CHECK (min_term > 0),
                        max_term INTEGER NOT NULL CHECK (max_term >= min_term),
                        base_interest_rate NUMERIC(5, 2) NOT NULL CHECK (base_interest_rate >= 0)
                    )
                """)
                
                # Таблица документов
                cur.execute("""
                    CREATE TABLE documents (
                        document_id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
                        document_type VARCHAR(100) NOT NULL,
                        series_number VARCHAR(100) NOT NULL,
                        issued_by VARCHAR(255),
                        issue_date DATE
                    )
                """)
                
                # Таблица кредитной истории
                cur.execute("""
                    CREATE TABLE credit_history (
                        history_id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
                        event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        event_type VARCHAR(50) NOT NULL,
                        description TEXT NOT NULL,
                        source VARCHAR(100) DEFAULT 'Внутренняя'
                    )
                """)
                
                # Таблица кредитных заявок
                cur.execute("""
                    CREATE TABLE credit_applications (
                        application_id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
                        employee_id INTEGER NOT NULL REFERENCES employees(employee_id) ON DELETE RESTRICT,
                        product_id INTEGER NOT NULL REFERENCES loan_products(product_id) ON DELETE RESTRICT,
                        application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        requested_amount NUMERIC(15, 2) NOT NULL CHECK (requested_amount > 0),
                        status VARCHAR(20) DEFAULT 'На рассмотрении'
                    )
                """)
                
                # Таблица связи заявок и документов
                cur.execute("""
                    CREATE TABLE application_documents (
                        application_id INTEGER NOT NULL REFERENCES credit_applications(application_id) ON DELETE CASCADE,
                        document_id INTEGER NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
                        PRIMARY KEY (application_id, document_id)
                    )
                """)
                
                # Таблица счетов
                cur.execute("""
                    CREATE TABLE accounts (
                        account_id SERIAL PRIMARY KEY,
                        client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
                        account_number VARCHAR(34) NOT NULL UNIQUE,
                        account_type VARCHAR(50) NOT NULL,
                        current_balance NUMERIC(15, 2) DEFAULT 0
                    )
                """)
                
                # Таблица кредитных договоров
                cur.execute("""
                    CREATE TABLE credit_contracts (
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
                """)
                
                # Таблица графика платежей
                cur.execute("""
                    CREATE TABLE payment_schedule (
                        schedule_id SERIAL PRIMARY KEY,
                        contract_id INTEGER NOT NULL REFERENCES credit_contracts(contract_id) ON DELETE CASCADE,
                        payment_date DATE NOT NULL,
                        payment_amount NUMERIC(15, 2) NOT NULL CHECK (payment_amount >= 0),
                        status VARCHAR(20) DEFAULT 'Ожидает оплаты'
                    )
                """)
                
                # Таблица платежей
                cur.execute("""
                    CREATE TABLE payments (
                        payment_id SERIAL PRIMARY KEY,
                        schedule_id INTEGER REFERENCES payment_schedule(schedule_id) ON DELETE SET NULL,
                        account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
                        operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        paid_amount NUMERIC(15, 2) NOT NULL CHECK (paid_amount > 0),
                        operation_type VARCHAR(50) NOT NULL
                    )
                """)
                
                self.conn.commit()
                print("Таблицы успешно созданы")
                
        except Exception as e:
            print(f"Ошибка создания таблиц: {str(e)}")
    
    def generate_test_data(self):
        """Генерация тестовых данных"""
        if not self.conn:
            print("Нет подключения к базе данных")
            return
            
        try:
            with self.conn.cursor() as cur:
                print("Начинаем генерацию тестовых данных...")
                
                # 1. Сотрудники (10 записей)
                employees_data = []
                positions = ['Менеджер', 'Аналитик', 'Специалист', 'Руководитель']
                for i in range(10):
                    employees_data.append((
                        fake.name(),
                        f"{random.choice(positions)} по кредитованию",
                        f"user_{i+1}",
                        'Активен'
                    ))
                
                cur.executemany(
                    "INSERT INTO employees (full_name, position, login, status) VALUES (%s, %s, %s, %s)",
                    employees_data
                )
                print("✓ Сотрудники добавлены")
                
                # 2. Клиенты (30 записей)
                clients_data = []
                for i in range(30):
                    clients_data.append((
                        fake.name(),
                        f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}",
                        f"+7{random.randint(9000000000, 9999999999)}",
                        fake.address()[:100],
                        'active'
                    ))
                
                cur.executemany(
                    "INSERT INTO clients (full_name, passport_number, phone_number, address, status) VALUES (%s, %s, %s, %s, %s)",
                    clients_data
                )
                print("✓ Клиенты добавлены")
                
                # 3. Кредитные продукты (5 записей)
                products_data = [
                    ('Потребительский кредит', 10000, 500000, 3, 60, 15.5),
                    ('Ипотечный кредит', 100000, 5000000, 12, 360, 8.5),
                    ('Автокредит', 50000, 3000000, 6, 84, 11.0),
                    ('Кредит на образование', 5000, 500000, 1, 120, 7.5),
                    ('Экспресс-кредит', 1000, 100000, 1, 24, 25.0)
                ]
                
                cur.executemany(
                    "INSERT INTO loan_products (product_name, min_amount, max_amount, min_term, max_term, base_interest_rate) VALUES (%s, %s, %s, %s, %s, %s)",
                    products_data
                )
                print("✓ Кредитные продукты добавлены")
                
                # 4. Документы (по 1 на клиента)
                documents_data = []
                for client_id in range(1, 31):
                    documents_data.append((
                        client_id,
                        'Паспорт',
                        f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}",
                        "МВД России",
                        fake.date_between(start_date='-10y', end_date='today')
                    ))
                
                cur.executemany(
                    "INSERT INTO documents (client_id, document_type, series_number, issued_by, issue_date) VALUES (%s, %s, %s, %s, %s)",
                    documents_data
                )
                print("✓ Документы добавлены")
                
                # 5. Кредитные заявки (40 записей)
                applications_data = []
                for i in range(40):
                    applications_data.append((
                        random.randint(1, 30),  # client_id
                        random.randint(1, 10),   # employee_id
                        random.randint(1, 5),    # product_id
                        fake.date_time_between(start_date='-180d', end_date='now'),
                        random.randint(10000, 300000),
                        random.choice(['На рассмотрении', 'Одобрена', 'Отклонена'])
                    ))
                
                cur.executemany(
                    "INSERT INTO credit_applications (client_id, employee_id, product_id, application_date, requested_amount, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    applications_data
                )
                print("✓ Кредитные заявки добавлены")
                
                # 6. Счета (по 1 на клиента)
                accounts_data = []
                used_account_numbers = set()
                for client_id in range(1, 31):
                    while True:
                        account_number = f"40702810{random.randint(1000000000, 9999999999)}"
                        if account_number not in used_account_numbers:
                            used_account_numbers.add(account_number)
                            break
                    
                    accounts_data.append((
                        client_id,
                        account_number,
                        'Расчетный',
                        random.randint(0, 500000)
                    ))
                
                cur.executemany(
                    "INSERT INTO accounts (client_id, account_number, account_type, current_balance) VALUES (%s, %s, %s, %s)",
                    accounts_data
                )
                print("✓ Счета добавлены")
                
                # 7. Кредитные договоры (только для одобренных заявок)
                contracts_data = []
                approved_apps = []
                
                # Получаем одобренные заявки
                cur.execute("SELECT application_id, client_id, product_id, requested_amount FROM credit_applications WHERE status = 'Одобрена'")
                approved_apps = cur.fetchall()
                
                used_account_ids = set()
                for i, (app_id, client_id, product_id, amount) in enumerate(approved_apps[:15]):  # Максимум 15 договоров
                    # Находим свободный account_id для этого клиента
                    cur.execute("SELECT account_id FROM accounts WHERE client_id = %s", (client_id,))
                    client_accounts = cur.fetchall()
                    
                    for account in client_accounts:
                        account_id = account[0]
                        if account_id not in used_account_ids:
                            used_account_ids.add(account_id)
                            contracts_data.append((
                                app_id,
                                product_id,
                                account_id,
                                f"ДОГ-2024-{i+1:04d}",
                                fake.date_between(start_date='-180d', end_date='today'),
                                amount,
                                random.uniform(8.0, 20.0),
                                random.randint(12, 36)
                            ))
                            break
                
                if contracts_data:
                    cur.executemany(
                        "INSERT INTO credit_contracts (application_id, product_id, account_id, contract_number, signing_date, loan_amount, interest_rate, loan_term) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        contracts_data
                    )
                    print("✓ Кредитные договоры добавлены")
                
                # 8. График платежей
                schedule_data = []
                
                for contract_id in range(1, len(contracts_data) + 1):
                    cur.execute("SELECT loan_amount, interest_rate, loan_term, signing_date FROM credit_contracts WHERE contract_id = %s", (contract_id,))
                    contract_data = cur.fetchone()
                    
                    if contract_data:
                        loan_amount, interest_rate, loan_term, signing_date = contract_data
                        # Упрощенный расчет аннуитетного платежа
                        monthly_rate = interest_rate / 100 / 12
                        monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate) ** loan_term / ((1 + monthly_rate) ** loan_term - 1)
                        
                        for month in range(1, loan_term + 1):
                            payment_date = signing_date + timedelta(days=30 * month)
                            status = 'Ожидает оплаты'
                            if payment_date < datetime.now().date():
                                status = random.choice(['Оплачен', 'Просрочен'])
                            
                            schedule_data.append((
                                contract_id,
                                payment_date,
                                round(monthly_payment, 2),
                                status
                            ))
                
                if schedule_data:
                    cur.executemany(
                        "INSERT INTO payment_schedule (contract_id, payment_date, payment_amount, status) VALUES (%s, %s, %s, %s)",
                        schedule_data[:50]  # Ограничиваем 50 платежами
                    )
                    print("✓ График платежей добавлен")
                
                # 9. Платежи
                payments_data = []
                for schedule_id in range(1, min(20, len(schedule_data) + 1)):
                    if random.random() < 0.7:  # 70% платежей совершены
                        # Получаем данные платежа
                        cur.execute("SELECT contract_id, payment_amount FROM payment_schedule WHERE schedule_id = %s", (schedule_id,))
                        schedule_data_row = cur.fetchone()
                        if schedule_data_row:
                            contract_id, payment_amount = schedule_data_row
                            # Получаем account_id из договора
                            cur.execute("SELECT account_id FROM credit_contracts WHERE contract_id = %s", (contract_id,))
                            contract_data = cur.fetchone()
                            if contract_data:
                                account_id = contract_data[0]
                                payments_data.append((
                                    schedule_id,
                                    account_id,
                                    fake.date_time_between(start_date='-90d', end_date='now'),
                                    payment_amount,
                                    'Погашение кредита'
                                ))
                
                if payments_data:
                    cur.executemany(
                        "INSERT INTO payments (schedule_id, account_id, operation_date, paid_amount, operation_type) VALUES (%s, %s, %s, %s, %s)",
                        payments_data
                    )
                    print("✓ Платежи добавлены")
                
                self.conn.commit()
                print("✓ Тестовые данные успешно сгенерированы")
                
        except Exception as e:
            print(f"✗ Ошибка генерации данных: {str(e)}")
            self.conn.rollback()
    
    def execute_queries(self):
        """Выполнение запросов разной сложности"""
        if not self.conn:
            print("Нет подключения к базе данных")
            return {}
            
        queries = {
            # ПРОСТЫЕ ЗАПРОСЫ
            "1_Простой_Активные_клиенты": """
                SELECT client_id, full_name, phone_number 
                FROM clients 
                WHERE status = 'active'
                LIMIT 10;
            """,
            
            "2_Простой_Количество_сотрудников": """
                SELECT COUNT(*) as total_employees,
                       COUNT(CASE WHEN status = 'Активен' THEN 1 END) as active_employees
                FROM employees;
            """,
            
            "3_Простой_Макс_Мин_кредиты": """
                SELECT MAX(loan_amount) as max_loan,
                       MIN(loan_amount) as min_loan,
                       AVG(loan_amount) as avg_loan
                FROM credit_contracts;
            """,
            
            "4_Простой_Кредитные_продукты": """
                SELECT product_name, base_interest_rate
                FROM loan_products
                ORDER BY base_interest_rate DESC;
            """,
            
            # СРЕДНИЕ ЗАПРОСЫ
            "5_Средний_Одобренные_заявки": """
                SELECT ca.application_id, c.full_name, ca.requested_amount, ca.application_date
                FROM credit_applications ca
                JOIN clients c ON ca.client_id = c.client_id
                WHERE ca.status = 'Одобрена'
                ORDER BY ca.application_date DESC
                LIMIT 10;
            """,
            
            "6_Средний_График_платежей": """
                SELECT ps.payment_date, ps.payment_amount, ps.status,
                       c.full_name, cc.contract_number
                FROM payment_schedule ps
                JOIN credit_contracts cc ON ps.contract_id = cc.contract_id
                JOIN credit_applications ca ON cc.application_id = ca.application_id
                JOIN clients c ON ca.client_id = c.client_id
                WHERE ps.contract_id = 1
                ORDER BY ps.payment_date;
            """,
            
            "7_Средний_Сумма_кредитов_по_месяцам": """
                SELECT 
                    EXTRACT(YEAR FROM signing_date) as year,
                    EXTRACT(MONTH FROM signing_date) as month,
                    COUNT(*) as contract_count,
                    SUM(loan_amount) as total_issued
                FROM credit_contracts
                GROUP BY year, month
                ORDER BY year, month;
            """,
            
            "8_Средний_Клиенты_просрочки": """
                SELECT DISTINCT c.client_id, c.full_name, c.phone_number,
                       COUNT(ps.schedule_id) as overdue_count
                FROM clients c
                JOIN credit_applications ca ON c.client_id = ca.client_id
                JOIN credit_contracts cc ON ca.application_id = cc.application_id
                JOIN payment_schedule ps ON cc.contract_id = ps.contract_id
                WHERE ps.status = 'Просрочен'
                GROUP BY c.client_id, c.full_name, c.phone_number
                ORDER BY overdue_count DESC
                LIMIT 10;
            """,
            
            # СЛОЖНЫЕ ЗАПРОСЫ
            "9_Сложный_CASE_Статус_клиентов": """
                SELECT 
                    c.full_name,
                    c.phone_number,
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 FROM credit_applications ca
                            JOIN credit_contracts cc ON ca.application_id = cc.application_id
                            JOIN payment_schedule ps ON cc.contract_id = ps.contract_id
                            WHERE ca.client_id = c.client_id AND ps.status = 'Просрочен'
                        ) THEN 'Есть просрочки'
                        WHEN EXISTS (
                            SELECT 1 FROM credit_applications ca2
                            WHERE ca2.client_id = c.client_id AND ca2.status = 'Одобрена'
                        ) THEN 'Активный заемщик'
                        ELSE 'Потенциальный клиент'
                    END as client_status
                FROM clients c
                ORDER BY client_status, c.full_name
                LIMIT 15;
            """,
            
            "10_Сложный_Никогда_не_брали_кредиты": """
                SELECT c.client_id, c.full_name
                FROM clients c
                WHERE NOT EXISTS (
                    SELECT 1 FROM credit_applications ca
                    WHERE ca.client_id = c.client_id AND ca.status = 'Одобрена'
                )
                LIMIT 10;
            """,
            
            "11_Сложный_Статистика_по_продуктам": """
                SELECT 
                    lp.product_name,
                    COUNT(ca.application_id) as total_applications,
                    COUNT(CASE WHEN ca.status = 'Одобрена' THEN 1 END) as approved_applications,
                    ROUND(COUNT(CASE WHEN ca.status = 'Одобрена' THEN 1 END) * 100.0 / COUNT(ca.application_id), 2) as approval_rate,
                    AVG(CASE WHEN ca.status = 'Одобрена' THEN ca.requested_amount END) as avg_approved_amount
                FROM loan_products lp
                LEFT JOIN credit_applications ca ON lp.product_id = ca.product_id
                GROUP BY lp.product_id, lp.product_name
                ORDER BY approval_rate DESC NULLS LAST;
            """
        }
        
        results = {}
        for query_name, query in queries.items():
            try:
                with self.conn.cursor() as cur:
                    cur.execute(query)
                    
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        data = cur.fetchall()
                        results[query_name] = {
                            'columns': columns,
                            'data': data
                        }
                    else:
                        results[query_name] = {
                            'columns': ['Result'],
                            'data': [['Query executed successfully']]
                        }
                    
            except Exception as e:
                results[query_name] = {
                    'columns': ['Error'],
                    'data': [[f"Error: {str(e)}"]]
                }
        
        return results
    
    def print_results(self, results):
        """Красивый вывод результатов"""
        for query_name, result in results.items():
            print(f"\n{'='*60}")
            print(f"ЗАПРОС: {query_name}")
            print(f"{'='*60}")
            
            if 'columns' in result and 'data' in result:
                # Вывод заголовков
                headers = result['columns']
                print(" | ".join(f"{str(header):<20}" for header in headers))
                print("-" * (len(headers) * 22))
                
                # Вывод данных
                for row in result['data'][:10]:
                    formatted_row = []
                    for value in row:
                        if value is None:
                            formatted_row.append("NULL")
                        elif isinstance(value, float):
                            formatted_row.append(f"{value:.2f}")
                        else:
                            formatted_row.append(str(value))
                    print(" | ".join(f"{value:<20}" for value in formatted_row))
                
                if len(result['data']) > 10:
                    print(f"... и еще {len(result['data']) - 10} строк")
            
            print(f"{'='*60}")

def main():
    """Основная функция"""
    print("Запуск системы управления кредитной базой данных...")
    db = CreditDatabase()
    
    if not db.conn:
        print("Не удалось подключиться к базе данных. Проверьте параметры подключения.")
        return
    
    # Создание таблиц
    print("\n1. Создание таблиц...")
    db.create_tables()
    
    # Генерация тестовых данных
    print("\n2. Генерация тестовых данных...")
    db.generate_test_data()
    
    # Выполнение запросов
    print("\n3. Выполнение запросов...")
    results = db.execute_queries()
    
    # Вывод результатов
    print("\n4. Результаты запросов:")
    db.print_results(results)
    
    # Закрытие соединения
    if db.conn:
        db.conn.close()
        print("\nСоединение с базой данных закрыто")

if __name__ == "__main__":
    main()