<?php

require_once __DIR__ . '/../../config/conexion.php';

class CategoriaController {

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
            $stmt = $this->db->prepare("SELECT id_categoria AS id_categoria, nombre, descripcion FROM categoria WHERE id_categoria = :id");
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
            $stmt = $this->db->query("SELECT id_categoria AS id_categoria, nombre, descripcion FROM categoria ORDER BY id_categoria ASC");
            echo json_encode(["status" => "success", "data" => $stmt->fetchAll()]);
        }
    }

    public function create(): void {
        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin BD"]);
            return;
        }
        $data = json_decode(file_get_contents("php://input"), true);

        if (
            !is_array($data)
            || !isset($data["nombre"])
            || !is_string($data["nombre"])
            || trim($data["nombre"]) === ""
            || (array_key_exists("descripcion", $data) && $data["descripcion"] !== null && !is_string($data["descripcion"]))
        ) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Nombre requerido"]);
            return;
        }

        try {
            $stmt = $this->db->prepare("INSERT INTO categoria (nombre, descripcion) VALUES (:nombre, :descripcion)");
            $stmt->bindValue(':nombre', trim($data["nombre"]), PDO::PARAM_STR);
            $descripcion = isset($data["descripcion"]) && trim((string)$data["descripcion"]) !== ""
                ? trim((string)$data["descripcion"])
                : null;
            $stmt->bindValue(':descripcion', $descripcion, $descripcion === null ? PDO::PARAM_NULL : PDO::PARAM_STR);
            $stmt->execute();

            http_response_code(201);
            echo json_encode([
                "status" => "success",
                "id" => $this->db->lastInsertId()
            ]);
        } catch (PDOException $error) {
            error_log("Error al crear categoría: " . $error->getMessage());
            http_response_code($error->getCode() === "23000" ? 409 : 500);
            echo json_encode(["status" => "error", "message" => "No se pudo crear la categoría"]);
        }
    }

    public function updateFull(int $id): void {
        $data = json_decode(file_get_contents("php://input"), true);
        if (
            !is_array($data)
            || !isset($data["nombre"])
            || !is_string($data["nombre"])
            || trim($data["nombre"]) === ""
            || (array_key_exists("descripcion", $data) && $data["descripcion"] !== null && !is_string($data["descripcion"]))
        ) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Nombre requerido"]);
            return;
        }

        $descripcion = isset($data["descripcion"]) && trim((string)$data["descripcion"]) !== ""
            ? trim((string)$data["descripcion"])
            : null;
        $this->actualizar($id, trim($data["nombre"]), $descripcion);
    }

    public function updatePartial(int $id): void {
        $data = json_decode(file_get_contents("php://input"), true);
        if (!is_array($data) || !$data || array_diff(array_keys($data), ["nombre", "descripcion"])) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Debe enviar nombre y/o descripción"]);
            return;
        }
        if (
            (isset($data["nombre"]) && (!is_string($data["nombre"]) || trim($data["nombre"]) === ""))
            || (array_key_exists("descripcion", $data) && $data["descripcion"] !== null && !is_string($data["descripcion"]))
        ) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Nombre inválido"]);
            return;
        }

        $campos = [];
        $parametros = [":id" => $id];
        if (array_key_exists("nombre", $data)) {
            $campos[] = "nombre = :nombre";
            $parametros[":nombre"] = trim($data["nombre"]);
        }
        if (array_key_exists("descripcion", $data)) {
            $campos[] = "descripcion = :descripcion";
            $descripcion = $data["descripcion"];
            $parametros[":descripcion"] = is_string($descripcion) && trim($descripcion) !== "" ? trim($descripcion) : null;
        }
        $this->actualizarCampos($id, $campos, $parametros);
    }

    public function delete(int $id): void {
        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin BD"]);
            return;
        }
        try {
            $stmt = $this->db->prepare("DELETE FROM categoria WHERE id_categoria = :id");
            $stmt->bindValue(':id', $id, PDO::PARAM_INT);
            $stmt->execute();
            if ($stmt->rowCount() === 0) {
                http_response_code(404);
                echo json_encode(["status" => "error", "message" => "No encontrada"]);
                return;
            }
            echo json_encode(["status" => "success"]);
        } catch (PDOException $error) {
            error_log("Error al eliminar categoría: " . $error->getMessage());
            http_response_code($error->getCode() === "23000" ? 409 : 500);
            echo json_encode(["status" => "error", "message" => "No se pudo eliminar la categoría"]);
        }
    }

    private function actualizar(int $id, string $nombre, ?string $descripcion): void {
        $this->actualizarCampos(
            $id,
            ["nombre = :nombre", "descripcion = :descripcion"],
            [":id" => $id, ":nombre" => $nombre, ":descripcion" => $descripcion]
        );
    }

    private function actualizarCampos(int $id, array $campos, array $parametros): void {
        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin BD"]);
            return;
        }
        try {
            $stmt = $this->db->prepare(
                "UPDATE categoria SET " . implode(", ", $campos) . " WHERE id_categoria = :id"
            );
            foreach ($parametros as $nombre => $valor) {
                $stmt->bindValue(
                    $nombre,
                    $valor,
                    $valor === null ? PDO::PARAM_NULL : (is_int($valor) ? PDO::PARAM_INT : PDO::PARAM_STR)
                );
            }
            $stmt->execute();
            if ($stmt->rowCount() === 0 && !$this->existe($id)) {
                http_response_code(404);
                echo json_encode(["status" => "error", "message" => "No encontrada"]);
                return;
            }
            echo json_encode(["status" => "success"]);
        } catch (PDOException $error) {
            error_log("Error al actualizar categoría: " . $error->getMessage());
            http_response_code($error->getCode() === "23000" ? 409 : 500);
            echo json_encode(["status" => "error", "message" => "No se pudo actualizar la categoría"]);
        }
    }

    private function existe(int $id): bool {
        $stmt = $this->db->prepare("SELECT 1 FROM categoria WHERE id_categoria = :id");
        $stmt->bindValue(":id", $id, PDO::PARAM_INT);
        $stmt->execute();
        return (bool)$stmt->fetchColumn();
    }
}