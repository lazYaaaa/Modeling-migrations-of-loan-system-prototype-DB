<?php
// Simple router for PHP built-in server.
// Routes requests starting with /api to api/index.php while allowing static files to be served.

$uri = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));
$docRoot = __DIR__;

$requested = $docRoot . $uri;
// If the request matches an existing file, let the built-in server serve it.
if ($uri !== '/' && file_exists($requested)) {
    return false;
}

// Route API requests to api/index.php
if (preg_match('#^/api($|/)#', $uri)) {
    require $docRoot . '/api/index.php';
    return;
}

// Redirect root to frontend folder for convenience
if ($uri === '/' || $uri === '') {
    header('Location: /frontend/');
    return;
}

// Not found — let the built-in server handle it (will return 404).
return false;
