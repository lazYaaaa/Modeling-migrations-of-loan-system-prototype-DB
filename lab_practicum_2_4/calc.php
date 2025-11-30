<?php
header('Content-Type: text/html; charset=utf-8');

$v1 = $v2 = $res = '';
$error = '';

if ($_POST['action'] ?? '' == 'submitted') {
    $v1 = $_POST['var1'] ?? '';
    $v2 = $_POST['var2'] ?? '';
    
    if (is_numeric($v1) && is_numeric($v2)) {
        $v1 = floatval($v1);
        $v2 = floatval($v2);
        $res = $v1 + $v2;
    } else {
        $error = "Введите числа!";
    }
}
?>
<html>
<head>
    <title>Задание 3. Калькулятор</title>
</head>
<body>
    <h2>Калькулятор сложения</h2>
    <?php if ($error): ?>
        <div style="color: red;"><?= $error ?></div>
    <?php endif; ?>
    
    <form method="post">
        <input type="text" name="var1" value="<?= htmlspecialchars($v1) ?>" size="5">
        +
        <input type="text" name="var2" value="<?= htmlspecialchars($v2) ?>" size="5">
        = <?= $res ?>
        <br><br>
        <input type="hidden" name="action" value="submitted">
        <input type="submit" value="Посчитать!">
    </form>
</body>
</html>