-- Script de actualización para el sistema de sesiones de grupo con códigos de sala
-- Este script asegura que las tablas tengan la estructura correcta para el nuevo flujo

-- =====================================================
-- 1. Verificar y actualizar tabla sesiones_grupo
-- =====================================================

-- La tabla sesiones_grupo debe tener estas columnas:
-- - id (INT, AUTO_INCREMENT, PRIMARY KEY)
-- - grupo_id (INT, FK a grupos)
-- - cuestionario_id (INT, FK a cuestionarios)
-- - iniciado_por (INT, FK a users)
-- - session_code (VARCHAR(6), UNIQUE) -- Código de sala de 6 caracteres
-- - estado (ENUM: 'esperando', 'en_progreso', 'finalizado')
-- - created_at (TIMESTAMP)
-- - started_at (TIMESTAMP NULL)
-- - finished_at (TIMESTAMP NULL)

-- Verificar que session_code existe y es UNIQUE
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE,
    COLUMN_KEY
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'sesiones_grupo' 
AND COLUMN_NAME = 'session_code';

-- Si no existe, agregarlo (descomentar si es necesario):
-- ALTER TABLE sesiones_grupo 
-- ADD COLUMN session_code VARCHAR(6) NOT NULL,
-- ADD UNIQUE KEY session_code (session_code);

-- =====================================================
-- 2. Verificar y actualizar tabla usuario_estado_grupo
-- =====================================================

-- La tabla usuario_estado_grupo debe tener:
-- - id (INT, AUTO_INCREMENT, PRIMARY KEY)
-- - sesion_id (INT, FK a sesiones_grupo)
-- - user_id (INT, FK a users)
-- - esta_listo (TINYINT(1), DEFAULT 0)
-- - created_at (TIMESTAMP)
-- - updated_at (TIMESTAMP)
-- - UNIQUE KEY unique_user_session (sesion_id, user_id)

-- Verificar estructura
SELECT 
    COLUMN_NAME, 
    COLUMN_TYPE, 
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'usuario_estado_grupo';

-- Verificar que existe la restricción UNIQUE
SELECT 
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
WHERE TABLE_NAME = 'usuario_estado_grupo'
AND CONSTRAINT_TYPE = 'UNIQUE';

-- =====================================================
-- 3. Verificar índices necesarios
-- =====================================================

-- Verificar índices en sesiones_grupo
SHOW INDEX FROM sesiones_grupo;

-- Verificar índices en usuario_estado_grupo  
SHOW INDEX FROM usuario_estado_grupo;

-- =====================================================
-- 4. Datos de prueba (opcional)
-- =====================================================

-- Para crear una sesión de prueba, puedes usar:
/*
INSERT INTO sesiones_grupo (grupo_id, cuestionario_id, iniciado_por, session_code, estado, created_at)
VALUES (1, 1, 1, 'ABC123', 'esperando', NOW());

-- Para registrar usuarios en la sesión:
INSERT INTO usuario_estado_grupo (sesion_id, user_id, esta_listo)
VALUES (1, 1, 0), (1, 2, 0);
*/

-- =====================================================
-- 5. Limpiar sesiones antiguas (opcional)
-- =====================================================

-- Para limpiar sesiones que llevan más de 24 horas en estado 'esperando':
/*
UPDATE sesiones_grupo 
SET estado = 'finalizado', finished_at = NOW()
WHERE estado = 'esperando' 
AND created_at < DATE_SUB(NOW(), INTERVAL 24 HOUR);
*/

-- =====================================================
-- NOTAS IMPORTANTES
-- =====================================================

/*
CAMBIOS CLAVE EN EL NUEVO FLUJO:

1. CÓDIGO DE SALA (session_code):
   - Cada sesión de grupo tiene un código único de 6 caracteres
   - Los usuarios pueden unirse usando este código desde el botón "Unirse" del header
   - Solo los miembros del grupo pueden unirse a la sesión

2. REGISTRO EN SESIÓN (usuario_estado_grupo):
   - Los usuarios se registran automáticamente al entrar a /grupo/quiz/<sesion_id>
   - También pueden registrarse usando el endpoint /api/grupo/unirse-sesion con el código
   - Solo los usuarios registrados en usuario_estado_grupo aparecen en la sala

3. LÓGICA DE "LISTO":
   - El juego empieza cuando TODOS los que están EN LA SALA estén listos
   - NO espera a todos los miembros del grupo, solo a los que se unieron
   - Esto permite que grupos grandes jueguen con solo algunos miembros

4. VALIDACIONES:
   - Se verifica que el usuario sea miembro del grupo antes de permitir unirse
   - Se verifica que la sesión no esté finalizada
   - Se previenen duplicados con ON DUPLICATE KEY UPDATE

ESTRUCTURA DE TABLAS ACTUAL (según database.sql):

✅ sesiones_grupo - Tabla OK con todas las columnas necesarias
✅ usuario_estado_grupo - Tabla OK con UNIQUE constraint
✅ grupos - Tabla OK
✅ grupo_miembros - Tabla OK

No se requieren cambios en la estructura de la base de datos si ya ejecutaste database.sql
*/

