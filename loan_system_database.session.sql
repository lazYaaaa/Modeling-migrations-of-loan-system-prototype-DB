


-- Запрос 1: Получить список всех активных клиентов
-- Цель: Отобразить идентификатор, ФИО и телефон всех клиентов со статусом 'active'
SELECT client_id, full_name, phone_number 
FROM clients 
WHERE status = 'active';

-- Запрос 2: Найти все одобренные кредитные заявки за последний месяц
-- Цель: Получить информацию об одобренных заявках за последние 30 дней с данными клиентов
SELECT ca.application_id, c.full_name, ca.requested_amount, ca.application_date
FROM credit_applications ca
JOIN clients c ON ca.client_id = c.client_id
WHERE ca.status = 'Одобрена' 
AND ca.application_date >= CURRENT_DATE - INTERVAL '6 month'

-- Запрос 3: Получить график платежей для конкретного договора
-- Цель: Отобразить расписание платежей для договора с ID=1 с сортировкой по дате
SELECT payment_date, payment_amount, status
FROM payment_schedule
WHERE contract_id = 1
ORDER BY payment_date;

-- Запрос 4: Найти общую сумму выданных кредитов по месяцам
-- Цель: Агрегировать сумму выданных кредитов по годам и месяцам для анализа динамики
SELECT 
EXTRACT(YEAR FROM signing_date) as year,
EXTRACT(MONTH FROM signing_date) as month,
SUM(loan_amount) as total_issued
FROM credit_contracts
GROUP BY year, month
ORDER BY year, month;

-- Запрос 5: Получить клиентов с просроченными платежами
-- Цель: Выявить клиентов с просроченными платежами и посчитать количество просрочек по каждому
SELECT DISTINCT c.full_name, c.phone_number
FROM clients c
JOIN credit_applications ca ON c.client_id = ca.client_id
JOIN credit_contracts cc ON ca.application_id = cc.application_id
JOIN payment_schedule ps ON cc.contract_id = ps.contract_id
WHERE ps.status = 'Просрочен' 
AND ps.payment_date < CURRENT_DATE;

-- Запрос 6: Получить количество сотрудников и активных сотрудников
-- Цель: Получить общую статистику по сотрудникам - общее количество и количество активных
SELECT COUNT(*) as total_employees,
       COUNT(CASE WHEN status = 'Активен' THEN 1 END) as active_employees
FROM employees;

-- Запрос 7: Найти максимальную, минимальную и среднюю сумму кредитов
-- Цель: Проанализировать распределение сумм кредитов через базовые статистические показатели
SELECT MAX(loan_amount) as max_loan,
       MIN(loan_amount) as min_loan,
       AVG(loan_amount) as avg_loan
FROM credit_contracts;

-- Запрос 8: Получить список кредитных продуктов с процентными ставками
-- Цель: Отсортировать кредитные продукты по убыванию процентной ставки для сравнения условий
SELECT product_name, base_interest_rate
FROM loan_products
ORDER BY base_interest_rate DESC;

-- Запрос 9: Отсортировать и вывести клиентов по статусу кредитной истории
-- Цель: Классифицировать клиентов на три категории по их кредитной истории для сегментации
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
ORDER BY client_status, c.full_name;

-- Запрос 10: Найти клиентов, которые никогда не брали кредиты
-- Цель: Выявить клиентов без одобренных кредитных заявок для маркетинговых кампаний
SELECT c.client_id, c.full_name
FROM clients c
WHERE NOT EXISTS (
    SELECT 1 FROM credit_applications ca
    WHERE ca.client_id = c.client_id AND ca.status = 'Одобрена'
)

--Запрос 11: Статистика по кредитным продуктам (сколько одобрено по каждому)
SELECT 
    lp.product_name,
    COUNT(ca.application_id) as total_applications,
    COUNT(CASE WHEN ca.status = 'Одобрена' THEN 1 END) as approved_applications,
    ROUND(COUNT(CASE WHEN ca.status = 'Одобрена' THEN 1 END) * 100.0 / COUNT(ca.application_id), 2) as approval_rate,
    AVG(CASE WHEN ca.status = 'Одобрена' THEN ca.requested_amount END) as avg_approved_amount
FROM loan_products lp
LEFT JOIN credit_applications ca ON lp.product_id = ca.product_id
GROUP BY lp.product_id, lp.product_name
ORDER BY approval_rate;
