<?php
// Test authentication
$ch = curl_init("http://localhost:8000/api/auth");
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(["login" => "user_1", "password" => "user_1"]));
curl_setopt($ch, CURLOPT_HTTPHEADER, ["Content-Type: application/json"]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_COOKIEJAR, '/tmp/cookies.txt');
$response = curl_exec($ch);
echo "Response: " . $response . "\n";
curl_close($ch);
?>
