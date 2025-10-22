-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: Grupo2dawb.mysql.pythonanywhere-services.com    Database: Grupo2dawb$Kahoot
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cuestionarios`
--

DROP TABLE IF EXISTS `cuestionarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cuestionarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text,
  `imagen_portada` varchar(500) DEFAULT NULL,
  `pin` varchar(10) DEFAULT NULL,
  `estado` enum('publico','privado') NOT NULL DEFAULT 'publico',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pin` (`pin`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pin` (`pin`),
  CONSTRAINT `cuestionarios_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cuestionarios`
--

LOCK TABLES `cuestionarios` WRITE;
/*!40000 ALTER TABLE `cuestionarios` DISABLE KEYS */;
INSERT INTO `cuestionarios` VALUES (8,9,'Rock','fsfadffsdfafs','kaiss_1760911888_1760918426.jpg','UMFW','publico','2025-10-20 00:00:26','2025-10-20 00:00:26'),(9,9,'Volver al Futuro','asdasdfasfsadfsf','futuro_1760911603_1760919000.jpg','FXSN','publico','2025-10-20 00:10:00','2025-10-20 00:21:33'),(10,9,'Ciberseguridad','asdasdasda','ciberseguridad_1760912645_1760919812.jpg','K9GX','publico','2025-10-20 00:23:32','2025-10-20 00:23:32'),(11,9,'Salsa','ASFSDFASDFSDFSDFASDF','salsa_1760911331_1760920126.jpg','PGRX','publico','2025-10-20 00:28:46','2025-10-20 00:29:33'),(12,9,'Fisica','afsdfsdfasfasdfasdfsadf','Fisica_1760920317.jpg','A703','publico','2025-10-20 00:31:57','2025-10-20 00:31:57'),(13,9,'Geometria','fsdfasdfasfdaf','gemetria_1760920376.jpg','NMSX','publico','2025-10-20 00:32:56','2025-10-20 00:32:56'),(14,9,'IngeneriaPesquera','asdfasdfsdfasdfsad','IngeneriaPesquera_1760920608.png','MOUB','publico','2025-10-20 00:36:48','2025-10-20 00:36:48'),(15,9,'Salsa2','dsdfsdfsdafsdf',NULL,'I8NQ','publico','2025-10-20 00:47:24','2025-10-20 00:47:24'),(16,9,'Rock','fdsfafsdfsdfaf','kaiss_1760921671.jpg','B8YR','publico','2025-10-20 00:54:31','2025-10-20 00:54:31'),(17,9,'llama','llama','descarga_1760984207.jpg','8NG1','publico','2025-10-20 18:16:47','2025-10-20 18:16:47'),(19,12,'¿Cuál es una etiqueta de titulo en HTML?','Dominar conocimientos de HTML','descarga_1760988809.png','DB2Y','publico','2025-10-20 19:33:29','2025-10-20 19:33:29'),(20,12,'¿En qué mundial participo perú actualmente?','Conocimientos del fútbol peruano','descarga_2_1760989323.jpeg','MV1A','publico','2025-10-20 19:42:03','2025-10-20 19:42:03'),(21,12,'Examen de Seguridad Informática - Parte 2','Evaluación complementaria sobre amenazas, criptografía y herramientas de seguridad',NULL,'SEG2025B','privado','2025-10-20 20:11:35','2025-10-20 20:11:35'),(22,14,'Flask v1','Bases de Flask',NULL,'8857','publico','2025-10-20 20:55:53','2025-10-20 20:56:43');
/*!40000 ALTER TABLE `cuestionarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupo_miembros`
--

DROP TABLE IF EXISTS `grupo_miembros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupo_miembros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grupo_id` int NOT NULL,
  `user_id` int NOT NULL,
  `joined_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_member` (`grupo_id`,`user_id`),
  KEY `idx_grupo_id` (`grupo_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `grupo_miembros_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `grupo_miembros_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupo_miembros`
--

LOCK TABLES `grupo_miembros` WRITE;
/*!40000 ALTER TABLE `grupo_miembros` DISABLE KEYS */;
INSERT INTO `grupo_miembros` VALUES (1,1,13,'2025-10-21 22:03:53'),(2,1,8,'2025-10-21 22:04:05'),(3,2,15,'2025-10-21 22:08:36'),(4,3,13,'2025-10-21 22:22:29'),(5,2,12,'2025-10-21 22:23:34');
/*!40000 ALTER TABLE `grupo_miembros` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupos`
--

DROP TABLE IF EXISTS `grupos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grupos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `descripcion` text,
  `codigo` varchar(8) NOT NULL,
  `es_publico` tinyint(1) DEFAULT '0',
  `admin_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idx_codigo` (`codigo`),
  KEY `idx_admin_id` (`admin_id`),
  CONSTRAINT `grupos_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupos`
--

LOCK TABLES `grupos` WRITE;
/*!40000 ALTER TABLE `grupos` DISABLE KEYS */;
INSERT INTO `grupos` VALUES (1,'Grupo 1','','P8IH054F',1,13,'2025-10-21 22:03:53'),(2,'PRUEBA1','prueba1','QRRJ450X',1,15,'2025-10-21 22:08:36'),(3,'grupo 2','','JBFLKUVL',0,13,'2025-10-21 22:22:29');
/*!40000 ALTER TABLE `grupos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `opciones_respuesta`
--

DROP TABLE IF EXISTS `opciones_respuesta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `opciones_respuesta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pregunta_id` int NOT NULL,
  `texto_opcion` text NOT NULL,
  `es_correcta` tinyint(1) DEFAULT '0',
  `orden` int NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  CONSTRAINT `opciones_respuesta_ibfk_1` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `opciones_respuesta`
--

LOCK TABLES `opciones_respuesta` WRITE;
/*!40000 ALTER TABLE `opciones_respuesta` DISABLE KEYS */;
INSERT INTO `opciones_respuesta` VALUES (73,25,'sdfafdf',0,0,'2025-10-20 00:01:15'),(74,25,'sdfsdf',1,1,'2025-10-20 00:01:15'),(75,25,'sdfs',0,2,'2025-10-20 00:01:15'),(76,25,'dfsadf',0,3,'2025-10-20 00:01:15'),(89,29,'ssdfasdfs',0,0,'2025-10-20 00:21:33'),(90,29,'sdfafsdfs',1,1,'2025-10-20 00:21:33'),(91,29,'dfsaf',0,2,'2025-10-20 00:21:33'),(92,29,'a',0,3,'2025-10-20 00:21:33'),(93,30,'asdasdas',0,0,'2025-10-20 00:23:32'),(94,30,'dasdas',1,1,'2025-10-20 00:23:32'),(95,30,'dasdadasd',0,2,'2025-10-20 00:23:32'),(96,30,'asdasdasd',0,3,'2025-10-20 00:23:32'),(105,33,'asdfsdfasdff',0,0,'2025-10-20 00:29:33'),(106,33,'sdfsdafasdfs',1,1,'2025-10-20 00:29:33'),(107,33,'adfasdfasdf',0,2,'2025-10-20 00:29:33'),(108,33,'asfasdf',0,3,'2025-10-20 00:29:33'),(109,34,'sdfasdfsdaf',0,0,'2025-10-20 00:31:57'),(110,34,'sadfsd',0,1,'2025-10-20 00:31:57'),(111,34,'fasdfasd',1,2,'2025-10-20 00:31:57'),(112,34,'fasdf',0,3,'2025-10-20 00:31:57'),(113,35,'sdfsdafsadfsad',0,0,'2025-10-20 00:32:56'),(114,35,'fasdfasdfsdf',0,1,'2025-10-20 00:32:56'),(115,35,'asdfasdf',0,2,'2025-10-20 00:32:56'),(116,35,'asdfasdf',1,3,'2025-10-20 00:32:56'),(117,36,'asdfsdfasd',0,0,'2025-10-20 00:36:48'),(118,36,'fasdfasdf',0,1,'2025-10-20 00:36:48'),(119,36,'asdfasdfasd',0,2,'2025-10-20 00:36:48'),(120,36,'fsdfasdfsdfs',1,3,'2025-10-20 00:36:48'),(121,37,'sdfsdfsda',1,0,'2025-10-20 00:47:24'),(122,37,'fasdf',0,1,'2025-10-20 00:47:24'),(123,37,'sdafasdfasd',0,2,'2025-10-20 00:47:24'),(124,37,'fsdfasdfsad',0,3,'2025-10-20 00:47:24'),(125,38,'fsdfsdfs',0,0,'2025-10-20 00:54:31'),(126,38,'dfsdfasdf',1,1,'2025-10-20 00:54:31'),(127,38,'sadfasdf',0,2,'2025-10-20 00:54:31'),(128,38,'asdfasdfasdfs',0,3,'2025-10-20 00:54:31'),(129,39,'ca',1,0,'2025-10-20 18:16:47'),(130,39,'ca',0,1,'2025-10-20 18:16:47'),(131,39,'as',0,2,'2025-10-20 18:16:47'),(132,39,'as',0,3,'2025-10-20 18:16:47'),(136,41,'Etiqueta',1,0,'2025-10-20 19:33:29'),(137,41,'Programacion',0,1,'2025-10-20 19:33:29'),(138,41,'Movil',0,2,'2025-10-20 19:33:29'),(139,41,'Humano',0,3,'2025-10-20 19:33:29'),(140,42,'Rusia 2018',1,0,'2025-10-20 19:42:03'),(141,42,'Catar 2022',0,1,'2025-10-20 19:42:03'),(142,42,'Brazil 2014',0,2,'2025-10-20 19:42:03'),(143,42,'EE.UU, Canada, Mexico 2026',0,3,'2025-10-20 19:42:03'),(144,42,'Alemania 2010',0,4,'2025-10-20 19:42:03'),(145,43,'Perú',1,0,'2025-10-20 19:42:03'),(146,43,'Venezuela',0,1,'2025-10-20 19:42:03'),(147,43,'Mexico',0,2,'2025-10-20 19:42:03'),(148,43,'Chile',0,3,'2025-10-20 19:42:03'),(153,45,'halt',1,0,'2025-10-20 20:56:43'),(154,45,'exit',0,1,'2025-10-20 20:56:43'),(155,45,'logout',0,2,'2025-10-20 20:56:43'),(156,45,'close',0,3,'2025-10-20 20:56:43'),(157,46,'group by',0,0,'2025-10-20 20:56:43'),(158,46,'INSERT',0,1,'2025-10-20 20:56:43'),(159,46,'SELECT',1,2,'2025-10-20 20:56:43'),(160,46,'DROP',0,3,'2025-10-20 20:56:43');
/*!40000 ALTER TABLE `opciones_respuesta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participantes`
--

DROP TABLE IF EXISTS `participantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sesion_id` int NOT NULL,
  `nombre_participante` varchar(255) NOT NULL,
  `puntaje_total` int DEFAULT '0',
  `fecha_union` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sesion_id` (`sesion_id`),
  CONSTRAINT `participantes_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participantes`
--

LOCK TABLES `participantes` WRITE;
/*!40000 ALTER TABLE `participantes` DISABLE KEYS */;
/*!40000 ALTER TABLE `participantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preguntas`
--

DROP TABLE IF EXISTS `preguntas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preguntas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cuestionario_id` int NOT NULL,
  `tipo_pregunta` enum('opcion_multiple','seleccion_simple','verdadero_falso') NOT NULL,
  `texto_pregunta` text NOT NULL,
  `imagen_pregunta` varchar(500) DEFAULT NULL,
  `orden` int NOT NULL DEFAULT '0',
  `tiempo_limite` int DEFAULT '30',
  `puntos` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_orden` (`orden`),
  CONSTRAINT `preguntas_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preguntas`
--

LOCK TABLES `preguntas` WRITE;
/*!40000 ALTER TABLE `preguntas` DISABLE KEYS */;
INSERT INTO `preguntas` VALUES (25,8,'opcion_multiple','sdfsdfff',NULL,0,30,1,'2025-10-20 00:01:15'),(29,9,'opcion_multiple','fsadfdfasfs',NULL,0,30,1,'2025-10-20 00:21:33'),(30,10,'opcion_multiple','asddasdasd',NULL,0,30,1,'2025-10-20 00:23:32'),(33,11,'opcion_multiple','SDFDFFSADFSDFASDF',NULL,0,30,1,'2025-10-20 00:29:33'),(34,12,'opcion_multiple','sadfsdafsdaf',NULL,0,30,3,'2025-10-20 00:31:57'),(35,13,'opcion_multiple','fasdfsfasdfsdf',NULL,0,30,4,'2025-10-20 00:32:56'),(36,14,'opcion_multiple','sadfsfsdfasdfasdf',NULL,0,30,3,'2025-10-20 00:36:48'),(37,15,'opcion_multiple','sdfsdfdsfsdf',NULL,0,30,1,'2025-10-20 00:47:24'),(38,16,'opcion_multiple','sdfsdfsdfsadfsadf',NULL,0,30,1,'2025-10-20 00:54:31'),(39,17,'opcion_multiple','ca',NULL,0,30,1,'2025-10-20 18:16:47'),(41,19,'opcion_multiple','Html es un lenguaje de:-------------?',NULL,0,30,1,'2025-10-20 19:33:29'),(42,20,'opcion_multiple','¿En que mundial perú participo?',NULL,0,30,1,'2025-10-20 19:42:03'),(43,20,'opcion_multiple','¿Cuál seleccion le dio más partdio a francia?',NULL,1,30,1,'2025-10-20 19:42:03'),(45,22,'opcion_multiple','Comando apagar',NULL,0,30,1,'2025-10-20 20:56:43'),(46,22,'seleccion_simple','Comando seleccionar',NULL,1,30,1,'2025-10-20 20:56:43');
/*!40000 ALTER TABLE `preguntas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `respuestas_grupo`
--

DROP TABLE IF EXISTS `respuestas_grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuestas_grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sesion_id` int NOT NULL,
  `user_id` int NOT NULL,
  `pregunta_id` int NOT NULL,
  `opcion_id` int DEFAULT NULL,
  `es_correcta` tinyint(1) DEFAULT '0',
  `puntos` int DEFAULT '0',
  `tiempo_respuesta` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_question` (`sesion_id`,`user_id`,`pregunta_id`),
  KEY `opcion_id` (`opcion_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  CONSTRAINT `respuestas_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_3` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_4` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuestas_grupo`
--

LOCK TABLES `respuestas_grupo` WRITE;
/*!40000 ALTER TABLE `respuestas_grupo` DISABLE KEYS */;
/*!40000 ALTER TABLE `respuestas_grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `respuestas_participantes`
--

DROP TABLE IF EXISTS `respuestas_participantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `respuestas_participantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `participante_id` int NOT NULL,
  `pregunta_id` int NOT NULL,
  `opcion_seleccionada_id` int DEFAULT NULL,
  `es_correcta` tinyint(1) DEFAULT '0',
  `tiempo_respuesta` int DEFAULT NULL,
  `puntos_obtenidos` int DEFAULT '0',
  `fecha_respuesta` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `opcion_seleccionada_id` (`opcion_seleccionada_id`),
  KEY `idx_participante_id` (`participante_id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  CONSTRAINT `respuestas_participantes_ibfk_1` FOREIGN KEY (`participante_id`) REFERENCES `participantes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_participantes_ibfk_2` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_participantes_ibfk_3` FOREIGN KEY (`opcion_seleccionada_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `respuestas_participantes`
--

LOCK TABLES `respuestas_participantes` WRITE;
/*!40000 ALTER TABLE `respuestas_participantes` DISABLE KEYS */;
/*!40000 ALTER TABLE `respuestas_participantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resultados`
--

DROP TABLE IF EXISTS `resultados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resultados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `cuestionario_id` int NOT NULL,
  `sesion_id` int DEFAULT NULL,
  `puntaje_obtenido` int DEFAULT '0',
  `puntaje_maximo` int NOT NULL,
  `total_preguntas` int NOT NULL,
  `respuestas_correctas` int DEFAULT '0',
  `tiempo_total` int DEFAULT NULL,
  `fecha_completado` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_fecha` (`fecha_completado`),
  CONSTRAINT `resultados_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `resultados_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resultados_ibfk_3` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resultados`
--

LOCK TABLES `resultados` WRITE;
/*!40000 ALTER TABLE `resultados` DISABLE KEYS */;
/*!40000 ALTER TABLE `resultados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesiones_grupo`
--

DROP TABLE IF EXISTS `sesiones_grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesiones_grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grupo_id` int NOT NULL,
  `cuestionario_id` int NOT NULL,
  `iniciado_por` int NOT NULL,
  `session_code` varchar(6) NOT NULL,
  `estado` enum('esperando','en_progreso','finalizado') DEFAULT 'esperando',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` timestamp NULL DEFAULT NULL,
  `finished_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`),
  KEY `iniciado_por` (`iniciado_por`),
  KEY `idx_grupo_id` (`grupo_id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_estado` (`estado`),
  KEY `idx_session_code` (`session_code`),
  CONSTRAINT `sesiones_grupo_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_3` FOREIGN KEY (`iniciado_por`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesiones_grupo`
--

LOCK TABLES `sesiones_grupo` WRITE;
/*!40000 ALTER TABLE `sesiones_grupo` DISABLE KEYS */;
INSERT INTO `sesiones_grupo` VALUES (1,1,22,8,'F3HLX4','esperando','2025-10-21 22:04:10',NULL,NULL),(2,1,22,8,'WMUQY5','esperando','2025-10-21 22:04:27',NULL,NULL),(3,1,22,8,'Z2B166','esperando','2025-10-21 22:04:27',NULL,NULL),(4,1,22,13,'HWX6NT','esperando','2025-10-21 22:07:56',NULL,NULL),(5,1,20,13,'1FPZF0','esperando','2025-10-21 22:08:06',NULL,NULL),(6,1,20,13,'V8LDSK','esperando','2025-10-21 22:08:07',NULL,NULL),(7,2,20,15,'A076NG','esperando','2025-10-21 22:08:46',NULL,NULL),(8,2,20,15,'MXNQXH','esperando','2025-10-21 22:08:54',NULL,NULL),(9,2,19,15,'4WRDGY','esperando','2025-10-21 22:09:01',NULL,NULL),(10,1,22,13,'4L15P1','esperando','2025-10-21 22:16:03',NULL,NULL),(11,1,22,13,'SCHOTZ','esperando','2025-10-21 22:22:19',NULL,NULL),(12,3,22,13,'PUM996','esperando','2025-10-21 22:22:34',NULL,NULL),(13,2,22,15,'GHC9KK','esperando','2025-10-21 22:23:27',NULL,NULL),(14,2,20,12,'T8Z6EF','esperando','2025-10-21 22:23:41',NULL,NULL),(15,2,22,15,'GTTZJM','esperando','2025-10-21 22:23:41',NULL,NULL),(16,2,20,12,'PBC2VX','esperando','2025-10-21 22:23:52',NULL,NULL),(17,2,20,12,'YWBPWU','esperando','2025-10-21 22:24:13',NULL,NULL),(18,2,21,12,'78ERBU','esperando','2025-10-21 22:24:44',NULL,NULL),(19,2,20,12,'HQOTT2','esperando','2025-10-21 22:24:44',NULL,NULL),(20,2,20,12,'U76EFE','esperando','2025-10-21 22:24:51',NULL,NULL),(21,3,22,13,'HVNVMF','esperando','2025-10-21 22:25:31',NULL,NULL),(22,1,22,13,'RNBN8X','esperando','2025-10-21 22:25:45',NULL,NULL),(23,1,22,13,'77KZTO','esperando','2025-10-21 22:25:55',NULL,NULL);
/*!40000 ALTER TABLE `sesiones_grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesiones_juego`
--

DROP TABLE IF EXISTS `sesiones_juego`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesiones_juego` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cuestionario_id` int NOT NULL,
  `pin_sesion` varchar(10) NOT NULL,
  `fecha_inicio` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_fin` timestamp NULL DEFAULT NULL,
  `estado` enum('esperando','en_progreso','finalizado') DEFAULT 'esperando',
  `created_by` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pin_sesion` (`pin_sesion`),
  KEY `created_by` (`created_by`),
  KEY `idx_pin_sesion` (`pin_sesion`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  CONSTRAINT `sesiones_juego_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_juego_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesiones_juego`
--

LOCK TABLES `sesiones_juego` WRITE;
/*!40000 ALTER TABLE `sesiones_juego` DISABLE KEYS */;
/*!40000 ALTER TABLE `sesiones_juego` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'usuario',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (3,'yasser','rosmer@gmail.com','scrypt:32768:8:1$CNTOFfCLm91gHlSF$c3d90f52e0910d3258bdf130a34543955738afb3a005c7d4f4fa7c90eec4f083968af7a17095943319f339b2d03766f383394716cd4abbbc58faadfab22977fb','usuario','2025-10-13 21:02:20'),(8,'nickname','minecrafts2112@gmail.com','scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86','usuario','2025-10-18 19:51:03'),(9,'Admin','76842145@usat.pe','scrypt:32768:8:1$HCj2AfFCZI5Twvpk$ca47f14b1c40d05709381aee4e481f5636cb9f749c299236bcaffcfa35c75c8fd467a0372a4eac300559f2c90c49bc823062234728bcb6b467083e1435138596','usuario','2025-10-19 22:47:16'),(12,'BreydiDesarrollador','74688572@usat.pe','scrypt:32768:8:1$Og5ptdEbW7EdiBPq$f585c93cd3cc4f848455d63168463786a58af9b5a5502780d1ab8eb5588725e61c2d65a1f64a196df7e0ab7a0418e77e52529abcced3b42a5a5dfab98a1eec6c','usuario','2025-10-20 19:20:17'),(13,'Valentino','71448627@usat.pe','scrypt:32768:8:1$5ci0A80kPtYaDtwK$6f17b1343c9b31da1feac47a3a8056b191c41dfbf410e434d64c0faa25b4620b9ce0e7219dc2c293a2ceee334734a8c317856cb3eec5d8ff7c36ee0e30f6f28c','usuario','2025-10-20 19:48:53'),(14,'jcachay','jcachay@usat.edu.pe','scrypt:32768:8:1$G5jelG7bYRzFLnsl$cee8b1f21cea336de32664b73616dfade965a029f7846fabd1523b02df1aeae5bce21d40610721ddf4b6f70b2c2f9ac5d7fd4bee1028c104090e4bc163bec367','usuario','2025-10-20 20:55:06'),(15,'SandovalMc','72693550@usat.pe','scrypt:32768:8:1$jWR3CKR6eiJeEYT2$cf6fc0a8272158a3f42e2240ac453b82b87345e7028e113705ecc9f5625e1cca443f759a336e5d7955a0717b7839cf08a55bf26504a31c9c841f46a70bfe8049','usuario','2025-10-21 20:11:35');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_estado_grupo`
--

DROP TABLE IF EXISTS `usuario_estado_grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_estado_grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sesion_id` int NOT NULL,
  `user_id` int NOT NULL,
  `esta_listo` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_session` (`sesion_id`,`user_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `usuario_estado_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuario_estado_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_estado_grupo`
--

LOCK TABLES `usuario_estado_grupo` WRITE;
/*!40000 ALTER TABLE `usuario_estado_grupo` DISABLE KEYS */;
INSERT INTO `usuario_estado_grupo` VALUES (1,21,13,1,'2025-10-21 22:25:37','2025-10-21 22:25:37'),(2,22,13,1,'2025-10-21 22:25:49','2025-10-21 22:25:49'),(3,23,13,1,'2025-10-21 22:25:59','2025-10-21 22:25:59');
/*!40000 ALTER TABLE `usuario_estado_grupo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-21 22:35:27


-----------------
-- 1. Añadir la columna user_id a sesiones_juego para registrar quién está jugando.
ALTER TABLE `sesiones_juego`
ADD COLUMN `user_id` INT NULL AFTER `cuestionario_id`,
ADD KEY `idx_user_id` (`user_id`),
ADD CONSTRAINT `fk_sesiones_juego_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

-- 2. Modificar la tabla de respuestas para que se relacione con la sesión y el usuario.
ALTER TABLE `respuestas_participantes`
DROP FOREIGN KEY `respuestas_participantes_ibfk_1`,
DROP FOREIGN KEY `respuestas_participantes_ibfk_3`,
DROP COLUMN `participante_id`,
ADD COLUMN `sesion_juego_id` INT NOT NULL AFTER `id`,
ADD COLUMN `user_id` INT NOT NULL AFTER `sesion_juego_id`,
ADD COLUMN `opcion_id` INT NULL AFTER `pregunta_id`,
DROP COLUMN `opcion_seleccionada_id`,
ADD KEY `idx_sesion_juego_id` (`sesion_juego_id`),
ADD KEY `idx_user_id` (`user_id`),
ADD CONSTRAINT `fk_respuestas_sesion` FOREIGN KEY (`sesion_juego_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_respuestas_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
ADD CONSTRAINT `fk_respuestas_opcion` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL;

-- 3. Eliminar la tabla 'participantes' que ya no se usará en este flujo.
DROP TABLE IF EXISTS `participantes`;



-- Eliminar la columna conflictiva 'pin_sesion' de la tabla de sesiones de juego
ALTER TABLE `sesiones_juego` DROP KEY `pin_sesion`, DROP COLUMN `pin_sesion`;

