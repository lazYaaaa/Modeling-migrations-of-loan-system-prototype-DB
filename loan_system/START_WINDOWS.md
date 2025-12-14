# БЫСТРЫЙ СТАРТ НА WINDOWS - 5 МИНУТ

## ✅ Имеете ли вы?

Перед запуском убедитесь:
- [ ] PHP установлена (7.4+)
- [ ] PostgreSQL установлена (12+)
- [ ] Браузер (Chrome/Firefox/Edge)

## Проверка наличия PHP и PostgreSQL

### Способ 1: Через командную строку

```bash
# Проверить PHP
php --version

# Проверить PostgreSQL  
psql --version

# Если команды не работают - см. "Установка" ниже
```

### Способ 2: Если не установлено

- **PHP:** скачайте с https://windows.php.net/
- **PostgreSQL:** скачайте с https://www.postgresql.org/download/windows/

---

## 🚀 САМЫЙ БЫСТРЫЙ СТАРТ (3 команды)

Откройте **PowerShell** в папке приложения:

```powershell
# 1️⃣ Создать БД и таблицы
php setup_db.php

# 2️⃣ Создать демо-данные
php create_demo_data.php

# 3️⃣ Запустить сервер
cd frontend
php -S localhost:8000
```

Откройте браузер: **http://localhost:8000**

Логин: **user_1**, Пароль: **любой**

---

## 📋 ПОШАГОВО

### Шаг 0: Открыть PowerShell

```
Нажмите Win+R → введите "powershell" → Enter
Перейдите в папку:
```

```powershell
cd c:\tt\lab_bd\loan_system
```

### Шаг 1: Проверить PostgreSQL

```powershell
# Запустить PostgreSQL (если не запущен)
# Windows Services → PostgreSQL → Запустить
# ИЛИ:
psql -U postgres -c "SELECT version();"
```

Если ошибка "пароль" - используйте пароль который устанавливали при установке.

### Шаг 2: Настроить параметры БД

**ВАЖНО!** Отредактировать файл: `api/config/database.php`

```php
$db_password = 'ВАШ_ПАРОЛЬ_POSTGRES'; // ← ИЗМЕНИТЬ!
```

### Шаг 3: Создать БД (если не создана)

```powershell
psql -U postgres
```

В PostgreSQL введите:
```sql
CREATE DATABASE loan_system;
\q
```

### Шаг 4: Инициализация

```powershell
php setup_db.php
```

Должно вывести: ✓ Все таблицы созданы

### Шаг 5: Демо-данные

```powershell
php create_demo_data.php
```

Должно вывести: ✓ 10 сотрудников, 5 клиентов, 4 продукта, 5 заявок

### Шаг 6: Запустить приложение

```powershell
cd frontend
php -S localhost:8000
```

Должно вывести:
```
Development Server
Listening on http://127.0.0.1:8000
```

### Шаг 7: Открыть браузер

```
http://localhost:8000
```

### Шаг 8: Вход

```
Логин: user_1
Пароль: (любой символ или Enter)
Нажать "Войти"
```

🎉 **Готово!**

---

## 🔧 Если что-то не работает

### Ошибка: "php command not found"

```
PHP не в PATH. Нужно:
1. Установить PHP
2. Добавить в Environment Variables

C:\ → Свойства → Дополнительные параметры системы 
→ Переменные окружения → Path → Добавить путь к PHP
```

### Ошибка: "Could not connect to server"

```
PostgreSQL не запущен. Нужно:

1. Открыть Services (Win+R → services.msc)
2. Найти "PostgreSQL"
3. Нажать "Запустить"

ИЛИ запустить вручную:
"C:\Program Files\PostgreSQL\15\bin\postgres.exe"
```

### Ошибка: "Пароль неверный"

Отредактировать: `api/config/database.php`

```php
$db_password = 'postgres'; // ← Какой пароль установили при установке
```

Если забыли пароль:
- Переустановить PostgreSQL
- Или: `ALTER USER postgres WITH PASSWORD 'новый_пароль';`

### Ошибка: "Class 'PDO' not found"

```
Требуется расширение pdo_pgsql.

Решение:
1. Найти php.ini
   php --ini
   
2. Открыть php.ini в блокноте

3. Найти строку:
   ;extension=pdo_pgsql
   
4. Убрать точку с запятой:
   extension=pdo_pgsql
   
5. Сохранить и перезагрузить PHP
```

### Ошибка: "application_locks table not found"

```powershell
php setup_db.php
```

---

## 💡 СОВЕТЫ

### Остановить сервер

```
Нажмите Ctrl+C в PowerShell
```

### Перезапустить

```powershell
# Ctrl+C

# Потом заново
cd frontend
php -S localhost:8000
```

### Изменить порт (если 8000 занят)

```powershell
php -S localhost:8001
# или любой другой номер вместо 8001
```

### Доступ с другого компьютера

```
Вместо localhost используйте IP:
php -S 192.168.1.100:8000

Откройте в браузере другого ПК:
http://192.168.1.100:8000
```

---

## 📱 МОБИЛЬНЫЙ ДОСТУП

На телефоне в одной сети:

```
http://192.168.1.XXX:8000
(где XXX - IP компьютера)
```

---

## 🎓 ТЕСТИРОВАНИЕ

### Тест 1: Открыть заявку

1. Нажать "Открыть" на любую заявку
2. Должно открыться модальное окно с деталями ✓

### Тест 2: Обработать заявку

1. Нажать "Обработать заявку"
2. Должна заблокироваться (покажет таймер)
3. Нажать "Одобрить"
4. Должно создаться в договор ✓

### Тест 3: Конкурентность

1. Открыть 2 вкладки
2. На разных пользователях войти (user_1, user_2)
3. Оба нажать "Обработать" на одну заявку
4. Второй должен получить ошибку ✓

---

## 🧹 ОЧИСТКА (если нужно начать заново)

```powershell
# В PowerShell подключиться к БД
psql -U postgres

# Удалить БД
DROP DATABASE loan_system;

# Создать новую
CREATE DATABASE loan_system;

# Выйти
\q

# Переинициализировать
php setup_db.php
php create_demo_data.php
```

---

## 📞 ЧАСТЫЕ ВОПРОСЫ

**В: Где логируются операции?**
О: Логирование не включено в демо. Добавьте в production.

**В: Где изменить данные сотрудников?**
О: В БД таблица `employees`. Используйте pgAdmin или psql.

**В: Где хранятся файлы договоров?**
О: Демо не создает PDF. Добавьте генерацию в production.

**В: Как сделать бэкап БД?**
О: 
```powershell
pg_dump -U postgres loan_system > backup.sql
```

**В: Как восстановить из бэкапа?**
О:
```powershell
psql -U postgres loan_system < backup.sql
```

---

## ✅ КОНТРОЛЬНЫЙ СПИСОК

Перед первым запуском:

- [ ] PHP установлена
- [ ] PostgreSQL запущена
- [ ] БД `loan_system` создана
- [ ] `api/config/database.php` отредактирована
- [ ] `php setup_db.php` выполнена без ошибок
- [ ] `php create_demo_data.php` выполнена
- [ ] Браузер открыт на `http://localhost:8000`
- [ ] Вход прошел успешно
- [ ] Видно 5+ заявок в таблице

Если все галочки - **поздравляем!** 🎉

---

## 📚 ДАЛЬШЕ

После запуска смотрите:

1. **QUICKSTART.md** - как пользоваться приложением
2. **README.md** - полная документация
3. **API.md** - если разрабатываете
4. **DEPLOYMENT.md** - если деплоите на сервер

---

**Дата:** 14 декабря 2024
**Версия:** 1.0.0
**Статус:** Ready to Use
