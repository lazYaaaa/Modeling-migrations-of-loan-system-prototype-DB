<?php
class Client {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    public function getAllClients() {
        $sql = "SELECT * FROM clients ORDER BY full_name";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    public function getClientById($id) {
        $sql = "SELECT * FROM clients WHERE client_id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
    
    public function getClientDocuments($client_id) {
        $sql = "SELECT * FROM documents WHERE client_id = ? ORDER BY issue_date DESC";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$client_id]);
        return $stmt->fetchAll();
    }
    
    public function getClientCreditHistory($client_id) {
        $sql = "SELECT * FROM credit_history WHERE client_id = ? ORDER BY event_date DESC";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$client_id]);
        return $stmt->fetchAll();
    }
    
    public function getClientAccounts($client_id) {
        $sql = "SELECT * FROM accounts WHERE client_id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$client_id]);
        return $stmt->fetchAll();
    }
    
    public function createClient($data) {
        $sql = "INSERT INTO clients (full_name, passport_number, phone_number, address) 
               VALUES (?, ?, ?, ?)";
        $stmt = $this->pdo->prepare($sql);
        $result = $stmt->execute([
            $data['full_name'],
            $data['passport_number'],
            $data['phone_number'] ?? null,
            $data['address'] ?? null
        ]);
        
        return $result ? $this->pdo->lastInsertId() : false;
    }
    
    public function updateClient($id, $data) {
        $sql = "UPDATE clients SET full_name = ?, phone_number = ?, address = ? 
               WHERE client_id = ?";
        $stmt = $this->pdo->prepare($sql);
        return $stmt->execute([
            $data['full_name'],
            $data['phone_number'] ?? null,
            $data['address'] ?? null,
            $id
        ]);
    }
}
?>
