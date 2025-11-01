-- Agregar columnas para sincronizar el timer del juego grupal
-- Estas columnas permiten que todos los jugadores compartan el mismo tiempo
-- SINTAXIS PARA MySQL/MariaDB

ALTER TABLE sesiones_grupo 
ADD COLUMN pregunta_actual_id INT DEFAULT NULL COMMENT 'ID de la pregunta que está siendo mostrada actualmente',
ADD COLUMN pregunta_inicio_time TIMESTAMP NULL DEFAULT NULL COMMENT 'Timestamp cuando el docente inició esta pregunta',
ADD COLUMN pregunta_tiempo_limite INT DEFAULT 30 COMMENT 'Tiempo límite en segundos para la pregunta actual';

-- Crear índice para mejorar performance de consultas
CREATE INDEX idx_sesion_pregunta ON sesiones_grupo(id, pregunta_actual_id);

