-- =====================================================
-- BASE DE DATOS COMPLETA - SISTEMA DE CUESTIONARIOS
-- =====================================================
-- 
-- Este archivo crea la estructura completa de la base de datos
-- desde cero, incluyendo todas las funcionalidades:
-- - Sistema de usuarios
-- - Sistema de grupos
-- - Sistema de cuestionarios
-- - Sistema de sesiones de grupo (con códigos de sala)
-- - Sistema de sesiones individuales (con códigos de sala)
-- - Sistema de respuestas y resultados
--
-- INSTRUCCIONES:
-- 1. Crear base de datos: CREATE DATABASE tu_base_datos CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 2. Usar base de datos: USE tu_base_datos;
-- 3. Ejecutar este script completo
--
-- =====================================================

SET FOREIGN_KEY_CHECKS=0;

-- =====================================================
-- TABLA: users
-- Usuarios del sistema
-- =====================================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: grupos
-- Grupos de usuarios para cuestionarios colaborativos
-- =====================================================
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
  KEY `idx_codigo` (`codigo`),
  KEY `idx_admin_id` (`admin_id`),
  CONSTRAINT `grupos_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: grupo_miembros
-- Relación entre usuarios y grupos
-- =====================================================
DROP TABLE IF EXISTS `grupo_miembros`;
CREATE TABLE `grupo_miembros` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `grupo_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `joined_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_member` (`grupo_id`, `user_id`),
  KEY `idx_grupo_id` (`grupo_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `grupo_miembros_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `grupo_miembros_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: cuestionarios
-- Cuestionarios creados por los usuarios
-- NOTA: estado usa 'publico' y 'privado' (ya actualizado)
-- =====================================================
DROP TABLE IF EXISTS `cuestionarios`;
CREATE TABLE `cuestionarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `titulo` VARCHAR(255) NOT NULL,
  `descripcion` TEXT,
  `imagen_portada` VARCHAR(500) DEFAULT NULL,
  `pin` VARCHAR(10) DEFAULT NULL,
  `estado` ENUM('publico', 'privado') NOT NULL DEFAULT 'publico',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pin` (`pin`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pin` (`pin`),
  CONSTRAINT `cuestionarios_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: preguntas
-- Preguntas de cada cuestionario
-- =====================================================
DROP TABLE IF EXISTS `preguntas`;
CREATE TABLE `preguntas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cuestionario_id` INT NOT NULL,
  `tipo_pregunta` ENUM('opcion_multiple', 'seleccion_simple', 'verdadero_falso') NOT NULL,
  `texto_pregunta` TEXT NOT NULL,
  `imagen_pregunta` VARCHAR(500) DEFAULT NULL,
  `orden` INT NOT NULL DEFAULT '0',
  `tiempo_limite` INT DEFAULT '30',
  `puntos` INT DEFAULT '1',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_orden` (`orden`),
  CONSTRAINT `preguntas_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: opciones_respuesta
-- Opciones de respuesta para cada pregunta
-- =====================================================
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: sesiones_grupo
-- Sesiones de juego en grupo con códigos de sala
-- =====================================================
DROP TABLE IF EXISTS `sesiones_grupo`;
CREATE TABLE `sesiones_grupo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `grupo_id` INT NOT NULL,
  `cuestionario_id` INT NOT NULL,
  `iniciado_por` INT NOT NULL,
  `session_code` VARCHAR(6) NOT NULL,
  `estado` ENUM('esperando', 'en_progreso', 'finalizado') DEFAULT 'esperando',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` TIMESTAMP NULL DEFAULT NULL,
  `finished_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`),
  KEY `idx_grupo_id` (`grupo_id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_iniciado_por` (`iniciado_por`),
  KEY `idx_estado` (`estado`),
  KEY `idx_session_code` (`session_code`),
  CONSTRAINT `sesiones_grupo_ibfk_1` FOREIGN KEY (`grupo_id`) REFERENCES `grupos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_grupo_ibfk_3` FOREIGN KEY (`iniciado_por`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: usuario_estado_grupo
-- Estado de los usuarios en sesiones de grupo (listos/no listos)
-- =====================================================
DROP TABLE IF EXISTS `usuario_estado_grupo`;
CREATE TABLE `usuario_estado_grupo` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sesion_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `esta_listo` TINYINT(1) DEFAULT '0',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_session` (`sesion_id`, `user_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `usuario_estado_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuario_estado_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: respuestas_grupo
-- Respuestas de usuarios en sesiones de grupo
-- =====================================================
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
  UNIQUE KEY `unique_user_question` (`sesion_id`, `user_id`, `pregunta_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  KEY `opcion_id` (`opcion_id`),
  CONSTRAINT `respuestas_grupo_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_grupo` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_3` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_grupo_ibfk_4` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: sesiones_individual
-- Sesiones de juego individual con códigos de sala
-- =====================================================
DROP TABLE IF EXISTS `sesiones_individual`;
CREATE TABLE `sesiones_individual` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cuestionario_id` INT NOT NULL,
  `iniciado_por` INT NOT NULL,
  `session_code` VARCHAR(6) NOT NULL,
  `estado` ENUM('esperando', 'en_progreso', 'finalizado') DEFAULT 'esperando',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` TIMESTAMP NULL DEFAULT NULL,
  `finished_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_iniciado_por` (`iniciado_por`),
  KEY `idx_estado` (`estado`),
  KEY `idx_session_code` (`session_code`),
  CONSTRAINT `sesiones_individual_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_individual_ibfk_2` FOREIGN KEY (`iniciado_por`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: usuario_estado_individual
-- Estado de los usuarios en sesiones individuales (listos/no listos)
-- =====================================================
DROP TABLE IF EXISTS `usuario_estado_individual`;
CREATE TABLE `usuario_estado_individual` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `sesion_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `esta_listo` TINYINT(1) DEFAULT '0',
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_session` (`sesion_id`, `user_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `usuario_estado_individual_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_individual` (`id`) ON DELETE CASCADE,
  CONSTRAINT `usuario_estado_individual_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: respuestas_individual
-- Respuestas de usuarios en sesiones individuales
-- =====================================================
DROP TABLE IF EXISTS `respuestas_individual`;
CREATE TABLE `respuestas_individual` (
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
  UNIQUE KEY `unique_user_question` (`sesion_id`, `user_id`, `pregunta_id`),
  KEY `idx_sesion_id` (`sesion_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pregunta_id` (`pregunta_id`),
  KEY `opcion_id` (`opcion_id`),
  CONSTRAINT `respuestas_individual_ibfk_1` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_individual` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_individual_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_individual_ibfk_3` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_individual_ibfk_4` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: sesiones_juego
-- Sesiones de juego antiguas/legacy (sin pin_sesion, con user_id)
-- NOTA: Esta tabla se mantiene para compatibilidad con código antiguo
-- =====================================================
DROP TABLE IF EXISTS `sesiones_juego`;
CREATE TABLE `sesiones_juego` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cuestionario_id` INT NOT NULL,
  `user_id` INT NULL,
  `fecha_inicio` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_fin` TIMESTAMP NULL DEFAULT NULL,
  `estado` ENUM('esperando', 'en_progreso', 'finalizado') DEFAULT 'esperando',
  `created_by` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `sesiones_juego_ibfk_1` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sesiones_juego_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_sesiones_juego_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: respuestas_participantes
-- Respuestas en sesiones_juego (legacy, modificada)
-- =====================================================
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
  KEY `idx_pregunta_id` (`pregunta_id`),
  KEY `opcion_id` (`opcion_id`),
  CONSTRAINT `fk_respuestas_sesion` FOREIGN KEY (`sesion_juego_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `respuestas_participantes_ibfk_2` FOREIGN KEY (`pregunta_id`) REFERENCES `preguntas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_respuestas_opcion` FOREIGN KEY (`opcion_id`) REFERENCES `opciones_respuesta` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: resultados
-- Resultados de cuestionarios completados
-- =====================================================
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
  KEY `idx_user_id` (`user_id`),
  KEY `idx_cuestionario_id` (`cuestionario_id`),
  KEY `idx_fecha` (`fecha_completado`),
  KEY `sesion_id` (`sesion_id`),
  CONSTRAINT `resultados_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `resultados_ibfk_2` FOREIGN KEY (`cuestionario_id`) REFERENCES `cuestionarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resultados_ibfk_3` FOREIGN KEY (`sesion_id`) REFERENCES `sesiones_juego` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS=1;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================

/*
NOTAS IMPORTANTES:

1. ESTRUCTURA COMPLETA:
   ✅ Sistema de usuarios
   ✅ Sistema de grupos (con miembros)
   ✅ Sistema de cuestionarios (con estado publico/privado)
   ✅ Sistema de preguntas y opciones
   ✅ Sistema de sesiones de grupo (con códigos de sala)
   ✅ Sistema de sesiones individuales (con códigos de sala)
   ✅ Sistema de respuestas (grupo e individual)
   ✅ Sistema de resultados

2. CAMBIOS INTEGRADOS:
   ✅ cuestionarios.estado: 'publico'/'privado' (en lugar de borrador/publicado/archivado)
   ✅ sesiones_juego: Sin pin_sesion, con user_id
   ✅ respuestas_participantes: Modificada para usar user_id en lugar de participante_id
   ✅ Eliminada tabla participantes (no se usa)

3. FUNCIONALIDADES:
   - Sesiones de grupo: Requiere ser miembro del grupo para jugar
   - Sesiones individuales: Cualquiera con el código puede jugar
   - Códigos de sala: 6 caracteres únicos (ABC123)
   - Sistema de "listo": Todos deben estar listos para empezar
   - Cálculo de puntos: Basado en correctitud y tiempo de respuesta

4. CHARSET:
   - utf8mb4: Soporte completo para emojis y caracteres especiales
   - utf8mb4_unicode_ci: Ordenación sensible a acentos

5. ENGINE:
   - InnoDB: Soporte completo para transacciones y claves foráneas

6. ÍNDICES:
   - Optimizado para consultas frecuentes
   - Índices en claves foráneas
   - Índices en campos de búsqueda (session_code, pin, estado)

ORDEN DE EJECUCIÓN:
Este script está diseñado para ejecutarse en orden y crear todas
las tablas con sus dependencias correctamente resueltas.
*/


