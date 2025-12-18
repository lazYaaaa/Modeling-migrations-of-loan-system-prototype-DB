
const API_URL = '/api';

class StateManager {
    constructor() {
        this.locksEnabled = true;
        this.applicationLocks = {}; 
        this.lockUpdateTimer = null;
        this.init();
    }
    
    async init() {P

        try {
            const res = await fetch(`${API_URL}/state/locks-enabled`);
            const data = await res.json();
            if (data.success) {
                this.locksEnabled = data.data.enabled;
            }
        } catch (e) {
            console.log('StateManager init: using default locks enabled = true');
        }
        

        this.startLockStatusTimer();
    }
    
    startLockStatusTimer() {
        this.lockUpdateTimer = setInterval(() => {
            this.updateLockDisplay();
        }, 10000);
    }
    
    updateLockDisplay() {

        document.querySelectorAll('[data-app-lock-timer]').forEach(el => {
            const appId = el.dataset.appLockTimer;
            const remaining = this.getTimeRemaining(appId);
            if (remaining > 0) {

                el.textContent = `⏱️ ${remaining}м`;
                el.style.color = remaining <= 2 ? '#fff' : '#fff';
                el.style.background = remaining <= 2 ? '#c92a2a' : '#ff6b6b';
            } else {
                el.textContent = '🔓 Свободна';
                el.style.color = '#2b8a3e';
                el.style.background = '#d3f9d8';
            }
        });
    }
    
    setLocksEnabled(enabled) {
        this.locksEnabled = enabled;
        fetch(`${API_URL}/state/locks-enabled`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        }).catch(e => console.error('Failed to persist locks state:', e));
    }
    
    setApplicationLock(appId, timeout_at, locked_by) {
        this.applicationLocks[appId] = { timeout_at, locked_by };
    }
    
    clearApplicationLock(appId) {
        delete this.applicationLocks[appId];
    }
    
    getApplicationLock(appId) {
        return this.applicationLocks[appId];
    }
    
    getTimeRemaining(appId) {
        const lock = this.applicationLocks[appId];
        if (!lock) return 0;
        const now = new Date().getTime();
        const timeout = new Date(lock.timeout_at).getTime();
        const remaining = Math.floor((timeout - now) / 60000);
        return remaining > 0 ? remaining : 0;
    }
}

const stateManager = new StateManager();


let currentUser = null;
let lockTimers = {};
let statusFilter = 'all';


document.addEventListener('DOMContentLoaded', function() {

    const savedUser = localStorage.getItem('user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        initializeApp();
    } else {
        showLoginPage();
    }
});


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


function logout() {
    localStorage.removeItem('user');
    currentUser = null;
    location.reload();
}


function initializeApp() {
    // Wait for StateManager to initialize
    const checkStateManager = setInterval(() => {
        if (stateManager && stateManager.locksEnabled !== undefined) {
            clearInterval(checkStateManager);
            
            document.getElementById('login-page').style.display = 'none';
            document.getElementById('app-container').style.display = 'flex';
            updateUserInfo();
            

            setTimeout(() => {
                const btn = document.getElementById('toggle-locks-btn');
                if (btn) {
                    if (!stateManager.locksEnabled) {
                        btn.classList.add('disabled');
                        btn.textContent = '🔒 Блокировки отключены';
                    } else {
                        btn.classList.remove('disabled');
                        btn.textContent = '🔓 Блокировки включены';
                    }
                }
            }, 100)
            
            loadApplications();
        }
    }, 50);
}

function showLoginPage() {
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('login-page').style.display = 'flex';
}


function updateUserInfo() {
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.name;
        document.getElementById('user-position').textContent = currentUser.position;
    }
}


function showPage(pageId) {

    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    

    document.querySelectorAll('nav a').forEach(link => {
        link.classList.remove('active');
    });
    

    document.getElementById(pageId).classList.add('active');
    

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

// Toggle locks globally
function toggleLocksGlobally() {
    stateManager.setLocksEnabled(!stateManager.locksEnabled);
    const btn = document.getElementById('toggle-locks-btn');
    if (!stateManager.locksEnabled) {
        btn.classList.add('disabled');
        btn.textContent = '🔒 Блокировки отключены';
        showAlert('Блокировки отключены для всего приложения', 'warning');
    } else {
        btn.classList.remove('disabled');
        btn.textContent = '🔓 Блокировки включены';
        showAlert('Блокировки включены', 'success');
    }
}

// Filter applications by status
function filterApplicationsByStatus(status) {
    statusFilter = status;

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.status === status) {
            btn.classList.add('active');
        }
    });
    loadApplications();
}


function renderApplicationsTable(applications) {

    let filtered = applications;
    if (statusFilter !== 'all') {
        filtered = applications.filter(app => {
            if (statusFilter === 'open') return ['Новая', 'В работе', 'На рассмотрении'].includes(app.status);
            if (statusFilter === 'closed') return ['Одобрена', 'Отклонена'].includes(app.status);
            if (statusFilter === 'archived') return app.status === 'Архив';
            return true;
        });
    }
    
    const tbody = document.getElementById('applications-tbody');
    tbody.innerHTML = '';
    
    filtered.forEach(app => {
        const row = document.createElement('tr');
        
        let lockBadge = '';
        let timerText = '';
        
        if (app.lock_id) {
            const remaining = stateManager.getTimeRemaining(app.application_id);
            if (remaining > 0) {
                timerText = `⏱️ ${remaining}м`;
                lockBadge = `<span class="lock-indicator locked" data-app-lock-timer="${app.application_id}" style="cursor: pointer; color: #fff; background: #ff6b6b;" title="Обновляется каждые 10 секунд">${timerText}</span>`;
            } else {
                timerText = '🔓 Свободна';
                lockBadge = `<span class="lock-indicator unlocked" data-app-lock-timer="${app.application_id}">${timerText}</span>`;
            }
        } else {
            lockBadge = `<span class="lock-indicator unlocked" data-app-lock-timer="${app.application_id}">🔓 Свободна</span>`;
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
            <td style="min-width: 100px;">
                <button class="btn btn-primary btn-small" onclick="openApplicationDetail(${app.application_id})">
                    Открыть
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}


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


function showApplicationModal(app) {
    const modal = document.getElementById('app-modal');
    
    const content = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Заявка #${app.application_id}</h2>
                <button class="close-btn" onclick="closeModal('app-modal')">&times;</button>
            </div>
            
            <div class="card">
                <h3>Информация о клиенте</h3>
                <div class="card-row">
                    <div style="color: #333;">
                        <strong>ФИО:</strong> <span style="color: #222; font-weight: 500;">${app.client_name}</span><br>
                        <strong>Паспорт:</strong> <span style="color: #222;">${app.passport_number}</span><br>
                        <strong>Телефон:</strong> <span style="color: #222;">${app.phone_number || '-'}</span><br>
                    </div>
                    <div style="color: #333;">
                        <strong>Адрес:</strong> <span style="color: #222;">${app.address || '-'}</span><br>
                        <strong>Дата подачи:</strong> <span style="color: #222;">${new Date(app.application_date).toLocaleDateString('ru-RU')}</span><br>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Информация о кредите</h3>
                <div class="card-row">
                    <div style="color: #333;">
                        <strong>Продукт:</strong> <span style="color: #222;">${app.product_name}</span><br>
                        <strong>Запрашиваемая сумма:</strong> <span style="color: #222;">${formatNumber(app.requested_amount)} ₽</span><br>
                    </div>
                    <div style="color: #333;">
                        <strong>Диапазон сумм:</strong> <span style="color: #222;">${formatNumber(app.min_amount)} - ${formatNumber(app.max_amount)} ₽</span><br>
                        <strong>Срок кредита:</strong> <span style="color: #222;">${app.min_term} - ${app.max_term} месяцев</span><br>
                        <strong>Базовая ставка:</strong> <span style="color: #222;">${app.base_interest_rate}%</span><br>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Статус заявки</h3>
                <span class="badge badge-${app.status.toLowerCase().replace(' ', '-')}">${app.status}</span>
                <br><br>
                <strong>Ответственный сотрудник:</strong> <span style="color: #222;">${app.employee_name}</span>
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
                            <strong>Блокировка:</strong> 10 минут до ${new Date(app.timeout_at || new Date().getTime() + 10*60*1000).toLocaleTimeString('ru-RU')}<br>
                            Статус: <span id="lock-status-text">Проверка...</span>
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
                    <button class="btn btn-primary" id="edit-btn" onclick="enableApplicationEdit(${app.application_id}, '${app.status}', ${app.locked_by || 'null'})">
                    Обработать заявку
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = content;
    modal.classList.add('active');
    

    if (app.status !== 'Новая' && app.status !== 'На рассмотрении') {
        document.getElementById('edit-btn').disabled = true;
        document.getElementById('edit-btn').textContent = 'Заявка уже обработана';
    }
}


function enableApplicationEdit(appId, status, lockedById) {
    if (status !== 'Новая' && status !== 'На рассмотрении') {
        showAlert('Эта заявка уже обработана', 'warning');
        return;
    }
    

    if (lockedById && parseInt(lockedById) === currentUser.id) {
        showAlert('Эту заявку уже обрабатываете вы. Нажмите кнопку редактирования', 'warning');
        document.getElementById('app-edit-controls').style.display = 'block';
        document.getElementById('edit-btn').style.display = 'none';
        document.getElementById('lock-status-text').textContent = '✓ Вы получили эксклюзивный доступ';
        document.getElementById('lock-status-text').style.color = '#2b8a3e';
        return;
    }
    
    if (!stateManager.locksEnabled) {
        document.getElementById('app-edit-controls').style.display = 'block';
        document.getElementById('edit-btn').style.display = 'none';
        document.getElementById('lock-status-text').textContent = '⚠️ Блокировки отключены';
        document.getElementById('lock-status-text').style.color = '#ff922b';
        showAlert('Блокировки отключены, вы можете редактировать', 'warning');
        return;
    }
    

    fetch(`${API_URL}/applications/${appId}/lock`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            stateManager.setApplicationLock(appId, data.data.timeout_at, currentUser.id);
            document.getElementById('app-edit-controls').style.display = 'block';
            document.getElementById('edit-btn').style.display = 'none';
            document.getElementById('lock-status-text').textContent = '✓ Вы получили эксклюзивный доступ';
            document.getElementById('lock-status-text').style.color = '#2b8a3e';
            startLockTimer(appId);
            showAlert('Заявка заблокирована для вас на 10 минут', 'success');
        } else {

            if (parseInt(data.locked_by) === currentUser.id) {
                document.getElementById('app-edit-controls').style.display = 'block';
                document.getElementById('edit-btn').style.display = 'none';
                document.getElementById('lock-status-text').textContent = '✓ Вы уже имеете доступ к этой заявке';
                document.getElementById('lock-status-text').style.color = '#2b8a3e';
                startLockTimer(appId);
            } else {
                showAlert(`Заявка уже обрабатывается другим сотрудником`, 'error');
            }
        }
    })
    .catch(err => {
        console.error('Lock error:', err);
        showAlert('Ошибка при попытке блокировки заявки', 'error');
    });
}


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
            stateManager.clearApplicationLock(appId);
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
    fetch(`${API_URL}/applications/${appId}/reject`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showAlert('Заявка отклонена и перемещена в архив', 'success');
            closeModal('app-modal');
            clearLockTimer(appId);
            stateManager.clearApplicationLock(appId);
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

function showClientModal(client) {
    const modal = document.getElementById('client-modal');
    
    const content = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>${client.full_name}</h2>
                <button class="close-btn" onclick="closeModal('client-modal')">&times;</button>
            </div>
            
            <div class="card">
                <h3>Персональные данные</h3>
                <div class="card-row">
                    <div style="color: #333;">
                        <strong>ФИО:</strong> <span style="color: #222; font-weight: 500;">${client.full_name}</span><br>
                        <strong>Паспорт:</strong> <span style="color: #222;">${client.passport_number}</span><br>
                    </div>
                    <div style="color: #333;">
                        <strong>Телефон:</strong> <span style="color: #222;">${client.phone_number || '-'}</span><br>
                        <strong>Адрес:</strong> <span style="color: #222;">${client.address || '-'}</span><br>
                    </div>
                </div>
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeModal('client-modal')">Закрыть</button>
            </div>
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
// Create application modal
function showCreateApplicationModal() {
    const modal = document.getElementById('app-modal');
    
    // First load clients and products
    Promise.all([
        fetch(`${API_URL}/clients`).then(r => r.json()),
        fetch(`${API_URL}/products`).then(r => r.json())
    ])
    .then(([clientsData, productsData]) => {
        if (!clientsData.success || !productsData.success) {
            showAlert('Ошибка загрузки данных', 'error');
            return;
        }
        
        // Store products globally for later form submission
        availableProducts = productsData.data || [];
        
        const clientsHtml = clientsData.data.map(c => 
            `<option value="${c.client_id}">${c.full_name}</option>`
        ).join('');
        
        const productsHtml = productsData.data.map(p => 
            `<option value="${p.product_id}">${p.product_name}</option>`
        ).join('');
        
        const content = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Создать новую заявку</h2>
                    <button class="close-btn" onclick="closeModal('app-modal')">&times;</button>
                </div>
                
                <div class="card">
                    <h3>Данные заявки</h3>
                    <div class="form-group">
                        <label for="create-client">Клиент:</label>
                        <select id="create-client" required>
                            <option value="">Выберите клиента</option>
                            ${clientsHtml}
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="create-product">Кредитный продукт:</label>
                        <select id="create-product" required onchange="updateProductInfo()">
                            <option value="">Выберите продукт</option>
                            ${productsHtml}
                        </select>
                    </div>
                    
                    <div id="product-info" style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px; display: none;">
                        <strong>Диапазон сумм:</strong> <span id="product-range">-</span><br>
                        <strong>Срок кредита:</strong> <span id="product-term">-</span><br>
                        <strong>Ставка:</strong> <span id="product-rate">-</span>%
                    </div>
                    
                    <div class="form-group">
                        <label for="create-amount">Сумма кредита (₽):</label>
                        <input type="number" id="create-amount" step="100" min="1" required placeholder="Введите сумму">
                    </div>
                </div>
                
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeModal('app-modal')">Отмена</button>
                    <button class="btn btn-success" id="submit-create-btn" onclick="submitCreateApplication()">
                        ✓ Создать заявку
                    </button>
                </div>
            </div>
        `;
        
        modal.innerHTML = content;
        modal.classList.add('active');
    })
    .catch(err => {
        console.error('Error loading data:', err);
        showAlert('Ошибка загрузки данных', 'error');
    });
}

function updateProductInfo() {
    // This will be called with products data available in scope
    // For now, we'll implement a simpler version
}

// Store products globally for form submission
let availableProducts = [];

function submitCreateApplication() {
    const clientId = document.getElementById('create-client').value;
    const productId = parseInt(document.getElementById('create-product').value);
    const amountInput = document.getElementById('create-amount').value;
    const amount = parseFloat(amountInput);
    
    // Validate
    if (!clientId || !productId || !amountInput || isNaN(amount)) {
        showAlert('Заполните все поля корректно', 'error');
        return;
    }
    
    const product = availableProducts.find(p => parseInt(p.product_id) === productId);
    if (!product) {
        console.error('Available products:', availableProducts);
        console.error('Looking for productId:', productId);
        showAlert('Продукт не найден', 'error');
        return;
    }
    
    // Ensure min_amount and max_amount are numbers for comparison
    const minAmount = parseFloat(product.min_amount);
    const maxAmount = parseFloat(product.max_amount);
    
    if (amount < minAmount || amount > maxAmount) {
        showAlert(`Сумма должна быть между ${formatNumber(minAmount)} и ${formatNumber(maxAmount)} ₽`, 'error');
        return;
    }
    
    // Submit
    fetch(`${API_URL}/applications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_id: parseInt(clientId),
            product_id: parseInt(productId),
            requested_amount: parseFloat(amount)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showAlert(`Заявка #${data.data.application_id} создана успешно`, 'success');
            closeModal('app-modal');
            loadApplications();
        } else {
            console.error('API Error:', data);
            showAlert(data.error || 'Ошибка при создании заявки', 'error');
        }
    })
    .catch(err => {
        console.error('Create error:', err);
        showAlert('Ошибка при создании заявки', 'error');
    });
}