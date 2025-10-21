import pymysql
from bd import obtener_conexion  # Tu función de conexión
from pymysql.cursors import DictCursor

# ==============================
# Unirse a un grupo
# ==============================
def unirse_a_grupo(grupo_id, user_id):
    """Agrega un usuario a un grupo si no está ya unido."""
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            # Revisar si ya está unido
            cursor.execute(
                "SELECT 1 FROM grupo_miembros WHERE grupo_id=%s AND user_id=%s",
                (grupo_id, user_id)
            )
            if cursor.fetchone():
                return False  # Ya estaba unido

            # Insertar al grupo
            cursor.execute(
                "INSERT INTO grupo_miembros (grupo_id, user_id) VALUES (%s, %s)",
                (grupo_id, user_id)
            )
            conn.commit()
            return True  # Unión exitosa
    finally:
        conn.close()


# ==============================
# Obtener miembros de un grupo
# ==============================
def obtener_miembros_por_grupo(grupo_id):
    """Devuelve la lista de miembros de un grupo."""
    conn = obtener_conexion()
    try:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT u.id, u.username
                FROM users u
                JOIN grupo_miembros gm ON u.id = gm.user_id
                WHERE gm.grupo_id = %s
            """, (grupo_id,))
            return cursor.fetchall()
    finally:
        conn.close()


# ==============================
# Obtener todos los grupos de un usuario
# ==============================
def obtener_grupos_por_usuario(user_id):
    conn = obtener_conexion()
    try:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT g.id, g.nombre, u.username AS creador_nombre, g.fecha_creacion
                FROM grupos g
                JOIN users u ON g.creador_id = u.id
                JOIN grupo_miembros gm ON gm.grupo_id = g.id
                WHERE gm.user_id = %s
                ORDER BY g.fecha_creacion DESC
            """, (user_id,))
            return cursor.fetchall()
    finally:
        conn.close()


# ==============================
# Obtener grupos de un usuario (alternativa)
# ==============================
def obtener_grupos_usuario(user_id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor(DictCursor) as cursor:
            cursor.execute("""
                SELECT g.id, g.nombre, g.fecha_creacion, u.username AS creador
                FROM grupos g
                JOIN users u ON g.creador_id = u.id
                JOIN grupo_miembros gm ON g.id = gm.grupo_id
                WHERE gm.user_id = %s
            """, (user_id,))
            grupos = cursor.fetchall()
        conexion.close()
        return grupos
    except Exception as e:
        print(f"❌ Error al obtener grupos del usuario: {e}")
        return []


# ==============================
# Obtener miembros de un grupo (detallado)
# ==============================
def obtener_miembros_grupo(grupo_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(DictCursor)
        query = """
            SELECT u.id, u.username, u.email, gm.fecha_union
            FROM users u
            JOIN grupo_miembros gm ON u.id = gm.user_id
            WHERE gm.grupo_id = %s
        """
        cursor.execute(query, (grupo_id,))
        miembros = cursor.fetchall()
        return miembros
    finally:
        cursor.close()
        conn.close()


# ==============================
# Agregar miembro a un grupo
# ==============================
def agregar_miembro_grupo(grupo_id, user_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO grupo_miembros (grupo_id, user_id) VALUES (%s, %s)"
        cursor.execute(query, (grupo_id, user_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


# ==============================
# Crear un nuevo grupo
# ==============================
def crear_grupo(nombre, creador_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = "INSERT INTO grupos (nombre, creador_id) VALUES (%s, %s)"
        cursor.execute(query, (nombre, creador_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


# ==============================
# Eliminar miembro de un grupo
# ==============================
def eliminar_miembro_grupo(grupo_id, user_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM grupo_miembros WHERE grupo_id = %s AND user_id = %s"
        cursor.execute(query, (grupo_id, user_id))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
