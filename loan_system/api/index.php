<?php
session_start();
header('Content-Type: application/json');

// Load configuration (files are inside api/config)
require_once __DIR__ . '/config/database.php';
require_once __DIR__ . '/config/constants.php';

// Load models (inside api/models)
require_once __DIR__ . '/models/Lock.php';
require_once __DIR__ . '/models/Application.php';
require_once __DIR__ . '/models/Client.php';
require_once __DIR__ . '/models/Employee.php';
require_once __DIR__ . '/models/LoanProduct.php';

// Initialize models
$lock = new Lock($pdo);
$application = new Application($pdo);
$client = new Client($pdo);
$employee = new Employee($pdo);
$product = new LoanProduct($pdo);

// Simple authentication - in production use proper sessions
$_SESSION['employee_id'] = $_SESSION['employee_id'] ?? 1;

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
// Normalize path: remove leading /api or /api/ so routing works under router.php
$path = preg_replace('#^/api/?#', '', $path);

$response = ['success' => false, 'data' => null, 'error' => null];

try {
    // Routes
    if ($path === 'applications') {
        if ($method === 'GET') {
            $response['data'] = $application->getAllApplications();
            $response['success'] = true;
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
    
    elseif (preg_match('/^applications\/(\d+)\/lock$/', $path, $matches)) {
        $app_id = $matches[1];
        $employee_id = $_SESSION['employee_id'];
        
        if ($method === 'POST') {
            $result = $lock->acquireLock($app_id, $employee_id, LOCK_TIMEOUT);
            if ($result['success']) {
                // Fetch the actual lock data to get timeout_at
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
        
        if ($method === 'POST') {
            $result = $application->createContract($app_id, $_SESSION['employee_id']);
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
    
    elseif (preg_match('/^applications\/(\d+)\/reject$/', $path, $matches)) {
        $app_id = $matches[1];
        
        if ($method === 'POST') {
            $application->updateApplicationStatus($app_id, STATUS_ARCHIVED);
            $lock->releaseLock($app_id);
            $response['success'] = true;
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
        // Get/Set global locks enabled state (stored in session)
        if ($method === 'GET') {
            $response['success'] = true;
            $response['data'] = [
                'enabled' => $_SESSION['locks_enabled'] ?? true
            ];
        } elseif ($method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $_SESSION['locks_enabled'] = $data['enabled'] ?? true;
            $response['success'] = true;
            $response['data'] = ['enabled' => $_SESSION['locks_enabled']];
        }
    }
    
    elseif ($path === 'applications' && $method === 'POST') {
        // Create new application
        $data = json_decode(file_get_contents('php://input'), true);
        
        $required = ['client_id', 'product_id', 'requested_amount'];
        $missing = array_diff($required, array_keys($data));
        
        if ($missing) {
            http_response_code(400);
            $response['error'] = 'Missing fields: ' . implode(', ', $missing);
        } else {
            try {
                $sql = "INSERT INTO credit_applications 
                       (client_id, employee_id, product_id, requested_amount, status)
                       VALUES (?, ?, ?, ?, 'Новая')
                       RETURNING application_id";
                $stmt = $pdo->prepare($sql);
                $stmt->execute([
                    $data['client_id'],
                    $_SESSION['employee_id'],
                    $data['product_id'],
                    $data['requested_amount']
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
                    $response['error'] = 'Failed to create application';
                }
            } catch (Exception $e) {
                http_response_code(400);
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
