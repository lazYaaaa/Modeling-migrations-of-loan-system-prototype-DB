<?php
class Lock {
    private $pdo;
    private $locks_table = 'application_locks';
    private $is_transaction_owner = false;
    
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
    
    public function acquireLock($application_id, $employee_id, $timeout_minutes = 10) {
        $this->removeExpiredLocks();
        
        $this->pdo->beginTransaction();
        $this->is_transaction_owner = true;
        
        try {
            $sql_app = "SELECT application_id FROM credit_applications 
                       WHERE application_id = ? FOR UPDATE NOWAIT";
            $stmt_app = $this->pdo->prepare($sql_app);
            
            try {
                $stmt_app->execute([$application_id]);
            } catch (Exception $e) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
                return ['success' => false, 'error' => 'Заявка сейчас изменяется другим пользователем'];
            }
            
            $lock = $this->isLocked($application_id);
            if ($lock) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
                return [
                    'success' => false,
                    'locked_by' => $lock['locked_by'],
                    'locked_at' => $lock['locked_at'],
                    'timeout_at' => $lock['timeout_at']
                ];
            }
            
            $sql = "INSERT INTO $this->locks_table (application_id, locked_by, timeout_at) 
                    VALUES (?, ?, NOW() + INTERVAL '{$timeout_minutes} minutes')";
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute([$application_id, $employee_id]);
            
            $this->pdo->commit();
            $this->is_transaction_owner = false;
            
            return ['success' => true];
        } catch (Exception $e) {
            if ($this->is_transaction_owner) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
            }
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }
    
    public function releaseLock($application_id, $commit_transaction = true) {
        try {
            $sql = "DELETE FROM $this->locks_table WHERE application_id = ?";
            $stmt = $this->pdo->prepare($sql);
            $result = $stmt->execute([$application_id]);
            
            if ($commit_transaction && $this->pdo->inTransaction()) {
                $this->pdo->commit();
                $this->is_transaction_owner = false;
            }
            
            return $result;
        } catch (Exception $e) {
            if ($commit_transaction && $this->pdo->inTransaction()) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
            }
            return false;
        }
    }
    
    public function releaseLockWithRollback($application_id) {
        try {
            $sql = "DELETE FROM $this->locks_table WHERE application_id = ?";
            $stmt = $this->pdo->prepare($sql);
            $result = $stmt->execute([$application_id]);
            
            if ($this->pdo->inTransaction()) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
            }
            
            return $result;
        } catch (Exception $e) {
            if ($this->pdo->inTransaction()) {
                $this->pdo->rollBack();
                $this->is_transaction_owner = false;
            }
            return false;
        }
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
    
    public function verifyLockOwnership($application_id, $employee_id) {
        $sql = "SELECT * FROM $this->locks_table 
                WHERE application_id = ? 
                AND locked_by = ? 
                AND timeout_at > NOW()";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$application_id, $employee_id]);
        return $stmt->fetch() ? true : false;
    }
    
    public function getLockInfo($application_id) {
        $sql = "SELECT l.*, e.name as employee_name 
                FROM $this->locks_table l
                LEFT JOIN employees e ON l.locked_by = e.employee_id
                WHERE l.application_id = ? AND l.timeout_at > NOW()";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$application_id]);
        return $stmt->fetch();
    }
    
    public function commitTransaction() {
        if ($this->pdo->inTransaction()) {
            $this->pdo->commit();
            $this->is_transaction_owner = false;
            return true;
        }
        return false;
    }
    
    public function rollbackTransaction() {
        if ($this->pdo->inTransaction()) {
            $this->pdo->rollBack();
            $this->is_transaction_owner = false;
            return true;
        }
        return false;
    }
}
?>
