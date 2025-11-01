-- Script para actualizar las contraseñas de los 3 docentes de prueba
-- Contraseña para todos: la misma que usaste como ejemplo

-- Actualizar contraseña de docente1
UPDATE users 
SET password = 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86'
WHERE username = 'docente1' AND email = 'docente1@usat.edu.pe';

-- Actualizar contraseña de docente2
UPDATE users 
SET password = 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86'
WHERE username = 'docente2' AND email = 'docente2@usat.edu.pe';

-- Actualizar contraseña de docente3
UPDATE users 
SET password = 'scrypt:32768:8:1$DYziSQnixODm9cfo$438adba2074f028ab80aac78b8156f2ddbb8c75aeb4698d29b1b4e2b2c2826675ec404301dfa1694712fc14f2aca43a3d2551dbdeed65317d8f120da0a66db86'
WHERE username = 'docente3' AND email = 'docente3@usat.edu.pe';

-- Verificar las actualizaciones
SELECT username, email, role, 
       LEFT(password, 50) as password_hash 
FROM users 
WHERE username IN ('docente1', 'docente2', 'docente3')
ORDER BY username;

