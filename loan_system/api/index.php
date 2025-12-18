<?php
session_start();
header('Content-Type: application/json');

require_once __DIR__ . '/config/database.php';
require_once __DIR__ . '/config/constants.php';

require_once __DIR__ . '/models/Lock.php';
require_once __DIR__ . '/models/Application.php';
require_once __DIR__ . '/models/Client.php';
require_once __DIR__ . '/models/Employee.php';
require_once __DIR__ . '/models/LoanProduct.php';

$lock = new Lock($pdo);
$application = new Application($pdo);
$client = new Client($pdo);
$employee = new Employee($pdo);
$product = new LoanProduct($pdo);

$_SESSION['employee_id'] = $_SESSION['employee_id'] ?? 1;

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = preg_replace('#^/api/?#', '', $path);

$response = ['success' => false, 'data' => null, 'error' => null];

try {
    if ($path === 'applications') {
        if ($method === 'GET') {
            $response['data'] = $application->getAllApplications();
            $response['success'] = true;
        } elseif ($method === 'POST') {
            try {
                $input = file_get_contents('php://input');
                $data = json_decode($input, true);
                
                if (!$data) {
                    throw new Exception('Invalid JSON in request body');
                }
                
                $required = ['client_id', 'product_id', 'requested_amount'];
                $missing = array_diff($required, array_keys($data ?? []));
                
                if ($missing) {
                    http_response_code(400);
                    $response['error'] = 'Missing fields: ' . implode(', ', $missing);
                } else if (!isset($_SESSION['employee_id'])) {
                    http_response_code(401);
                    $response['error'] = 'Not authenticated. Employee ID not set in session.';
                } else {
                    $client_check = $pdo->prepare("SELECT client_id FROM clients WHERE client_id = ?");
                    $client_check->execute([$data['client_id']]);
                    if (!$client_check->fetch()) {
                        throw new Exception("Client with ID {$data['client_id']} not found");
                    }
                    
                    $product_check = $pdo->prepare("SELECT product_id FROM loan_products WHERE product_id = ?");
                    $product_check->execute([$data['product_id']]);
                    if (!$product_check->fetch()) {
                        throw new Exception("Product with ID {$data['product_id']} not found");
                    }
                    
                    $sql = "INSERT INTO credit_applications 
                           (client_id, employee_id, product_id, requested_amount, status)
                           VALUES (?, ?, ?, ?, 'Новая')
                           RETURNING application_id";
                    $stmt = $pdo->prepare($sql);
                    $stmt->execute([
                        (int)$data['client_id'],
                        (int)$_SESSION['employee_id'],
                        (int)$data['product_id'],
                        (float)$data['requested_amount']
                    ]);
                    $result = $stmt->fetch();
                    
                    if ($result) {
                        $response['success'] = true;
                        $response['data'] = [
                            'application_id' => $result['application_id'],
                            'message' => 'Application created successfully'
                        ];
                    } else {
                        http_response_code(500);
                        $response['error'] = 'Failed to create application (no result returned)';
                    }
                }
            } catch (Exception $e) {
                http_response_code(400);
                $response['error'] = $e->getMessage();
            }
        }
    }
    
    elseif (preg_match('/^applications\/(\d+)$/', $path, $matches)) {
        $app_id = $matches[1];
        
        if ($method === 'GET') {
            $response['data'] = $application->getApplicationById($app_id);
            $response['success'] = true;
        }
        
        elseif ($method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $employee_id = $_SESSION['employee_id'] ?? null;
            
            if (!$employee_id) {
                http_response_code(401);
                $response['error'] = 'Not authenticated';
            } else {
                // ФИЗИЧЕСКАЯ БЛОКИРОВКА: проверяем, что блокировка есть и принадлежит этому сотруднику
                $has_lock = $lock->verifyLockOwnership($app_id, $employee_id);
                
                if (!$has_lock) {
                    // Проверяем, может быть заблокирована кем-то другим
                    $lock_check = $lock->isLocked($app_id);
                    if ($lock_check) {
                        http_response_code(403);
                        $response['error'] = 'This application is locked by another employee';
                    } else {
                        http_response_code(403);
                        $response['error'] = 'This application is not locked or lock has expired. You must acquire a lock before editing.';
                    }
                } else {
                    // Блокировка валидна — можем редактировать
                    if (isset($data['amount'])) {
                        $application->updateApplicationAmount($app_id, $data['amount']);
                    }
                    
                    if (isset($data['status'])) {
                        $application->updateApplicationStatus($app_id, $data['status']);
                    }
                    
                    $response['data'] = $application->getApplicationById($app_id);
                    $response['success'] = true;
                }
            }
        }
    }
    
    elseif (preg_match('/^applications\/(\d+)\/lock$/', $path, $matches)) {
        $app_id = $matches[1];
        $employee_id = $_SESSION['employee_id'];
        
        if ($method === 'POST') {
            $result = $lock->acquireLock($app_id, $employee_id, LOCK_TIMEOUT);
            if ($result['success']) {
                $lockData = $lock->isLocked($app_id);
                $response['success'] = true;
                $response['data'] = [
                    'locked' => true,
                    'timeout_at' => $lockData['timeout_at']
                ];
            } else {
                $response['error'] = 'Заявка уже обрабатывается другим сотрудником';
                $response['locked_by'] = $result['locked_by'];
                $response['timeout_at'] = $result['timeout_at'];
            }
        }
        
        elseif ($method === 'DELETE') {
            $lock->releaseLock($app_id);
            $response['success'] = true;
            $response['data'] = ['locked' => false];
        }
    }
    
    elseif (preg_match('/^applications\/(\d+)\/extend-lock$/', $path, $matches)) {
        $app_id = $matches[1];
        
        if ($method === 'POST') {
            $lock->extendLock($app_id, LOCK_TIMEOUT);
            $response['success'] = true;
        }
    }
    
    elseif (preg_match('/^applications\/(\d+)\/approve$/', $path, $matches)) {
        $app_id = $matches[1];
        $employee_id = $_SESSION['employee_id'];
        
        if ($method === 'POST') {
            // ФИЗИЧЕСКАЯ БЛОКИРОВКА: проверяем, что заявка заблокирована этим сотрудником
            $has_lock = $lock->verifyLockOwnership($app_id, $employee_id);
            
            if (!$has_lock) {
                http_response_code(403);
                $response['error'] = 'Cannot approve: application is not locked by you or lock has expired';
            } else {
                $result = $application->createContract($app_id, $employee_id);
                if ($result['success']) {
                    $application->updateApplicationStatus($app_id, STATUS_APPROVED);
                    $lock->releaseLock($app_id);
                    $response['success'] = true;
                    $response['data'] = $result;
                } else {
                    $response['error'] = $result['error'];
                }
            }
        }
    }
    
    elseif (preg_match('/^applications\/(\d+)\/reject$/', $path, $matches)) {
        $app_id = $matches[1];
        $employee_id = $_SESSION['employee_id'];
        
        if ($method === 'POST') {
            // ФИЗИЧЕСКАЯ БЛОКИРОВКА: проверяем, что заявка заблокирована этим сотрудником
            $has_lock = $lock->verifyLockOwnership($app_id, $employee_id);
            
            if (!$has_lock) {
                http_response_code(403);
                $response['error'] = 'Cannot reject: application is not locked by you or lock has expired';
            } else {
                $application->updateApplicationStatus($app_id, STATUS_ARCHIVED);
                $lock->releaseLock($app_id);
                $response['success'] = true;
            }
        }
    }
    
    elseif ($path === 'clients') {
        if ($method === 'GET') {
            $response['data'] = $client->getAllClients();
            $response['success'] = true;
        }
        
        elseif ($method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $id = $client->createClient($data);
            if ($id) {
                $response['data'] = $client->getClientById($id);
                $response['success'] = true;
            } else {
                $response['error'] = 'Failed to create client';
            }
        }
    }
    
    elseif (preg_match('/^clients\/(\d+)$/', $path, $matches)) {
        $client_id = $matches[1];
        
        if ($method === 'GET') {
            $response['data'] = $client->getClientById($client_id);
            $response['success'] = true;
        }
        
        elseif ($method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            if ($client->updateClient($client_id, $data)) {
                $response['data'] = $client->getClientById($client_id);
                $response['success'] = true;
            }
        }
    }
    
    elseif (preg_match('/^clients\/(\d+)\/documents$/', $path, $matches)) {
        $client_id = $matches[1];
        $response['data'] = $client->getClientDocuments($client_id);
        $response['success'] = true;
    }
    
    elseif (preg_match('/^clients\/(\d+)\/history$/', $path, $matches)) {
        $client_id = $matches[1];
        $response['data'] = $client->getClientCreditHistory($client_id);
        $response['success'] = true;
    }
    
    elseif ($path === 'employees') {
        if ($method === 'GET') {
            $response['data'] = $employee->getAllEmployees();
            $response['success'] = true;
        }
    }
    
    elseif ($path === 'products') {
        if ($method === 'GET') {
            $response['data'] = $product->getAllProducts();
            $response['success'] = true;
        }
    }
    
    elseif ($path === 'auth') {
        if ($method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $login = $data['login'] ?? null;
            $password = $data['password'] ?? null;

            if (!$login || !$password) {
                $response['error'] = 'Missing login or password';
            } else {
                $emp = $employee->authenticate($login, $password);
                if ($emp) {
                    $_SESSION['employee_id'] = $emp['employee_id'];
                    $_SESSION['employee_name'] = $emp['full_name'];
                    $response['success'] = true;
                    $response['data'] = [
                        'id' => $emp['employee_id'],
                        'name' => $emp['full_name'],
                        'position' => $emp['position']
                    ];
                } else {
                    http_response_code(401);
                    $response['error'] = 'Invalid credentials';
                }
            }
        }
    }
    
    elseif ($path === 'state/locks-enabled') {
        if ($method === 'GET') {
            try {
                $sql = "SELECT value FROM app_settings WHERE key = 'locks_enabled' LIMIT 1";
                $stmt = $pdo->prepare($sql);
                $stmt->execute();
                $result = $stmt->fetch();
                
                $enabled = true;
                if ($result) {
                    $enabled = $result['value'] === 'true' || $result['value'] === '1';
                }
                
                $response['success'] = true;
                $response['data'] = ['enabled' => $enabled];
            } catch (Exception $e) {
                $response['success'] = true;
                $response['data'] = ['enabled' => true];
            }
        } elseif ($method === 'POST') {
            try {
                $data = json_decode(file_get_contents('php://input'), true);
                $enabled = $data['enabled'] ? 'true' : 'false';
                
                // Create settings table if it doesn't exist
                $sql = "CREATE TABLE IF NOT EXISTS app_settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )";
                $pdo->exec($sql);
                
                $sql = "INSERT INTO app_settings (key, value, updated_at) 
                       VALUES ('locks_enabled', ?, CURRENT_TIMESTAMP)
                       ON CONFLICT (key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP";
                $stmt = $pdo->prepare($sql);
                $stmt->execute([$enabled, $enabled]);
                
                $response['success'] = true;
                $response['data'] = ['enabled' => $data['enabled']];
            } catch (Exception $e) {
                $response['error'] = $e->getMessage();
            }
        }
    }
    
    else {
        http_response_code(404);
        $response['error'] = 'Endpoint not found';
    }
    
} catch (Exception $e) {
    http_response_code(500);
    $response['error'] = $e->getMessage();
}

echo json_encode($response);
?>
