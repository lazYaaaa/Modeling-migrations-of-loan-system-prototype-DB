<?php

header('Content-Type: text/html; charset=utf-8');
?>
<html>
<head>
    <title>Задание 2. Факториал</title>
</head>
<body style="margin: 20px;">
    <h2>Вычисление факториала</h2>
    <?php
    function factorial($n) {
        if ($n <= 1) return 1;
        $result = 1;
        for ($i = 2; $i <= $n; $i++) {
            $result *= $i;
        }
        return $result;
    }
    
    for ($i = 0; $i <= 20; $i++) {
        echo "Факториал $i = " . factorial($i) . "<br>\n";
    }
    ?>
</body>
</html>