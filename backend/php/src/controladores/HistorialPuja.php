<?php

require_once __DIR__ . '/../../config/conexion.php';

class HistorialPujaController {

    private ?PDO $db;

    public function __construct() {
        $this->db = (new Database())->getConnection();
    }

    public function get(?int $id = null): void {

        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin BD"]);
            return;
        }

        if ($id) {
            $stmt = $this->db->prepare("SELECT id_historial_puja AS id_historial_puja, monto_oferta, monto_anterior , fecha , subasta_id_subasta, usuario_id_usuario FROM historial_puja WHERE id_historial_puja = :id");
            $stmt->bindParam(':id', $id, PDO::PARAM_INT);
            $stmt->execute();

            $data = $stmt->fetch();

            if ($data) {
                echo json_encode(["status" => "success", "data" => $data]);
            } else {
                http_response_code(404);
                echo json_encode(["status" => "error", "message" => "No encontrada"]);
            }

        } else {
            $stmt = $this->db->query("SELECT id_historial_puja AS id_historial_puja, monto_oferta, monto_anterior , fecha , subasta_id_subasta, usuario_id_usuario FROM historial_puja ORDER BY id_historial_puja ASC");
            echo json_encode(["status" => "success", "data" => $stmt->fetchAll()]);
        }
    }



    public function create(): void {
        header("Content-Type: application/json; charset=UTF-8");

        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin conexion a la BD"]);
            return;
        }

        $data = json_decode(file_get_contents("php://input"), true);

        // Validar que lleguen los campos obligatorios de la tabla historial_puja
        if (
            !isset($data["monto_oferta"], $data["fecha"], $data["subasta_id_subasta"], $data["usuario_id_usuario"])
        ) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Datos incompletos"]);
            return;
        }

        try {
            $sql = "INSERT INTO historial_puja (monto_oferta, monto_anterior, fecha, subasta_id_subasta, usuario_id_usuario) 
                    VALUES (:monto_oferta, :monto_anterior, :fecha, :subasta_id_subasta, :usuario_id_usuario)";
            
            $stmt = $this->db->prepare($sql);

            // Asignación de parámetros correcta coincidiendo con la consulta SQL
            $stmt->bindValue(':monto_oferta', $data["monto_oferta"], PDO::PARAM_STR);
            $stmt->bindValue(':monto_anterior', $data["monto_anterior"] ?? 0, PDO::PARAM_STR);
            $stmt->bindValue(':fecha', $data["fecha"], PDO::PARAM_STR);
            $stmt->bindValue(':subasta_id_subasta', (int)$data["subasta_id_subasta"], PDO::PARAM_INT);
            $stmt->bindValue(':usuario_id_usuario', (int)$data["usuario_id_usuario"], PDO::PARAM_INT);

            $stmt->execute();

            http_response_code(201);
            echo json_encode([
                "status" => "success",
                "id" => $this->db->lastInsertId()
            ]);
        } catch (PDOException $e) {
            http_response_code(500);
            echo json_encode([
                "status" => "error",
                "message" => "Error al registrar la puja: " . $e->getMessage()
            ]);
        }
    }
}