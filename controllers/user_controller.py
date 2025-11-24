from bd import obtener_conexion
from app import encriptar_sha256

import psycopg2

def insertar_usuario(username, email, password):
    conexion = obtener_conexion()
    
    # Determinar el rol según el dominio del email
    if email.endswith('@usat.edu.pe'):
        role = 'docente'
    elif email.endswith('@usat.pe'):
        role = 'alumno'
    else:
        role = 'usuario'  # Por si acaso hay otros dominios
    
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, encriptar_sha256(password), role))
    conexion.commit()
    conexion.close()

def obtener_usuario_por_email(email):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password, role FROM users WHERE email = %s", (email,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_por_username(username):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password, role FROM users WHERE username = %s", (username,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_por_id(user_id):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password, role FROM users WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_username(user_id, new_username):
    # Verificar si el username ya existe
    existing_user = obtener_usuario_por_username(new_username)
    if existing_user and existing_user['id'] != user_id:
        return False, "El nombre de usuario ya está en uso"

    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE users SET username = %s WHERE id = %s",
                      (new_username, user_id))
    conexion.commit()
    conexion.close()
    return True, "Nombre de usuario actualizado correctamente"

def actualizar_email(user_id, new_email):
    # Verificar si el email ya existe
    existing_user = obtener_usuario_por_email(new_email)
    if existing_user and existing_user['id'] != user_id:
        return False, "El correo electrónico ya está en uso"

    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE users SET email = %s WHERE id = %s",
                      (new_email, user_id))
    conexion.commit()
    conexion.close()
    return True, "Correo electrónico actualizado correctamente"

def actualizar_password(user_id, old_password, new_password):
    # Obtener usuario actual
    usuario = obtener_usuario_por_id(user_id)
    if not usuario:
        return False, "Usuario no encontrado"

    # Verificar contraseña anterior
    if usuario['password'] != encriptar_sha256(old_password):
        return False, "La contraseña anterior es incorrecta"

    # Actualizar contraseña
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE users SET password = %s WHERE id = %s",
                      (encriptar_sha256(new_password), user_id))
    conexion.commit()
    conexion.close()
    return True, "Contraseña actualizada correctamente"

def eliminar_usuario(db, user_id):
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        return True, "Tu cuenta ha sido eliminada exitosamente."
    except psycopg2.Error as e:
        db.rollback()
        return False, f"Error al eliminar la cuenta: {e.pgerror}"

def actualizar_password_por_email(email, new_password):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (encriptar_sha256(new_password), email)
        )
    conexion.commit()
    conexion.close()
    return True, "Contraseña actualizada correctamente"
