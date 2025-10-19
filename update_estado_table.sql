-- Script para actualizar la tabla cuestionarios
-- Cambiar el ENUM de estado para usar 'publico' y 'privado'

-- PASO 1: Modificar la columna para incluir temporalmente todos los valores
ALTER TABLE cuestionarios 
MODIFY COLUMN estado ENUM('borrador', 'publicado', 'archivado', 'publico', 'privado') DEFAULT 'publico';

-- PASO 2: Migrar datos existentes
UPDATE cuestionarios SET estado = 'publico' WHERE estado IN ('publicado', 'borrador');
UPDATE cuestionarios SET estado = 'privado' WHERE estado = 'archivado';

-- PASO 3: Modificar la columna para tener solo los valores finales
ALTER TABLE cuestionarios 
MODIFY COLUMN estado ENUM('publico', 'privado') DEFAULT 'publico';

-- Verificar el resultado
SELECT id, titulo, estado, pin FROM cuestionarios;
