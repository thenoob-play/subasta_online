-- Run once against an existing subasta_online database after reviewing the
-- duplicate checks below. Requires MySQL 8.0.16 or newer for enforced CHECKs.
USE `subasta_online`;

-- These queries must return no rows before applying the unique indexes:
SELECT `nombre`, COUNT(*) AS `cantidad`
FROM `categoria`
GROUP BY `nombre`
HAVING COUNT(*) > 1;

SELECT `articulo_id_articulo`, COUNT(*) AS `cantidad`
FROM `subasta`
GROUP BY `articulo_id_articulo`
HAVING COUNT(*) > 1;

SELECT `subasta_id_subasta`, COUNT(*) AS `cantidad`
FROM `pago`
GROUP BY `subasta_id_subasta`
HAVING COUNT(*) > 1;

SELECT `pago_id_pago`, COUNT(*) AS `cantidad`
FROM `transferencia_pago`
GROUP BY `pago_id_pago`
HAVING COUNT(*) > 1;

ALTER TABLE `usuario`
  ADD CONSTRAINT `chk_usuario_activo` CHECK (`activo` IN (0, 1));

ALTER TABLE `categoria`
  ADD UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  ADD CONSTRAINT `chk_categoria_nombre` CHECK (CHAR_LENGTH(TRIM(`nombre`)) > 0);

ALTER TABLE `subasta`
  ADD UNIQUE KEY `articulo_id_articulo_UNIQUE` (`articulo_id_articulo`),
  ADD CONSTRAINT `chk_subasta_precio_inicial` CHECK (`precio_inicial` >= 0),
  ADD CONSTRAINT `chk_subasta_incremento_minimo` CHECK (`incremento_minimo` > 0),
  ADD CONSTRAINT `chk_subasta_fechas` CHECK (`fecha_inicio` < `fecha_fin`);

ALTER TABLE `puja`
  ADD CONSTRAINT `chk_puja_monto` CHECK (`monto` > 0);

ALTER TABLE `pago`
  ADD COLUMN `metodo` enum('efectivo','transferencia') NOT NULL DEFAULT 'transferencia'
    AFTER `id_pago`,
  ADD UNIQUE KEY `subasta_id_subasta_UNIQUE` (`subasta_id_subasta`),
  ADD CONSTRAINT `chk_pago_monto` CHECK (`monto` > 0);

ALTER TABLE `transferencia_pago`
  ADD UNIQUE KEY `pago_id_pago_UNIQUE` (`pago_id_pago`);

CREATE TABLE `historial_puja` (
  `id_historial_puja` int NOT NULL AUTO_INCREMENT,
  `monto_oferta` decimal(10,2) NOT NULL,
  `monto_anterior` decimal(10,2) NOT NULL DEFAULT '0.00',
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `subasta_id_subasta` int NOT NULL,
  `usuario_id_usuario` int NOT NULL,
  PRIMARY KEY (`id_historial_puja`),
  KEY `fk_historial_puja_subasta` (`subasta_id_subasta`),
  KEY `fk_historial_puja_usuario` (`usuario_id_usuario`),
  CONSTRAINT `fk_historial_puja_subasta` FOREIGN KEY (`subasta_id_subasta`)
    REFERENCES `subasta` (`id_subasta`),
  CONSTRAINT `fk_historial_puja_usuario` FOREIGN KEY (`usuario_id_usuario`)
    REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `chk_historial_puja_monto_oferta` CHECK (`monto_oferta` > 0),
  CONSTRAINT `chk_historial_puja_monto_anterior` CHECK (`monto_anterior` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `vendedor` (
  `id_usuario` int NOT NULL,
  `documento` varchar(45) NOT NULL,
  `nombre_comercial` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `cuenta_bancaria` varchar(45) NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `documento_UNIQUE` (`documento`),
  UNIQUE KEY `cuenta_bancaria_UNIQUE` (`cuenta_bancaria`),
  CONSTRAINT `fk_vendedor_usuario` FOREIGN KEY (`id_usuario`)
    REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_vendedor_documento` CHECK (CHAR_LENGTH(TRIM(`documento`)) >= 6),
  CONSTRAINT `chk_vendedor_cuenta_bancaria`
    CHECK (CHAR_LENGTH(TRIM(`cuenta_bancaria`)) >= 6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
