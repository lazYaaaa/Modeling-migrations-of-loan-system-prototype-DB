<?php
// Constants
define('APP_NAME', 'Система управления кредитованием');
define('APP_VERSION', '1.0.0');

// Lock timeout in minutes
define('LOCK_TIMEOUT', 30);

// Application statuses
define('STATUS_NEW', 'Новая');
define('STATUS_PROCESSING', 'В работе');
define('STATUS_APPROVED', 'Одобрена');
define('STATUS_REJECTED', 'Отклонена');
define('STATUS_ARCHIVED', 'Архив');

// Payment statuses
define('PAYMENT_PENDING', 'Ожидает оплаты');
define('PAYMENT_COMPLETED', 'Оплачено');
define('PAYMENT_OVERDUE', 'Просроченно');

// Lock file path
define('LOCKS_DIR', __DIR__ . '/../../storage/locks/');

// Ensure locks directory exists
if (!is_dir(LOCKS_DIR)) {
    mkdir(LOCKS_DIR, 0777, true);
}
?>
