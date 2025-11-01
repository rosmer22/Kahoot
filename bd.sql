-- ======================================================================
-- BASE DE DATOS UNIFICADA: robot
-- Sistema RoBot - USAT
-- Incluye: Estructura completa + Mejoras de Timer Sincronizado + Roles
-- Fecha: Noviembre 2025
-- ======================================================================

CREATE DATABASE IF NOT EXISTS `robot` CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `robot`;
SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ======================================================================
-- ESTRUCTURA DE TABLAS
-- ======================================================================

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
-- 8. Tabla: respuestas_participantes
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
-- 9. Tabla: sesiones_grupo (CON TIMER SINCRONIZADO)
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
  `pregunta_actual_id` INT DEFAULT NULL COMMENT 'ID de la pregunta que está siendo mostrada actualmente',
  `pregunta_inicio_time` TIMESTAMP NULL DEFAULT NULL COMMENT 'Timestamp cuando el docente inició esta pregunta',
  `pregunta_tiempo_limite` INT DEFAULT 30 COMMENT 'Tiempo límite en segundos para la pregunta actual',
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`),
  KEY `idx_sesion_pregunta` (`id`, `pregunta_actual_id`),
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

-- ======================================================================
-- DATOS INICIALES Y ACTUALIZACIONES
-- ======================================================================

-- ------------------------------------------------------
-- DOCENTES DE PRUEBA
-- ------------------------------------------------------
-- Usuario: docente1 | Email: docente1@usat.edu.pe | Contraseña: (mismo hash)
-- Usuario: docente2 | Email: docente2@usat.edu.pe | Contraseña: (mismo hash)
-- Usuario: docente3 | Email: docente3@usat.edu.pe | Contraseña: (mismo hash)

INSERT INTO users (username, email, password, role, created_at)
VALUES 
    ('docente1', 'docente1@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW()),
    ('docente2', 'docente2@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW()),
    ('docente3', 'docente3@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW());

-- ------------------------------------------------------
-- ACTUALIZAR ROLES DE USUARIOS EXISTENTES
-- ------------------------------------------------------

-- Actualizar usuarios con dominio @usat.edu.pe como docentes
UPDATE users 
SET role = 'docente' 
WHERE email LIKE '%@usat.edu.pe' 
  AND role = 'usuario';

-- Actualizar usuarios con dominio @usat.pe como alumnos
UPDATE users 
SET role = 'alumno' 
WHERE email LIKE '%@usat.pe' 
  AND role = 'usuario';

-- Actualizar usuarios con otros dominios como alumnos por defecto
UPDATE users 
SET role = 'alumno' 
WHERE email NOT LIKE '%@usat.edu.pe' 
  AND email NOT LIKE '%@usat.pe'
  AND role = 'usuario';

-- ======================================================================
-- VERIFICACIÓN FINAL
-- ======================================================================

-- Mostrar todos los usuarios con sus roles
SELECT 
    id, 
    username, 
    email, 
    role, 
    created_at
FROM users 
ORDER BY role, username;

-- Contar usuarios por rol
SELECT 
    role, 
    COUNT(*) as cantidad
FROM users
GROUP BY role;

-- ======================================================================
-- FIN DEL SCRIPT
-- Base de datos 'robot' creada y configurada exitosamente
-- ======================================================================

