<?php

require_once __DIR__ . '/../baseDatos/bd.php';

class Database {

    private ?PDO $conn = null;

    public function getConnection(): ?PDO {

        try {
            $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;

            $this->conn = new PDO($dsn, DB_USER, DB_PASS, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false
            ]);

            return $this->conn;

        } catch (PDOException $e) {
            error_log("Error BD: " . $e->getMessage());
            return null;
        }
    }
}