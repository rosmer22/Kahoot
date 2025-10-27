"""
Script para crear el usuario valentinoandca@gmail.com
"""
from werkzeug.security import generate_password_hash
import pymysql
import bd

# Datos del usuario
username = "nickname2112"
email = "valentinoandca@gmail.com"
password = "Yk1s1wm1typ."

# Generar hash de la contraseña
password_hash = generate_password_hash(password)

print("=" * 60)
print("CREAR USUARIO - valentinoandca@gmail.com")
print("=" * 60)
print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"Password Hash: {password_hash}")
print()

# Opción 1: Insertar directamente en la BD
print("¿Deseas insertar este usuario en la base de datos? (si/no)")
respuesta = input().lower()

if respuesta == 'si' or respuesta == 's':
    try:
        conexion = bd.obtener_conexion()
        cursor = conexion.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"\n❌ ERROR: Ya existe un usuario con el email {email}")
            cursor.close()
            conexion.close()
            exit()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"\n❌ ERROR: Ya existe un usuario con el username {username}")
            cursor.close()
            conexion.close()
            exit()
        
        # Insertar usuario
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, 'usuario')
        )
        conexion.commit()
        
        # Obtener ID
        user_id = cursor.lastrowid
        
        cursor.close()
        conexion.close()
        
        print(f"\n✅ ¡Usuario creado exitosamente!")
        print(f"ID: {user_id}")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: usuario")
        
    except Exception as e:
        print(f"\n❌ ERROR al crear usuario: {e}")
else:
    print("\n📋 SQL para crear el usuario manualmente:")
    print("-" * 60)
    print(f"INSERT INTO users (username, email, password, role)")
    print(f"VALUES ('{username}', '{email}', '{password_hash}', 'usuario');")
    print("-" * 60)
    print("\nCopia y pega este SQL en tu gestor de base de datos.")

