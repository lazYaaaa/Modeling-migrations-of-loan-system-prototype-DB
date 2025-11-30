<?php
header("Content-type: image/png");

$img = imagecreatetruecolor(350, 200);

$red   = imagecolorallocate($img, 255, 0, 0);
$white = imagecolorallocate($img, 255, 255, 255);
$black = imagecolorallocate($img, 0, 0, 0);
$blue  = imagecolorallocate($img, 0, 0, 255);

imagefilledrectangle($img, 0, 0, 349, 199, $red);

imagefilledrectangle($img, 245, 25, 280, 180, $white);

imagefilledrectangle($img, 50, 50, 150, 150, $blue);

$text = 'Тест: Отдел 22';

$font_paths = [
    'C:/Windows/Fonts/arial.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
];

$font = null;
foreach ($font_paths as $path) {
    if (file_exists($path)) {
        $font = $path;
        break;
    }
}

if ($font) {
    imagettftext($img, 12, 0, 30, 30, $black, $font, $text);
    imagettftext($img, 10, 0, 40, 180, $white, $font, 'PostgreSQL + PHP');
} else {
    imagestring($img, 5, 30, 30, $text, $black);
    imagestring($img, 3, 40, 180, 'PostgreSQL + PHP', $white);
}

imagepng($img);
imagedestroy($img);
?>