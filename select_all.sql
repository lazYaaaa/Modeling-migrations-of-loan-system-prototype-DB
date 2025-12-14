SELECT * FROM (
    SELECT 
        'employees' as source_table,
        employee_id::text as id,
        full_name as name,
        position as details,
        status as additional_info,
        login as unique_identifier,
        1 as sort_order
    FROM employees

    UNION ALL

    SELECT 
        'clients',
        client_id::text,
        full_name,
        'Паспорт: ' || passport_number,
        'Тел: ' || COALESCE(phone_number, 'не указан'),
        passport_number,
        2
    FROM clients

    UNION ALL

    SELECT 
        'loan_products',
        product_id::text,
        product_name,
        'Сумма: ' || min_amount::text || '-' || max_amount::text,
        'Срок: ' || min_term::text || '-' || max_term::text || ' мес.',
        base_interest_rate::text || '%',
        3
    FROM loan_products

    UNION ALL

    SELECT 
        'documents',
        document_id::text,
        document_type,
        series_number,
        COALESCE(issued_by, 'не указано'),
        issue_date::text,
        4
    FROM documents

    UNION ALL

    SELECT 
        'credit_history',
        history_id::text,
        event_type,
        description,
        source,
        event_date::text,
        5
    FROM credit_history

    UNION ALL

    SELECT 
        'credit_applications',
        application_id::text,
        'Заявка #' || application_id::text,
        'Статус: ' || status,
        'Сумма: ' || requested_amount::text,
        application_date::text,
        6
    FROM credit_applications

    UNION ALL

    SELECT 
        'application_documents',
        application_id::text || '_' || document_id::text,
        'Связь заявки и документа',
        'Application: ' || application_id::text,
        'Document: ' || document_id::text,
        'Связь',
        7
    FROM application_documents

    UNION ALL

    SELECT 
        'accounts',
        account_id::text,
        'Счет ' || account_number,
        account_type,
        'Баланс: ' || current_balance::text,
        client_id::text,
        8
    FROM accounts

    UNION ALL

    SELECT 
        'credit_contracts',
        contract_id::text,
        'Договор ' || contract_number,
        'Сумма: ' || loan_amount::text,
        'Ставка: ' || interest_rate::text || '%, срок: ' || loan_term::text || ' мес.',
        signing_date::text,
        9
    FROM credit_contracts

    UNION ALL

    SELECT 
        'payment_schedule',
        schedule_id::text,
        'Платеж от ' || payment_date::text,
        'Сумма: ' || payment_amount::text,
        'Статус: ' || status,
        contract_id::text,
        10
    FROM payment_schedule

    UNION ALL

    SELECT 
        'payments',
        payment_id::text,
        'Платеж ' || operation_type,
        'Сумма: ' || paid_amount::text,
        'Счет: ' || account_id::text,
        operation_date::text,
        11
    FROM payments
) AS all_data
ORDER BY sort_order, id;