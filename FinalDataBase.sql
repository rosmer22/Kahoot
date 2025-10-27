-- ------------------------------------------------------
-- Base de datos: `robot`
-- ------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `robot` CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `robot`;
SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------
-- 1. Tabla: users
-- ------------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) NOT NULL DEFAULT 'usuario',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 2. Tabla: cuestionarios
-- ------------------------------------------------------
DROP TABLE IF EXISTS `cuestionarios`;
CREATE TABLE `cuestionarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `titulo` VARCHAR(255) NOT NULL,
  `descripcion` TEXT,
  `imagen_portada` VARCHAR(500) DEFAULT NULL,
  `pin` VARCHAR(10) DEFAULT NULL,
  `estado` ENUM('publico','privado') NOT NULL DEFAULT 'publico',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pin` (`pin`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `cuestionarios_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 3. Tabla: preguntas
-- ------------------------------------------------------
DROP TABLE IF EXISTS `preguntas`;
CREATE TABLE `preguntas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cuestionario_id` INT NOT NULL,
  `tipo_pregunta` ENUM('opcion_multiple','seleccion_simple','verdadero_falso') NOT NULL,
  `texto_pregunta` TEXT NOT NULL,
  `imagen_pregunta` VARCHAR(500) DEFAULT NULL,
  `orden` INT NOT NULL DEFAULT '0',
  `tiempo_limite` INT DEFAULT '30',
  `puntos` INT DEFAULT '1',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  CONSTRAINT `preguntas_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 4. Tabla: opciones_respuesta
-- ------------------------------------------------------
DROP TABLE IF EXISTS `opciones_respuesta`;
CREATE TABLE `opciones_respuesta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pregunta_id` INT NOT NULL,
  `texto_opcion` TEXT NOT NULL,
  `es_correcta` TINYINT(1) DEFAULT '0',
  `orden` INT NOT NULL DEFAULT '0',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  CONSTRAINT `opciones_respuesta_ibfk_1` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 5. Tabla: grupos
-- ------------------------------------------------------
DROP TABLE IF EXISTS `grupos`;
CREATE TABLE `grupos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT,
  `codigo` VARCHAR(8) NOT NULL,
  `es_publico` TINYINT(1) DEFAULT '0',
  `admin_id` INT NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  CONSTRAINT `grupos_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 6. Tabla: grupo_miembros
-- ------------------------------------------------------
DROP TABLE IF EXISTS `grupo_miembros`;
CREATE TABLE `grupo_miembros` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `grupo_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `joined_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_member` (`grupo_id`,`user_id`),
  CONSTRAINT `grupo_miembros_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `grupo_miembros_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 7. Tabla: sesiones_juego
-- ------------------------------------------------------
DROP TABLE IF EXISTS `sesiones_juego`;
CREATE TABLE `sesiones_juego` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cuestionario_id` INT NOT NULL,
  `user_id` INT NULL,
  `fecha_inicio` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_fin` TIMESTAMP NULL DEFAULT NULL,
  `estado` ENUM('esperando','en_progreso','finalizado') DEFAULT 'esperando',
  `created_by` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `sesiones_juego_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_juego_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sesiones_juego_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 8. Tabla: respuestas_participantes (actualizada)
-- ------------------------------------------------------
DROP TABLE IF EXISTS `respuestas_participantes`;
CREATE TABLE `respuestas_participantes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sesion_juego_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `pregunta_id` INT NOT NULL,
  `opcion_id` INT NULL,
  `es_correcta` TINYINT(1) DEFAULT '0',
  `tiempo_respuesta` INT DEFAULT NULL,
  `puntos_obtenidos` INT DEFAULT '0',
  `fecha_respuesta` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_sesion_juego_id` (`sesion_juego_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_respuestas_sesion` FOREIGN KEY (`sesion_juego_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_opcion` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_respuestas_pregunta` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 9. Tabla: sesiones_grupo
-- ------------------------------------------------------
DROP TABLE IF EXISTS `sesiones_grupo`;
CREATE TABLE `sesiones_grupo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `grupo_id` INT NOT NULL,
  `cuestionario_id` INT NOT NULL,
  `iniciado_por` INT NOT NULL,
  `session_code` VARCHAR(6) NOT NULL,
  `estado` ENUM('esperando','en_progreso','finalizado') DEFAULT 'esperando',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`),
  CONSTRAINT `sesiones_grupo_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_3` FOREIGN KEY (`iniciado_por`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 10. Tabla: usuario_estado_grupo
-- ------------------------------------------------------
DROP TABLE IF EXISTS `usuario_estado_grupo`;
CREATE TABLE `usuario_estado_grupo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sesion_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `esta_listo` TINYINT(1) DEFAULT '0',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_session` (`sesion_id`,`user_id`),
  CONSTRAINT `usuario_estado_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuario_estado_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 11. Tabla: respuestas_grupo
-- ------------------------------------------------------
DROP TABLE IF EXISTS `respuestas_grupo`;
CREATE TABLE `respuestas_grupo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sesion_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `pregunta_id` INT NOT NULL,
  `opcion_id` INT DEFAULT NULL,
  `es_correcta` TINYINT(1) DEFAULT '0',
  `puntos` INT DEFAULT '0',
  `tiempo_respuesta` INT DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_question` (`sesion_id`,`user_id`,`pregunta_id`),
  CONSTRAINT `respuestas_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_3` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_4` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ------------------------------------------------------
-- 12. Tabla: resultados
-- ------------------------------------------------------
DROP TABLE IF EXISTS `resultados`;
CREATE TABLE `resultados` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT NULL,
  `cuestionario_id` INT NOT NULL,
  `sesion_id` INT DEFAULT NULL,
  `puntaje_obtenido` INT DEFAULT '0',
  `puntaje_maximo` INT NOT NULL,
  `total_preguntas` INT NOT NULL,
  `respuestas_correctas` INT DEFAULT '0',
  `tiempo_total` INT DEFAULT NULL,
  `fecha_completado` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `resultados_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `resultados_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resultados_ibfk_3` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
SET FOREIGN_KEY_CHECKS = 1;

/*Data*/;
LOCK TABLES `cuestionarios` WRITE;
LOCK TABLES `grupo_miembros` WRITE;
LOCK TABLES `grupos` WRITE;
LOCK TABLES `opciones_respuesta` WRITE;
LOCK TABLES `participantes` WRITE;
LOCK TABLES `preguntas` WRITE;
LOCK TABLES `respuestas_grupo` WRITE;
LOCK TABLES `respuestas_participantes` WRITE;
LOCK TABLES `resultados` WRITE;
LOCK TABLES `sesiones_grupo` WRITE;
LOCK TABLES `sesiones_juego` WRITE;
LOCK TABLES `users` WRITE;
LOCK TABLES `usuario_estado_grupo` WRITE;
INSERT INTO `cuestionarios` VALUES (8,9,'Rock','fsfadffsdfafs','kaiss_1760911888_1760918426.jpg','UMFW','publico','2025-10-20 00:00:26','2025-10-20 00:00:26'),(9,9,'Volver al Futuro','asdasdfasfsadfsf','futuro_1760911603_1760919000.jpg','FXSN','publico','2025-10-20 00:10:00','2025-10-20 00:21:33'),(10,9,'Ciberseguridad','asdasdasda','ciberseguridad_1760912645_1760919812.jpg','K9GX','publico','2025-10-20 00:23:32','2025-10-20 00:23:32'),(11,9,'Salsa','ASFSDFASDFSDFSDFASDF','salsa_1760911331_1760920126.jpg','PGRX','publico','2025-10-20 00:28:46','2025-10-20 00:29:33'),(12,9,'Fisica','afsdfsdfasfasdfasdfsadf','Fisica_1760920317.jpg','A703','publico','2025-10-20 00:31:57','2025-10-20 00:31:57'),(13,9,'Geometria','fsdfasdfasfdaf','gemetria_1760920376.jpg','NMSX','publico','2025-10-20 00:32:56','2025-10-20 00:32:56'),(14,9,'IngeneriaPesquera','asdfasdfsdfasdfsad','IngeneriaPesquera_1760920608.png','MOUB','publico','2025-10-20 00:36:48','2025-10-20 00:36:48'),(15,9,'Salsa2','dsdfsdfsdafsdf',NULL,'I8NQ','publico','2025-10-20 00:47:24','2025-10-20 00:47:24'),(16,9,'Rock','fdsfafsdfsdfaf','kaiss_1760921671.jpg','B8YR','publico','2025-10-20 00:54:31','2025-10-20 00:54:31'),(17,9,'llama','llama','descarga_1760984207.jpg','8NG1','publico','2025-10-20 18:16:47','2025-10-20 18:16:47'),(19,12,'¿Cuál es una etiqueta de titulo en HTML?','Dominar conocimientos de HTML','descarga_1760988809.png','DB2Y','publico','2025-10-20 19:33:29','2025-10-20 19:33:29'),(20,12,'¿En qué mundial participo perú actualmente?','Conocimientos del fútbol peruano','descarga_2_1760989323.jpeg','MV1A','publico','2025-10-20 19:42:03','2025-10-20 19:42:03'),(21,12,'Examen de Seguridad Informática - Parte 2','Evaluación complementaria sobre amenazas, criptografía y herramientas de seguridad',NULL,'SEG2025B','privado','2025-10-20 20:11:35','2025-10-20 20:11:35'),(22,14,'Flask v1','Bases de Flask',NULL,'8857','publico','2025-10-20 20:55:53','2025-10-20 20:56:43');
INSERT INTO `grupo_miembros` VALUES (1,1,13,'2025-10-21 22:03:53'),(2,1,8,'2025-10-21 22:04:05'),(3,2,15,'2025-10-21 22:08:36'),(4,3,13,'2025-10-21 22:22:29'),(5,2,12,'2025-10-21 22:23:34');
INSERT INTO `grupos` VALUES (1,'Grupo 1','','P8IH054F',1,13,'2025-10-21 22:03:53'),(2,'PRUEBA1','prueba1','QRRJ450X',1,15,'2025-10-21 22:08:36'),(3,'grupo 2','','JBFLKUVL',0,13,'2025-10-21 22:22:29');
INSERT INTO `opciones_respuesta` VALUES (73,25,'sdfafdf',0,0,'2025-10-20 00:01:15'),(74,25,'sdfsdf',1,1,'2025-10-20 00:01:15'),(75,25,'sdfs',0,2,'2025-10-20 00:01:15'),(76,25,'dfsadf',0,3,'2025-10-20 00:01:15'),(89,29,'ssdfasdfs',0,0,'2025-10-20 00:21:33'),(90,29,'sdfafsdfs',1,1,'2025-10-20 00:21:33'),(91,29,'dfsaf',0,2,'2025-10-20 00:21:33'),(92,29,'a',0,3,'2025-10-20 00:21:33'),(93,30,'asdasdas',0,0,'2025-10-20 00:23:32'),(94,30,'dasdas',1,1,'2025-10-20 00:23:32'),(95,30,'dasdadasd',0,2,'2025-10-20 00:23:32'),(96,30,'asdasdasd',0,3,'2025-10-20 00:23:32'),(105,33,'asdfsdfasdff',0,0,'2025-10-20 00:29:33'),(106,33,'sdfsdafasdfs',1,1,'2025-10-20 00:29:33'),(107,33,'adfasdfasdf',0,2,'2025-10-20 00:29:33'),(108,33,'asfasdf',0,3,'2025-10-20 00:29:33'),(109,34,'sdfasdfsdaf',0,0,'2025-10-20 00:31:57'),(110,34,'sadfsd',0,1,'2025-10-20 00:31:57'),(111,34,'fasdfasd',1,2,'2025-10-20 00:31:57'),(112,34,'fasdf',0,3,'2025-10-20 00:31:57'),(113,35,'sdfsdafsadfsad',0,0,'2025-10-20 00:32:56'),(114,35,'fasdfasdfsdf',0,1,'2025-10-20 00:32:56'),(115,35,'asdfasdf',0,2,'2025-10-20 00:32:56'),(116,35,'asdfasdf',1,3,'2025-10-20 00:32:56'),(117,36,'asdfsdfasd',0,0,'2025-10-20 00:36:48'),(118,36,'fasdfasdf',0,1,'2025-10-20 00:36:48'),(119,36,'asdfasdfasd',0,2,'2025-10-20 00:36:48'),(120,36,'fsdfasdfsdfs',1,3,'2025-10-20 00:36:48'),(121,37,'sdfsdfsda',1,0,'2025-10-20 00:47:24'),(122,37,'fasdf',0,1,'2025-10-20 00:47:24'),(123,37,'sdafasdfasd',0,2,'2025-10-20 00:47:24'),(124,37,'fsdfasdfsad',0,3,'2025-10-20 00:47:24'),(125,38,'fsdfsdfs',0,0,'2025-10-20 00:54:31'),(126,38,'dfsdfasdf',1,1,'2025-10-20 00:54:31'),(127,38,'sadfasdf',0,2,'2025-10-20 00:54:31'),(128,38,'asdfasdfasdfs',0,3,'2025-10-20 00:54:31'),(129,39,'ca',1,0,'2025-10-20 18:16:47'),(130,39,'ca',0,1,'2025-10-20 18:16:47'),(131,39,'as',0,2,'2025-10-20 18:16:47'),(132,39,'as',0,3,'2025-10-20 18:16:47'),(136,41,'Etiqueta',1,0,'2025-10-20 19:33:29'),(137,41,'Programacion',0,1,'2025-10-20 19:33:29'),(138,41,'Movil',0,2,'2025-10-20 19:33:29'),(139,41,'Humano',0,3,'2025-10-20 19:33:29'),(140,42,'Rusia 2018',1,0,'2025-10-20 19:42:03'),(141,42,'Catar 2022',0,1,'2025-10-20 19:42:03'),(142,42,'Brazil 2014',0,2,'2025-10-20 19:42:03'),(143,42,'EE.UU, Canada, Mexico 2026',0,3,'2025-10-20 19:42:03'),(144,42,'Alemania 2010',0,4,'2025-10-20 19:42:03'),(145,43,'Perú',1,0,'2025-10-20 19:42:03'),(146,43,'Venezuela',0,1,'2025-10-20 19:42:03'),(147,43,'Mexico',0,2,'2025-10-20 19:42:03'),(148,43,'Chile',0,3,'2025-10-20 19:42:03'),(153,45,'halt',1,0,'2025-10-20 20:56:43'),(154,45,'exit',0,1,'2025-10-20 20:56:43'),(155,45,'logout',0,2,'2025-10-20 20:56:43'),(156,45,'close',0,3,'2025-10-20 20:56:43'),(157,46,'group by',0,0,'2025-10-20 20:56:43'),(158,46,'INSERT',0,1,'2025-10-20 20:56:43'),(159,46,'SELECT',1,2,'2025-10-20 20:56:43'),(160,46,'DROP',0,3,'2025-10-20 20:56:43');
INSERT INTO `preguntas` VALUES (25,8,'opcion_multiple','sdfsdfff',NULL,0,30,1,'2025-10-20 00:01:15'),(29,9,'opcion_multiple','fsadfdfasfs',NULL,0,30,1,'2025-10-20 00:21:33'),(30,10,'opcion_multiple','asddasdasd',NULL,0,30,1,'2025-10-20 00:23:32'),(33,11,'opcion_multiple','SDFDFFSADFSDFASDF',NULL,0,30,1,'2025-10-20 00:29:33'),(34,12,'opcion_multiple','sadfsdafsdaf',NULL,0,30,3,'2025-10-20 00:31:57'),(35,13,'opcion_multiple','fasdfsfasdfsdf',NULL,0,30,4,'2025-10-20 00:32:56'),(36,14,'opcion_multiple','sadfsfsdfasdfasdf',NULL,0,30,3,'2025-10-20 00:36:48'),(37,15,'opcion_multiple','sdfsdfdsfsdf',NULL,0,30,1,'2025-10-20 00:47:24'),(38,16,'opcion_multiple','sdfsdfsdfsadfsadf',NULL,0,30,1,'2025-10-20 00:54:31'),(39,17,'opcion_multiple','ca',NULL,0,30,1,'2025-10-20 18:16:47'),(41,19,'opcion_multiple','Html es un lenguaje de:-------------?',NULL,0,30,1,'2025-10-20 19:33:29'),(42,20,'opcion_multiple','¿En que mundial perú participo?',NULL,0,30,1,'2025-10-20 19:42:03'),(43,20,'opcion_multiple','¿Cuál seleccion le dio más partdio a francia?',NULL,1,30,1,'2025-10-20 19:42:03'),(45,22,'opcion_multiple','Comando apagar',NULL,0,30,1,'2025-10-20 20:56:43'),(46,22,'seleccion_simple','Comando seleccionar',NULL,1,30,1,'2025-10-20 20:56:43');
INSERT INTO `sesiones_grupo` VALUES (1,1,22,8,'F3HLX4','esperando','2025-10-21 22:04:10',NULL,NULL),(2,1,22,8,'WMUQY5','esperando','2025-10-21 22:04:27',NULL,NULL),(3,1,22,8,'Z2B166','esperando','2025-10-21 22:04:27',NULL,NULL),(4,1,22,13,'HWX6NT','esperando','2025-10-21 22:07:56',NULL,NULL),(5,1,20,13,'1FPZF0','esperando','2025-10-21 22:08:06',NULL,NULL),(6,1,20,13,'V8LDSK','esperando','2025-10-21 22:08:07',NULL,NULL),(7,2,20,15,'A076NG','esperando','2025-10-21 22:08:46',NULL,NULL),(8,2,20,15,'MXNQXH','esperando','2025-10-21 22:08:54',NULL,NULL),(9,2,19,15,'4WRDGY','esperando','2025-10-21 22:09:01',NULL,NULL),(10,1,22,13,'4L15P1','esperando','2025-10-21 22:16:03',NULL,NULL),(11,1,22,13,'SCHOTZ','esperando','2025-10-21 22:22:19',NULL,NULL),(12,3,22,13,'PUM996','esperando','2025-10-21 22:22:34',NULL,NULL),(13,2,22,15,'GHC9KK','esperando','2025-10-21 22:23:27',NULL,NULL),(14,2,20,12,'T8Z6EF','esperando','2025-10-21 22:23:41',NULL,NULL),(15,2,22,15,'GTTZJM','esperando','2025-10-21 22:23:41',NULL,NULL),(16,2,20,12,'PBC2VX','esperando','2025-10-21 22:23:52',NULL,NULL),(17,2,20,12,'YWBPWU','esperando','2025-10-21 22:24:13',NULL,NULL),(18,2,21,12,'78ERBU','esperando','2025-10-21 22:24:44',NULL,NULL),(19,2,20,12,'HQOTT2','esperando','2025-10-21 22:24:44',NULL,NULL),(20,2,20,12,'U76EFE','esperando','2025-10-21 22:24:51',NULL,NULL),(21,3,22,13,'HVNVMF','esperando','2025-10-21 22:25:31',NULL,NULL),(22,1,22,13,'RNBN8X','esperando','2025-10-21 22:25:45',NULL,NULL),(23,1,22,13,'77KZTO','esperando','2025-10-21 22:25:55',NULL,NULL);
INSERT INTO `users` VALUES (3,'yasser','rosmer@gmail.com','scrypt:32768:8:1$CNTOFfCLm91gHlSF$c3d90f52e0910d3258bdf130a34543955738afb3a005c7d4f4fa7c90eec4f083968af7a17095943319f339b2d03766f383394716cd4abbbc58faadfab22977fb','usuario','2025-10-13 21:02:20'),(8,'nickname','minecrafts2112@gmail.com','scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86','usuario','2025-10-18 19:51:03'),(9,'Admin','76842145@usat.pe','scrypt:32768:8:1$HCj2AfFCZI5Twvpk$ca47f14b1c40d05709381aee4e481f5636cb9f749c299236bcaffcfa35c75c8fd467a0372a4eac300559f2c90c49bc823062234728bcb6b467083e1435138596','usuario','2025-10-19 22:47:16'),(12,'BreydiDesarrollador','74688572@usat.pe','scrypt:32768:8:1$Og5ptdEbW7EdiBPq$f585c93cd3cc4f848455d63168463786a58af9b5a5502780d1ab8eb5588725e61c2d65a1f64a196df7e0ab7a0418e77e52529abcced3b42a5a5dfab98a1eec6c','usuario','2025-10-20 19:20:17'),(13,'Valentino','71448627@usat.pe','scrypt:32768:8:1$5ci0A80kPtYaDtwK$6f17b1343c9b31da1feac47a3a8056b191c41dfbf410e434d64c0faa25b4620b9ce0e7219dc2c293a2ceee334734a8c317856cb3eec5d8ff7c36ee0e30f6f28c','usuario','2025-10-20 19:48:53'),(14,'jcachay','jcachay@usat.edu.pe','scrypt:32768:8:1$G5jelG7bYRzFLnsl$cee8b1f21cea336de32664b73616dfade965a029f7846fabd1523b02df1aeae5bce21d40610721ddf4b6f70b2c2f9ac5d7fd4bee1028c104090e4bc163bec367','usuario','2025-10-20 20:55:06'),(15,'SandovalMc','72693550@usat.pe','scrypt:32768:8:1$jWR3CKR6eiJeEYT2$cf6fc0a8272158a3f42e2240ac453b82b87345e7028e113705ecc9f5625e1cca443f759a336e5d7955a0717b7839cf08a55bf26504a31c9c841f46a70bfe8049','usuario','2025-10-21 20:11:35');
INSERT INTO `usuario_estado_grupo` VALUES (1,21,13,1,'2025-10-21 22:25:37','2025-10-21 22:25:37'),(2,22,13,1,'2025-10-21 22:25:49','2025-10-21 22:25:49'),(3,23,13,1,'2025-10-21 22:25:59','2025-10-21 22:25:59');
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;
UNLOCK TABLES;