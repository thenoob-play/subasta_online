CREATE DATABASE  IF NOT EXISTS `subasta_online` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `subasta_online`;
-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: subasta_online
-- ------------------------------------------------------
-- Server version	9.6.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'd40ec8a6-2467-11f1-b260-489ebdf55486:1-1046';

--
-- Table structure for table `articulo`
--

DROP TABLE IF EXISTS `articulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `articulo` (
  `id_articulo` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(45) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `condicion` enum('nuevo','bueno','medio','malo') NOT NULL,
  `categoria_id_categoria` int NOT NULL,
  `usuario_id_vendedor` int NOT NULL,
  PRIMARY KEY (`id_articulo`),
  KEY `fk_articulo_categoria` (`categoria_id_categoria`),
  KEY `fk_articulo_usuario` (`usuario_id_vendedor`),
  CONSTRAINT `fk_articulo_categoria` FOREIGN KEY (`categoria_id_categoria`) REFERENCES `categoria` (`id_categoria`),
  CONSTRAINT `fk_articulo_usuario` FOREIGN KEY (`usuario_id_vendedor`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `articulo`
--

LOCK TABLES `articulo` WRITE;
/*!40000 ALTER TABLE `articulo` DISABLE KEYS */;
INSERT INTO `articulo` VALUES (2,'Chaqueta ','2Chaqueta de jean en buen estado, talla M.','bueno',1,1),(3,'Chaqueta ','2Chaqueta de jean en buen estado, talla M.','bueno',1,1),(4,'zapatos ','2Chaqueta de jean en buen estado, talla M.','bueno',1,1),(5,'balones ','balones del mundial de futbol 2026','bueno',1,1),(6,'balones ','balones del mundial de futbol 2026','bueno',1,1),(7,'balones22 ','balones del mundial de futbol 2026','bueno',1,1);
/*!40000 ALTER TABLE `articulo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categoria`
--

DROP TABLE IF EXISTS `categoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoria` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre_UNIQUE` (`nombre`),
  CONSTRAINT `chk_categoria_nombre` CHECK (CHAR_LENGTH(TRIM(`nombre`)) > 0)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoria`
--

LOCK TABLES `categoria` WRITE;
/*!40000 ALTER TABLE `categoria` DISABLE KEYS */;
INSERT INTO `categoria` VALUES (1,'ropa','la mejor ropa'),(2,'zapatos','los mjeores zapatosssss'),(4,'Electrónica','es muy bno el pantalon');
/*!40000 ALTER TABLE `categoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `imagen_articulo`
--

DROP TABLE IF EXISTS `imagen_articulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imagen_articulo` (
  `id_imagen` int NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `articulo_id_articulo` int NOT NULL,
  PRIMARY KEY (`id_imagen`),
  KEY `fk_imagen_articulo` (`articulo_id_articulo`),
  CONSTRAINT `fk_imagen_articulo` FOREIGN KEY (`articulo_id_articulo`) REFERENCES `articulo` (`id_articulo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imagen_articulo`
--

LOCK TABLES `imagen_articulo` WRITE;
/*!40000 ALTER TABLE `imagen_articulo` DISABLE KEYS */;
INSERT INTO `imagen_articulo` VALUES (3,'https://ejemplo.com/imagenes/chaqueta1.jpg',2),(4,'https://ejemplo.com/imagenes/chaqueta2.jpg',2),(5,'https://ejemplo.com/imagenes/chaqueta1.jpg',3),(6,'https://ejemplo.com/imagenes/chaqueta2.jpg',3),(7,'https://ejemplo.com/imagenes/chaqueta1.jpg',4),(8,'https://ejemplo.com/imagenes/chaqueta2.jpg',4),(9,'https://ejemplo.com/imagenes/chaqueta1.jpg',5),(10,'https://ejemplo.com/imagenes/chaqueta2.jpg',5),(11,'https://ejemplo.com/imagenes/chaqueta1.jpg',6),(12,'https://ejemplo.com/imagenes/chaqueta2.jpg',6),(13,'https://ejemplo.com/imagenes/chaqueta1.jpg',7),(14,'https://ejemplo.com/imagenes/chaqueta2.jpg',7);
/*!40000 ALTER TABLE `imagen_articulo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pago`
--

DROP TABLE IF EXISTS `pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pago` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `metodo` enum('efectivo','transferencia') NOT NULL DEFAULT 'transferencia',
  `monto` decimal(10,2) NOT NULL,
  `estado_pago` enum('realizado','en_espera','rechazado') NOT NULL,
  `fechapago` datetime DEFAULT NULL,
  `subasta_id_subasta` int NOT NULL,
  `usuario_id_comprador` int NOT NULL,
  PRIMARY KEY (`id_pago`),
  UNIQUE KEY `subasta_id_subasta_UNIQUE` (`subasta_id_subasta`),
  KEY `fk_pago_usuario` (`usuario_id_comprador`),
  CONSTRAINT `fk_pago_subasta` FOREIGN KEY (`subasta_id_subasta`) REFERENCES `subasta` (`id_subasta`),
  CONSTRAINT `fk_pago_usuario` FOREIGN KEY (`usuario_id_comprador`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `chk_pago_monto` CHECK (`monto` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pago`
--

LOCK TABLES `pago` WRITE;
/*!40000 ALTER TABLE `pago` DISABLE KEYS */;
INSERT INTO `pago` (`id_pago`,`metodo`,`monto`,`estado_pago`,`fechapago`,`subasta_id_subasta`,`usuario_id_comprador`) VALUES (1,'transferencia',150000.00,'rechazado','2026-10-05 00:00:00',2,2),(2,'transferencia',150000.00,'rechazado',NULL,3,2);
/*!40000 ALTER TABLE `pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `puja`
--

DROP TABLE IF EXISTS `puja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `puja` (
  `id_puja` int NOT NULL AUTO_INCREMENT,
  `monto` decimal(10,2) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `subasta_id_subasta` int NOT NULL,
  `usuario_id_usuario` int NOT NULL,
  PRIMARY KEY (`id_puja`),
  KEY `fk_puja_subasta` (`subasta_id_subasta`),
  KEY `fk_puja_usuario` (`usuario_id_usuario`),
  CONSTRAINT `fk_puja_subasta` FOREIGN KEY (`subasta_id_subasta`) REFERENCES `subasta` (`id_subasta`),
  CONSTRAINT `fk_puja_usuario` FOREIGN KEY (`usuario_id_usuario`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `chk_puja_monto` CHECK (`monto` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `puja`
--

LOCK TABLES `puja` WRITE;
/*!40000 ALTER TABLE `puja` DISABLE KEYS */;
INSERT INTO `puja` VALUES (1,65000.00,'2026-10-05 08:47:38',2,1),(3,95000.00,'2026-10-05 19:50:16',7,2);
/*!40000 ALTER TABLE `puja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subasta`
--

DROP TABLE IF EXISTS `subasta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subasta` (
  `id_subasta` int NOT NULL AUTO_INCREMENT,
  `precio_inicial` decimal(10,2) NOT NULL,
  `incremento_minimo` decimal(10,2) NOT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime NOT NULL,
  `estado` enum('en_curso','por_empezar','terminada','cancelada') NOT NULL,
  `articulo_id_articulo` int NOT NULL,
  `usuario_id_ganador` int DEFAULT NULL,
  PRIMARY KEY (`id_subasta`),
  UNIQUE KEY `articulo_id_articulo_UNIQUE` (`articulo_id_articulo`),
  KEY `fk_subasta_articulo` (`articulo_id_articulo`),
  KEY `fk_subasta_ganador` (`usuario_id_ganador`),
  CONSTRAINT `fk_subasta_articulo` FOREIGN KEY (`articulo_id_articulo`) REFERENCES `articulo` (`id_articulo`),
  CONSTRAINT `fk_subasta_ganador` FOREIGN KEY (`usuario_id_ganador`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `chk_subasta_precio_inicial` CHECK (`precio_inicial` >= 0),
  CONSTRAINT `chk_subasta_incremento_minimo` CHECK (`incremento_minimo` > 0),
  CONSTRAINT `chk_subasta_fechas` CHECK (`fecha_inicio` < `fecha_fin`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subasta`
--

LOCK TABLES `subasta` WRITE;
/*!40000 ALTER TABLE `subasta` DISABLE KEYS */;
INSERT INTO `subasta` VALUES (2,50000.00,5000.00,'2026-10-05 08:00:00','2026-10-13 18:00:00','cancelada',2,NULL),(3,50000.00,5000.00,'2026-10-06 08:00:00','2026-10-13 18:00:00','por_empezar',3,NULL),(4,25000.00,5000.00,'2026-10-06 08:00:00','2026-10-13 18:00:00','por_empezar',4,NULL),(5,50000.00,5000.00,'2026-10-06 16:00:00','2026-10-13 18:00:00','por_empezar',5,NULL),(6,50000.00,5000.00,'2026-10-06 16:00:00','2026-10-13 18:00:00','por_empezar',6,NULL),(7,50000.00,5000.00,'2026-10-05 19:00:00','2026-10-13 18:00:00','en_curso',7,NULL);
/*!40000 ALTER TABLE `subasta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transferencia_pago`
--

DROP TABLE IF EXISTS `transferencia_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transferencia_pago` (
  `id_transferencia_pago` int NOT NULL AUTO_INCREMENT,
  `metodo_pago` enum('nequi','bancolombia','mercadopago') NOT NULL,
  `codigo_verificacion` varchar(45) NOT NULL,
  `nombre_asociado` varchar(100) NOT NULL,
  `numero_cuenta` varchar(45) NOT NULL,
  `numero_identificacion` varchar(45) NOT NULL,
  `tipo_documento` enum('CC','TI','CE','PAS','NIT','PEP','PPT') NOT NULL,
  `pago_id_pago` int NOT NULL,
  PRIMARY KEY (`id_transferencia_pago`),
  UNIQUE KEY `codigo_verificacion_UNIQUE` (`codigo_verificacion`),
  UNIQUE KEY `pago_id_pago_UNIQUE` (`pago_id_pago`),
  CONSTRAINT `fk_transferencia_pago_pago` FOREIGN KEY (`pago_id_pago`) REFERENCES `pago` (`id_pago`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transferencia_pago`
--

LOCK TABLES `transferencia_pago` WRITE;
/*!40000 ALTER TABLE `transferencia_pago` DISABLE KEYS */;
INSERT INTO `transferencia_pago` VALUES (2,'nequi','CODIGO-UNICO-001','Nombre del titular','123456789','1234567890','CC',2);
/*!40000 ALTER TABLE `transferencia_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(45) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `telefono` varchar(13) NOT NULL,
  `rol` enum('vendedor','comprador','admin') NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo_UNIQUE` (`correo`),
  UNIQUE KEY `telefono_UNIQUE` (`telefono`),
  CONSTRAINT `chk_usuario_activo` CHECK (`activo` IN (0, 1))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'andres durango','juan.bbb@gmail.com','$2b$12$mtiUo8d8ZpTPB0HBMUt/AOSqH0w.yq.T6CMNqVYl1J2zVMOzJyyi.','3101243567','vendedor',1,'2026-10-05 00:00:00'),(2,'julian andres benavides durango','julian.benavides@gmail.com','$2b$12$lT1UlV5kYZN7d353RWLD3e5D5nNtaPzA6CDEh0PKpUow3XC2ucsSO','3215655016','comprador',1,'2026-10-05 00:00:00');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_puja`
--

DROP TABLE IF EXISTS `historial_puja`;
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
  CONSTRAINT `fk_historial_puja_subasta` FOREIGN KEY (`subasta_id_subasta`) REFERENCES `subasta` (`id_subasta`),
  CONSTRAINT `fk_historial_puja_usuario` FOREIGN KEY (`usuario_id_usuario`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `chk_historial_puja_monto_oferta` CHECK (`monto_oferta` > 0),
  CONSTRAINT `chk_historial_puja_monto_anterior` CHECK (`monto_anterior` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `vendedor`
--

DROP TABLE IF EXISTS `vendedor`;
CREATE TABLE `vendedor` (
  `id_usuario` int NOT NULL,
  `documento` varchar(45) NOT NULL,
  `nombre_comercial` varchar(100) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `cuenta_bancaria` varchar(45) NOT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `documento_UNIQUE` (`documento`),
  UNIQUE KEY `cuenta_bancaria_UNIQUE` (`cuenta_bancaria`),
  CONSTRAINT `fk_vendedor_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_vendedor_documento` CHECK (CHAR_LENGTH(TRIM(`documento`)) >= 6),
  CONSTRAINT `chk_vendedor_cuenta_bancaria` CHECK (CHAR_LENGTH(TRIM(`cuenta_bancaria`)) >= 6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-05 21:47:50
