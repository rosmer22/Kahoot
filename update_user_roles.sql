-- Script para actualizar los roles de usuarios existentes
-- basándose en el dominio de su correo electrónico

-- =====================================================
-- PARTE 1: CREAR DOCENTES DE PRUEBA
-- =====================================================
-- NOTA: Genera los hashes en tu BD usando la función de tu aplicación
-- O crea los usuarios desde el formulario de registro con estos datos:

-- Usuario: docente1 | Email: docente1@usat.edu.pe | Contraseña: docente1
-- Usuario: docente2 | Email: docente2@usat.edu.pe | Contraseña: docente2  
-- Usuario: docente3 | Email: docente3@usat.edu.pe | Contraseña: docente3

-- OPCIÓN 1: Registrar manualmente desde la aplicación (RECOMENDADO)
-- Ve a /register y registra cada docente con sus credenciales

-- OPCIÓN 2: Insertar directamente en BD
INSERT INTO users (username, email, password, role, created_at)
VALUES 
    ('docente1', 'docente1@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW()),
    ('docente2', 'docente2@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW()),
    ('docente3', 'docente3@usat.edu.pe', 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86', 'docente', NOW());

-- =====================================================
-- PARTE 2: ACTUALIZAR USUARIOS EXISTENTES
-- =====================================================

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

-- =====================================================
-- VERIFICACIÓN DE LOS CAMBIOS
-- =====================================================

-- Verificar todos los usuarios y sus roles
SELECT id, username, email, role, created_at
FROM users 
ORDER BY role, username;

-- Contar usuarios por rol
SELECT role, COUNT(*) as cantidad
FROM users
GROUP BY role;

