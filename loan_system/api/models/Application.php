<?php
class Application {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    public function getAllApplications() {
        $sql = "
            SELECT 
                ca.application_id,
                ca.application_date,
                ca.requested_amount,
                ca.status,
                cl.full_name as client_name,
                cl.passport_number,
                e.full_name as employee_name,
                lp.product_name,
                al.lock_id,
                al.locked_by,
                e_lock.full_name as locked_by_name,
                al.timeout_at
            FROM credit_applications ca
            JOIN clients cl ON ca.client_id = cl.client_id
            JOIN employees e ON ca.employee_id = e.employee_id
            JOIN loan_products lp ON ca.product_id = lp.product_id
            LEFT JOIN application_locks al ON ca.application_id = al.application_id
            LEFT JOIN employees e_lock ON al.locked_by = e_lock.employee_id
            ORDER BY ca.application_date DESC
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    public function getApplicationById($id) {
        $sql = "
            SELECT 
                ca.*,
                cl.full_name as client_name,
                cl.passport_number,
                cl.phone_number,
                cl.address,
                e.full_name as employee_name,
                lp.product_name,
                lp.min_amount,
                lp.max_amount,
                lp.min_term,
                lp.max_term,
                lp.base_interest_rate,
                al.timeout_at,
                al.locked_by
            FROM credit_applications ca
            JOIN clients cl ON ca.client_id = cl.client_id
            JOIN employees e ON ca.employee_id = e.employee_id
            JOIN loan_products lp ON ca.product_id = lp.product_id
            LEFT JOIN application_locks al ON ca.application_id = al.application_id
            WHERE ca.application_id = ?
        ";
        
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
    
    public function updateApplicationStatus($application_id, $status) {
        $sql = "UPDATE credit_applications SET status = ? WHERE application_id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$status, $application_id]);
    }
    
    public function updateApplicationAmount($application_id, $requested_amount) {
        $sql = "UPDATE credit_applications SET requested_amount = ? WHERE application_id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([$requested_amount, $application_id]);
    }
    
    public function createContract($application_id, $employee_id) {
        try {
            $this->pdo->beginTransaction();
            
            // Get application data
            $app = $this->getApplicationById($application_id);
            
            // Create account
            $account_sql = "INSERT INTO accounts (client_id, account_number, account_type, current_balance) 
                           VALUES (?, ?, ?, ?)";
            $stmt = $this->pdo->prepare($account_sql);
            $account_number = 'ACC' . date('YmdHis') . $application_id;
            $stmt->execute([$app['client_id'], $account_number, 'Кредитный счет', 0]);
            $account_id = $this->pdo->lastInsertId();
            
            // Create contract
            $contract_sql = "INSERT INTO credit_contracts 
                           (application_id, product_id, account_id, contract_number, signing_date, 
                            loan_amount, interest_rate, loan_term) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
            $stmt = $this->pdo->prepare($contract_sql);
            $contract_number = 'CONT' . date('YmdHis') . $application_id;
            $stmt->execute([
                $application_id,
                $app['product_id'],
                $account_id,
                $contract_number,
                date('Y-m-d'),
                $app['requested_amount'],
                $app['base_interest_rate'],
                12 // Default term 12 months
            ]);
            $contract_id = $this->pdo->lastInsertId();
            
            // Generate payment schedule (annuity)
            $this->generatePaymentSchedule($contract_id, $app['requested_amount'], 
                                         $app['base_interest_rate'], 12);
            
            // Update account balance
            $update_balance = "UPDATE accounts SET current_balance = ? WHERE account_id = ?";
            $stmt = $this->pdo->prepare($update_balance);
            $stmt->execute([$app['requested_amount'], $account_id]);
            
            $this->pdo->commit();
            
            return [
                'success' => true,
                'contract_id' => $contract_id,
                'contract_number' => $contract_number
            ];
        } catch (Exception $e) {
            $this->pdo->rollBack();
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }
    
    private function generatePaymentSchedule($contract_id, $amount, $rate, $months) {
        // Calculate annuity payment
        $monthly_rate = $rate / 100 / 12;
        $payment = $amount * ($monthly_rate * pow(1 + $monthly_rate, $months)) / 
                   (pow(1 + $monthly_rate, $months) - 1);
        
        $date = new DateTime();
        $sql = "INSERT INTO payment_schedule (contract_id, payment_date, payment_amount, status) 
               VALUES (?, ?, ?, ?)";
        $stmt = $this->pdo->prepare($sql);
        
        for ($i = 1; $i <= $months; $i++) {
            $date->add(new DateInterval('P1M'));
            $stmt->execute([
                $contract_id,
                $date->format('Y-m-d'),
                round($payment, 2),
                'Ожидает оплаты'
            ]);
        }
    }
}
?>
