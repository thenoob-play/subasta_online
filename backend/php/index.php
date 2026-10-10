<?php

require_once __DIR__ . '/src/controladores/Categoria.php';
require_once __DIR__ . '/src/controladores/Puja.php';
require_once __DIR__ . '/src/controladores/HistorialPuja.php';


header("Content-Type: application/json");
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") {
    http_response_code(200);
    exit;
}

$uri = explode("/", trim(parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH), "/"));

$resource = $uri[0] ?? null;
$id = isset($uri[1]) ? (int)$uri[1] : null;
$method = $_SERVER["REQUEST_METHOD"];

switch ($resource) {

    case "categoria":
        $controller = new CategoriaController();

        if ($method === "GET") $controller->get($id);
        elseif ($method === "POST") $controller->create();
        elseif ($method === "PUT") $controller->updateFull($id);
        elseif ($method === "PATCH") $controller->updatePartial($id);
        elseif ($method === "DELETE") $controller->delete($id);
        break;
    
    case "puja":
        $controller = new PujaController();
        if ($method === "GET" && ($uri[1] ?? null) === "ultima") {
            $idSubasta = filter_var(
                $uri[2] ?? null,
                FILTER_VALIDATE_INT,
                ["options" => ["min_range" => 1]]
            );
            $controller->getUltimaPorSubasta($idSubasta === false ? null : $idSubasta);
        }
        elseif ($method === "GET") $controller->get($id);
        elseif ($method === "POST") $controller->create();
        elseif ($method === "DELETE") $controller->delete($id);
        break;
 

    case "historialPuja":
        $controller = new HistorialPujaController();
        if ($method === "GET") $controller->get($id);
        elseif ($method === "POST") $controller->create();
        #elseif ($method === "PUT") $controller->updateFull($id);
        #elseif ($method === "PATCH") $controller->updatePartial($id);
        #elseif ($method === "DELETE") $controller->delete($id);
        break;

    default:
        http_response_code(404);
        echo json_encode(["status" => "error", "message" => "Recurso no encontrado"]);
}