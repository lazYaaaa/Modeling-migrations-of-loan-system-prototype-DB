<?php
class Employee {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    public function getAllEmployees() {
        $sql = "SELECT * FROM employees WHERE status = 'Активен' ORDER BY full_name";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    public function getEmployeeById($id) {
        $sql = "SELECT * FROM employees WHERE employee_id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
    
    public function authenticate($login, $password = null) {
        // Authenticate using stored password hash
        $sql = "SELECT * FROM employees WHERE login = ? AND status = 'Активен'";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$login]);
        $emp = $stmt->fetch();

        if (!$emp) return false;

        if (!isset($emp['password_hash']) || !$password) return false;

        if (password_verify($password, $emp['password_hash'])) {
            return $emp;
        }

        return false;
    }
    
    public function getEmployeeApplications($employee_id) {
        $sql = "SELECT COUNT(*) as count FROM credit_applications WHERE employee_id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$employee_id]);
        $result = $stmt->fetch();
        return $result['count'] ?? 0;
    }
}
?>
