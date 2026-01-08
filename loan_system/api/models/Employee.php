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
        $sql = "SELECT * FROM employees WHERE login = ? AND status = 'Активен'";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$login]);
        $emp = $stmt->fetch();

        if (!$emp) return false;

        // Fallback for demo data without hashes: accept password == login when hash is empty
        if (empty($emp['password_hash'])) {
            if ($password === $emp['login']) {
                return $emp;
            }
            return false;
        }

        if (!password_verify($password, $emp['password_hash'])) {
            return false;
        }

        return $emp;
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
