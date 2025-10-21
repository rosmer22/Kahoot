-- Script para crear las tablas necesarias para la funcionalidad de grupos

-- Tabla de grupos
CREATE TABLE IF NOT EXISTS grupos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    codigo VARCHAR(8) UNIQUE NOT NULL,
    es_publico BOOLEAN DEFAULT FALSE,
    admin_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de miembros de grupos
CREATE TABLE IF NOT EXISTS grupo_miembros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_member (grupo_id, user_id)
);

-- Tabla de sesiones de cuestionarios en grupo
CREATE TABLE IF NOT EXISTS sesiones_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    cuestionario_id INT NOT NULL,
    iniciado_por INT NOT NULL,
    estado ENUM('esperando', 'activo', 'finalizado') DEFAULT 'esperando',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    FOREIGN KEY (grupo_id) REFERENCES grupos(id) ON DELETE CASCADE,
    FOREIGN KEY (cuestionario_id) REFERENCES cuestionarios(id) ON DELETE CASCADE,
    FOREIGN KEY (iniciado_por) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de respuestas de usuarios en sesiones de grupo
CREATE TABLE IF NOT EXISTS respuestas_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    user_id INT NOT NULL,
    pregunta_id INT NOT NULL,
    opcion_id INT NOT NULL,
    es_correcta BOOLEAN,
    tiempo_respuesta INT, -- en segundos
    puntos INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_grupo(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE,
    FOREIGN KEY (opcion_id) REFERENCES opciones_respuesta(id) ON DELETE CASCADE,
    UNIQUE KEY unique_response (sesion_id, user_id, pregunta_id)
);

-- Tabla de estado de preparación de usuarios
CREATE TABLE IF NOT EXISTS usuario_estado_grupo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sesion_id INT NOT NULL,
    user_id INT NOT NULL,
    esta_listo BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_grupo(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_session (sesion_id, user_id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_grupos_codigo ON grupos(codigo);
CREATE INDEX idx_grupos_admin ON grupos(admin_id);
CREATE INDEX idx_grupo_miembros_grupo ON grupo_miembros(grupo_id);
CREATE INDEX idx_grupo_miembros_user ON grupo_miembros(user_id);
CREATE INDEX idx_sesiones_grupo ON sesiones_grupo(grupo_id);
CREATE INDEX idx_respuestas_sesion ON respuestas_grupo(sesion_id);
CREATE INDEX idx_respuestas_user ON respuestas_grupo(user_id);
CREATE INDEX idx_estado_sesion ON usuario_estado_grupo(sesion_id);
CREATE INDEX idx_estado_user ON usuario_estado_grupo(user_id);
