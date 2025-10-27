-- =====================================================
-- Script para crear sistema de sesiones individuales
-- con códigos de sala (similar al sistema de grupos)
-- =====================================================

-- 1. Crear tabla sesiones_individual
CREATE TABLE IF NOT EXISTS `sesiones_individual` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Crear tabla usuario_estado_individual
CREATE TABLE IF NOT EXISTS `usuario_estado_individual` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*
FUNCIONALIDAD DEL SISTEMA:

1. SESIÓN INDIVIDUAL (sesiones_individual):
   - Se crea cuando un usuario quiere iniciar un cuestionario
   - Genera un session_code único de 6 caracteres
   - Permite que otros usuarios se unan usando el código
   - Estado: 'esperando' -> 'en_progreso' -> 'finalizado'

2. REGISTRO EN SESIÓN (usuario_estado_individual):
   - Los usuarios se registran al entrar a la sala
   - Pueden marcar "Estoy Listo" (esta_listo = 1)
   - Solo los usuarios registrados aparecen en la sala
   - UNIQUE constraint evita duplicados

3. LÓGICA DE "LISTO":
   - El juego empieza cuando TODOS los que están EN LA SALA estén listos
   - El creador puede jugar solo o esperar a que otros se unan
   - Flexible para juego individual o multijugador

4. DIFERENCIA CON GRUPOS:
   - No requiere pertenencia a un grupo
   - Cualquier usuario puede unirse si tiene el código
   - Más abierto que el sistema de grupos

FLUJO DE USO:

1. Usuario selecciona "Empezar" en un cuestionario
2. Se crea una sesión con código (ej: "A1B2C3")
3. Usuario va a la sala de espera (individual_quiz.html)
4. Puede compartir el código con otros
5. Otros se unen usando "Unirse" en el header
6. Todos marcan "Estoy Listo"
7. Cuando todos están listos, inicia el juego
8. Juegan en juego_individual.html
9. Al finalizar, ven sus resultados
*/

-- 3. Crear tabla respuestas_individual (similar a respuestas_grupo)
CREATE TABLE IF NOT EXISTS `respuestas_individual` (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

/*
TABLA respuestas_individual:

Guarda las respuestas de cada participante en sesiones individuales.
Similar a respuestas_grupo pero para cuestionarios individuales.

Campos importantes:
- sesion_id: Referencia a la sesión individual
- user_id: Usuario que respondió
- pregunta_id: Pregunta respondida
- opcion_id: Opción seleccionada
- es_correcta: Si la respuesta fue correcta (1) o incorrecta (0)
- puntos: Puntos obtenidos (calculados con fórmula de Kahoot)
- tiempo_respuesta: Segundos que tardó en responder
- UNIQUE constraint: Un usuario solo puede responder una vez cada pregunta por sesión
*/

