<?php
header("Content-type: image/png");
$img = imagecreatetruecolor(350, 200);
$red   = imagecolorallocate($img, 255,   0,   0);
$white = imagecolorallocate($img, 255, 255, 255);
$black = imagecolorallocate($img, 0, 0, 0);
imagefilledrectangle($img, 0, 0, 350, 199, $red);

imagefilledrectangle($img, 245, 25, 280, 180, $white);   

$text = 'Testing...  Dept. 22';
$font = 'C:\\Windows\\Fonts\\arial.ttf';

imagettftext($img, 20, 20, 10, 120, $black, $font, $text);
imagepng($img);
imagedestroy($img);
?>