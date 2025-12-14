<?php
class LoanProduct {
    private $pdo;
    
    public function __construct($pdo) {
        $this->pdo = $pdo;
    }
    
    public function getAllProducts() {
        $sql = "SELECT * FROM loan_products ORDER BY product_name";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute();
        return $stmt->fetchAll();
    }
    
    public function getProductById($id) {
        $sql = "SELECT * FROM loan_products WHERE product_id = ?";
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute([$id]);
        return $stmt->fetch();
    }
    
    public function validateAmount($product_id, $amount) {
        $product = $this->getProductById($product_id);
        if (!$product) return false;
        
        return $amount >= $product['min_amount'] && 
               $amount <= $product['max_amount'];
    }
}
?>
