<?php


require_once __DIR__ . '/../../config/conexion.php';

class PujaController {

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
            $stmt = $this->db->prepare("SELECT id_puja, monto, fecha, subasta_id_subasta, usuario_id_usuario FROM puja WHERE id_puja = :id_puja");
            $stmt->bindParam(':id_puja', $id, PDO::PARAM_INT);
            $stmt->execute();

            $data = $stmt->fetch();

            if ($data) {
                echo json_encode(["status" => "success", "data" => $data]);
            } else {
                http_response_code(404);
                echo json_encode(["status" => "error", "message" => "No encontrada"]);
            }

        } else {
            $stmt = $this->db->query("SELECT id_puja, monto, fecha, subasta_id_subasta, usuario_id_usuario FROM puja ORDER BY id_puja ASC");
            echo json_encode(["status" => "success", "data" => $stmt->fetchAll()]);
        }
    }

    public function getUltimaPorSubasta(?int $idSubasta): void
    {
        header("Content-Type: application/json; charset=UTF-8");

        if (!$this->db) {
            $this->responder(500, ["status" => "error", "message" => "Sin conexión a la BD"]);
            return;
        }
        if ($idSubasta === null || $idSubasta < 1) {
            $this->responder(400, ["status" => "error", "message" => "ID de subasta inválido"]);
            return;
        }

        try {
            $stmt = $this->db->prepare(
                "SELECT id_puja, monto, fecha, subasta_id_subasta, usuario_id_usuario
                 FROM puja
                 WHERE subasta_id_subasta = :id_subasta
                 ORDER BY fecha DESC, id_puja DESC
                 LIMIT 1"
            );
            $stmt->bindValue(":id_subasta", $idSubasta, PDO::PARAM_INT);
            $stmt->execute();
            $ultimaPuja = $stmt->fetch(PDO::FETCH_ASSOC);

            $this->responder(200, [
                "status" => "success",
                "data" => $ultimaPuja ?: null,
            ]);
        } catch (PDOException $error) {
            error_log("Error al consultar la última puja: " . $error->getMessage());
            $this->responder(500, ["status" => "error", "message" => "No se pudo consultar la última puja"]);
        }
    }

    public function create(): void
    {
        header("Content-Type: application/json; charset=UTF-8");

        if (!$this->db) {
            $this->responder(500, ["status" => "error", "message" => "Sin conexión a la BD"]);
            return;
        }

        $data = json_decode(file_get_contents("php://input"), true);
        if (
            !is_array($data)
            || !isset($data["monto"], $data["subasta_id_subasta"], $data["usuario_id_usuario"])
        ) {
            $this->responder(400, ["status" => "error", "message" => "Datos incompletos o JSON inválido"]);
            return;
        }

        $idSubasta = filter_var($data["subasta_id_subasta"], FILTER_VALIDATE_INT, ["options" => ["min_range" => 1]]);
        $idUsuario = filter_var($data["usuario_id_usuario"], FILTER_VALIDATE_INT, ["options" => ["min_range" => 1]]);
        $monto = $this->validarMonto($data["monto"]);

        if ($idSubasta === false || $idUsuario === false || $monto === null) {
            $this->responder(400, [
                "status" => "error",
                "message" => "Se requieren IDs positivos y un monto positivo con máximo dos decimales",
            ]);
            return;
        }

        try {
            $this->db->beginTransaction();

            $stmtSubasta = $this->db->prepare(
                "SELECT estado, precio_inicial, incremento_minimo, fecha_inicio, fecha_fin, NOW() AS fecha_actual
                 FROM subasta
                 WHERE id_subasta = :id_subasta
                 FOR UPDATE"
            );
            $stmtSubasta->bindValue(":id_subasta", $idSubasta, PDO::PARAM_INT);
            $stmtSubasta->execute();
            $subasta = $stmtSubasta->fetch(PDO::FETCH_ASSOC);

            if (!$subasta) {
                $this->db->rollBack();
                $this->responder(404, ["status" => "error", "message" => "Subasta no encontrada"]);
                return;
            }

            $ahora = $subasta["fecha_actual"];
            if (
                !in_array($subasta["estado"], ["por_empezar", "en_curso"], true)
                || $ahora < $subasta["fecha_inicio"]
                || $ahora >= $subasta["fecha_fin"]
            ) {
                $this->db->rollBack();
                $this->responder(409, ["status" => "error", "message" => "La subasta no está activa para recibir pujas"]);
                return;
            }

            $stmtUltimaPuja = $this->db->prepare(
                "SELECT usuario_id_usuario
                 FROM puja
                 WHERE subasta_id_subasta = :id_subasta
                 ORDER BY fecha DESC, id_puja DESC
                 LIMIT 1"
            );
            $stmtUltimaPuja->bindValue(":id_subasta", $idSubasta, PDO::PARAM_INT);
            $stmtUltimaPuja->execute();
            $ultimoUsuario = $stmtUltimaPuja->fetchColumn();

            if ($ultimoUsuario !== false && (int) $ultimoUsuario === $idUsuario) {
                $this->db->rollBack();
                $this->responder(409, [
                    "status" => "error",
                    "message" => "No puedes ofertar porque tu usuario realizó la última puja de esta subasta. Espera a que otro usuario oferte.",
                ]);
                return;
            }

            $precioInicial = $this->validarMonto($subasta["precio_inicial"]);
            $incremento = $this->validarMonto($subasta["incremento_minimo"]);
            if ($precioInicial === null || $incremento === null) {
                throw new RuntimeException("La subasta tiene valores monetarios inválidos");
            }

            $stmtMax = $this->db->prepare(
                "SELECT MAX(monto) FROM puja WHERE subasta_id_subasta = :id_subasta"
            );
            $stmtMax->bindValue(":id_subasta", $idSubasta, PDO::PARAM_INT);
            $stmtMax->execute();
            $pujaMaxima = $stmtMax->fetchColumn();

            $montoActualCentavos = $precioInicial;
            if ($pujaMaxima !== false && $pujaMaxima !== null) {
                $pujaMaximaCentavos = $this->validarMonto($pujaMaxima);
                if ($pujaMaximaCentavos === null) {
                    throw new RuntimeException("La subasta tiene una puja registrada con monto inválido");
                }
                $montoActualCentavos = max($montoActualCentavos, $pujaMaximaCentavos);
            }

            $montoMinimoCentavos = $montoActualCentavos + $incremento;
            if ($monto < $montoMinimoCentavos) {
                $this->db->rollBack();
                $this->responder(400, [
                    "status" => "error",
                    "message" => "Monto insuficiente. La puja mínima requerida es " . $this->formatearMonto($montoMinimoCentavos),
                    "monto_minimo" => $this->formatearMonto($montoMinimoCentavos),
                ]);
                return;
            }

            $stmtInsert = $this->db->prepare(
                "INSERT INTO puja (monto, subasta_id_subasta, usuario_id_usuario)
                 VALUES (:monto, :id_subasta, :id_usuario)"
            );
            $stmtInsert->bindValue(":monto", $this->formatearMonto($monto), PDO::PARAM_STR);
            $stmtInsert->bindValue(":id_subasta", $idSubasta, PDO::PARAM_INT);
            $stmtInsert->bindValue(":id_usuario", $idUsuario, PDO::PARAM_INT);
            $stmtInsert->execute();
            $pujaId = $this->db->lastInsertId();

            $this->db->commit();
            $this->responder(201, [
                "status" => "success",
                "message" => "Puja aceptada correctamente",
                "id_puja" => $pujaId,
            ]);
        } catch (Throwable $error) {
            if ($this->db->inTransaction()) {
                $this->db->rollBack();
            }
            error_log("Error al registrar la puja: " . $error->getMessage());
            $this->responder(500, ["status" => "error", "message" => "No se pudo registrar la puja"]);
        }
    }

    public function delete(?int $id = null): void {

        if (!$this->db) {
            http_response_code(500);
            echo json_encode(["status" => "error", "message" => "Sin conexion a la BD"]);
            return;
        }

        if ($id === null) {
            $data = json_decode(file_get_contents("php://input"), true);
            $id = is_array($data) ? ($data["id_puja"] ?? null) : null;
        }

        $id = filter_var($id, FILTER_VALIDATE_INT, ["options" => ["min_range" => 1]]);
        if ($id === false) {
            http_response_code(400);
            echo json_encode(["status" => "error", "message" => "Falta un ID válido de la puja a eliminar"]);
            return;
        }

        $stmt = $this->db->prepare("DELETE FROM puja WHERE id_puja = :id");
        $stmt->bindValue(':id', $id, PDO::PARAM_INT);
        $stmt->execute();

        echo json_encode(["status" => "success"]);
    }

    private function validarMonto($monto): ?int
    {
        if (!is_numeric($monto) || !preg_match('/^\d{1,8}(?:\.\d{1,2})?$/', (string) $monto)) {
            return null;
        }

        $partes = explode(".", (string) $monto, 2);
        $unidades = (int) $partes[0];
        $centavos = isset($partes[1]) ? (int) str_pad($partes[1], 2, "0") : 0;
        $total = ($unidades * 100) + $centavos;

        return $total > 0 ? $total : null;
    }

    private function formatearMonto(int $centavos): string
    {
        return intdiv($centavos, 100) . "." . str_pad((string) ($centavos % 100), 2, "0", STR_PAD_LEFT);
    }

    private function responder(int $codigo, array $respuesta): void
    {
        http_response_code($codigo);
        echo json_encode($respuesta, JSON_UNESCAPED_UNICODE);
    }
}