<?php
if (parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) === '/api/user') {
    header('Content-Type: application/json');
    echo json_encode([
        "name" => "Muavia",
        "project" => "Mamba",
        "role" => "AI Engineer",
        "version" => "0.1.0"
    ]);
}
?>