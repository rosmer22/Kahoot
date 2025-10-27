"""
Script de ayuda para configurar PythonAnywhere
Ejecuta esto DESPUÉS de subir los archivos al servidor
"""

print("=" * 70)
print("🚀 CONFIGURACIÓN PARA PYTHONANYWHERE")
print("=" * 70)
print()

# PASO 1: Información del usuario
print("📝 PASO 1: Información de tu cuenta")
print("-" * 70)
usuario = input("Tu usuario de PythonAnywhere: ")
db_password = input("Contraseña de tu base de datos MySQL: ")
db_name = input("Nombre de tu base de datos (ej: tuusuario$Kahoot): ")

print()

# PASO 2: Generar configuración de bd.py
print("📊 PASO 2: Configuración de Base de Datos")
print("-" * 70)
print("\nCopia y pega esto en tu archivo bd.py:\n")

bd_config = f"""import pymysql

def obtener_conexion():
    return pymysql.connect(
        host='{usuario}.mysql.pythonanywhere-services.com',
        user='{usuario}',
        password='{db_password}',
        db='{db_name}',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
"""

print(bd_config)
print()

# PASO 3: URI de redirección para Google OAuth
print("🔐 PASO 3: Google OAuth - Redirect URI")
print("-" * 70)
redirect_uri = f"https://{usuario}.pythonanywhere.com/oauth2callback"
print(f"\nAgrega esta URI en Google Cloud Console:")
print(f"👉 {redirect_uri}")
print()
print("Pasos:")
print("1. Ve a: https://console.cloud.google.com/apis/credentials?project=robot-cuestionarios")
print("2. Edita 'Cuestionarios OAuth Client'")
print("3. En 'URIs de redirección autorizados', agrega:")
print(f"   {redirect_uri}")
print("4. GUARDA")
print()

# PASO 4: Configuración WSGI
print("⚙️ PASO 4: Configuración del archivo WSGI")
print("-" * 70)
proyecto = input("Nombre de tu carpeta del proyecto (ej: mi-app): ")
print()
print(f"Copia y pega esto en tu archivo WSGI de PythonAnywhere:\n")

wsgi_config = f"""import sys
import os

# Agregar el path de tu proyecto
path = '/home/{usuario}/{proyecto}/Kahoot'
if path not in sys.path:
    sys.path.insert(0, path)

# Cambiar al directorio del proyecto
os.chdir(path)

# Importar la app de Flask
from app import app as application
"""

print(wsgi_config)
print()

# PASO 5: Static files
print("📂 PASO 5: Configuración de Static Files")
print("-" * 70)
print("\nEn la sección 'Web' → 'Static files', agrega:")
print()
print("URL                     | Directory")
print("-" * 70)
print(f"/static/                | /home/{usuario}/{proyecto}/Kahoot/static/")
print()

# PASO 6: Comandos útiles
print("💻 PASO 6: Comandos útiles en la consola Bash")
print("-" * 70)
print()
print("# Navegar a tu proyecto:")
print(f"cd ~/\n{proyecto}/Kahoot")
print()
print("# Instalar dependencias:")
print("pip3.10 install --user -r requirements.txt")
print()
print("# Ejecutar script SQL:")
print(f"mysql -u {usuario} -h {usuario}.mysql.pythonanywhere-services.com -p {db_name} < database_completo.sql")
print()
print("# Ver logs de error:")
print("tail -f /var/log/*.pythonanywhere.com.error.log")
print()

# PASO 7: Recordatorios
print("⚠️ PASO 7: RECORDATORIOS IMPORTANTES")
print("-" * 70)
print()
print("1. ❌ Elimina o comenta en app.py:")
print("   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'")
print()
print("2. 📤 Sube manualmente estos archivos (NO los subas a Git):")
print("   - oauth_config.json")
print("   - robot-cuestionarios-0c0d91bed8ea.json")
print()
print("3. 🔐 Después de configurar todo, autoriza Google Drive:")
print(f"   Ve a: https://{usuario}.pythonanywhere.com")
print("   Perfil → 🔐 Autorizar Google Drive")
print()
print("4. 🔄 Recarga la aplicación después de cada cambio:")
print("   Web → Reload button (verde)")
print()

# Resumen final
print("=" * 70)
print("✅ CONFIGURACIÓN LISTA")
print("=" * 70)
print()
print(f"Tu aplicación estará en: https://{usuario}.pythonanywhere.com")
print()
print("📖 Lee la guía completa en: GUIA_PYTHONANYWHERE.md")
print()

