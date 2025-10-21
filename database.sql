-- =========================================================
-- 🚀 CREACIÓN DE TABLAS PARA SISTEMA DE CUESTIONARIOS
-- =========================================================
-- NOTA: Ejecutar este script completo de inicio a fin.
-- Asegúrate de usar MySQL 5.7+ o MariaDB 10.3+.
-- =========================================================

-- Elimina las tablas existentes (en orden inverso)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS resultados_grupo, respuestas_grupo, sesiones_grupo, grupo_miembros, grupos,
resultados, respuestas_participantes, participantes, sesiones_juego, opciones_respuesta,
preguntas, cuestionarios, users;
SET FOREIGN_KEY_CHECKS = 1;

-- =========================================================
-- 1️⃣ USERS
-- =========================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'usuario',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================================================
-- 2️⃣ CUESTIONARIOS
-- =========================================================
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
) ENGINE=InnoDB;

-- =========================================================
-- 3️⃣ PREGUNTAS
-- =========================================================
CREATE TABLE preguntas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuestionario_id INT NOT NULL,
    tipo_pregunta ENUM('opcion_multiple', 'seleccion_simple', 'verdadero_falso') NOT NULL,
    texto_pregunta TEXT NOT NULL,
    imagen_pregunta VARCHAR(500),
    orden INT NOT NULL DEFAULT 0,
    tiempo_limite INT DEFAULT 30,
    puntos INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    INDEX idx_cuestionario_id (cuestionario_id),
    INDEX idx_orden (orden)
) ENGINE=InnoDB;

-- =========================================================
-- 4️⃣ OPCIONES DE RESPUESTA
-- =========================================================
CREATE TABLE opciones_respuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pregunta_id INT NOT NULL,
    texto_opcion TEXT NOT NULL,
    es_correcta BOOLEAN DEFAULT FALSE,
    orden INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    INDEX idx_pregunta_id (pregunta_id)
) ENGINE=InnoDB;

-- =========================================================
-- 5️⃣ SESIONES DE JUEGO
-- =========================================================
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
) ENGINE=InnoDB;

-- =========================================================
-- 6️⃣ PARTICIPANTES
-- =========================================================
CREATE TABLE participantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    nombre_participante VARCHAR(255) NOT NULL,
    puntaje_total INT DEFAULT 0,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE,
    INDEX idx_sesion_id (sesion_id)
) ENGINE=InnoDB;

-- =========================================================
-- 7️⃣ RESPUESTAS DE PARTICIPANTES
-- =========================================================
CREATE TABLE respuestas_participantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    participante_id INT NOT NULL,
    pregunta_id INT NOT NULL,
    opcion_seleccionada_id INT,
    es_correcta BOOLEAN DEFAULT FALSE,
    tiempo_respuesta INT,
    puntos_obtenidos INT DEFAULT 0,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (participante_id) REFERENCES participantes(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (opcion_seleccionada_id) REFERENCES opciones_respuesta(id) ON DELETE SET NULL,
    INDEX idx_participante_id (participante_id),
    INDEX idx_pregunta_id (pregunta_id)
) ENGINE=InnoDB;

-- =========================================================
-- 8️⃣ RESULTADOS
-- =========================================================
CREATE TABLE resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cuestionario_id INT NOT NULL,
    sesion_id INT,
    puntaje_obtenido INT DEFAULT 0,
    puntaje_maximo INT NOT NULL,
    total_preguntas INT NOT NULL,
    respuestas_correctas INT DEFAULT 0,
    tiempo_total INT,
    fecha_completado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_cuestionario_id (cuestionario_id),
    INDEX idx_fecha (fecha_completado)
) ENGINE=InnoDB;

-- =========================================================
-- 9️⃣ GRUPOS
-- =========================================================
CREATE TABLE grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    creador_id INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creador_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- 🔟 GRUPO MIEMBROS
-- =========================================================
CREATE TABLE grupo_miembros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    user_id INT NOT NULL,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- 11️⃣ SESIONES DE GRUPO
-- =========================================================
CREATE TABLE sesiones_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    sesion_id INT NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,
    estado ENUM('esperando','en_progreso','finalizado') DEFAULT 'esperando',
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_juego(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- =========================================================
-- 12️⃣ RESPUESTAS DE GRUPO
-- =========================================================
CREATE TABLE respuestas_grupo (
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
) ENGINE=InnoDB;

-- =========================================================
-- 13️⃣ RESULTADOS DE GRUPO
-- =========================================================
CREATE TABLE resultados_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    sesion_grupo_id INT NOT NULL,
    cuestionario_id INT NOT NULL,
    puntaje_obtenido INT DEFAULT 0,
    puntaje_maximo INT NOT NULL,
    respuestas_correctas INT DEFAULT 0,
    total_preguntas INT NOT NULL,
    tiempo_total INT,
    fecha_finalizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sesion_grupo_id) REFERENCES sesiones_grupo(id) ON DELETE CASCADE
) ENGINE=InnoDB;