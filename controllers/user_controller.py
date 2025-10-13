from bd import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash

def insertar_usuario(username, email, password):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, generate_password_hash(password)))
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
    if not check_password_hash(usuario['password'], old_password):
        return False, "La contraseña anterior es incorrecta"
    
    # Actualizar contraseña
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                      (generate_password_hash(new_password), user_id))
    conexion.commit()
    conexion.close()
    return True, "Contraseña actualizada correctamente"
