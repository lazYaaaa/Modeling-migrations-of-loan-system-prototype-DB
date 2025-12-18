# API Documentation - Система управления кредитованием

## Базовая информация

- **Base URL:** `http://localhost:8000/api/`
- **Формат ответов:** JSON
- **Аутентификация:** Session-based

## Аутентификация

### POST /auth

Вход в систему

**Request:**
```json
{
  "login": "user_1",
  "password": "any"
}
```

**Response (успех):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Варвара Валентиновна Соколова",
    "position": "Менеджер по кредитованию"
  }
}
```

**Response (ошибка):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

## Заявки (Applications)

### GET /applications

Получить все кредитные заявки

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "application_id": 1,
      "client_name": "Сорокина Анна Владимировна",
      "product_name": "Потребительский кредит",
      "requested_amount": "150000.00",
      "status": "Новая",
      "lock_id": null,
      "locked_by": null,
      "locked_by_name": null,
      "employee_name": "Варвара Валентиновна Соколова",
      "application_date": "2024-12-14T10:30:00+00:00"
    }
  ]
}
```

---

### GET /applications/{id}

Получить информацию о конкретной заявке

**Parameters:**
- `id` (integer, required) - ID заявки

**Response:**
```json
{
  "success": true,
  "data": {
    "application_id": 1,
    "client_id": 1,
    "employee_id": 1,
    "product_id": 1,
    "application_date": "2024-12-14T10:30:00+00:00",
    "requested_amount": "150000.00",
    "status": "Новая",
    "client_name": "Сорокина Анна Владимировна",
    "passport_number": "8694 973235",
    "phone_number": "+79391008512",
    "address": null,
    "employee_name": "Варвара Валентиновна Соколова",
    "product_name": "Потребительский кредит",
    "min_amount": "50000.00",
    "max_amount": "500000.00",
    "min_term": 12,
    "max_term": 60,
    "base_interest_rate": "12.50"
  }
}
```

---

### PUT /applications/{id}

Обновить заявку (сумма, статус)

**Parameters:**
- `id` (integer, required) - ID заявки

**Request:**
```json
{
  "amount": 160000,
  "status": "В работе"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "application_id": 1,
    "requested_amount": "160000.00",
    "status": "В работе"
  }
}
```

---

## Система блокировок

### POST /applications/{id}/lock

Установить блокировку на заявку (эксклюзивный доступ)

**Parameters:**
- `id` (integer, required) - ID заявки

**Response (успех):**
```json
{
  "success": true,
  "data": {
    "locked": true
  }
}
```

**Response (заявка уже заблокирована):**
```json
{
  "success": false,
  "error": "Заявка уже обрабатывается другим сотрудником",
  "locked_by": 2,
  "timeout_at": "2024-12-14T11:45:00+00:00"
}
```

---

### DELETE /applications/{id}/lock

Снять блокировку с заявки

**Parameters:**
- `id` (integer, required) - ID заявки

**Response:**
```json
{
  "success": true,
  "data": {
    "locked": false
  }
}
```

---

### POST /applications/{id}/extend-lock

Продлить блокировку на еще 30 минут

**Parameters:**
- `id` (integer, required) - ID заявки

**Response:**
```json
{
  "success": true
}
```

---

## Принятие решений

### POST /applications/{id}/approve

Одобрить заявку и создать договор

**Parameters:**
- `id` (integer, required) - ID заявки

**Response:**
```json
{
  "success": true,
  "data": {
    "contract_id": 1,
    "contract_number": "CONT20241214101301"
  }
}
```

**Что происходит:**
1. Создается счет (account)
2. Создается договор (contract)
3. Генерируется график платежей (payment_schedule)
4. Заявка переводится в статус "Одобрена"
5. Блокировка снимается

---

### POST /applications/{id}/reject

Отклонить заявку и отправить в архив

**Parameters:**
- `id` (integer, required) - ID заявки

**Response:**
```json
{
  "success": true
}
```

**Что происходит:**
1. Заявка переводится в статус "Архив"
2. Блокировка снимается

---

## Клиенты (Clients)

### GET /clients

Получить список всех клиентов

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "client_id": 1,
      "full_name": "Сорокина Анна Владимировна",
      "passport_number": "8694 973235",
      "phone_number": "+79391008512",
      "address": null
    }
  ]
}
```

---

### GET /clients/{id}

Получить информацию о клиенте

**Parameters:**
- `id` (integer, required) - ID клиента

**Response:**
```json
{
  "success": true,
  "data": {
    "client_id": 1,
    "full_name": "Сорокина Анна Владимировна",
    "passport_number": "8694 973235",
    "phone_number": "+79391008512",
    "address": null
  }
}
```

---

### GET /clients/{id}/documents

Получить документы клиента

**Parameters:**
- `id` (integer, required) - ID клиента

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "document_id": 1,
      "client_id": 1,
      "document_type": "Паспорт",
      "series_number": "8694 973235",
      "issued_by": "МВД РФ",
      "issue_date": "2015-05-20"
    }
  ]
}
```

---

### GET /clients/{id}/history

Получить кредитную историю клиента

**Parameters:**
- `id` (integer, required) - ID клиента

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "history_id": 1,
      "client_id": 1,
      "event_date": "2024-12-14T10:30:00+00:00",
      "event_type": "Application",
      "description": "Подана заявка на потребительский кредит",
      "source": "Внутренняя"
    }
  ]
}
```

---

## Справочники

### GET /employees

Получить список активных сотрудников

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "employee_id": 1,
      "full_name": "Варвара Валентиновна Соколова",
      "position": "Менеджер по кредитованию",
      "login": "user_1",
      "status": "Активен"
    }
  ]
}
```

---

### GET /products

Получить список кредитных продуктов

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": 1,
      "product_name": "Потребительский кредит",
      "min_amount": "50000.00",
      "max_amount": "500000.00",
      "min_term": 12,
      "max_term": 60,
      "base_interest_rate": "12.50"
    }
  ]
}
```

---

## Коды ошибок

| Код | Описание |
|-----|---------|
| 200 | Успешно (success: true) |
| 400 | Неверный запрос |
| 404 | Ресурс не найден |
| 500 | Внутренняя ошибка сервера |
| 409 | Заявка уже заблокирована (conflict) |

## Примеры использования

### JavaScript (Fetch API)

```javascript

fetch('http://localhost:8000/api/auth', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    login: 'user_1',
    password: 'any'
  })
})
.then(res => res.json())
.then(data => console.log(data));

// Получить заявки
fetch('http://localhost:8000/api/applications')
  .then(res => res.json())
  .then(data => console.log(data));

// Заблокировать заявку
fetch('http://localhost:8000/api/applications/1/lock', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data));

// Одобрить заявку
fetch('http://localhost:8000/api/applications/1/approve', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data));
```

### cURL

```bash
# Вход
curl -X POST http://localhost:8000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"login":"user_1","password":"any"}'

# Получить заявки
curl http://localhost:8000/api/applications

# Заблокировать заявку
curl -X POST http://localhost:8000/api/applications/1/lock

# Одобрить заявку
curl -X POST http://localhost:8000/api/applications/1/approve
```

---

## Статусы заявок

| Статус | Описание |
|--------|---------|
| Новая | Только что создана, не обработана |
| В работе | Обрабатывается сотрудником |
| Одобрена | Одобрена, создан договор |
| Отклонена | Отклонена |
| Архив | В архиве (отклоненные или завершенные) |

---

## Версия API

- **Version:** 1.0.0
- **Last Updated:** 2024-12-14

Для дополнительной информации смотрите README.md и QUICKSTART.md
