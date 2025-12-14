// API Base URL - expects server root to be project root so API is available at /api
const API_URL = '/api';

// Global state
let currentUser = null;
let lockTimers = {};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        initializeApp();
    } else {
        showLoginPage();
    }
});

// Login function
function login() {
    const login = document.getElementById('login-input').value;
    const password = document.getElementById('password-input').value;
    
    if (!login) {
        showAlert('Пожалуйста введите логин', 'error');
        return;
    }
    
    fetch(`${API_URL}/auth`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ login, password })
    })
    .then(async res => {
        const ct = res.headers.get('Content-Type') || '';
        const text = await res.text();
        try {
            const data = ct.includes('application/json') ? JSON.parse(text) : JSON.parse(text);
            if (data && data.success) {
                currentUser = data.data;
                localStorage.setItem('user', JSON.stringify(currentUser));
                document.getElementById('login-page').style.display = 'none';
                initializeApp();
            } else {
                showAlert((data && data.error) || 'Ошибка входа', 'error');
            }
        } catch (e) {
            console.error('Login error: could not parse response', text);
            // If server returned HTML (index.html), it's likely the built-in PHP server was started in the frontend folder.
            if (text && text.trim().startsWith('<!DOCTYPE')) {
                showAlert('Сервер вернул HTML вместо JSON. Запустите PHP-сервер из корня проекта, например:\nphp -S localhost:8000 -t .\nи откройте http://localhost:8000/frontend', 'error');
            } else {
                showAlert('Ошибка входа: сервер вернул неожиданный ответ', 'error');
            }
        }
    })
    .catch(err => {
        console.error('Login error:', err);
        showAlert('Ошибка подключения к серверу', 'error');
    });
}

// Logout function
function logout() {
    if (confirm('Вы уверены что хотите выйти?')) {
        localStorage.removeItem('user');
        currentUser = null;
        location.reload();
    }
}

// Initialize main app
function initializeApp() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('app-container').style.display = 'flex';
    updateUserInfo();
    loadApplications();
}

function showLoginPage() {
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('login-page').style.display = 'flex';
}

// Update user info in header
function updateUserInfo() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.name;
        document.getElementById('user-position').textContent = currentUser.position;
    }
}

// Navigation
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Remove active from nav
    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    
    // Mark nav as active
    event.target.classList.add('active');
    
    // Load data based on page
    if (pageId === 'applications') {
        loadApplications();
    } else if (pageId === 'clients') {
        loadClients();
    } else if (pageId === 'products') {
        loadProducts();
    }
}

// Load applications
function loadApplications() {
    fetch(`${API_URL}/applications`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderApplicationsTable(data.data);
            }
        })
        .catch(err => console.error('Load applications error:', err));
}

// Render applications table
function renderApplicationsTable(applications) {
    const tbody = document.getElementById('applications-tbody');
    tbody.innerHTML = '';
    
    applications.forEach(app => {
        const row = document.createElement('tr');
        
        let lockBadge = '';
        let statusColor = getStatusColor(app.status);
        
        if (app.lock_id) {
            lockBadge = `<span class="lock-indicator locked">🔒 Заблокирована</span>`;
        } else {
            lockBadge = `<span class="lock-indicator unlocked">🔓 Свободна</span>`;
        }
        
        row.innerHTML = `
            <td>${app.application_id}</td>
            <td>${app.client_name}</td>
            <td>${app.product_name}</td>
            <td>${formatNumber(app.requested_amount)} ₽</td>
            <td><span class="badge badge-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span></td>
            <td>${lockBadge}</td>
            <td>${app.locked_by_name || '-'}</td>
            <td>${app.employee_name}</td>
            <td>
                <button class="btn btn-primary btn-small" onclick="openApplicationDetail(${app.application_id})">
                    Открыть
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Open application detail
function openApplicationDetail(appId) {
    fetch(`${API_URL}/applications/${appId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showApplicationModal(data.data);
            }
        })
        .catch(err => console.error('Load detail error:', err));
}

// Show application modal
function showApplicationModal(app) {
    const modal = document.getElementById('app-modal');
    
    // Fill in the modal content
    const content = `
        <div class="modal-header">
            <h2>Заявка #${app.application_id}</h2>
            <button class="close-btn" onclick="closeModal('app-modal')">&times;</button>
        </div>
        
        <div class="card">
            <h3>Информация о клиенте</h3>
            <div class="card-row">
                <div>
                    <strong>ФИО:</strong> ${app.client_name}<br>
                    <strong>Паспорт:</strong> ${app.passport_number}<br>
                    <strong>Телефон:</strong> ${app.phone_number || '-'}<br>
                </div>
                <div>
                    <strong>Адрес:</strong> ${app.address || '-'}<br>
                    <strong>Дата подачи:</strong> ${new Date(app.application_date).toLocaleDateString('ru-RU')}<br>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Информация о кредите</h3>
            <div class="card-row">
                <div>
                    <strong>Продукт:</strong> ${app.product_name}<br>
                    <strong>Запрашиваемая сумма:</strong> ${formatNumber(app.requested_amount)} ₽<br>
                </div>
                <div>
                    <strong>Диапазон сумм:</strong> ${formatNumber(app.min_amount)} - ${formatNumber(app.max_amount)} ₽<br>
                    <strong>Срок кредита:</strong> ${app.min_term} - ${app.max_term} месяцев<br>
                    <strong>Базовая ставка:</strong> ${app.base_interest_rate}%<br>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>Статус заявки</h3>
            <span class="badge badge-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span>
            <br><br>
            <strong>Ответственный сотрудник:</strong> ${app.employee_name}
        </div>
        
        <div id="app-edit-controls" style="display: none;">
            <div class="card">
                <h3>Редактирование</h3>
                <div class="form-group">
                    <label for="app-amount">Сумма кредита:</label>
                    <input type="number" id="app-amount" value="${app.requested_amount}" step="100">
                </div>
            </div>
            
            <div class="card">
                <h3>Принятие решения</h3>
                <div class="lock-controls">
                    <div class="lock-status">
                        Статус блокировки: <span id="lock-status-text">Проверка...</span>
                    </div>
                    <div class="lock-buttons">
                        <button class="btn btn-success" id="approve-btn" onclick="approveApplication(${app.application_id})">
                            ✓ Одобрить заявку
                        </button>
                        <button class="btn btn-danger" id="reject-btn" onclick="rejectApplication(${app.application_id})">
                            ✗ Отклонить заявку
                        </button>
                        <button class="btn btn-secondary" id="unlock-btn" onclick="releaseLock(${app.application_id})" style="display: none;">
                            🔓 Отпустить заявку
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('app-modal')">Закрыть</button>
            <button class="btn btn-primary" id="edit-btn" onclick="enableApplicationEdit(${app.application_id}, '${app.status}')">
                Обработать заявку
            </button>
        </div>
    `;
    
    modal.innerHTML = content;
    modal.classList.add('active');
    
    // Check if application is already locked
    if (app.status !== 'Новая' && app.status !== 'На рассмотрении') {
        document.getElementById('edit-btn').disabled = true;
        document.getElementById('edit-btn').textContent = 'Заявка уже обработана';
    }
}

// Enable application edit and acquire lock
function enableApplicationEdit(appId, status) {
    // Check if already processed
    if (status !== 'Новая' && status !== 'На рассмотрении') {
        showAlert('Эта заявка уже обработана', 'warning');
        return;
    }
    
    // Try to acquire lock
    fetch(`${API_URL}/applications/${appId}/lock`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('app-edit-controls').style.display = 'block';
            document.getElementById('edit-btn').style.display = 'none';
            document.getElementById('lock-status-text').textContent = '✓ Вы получили эксклюзивный доступ';
            document.getElementById('lock-status-text').style.color = '#2b8a3e';
            startLockTimer(appId);
            showAlert('Заявка заблокирована для вас на 30 минут', 'success');
        } else {
            showAlert(`Заявка уже обрабатывается сотрудником: ${data.locked_by}`, 'error');
        }
    })
    .catch(err => {
        console.error('Lock error:', err);
        showAlert('Ошибка при попытке блокировки заявки', 'error');
    });
}

// Release lock
function releaseLock(appId) {
    fetch(`${API_URL}/applications/${appId}/lock`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.getElementById('app-edit-controls').style.display = 'none';
            document.getElementById('edit-btn').style.display = 'block';
            document.getElementById('unlock-btn').style.display = 'none';
            clearLockTimer(appId);
            showAlert('Блокировка заявки снята', 'info');
        }
    })
    .catch(err => console.error('Unlock error:', err));
}

// Start lock timer
function startLockTimer(appId) {
    const timerInterval = setInterval(() => {
        fetch(`${API_URL}/applications/${appId}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.data) {
                    const lockStatus = document.getElementById('lock-status-text');
                    if (!lockStatus) {
                        clearInterval(timerInterval);
                        return;
                    }
                    
                    const timeRemaining = calculateTimeRemaining(data.data.timeout_at);
                    if (timeRemaining > 0) {
                        lockStatus.innerHTML = `✓ Эксклюзивный доступ (осталось: <span class="timer">${timeRemaining}m</span>)`;
                    } else {
                        lockStatus.textContent = '✗ Время блокировки истекло';
                        lockStatus.style.color = '#c92a2a';
                        clearInterval(timerInterval);
                    }
                }
            });
    }, 5000);
    
    lockTimers[appId] = timerInterval;
}

// Clear lock timer
function clearLockTimer(appId) {
    if (lockTimers[appId]) {
        clearInterval(lockTimers[appId]);
        delete lockTimers[appId];
    }
}

// Calculate time remaining
function calculateTimeRemaining(timeoutAt) {
    const now = new Date().getTime();
    const timeout = new Date(timeoutAt).getTime();
    const remaining = Math.floor((timeout - now) / 60000);
    return remaining > 0 ? remaining : 0;
}

// Approve application
function approveApplication(appId) {
    const amount = document.getElementById('app-amount')?.value;
    
    if (!confirm('Вы уверены что хотите одобрить эту заявку?')) {
        return;
    }
    
    // First update amount if changed
    if (amount) {
        fetch(`${API_URL}/applications/${appId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount: parseFloat(amount) })
        })
        .then(res => res.json())
        .catch(err => console.error('Update error:', err));
    }
    
    // Then approve and create contract
    fetch(`${API_URL}/applications/${appId}/approve`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showAlert(`Заявка одобрена! Контракт: ${data.data.contract_number}`, 'success');
            closeModal('app-modal');
            clearLockTimer(appId);
            loadApplications();
        } else {
            showAlert(data.error || 'Ошибка при одобрении заявки', 'error');
        }
    })
    .catch(err => {
        console.error('Approve error:', err);
        showAlert('Ошибка при обработке заявки', 'error');
    });
}

// Reject application
function rejectApplication(appId) {
    if (!confirm('Вы уверены что хотите отклонить эту заявку?')) {
        return;
    }
    
    fetch(`${API_URL}/applications/${appId}/reject`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showAlert('Заявка отклонена', 'success');
            closeModal('app-modal');
            clearLockTimer(appId);
            loadApplications();
        } else {
            showAlert(data.error || 'Ошибка при отклонении заявки', 'error');
        }
    })
    .catch(err => {
        console.error('Reject error:', err);
        showAlert('Ошибка при обработке заявки', 'error');
    });
}

// Load clients
function loadClients() {
    fetch(`${API_URL}/clients`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderClientsTable(data.data);
            }
        })
        .catch(err => console.error('Load clients error:', err));
}

// Render clients table
function renderClientsTable(clients) {
    const tbody = document.getElementById('clients-tbody');
    tbody.innerHTML = '';
    
    clients.forEach(client => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${client.client_id}</td>
            <td>${client.full_name}</td>
            <td>${client.passport_number}</td>
            <td>${client.phone_number || '-'}</td>
            <td>${client.address || '-'}</td>
            <td>
                <button class="btn btn-primary btn-small" onclick="openClientDetail(${client.client_id})">
                    Просмотр
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Open client detail
function openClientDetail(clientId) {
    fetch(`${API_URL}/clients/${clientId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showClientModal(data.data);
            }
        })
        .catch(err => console.error('Load client error:', err));
}

// Show client modal
function showClientModal(client) {
    const modal = document.getElementById('client-modal');
    
    const content = `
        <div class="modal-header">
            <h2>${client.full_name}</h2>
            <button class="close-btn" onclick="closeModal('client-modal')">&times;</button>
        </div>
        
        <div class="card">
            <h3>Персональные данные</h3>
            <div class="card-row">
                <div>
                    <strong>ФИО:</strong> ${client.full_name}<br>
                    <strong>Паспорт:</strong> ${client.passport_number}<br>
                </div>
                <div>
                    <strong>Телефон:</strong> ${client.phone_number || '-'}<br>
                    <strong>Адрес:</strong> ${client.address || '-'}<br>
                </div>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn btn-secondary" onclick="closeModal('client-modal')">Закрыть</button>
        </div>
    `;
    
    modal.innerHTML = content;
    modal.classList.add('active');
}

// Load products
function loadProducts() {
    fetch(`${API_URL}/products`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderProductsTable(data.data);
            }
        })
        .catch(err => console.error('Load products error:', err));
}

// Render products table
function renderProductsTable(products) {
    const tbody = document.getElementById('products-tbody');
    tbody.innerHTML = '';
    
    products.forEach(product => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.product_name}</td>
            <td>${formatNumber(product.min_amount)} ₽</td>
            <td>${formatNumber(product.max_amount)} ₽</td>
            <td>${product.min_term} - ${product.max_term}</td>
            <td>${product.base_interest_rate}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
    const appId = document.getElementById(modalId)?.dataset.appId;
    if (appId) {
        clearLockTimer(appId);
    }
}

// Show alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} show`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.content');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

function getStatusColor(status) {
    switch(status) {
        case 'Новая': return 'new';
        case 'В работе': return 'processing';
        case 'Одобрена': return 'approved';
        case 'Отклонена':
        case 'Архив': return 'rejected';
        default: return 'secondary';
    }
}
