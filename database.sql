-- Tabla de usuarios
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de cuestionarios
CREATE TABLE cuestionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    imagen_portada VARCHAR(500),
    pin VARCHAR(10) UNIQUE,
    estado ENUM('publico', 'privado') DEFAULT 'publico',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_pin (pin)
);

-- Tabla de preguntas
CREATE TABLE preguntas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuestionario_id INT NOT NULL,
    tipo_pregunta ENUM('opcion_multiple', 'seleccion_simple', 'verdadero_falso') NOT NULL,
    texto_pregunta TEXT NOT NULL,
    imagen_pregunta VARCHAR(500),
    orden INT NOT NULL DEFAULT 0,
    tiempo_limite INT DEFAULT 30, -- tiempo específico para esta pregunta (opcional)
    puntos INT DEFAULT 1, -- puntos específicos para esta pregunta (opcional)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    INDEX idx_cuestionario_id (cuestionario_id),
    INDEX idx_orden (orden)
);

-- Tabla de opciones de respuesta
CREATE TABLE opciones_respuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pregunta_id INT NOT NULL,
    texto_opcion TEXT NOT NULL,
    es_correcta BOOLEAN DEFAULT FALSE,
    orden INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    INDEX idx_pregunta_id (pregunta_id)
);

-- Tabla de sesiones de juego (cuando alguien juega un cuestionario)
CREATE TABLE sesiones_juego (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuestionario_id INT NOT NULL,
    pin_sesion VARCHAR(10) UNIQUE NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,
    estado ENUM('esperando', 'en_progreso', 'finalizado') DEFAULT 'esperando',
    created_by INT NOT NULL,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_pin_sesion (pin_sesion),
    INDEX idx_cuestionario_id (cuestionario_id)
);

-- Tabla de participantes en sesiones de juego
CREATE TABLE participantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    nombre_participante VARCHAR(255) NOT NULL,
    puntaje_total INT DEFAULT 0,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE,
    INDEX idx_sesion_id (sesion_id)
);

-- Tabla de respuestas de participantes
CREATE TABLE respuestas_participantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    participante_id INT NOT NULL,
    pregunta_id INT NOT NULL,
    opcion_seleccionada_id INT,
    es_correcta BOOLEAN DEFAULT FALSE,
    tiempo_respuesta INT, -- en segundos
    puntos_obtenidos INT DEFAULT 0,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (opcion_seleccionada_id) REFERENCES opciones_respuesta(id) ON DELETE SET NULL,
    INDEX idx_participante_id (participante_id),
    INDEX idx_pregunta_id (pregunta_id)
);

-- Tabla de resultados guardados (historial de cuestionarios completados)
CREATE TABLE resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cuestionario_id INT NOT NULL,
    sesion_id INT,
    puntaje_obtenido INT DEFAULT 0,
    puntaje_maximo INT NOT NULL,
    total_preguntas INT NOT NULL,
    respuestas_correctas INT DEFAULT 0,
    tiempo_total INT, -- en segundos
    fecha_completado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_cuestionario_id (cuestionario_id),
    INDEX idx_fecha (fecha_completado)
);

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


CREATE TABLE IF NOT EXISTS grupos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    creador_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS grupo_miembros (
    id SERIAL PRIMARY KEY,
    grupo_id INT NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS sesiones_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    sesion_id INT NOT NULL,  -- se vincula a sesiones_juego existente
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,
    estado ENUM('esperando','en_progreso', 'finalizado') DEFAULT 'esperando',
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE
);

-- Respuestas del grupo (en lugar de participante individual)
CREATE TABLE IF NOT EXISTS respuestas_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_grupo_id INT NOT NULL,
    pregunta_id INT NOT NULL,
    opcion_seleccionada_id INT,
    es_correcta BOOLEAN DEFAULT FALSE,
    puntos_obtenidos INT DEFAULT 0,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_grupo_id) REFERENCES sesiones_grupo(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (opcion_seleccionada_id) REFERENCES opciones_respuesta(id) ON DELETE SET NULL
);

-- Resultados finales por grupo
CREATE TABLE IF NOT EXISTS resultados_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    sesion_grupo_id INT NOT NULL,
    cuestionario_id INT NOT NULL,
    puntaje_obtenido INT DEFAULT 0,
    puntaje_maximo INT NOT NULL,
    respuestas_correctas INT DEFAULT 0,
    total_preguntas INT NOT NULL,
    tiempo_total INT, -- en segundos
    fecha_finalizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_grupo_id) REFERENCES sesiones_grupo(id) ON DELETE CASCADE
);