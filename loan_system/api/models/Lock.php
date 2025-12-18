<?php
class Lock {
    private $pdo;
    private $locks_table = 'application_locks';
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
        $this->createLockTable();
    }
    
    private function createLockTable() {
        $sql = "
            CREATE TABLE IF NOT EXISTS $this->locks_table (
                lock_id SERIAL PRIMARY KEY,
                application_id INTEGER NOT NULL UNIQUE,
                locked_by INTEGER NOT NULL,
                locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                timeout_at TIMESTAMP NOT NULL,
                FOREIGN KEY (application_id) REFERENCES credit_applications(application_id) ON DELETE CASCADE,
                FOREIGN KEY (locked_by) REFERENCES employees(employee_id) ON DELETE CASCADE
            )
        ";
        try {
            $this->pdo->exec($sql);
        } catch (Exception $e) {

        }
    }
    
    public function isLocked($application_id) {
        $sql = "SELECT * FROM $this->locks_table 
                WHERE application_id = ? AND timeout_at > NOW()";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$application_id]);
        return $stmt->fetch();
    }
    
    public function acquireLock($application_id, $employee_id, $timeout_minutes = 30) {

        $this->removeExpiredLocks();
        
        // Check if already locked
        $lock = $this->isLocked($application_id);
        if ($lock) {
            return [
                'success' => false,
                'locked_by' => $lock['locked_by'],
                'locked_at' => $lock['locked_at'],
                'timeout_at' => $lock['timeout_at']
            ];
        }
        
        // Try to acquire lock
        try {
            $sql = "INSERT INTO $this->locks_table (application_id, locked_by, timeout_at) 
                    VALUES (?, ?, NOW() + INTERVAL '{$timeout_minutes} minutes')";
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute([$application_id, $employee_id]);
            
            return ['success' => true];
        } catch (Exception $e) {
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }
    
    public function releaseLock($application_id) {
        $sql = "DELETE FROM $this->locks_table WHERE application_id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$application_id]);
    }
    
    public function removeExpiredLocks() {
        $sql = "DELETE FROM $this->locks_table WHERE timeout_at <= NOW()";
        $this->pdo->exec($sql);
    }
    
    public function extendLock($application_id, $minutes = 30) {
        $sql = "UPDATE $this->locks_table 
                SET timeout_at = NOW() + INTERVAL '{$minutes} minutes'
                WHERE application_id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$application_id]);
    }
}
?>
