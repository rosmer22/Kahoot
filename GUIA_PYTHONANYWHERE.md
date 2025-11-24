# 🚀 GUÍA COMPLETA PARA SUBIR A PYTHONANYWHERE

## ⚠️ IMPORTANTE ANTES DE EMPEZAR

1. **NO subas archivos sensibles** al repositorio público:
   - ❌ `token.pickle`
   - ❌ `oauth_config.json`
   - ❌ `robot-cuestionarios-0c0d91bed8ea.json`

2. **Configuración de base de datos:** Usa las credenciales de PythonAnywhere

---

## 📦 PASO 1: SUBIR ARCHIVOS A PYTHONANYWHERE

### Opción A: Usando Git (Recomendado)

1. **En tu computadora local, inicializa git:**
   ```bash
   cd Kahoot
   git init
   git add .
   git commit -m "Configuración inicial"
   ```

2. **Sube a GitHub/GitLab** (repositorio PRIVADO)

3. **En PythonAnywhere, clona el repositorio:**
   ```bash
   cd ~
   git clone https://github.com/tu-usuario/tu-repo.git
   ```

### Opción B: Subir archivos manualmente

1. Usa el botón "Files" en PythonAnywhere
2. Sube los archivos uno por uno (tedioso pero funciona)

---

## 🗄️ PASO 2: CONFIGURAR BASE DE DATOS

### En PythonAnywhere:

1. Ve a **"Databases"** en el dashboard
2. Copia tus credenciales MySQL:
   - Host: `tuusuario.mysql.pythonanywhere-services.com`
   - Database name: `tuusuario$nombre_bd`
   - Username: `tuusuario`
   - Password: [tu contraseña]

### Actualizar `bd.py`:

```python
import pymysql

def obtener_conexion():
    return pymysql.connect(
        host='tuusuario.mysql.pythonanywhere-services.com',
        user='tuusuario',
        password='TU_PASSWORD_AQUI',
        db='tuusuario$Kahoot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
```

### Ejecutar el script SQL:

1. Ve a **"Databases"** → **"Go to MySQL console"**
2. Ejecuta el archivo `database_completo.sql` completo
3. O usa esta consola Bash:
   ```bash
   mysql -u tuusuario -h tuusuario.mysql.pythonanywhere-services.com -p tuusuario$Kahoot < database_completo.sql
   ```

---

## 📚 PASO 3: INSTALAR DEPENDENCIAS

En la consola Bash de PythonAnywhere:

```bash
cd ~/tu-proyecto/Kahoot
pip3.10 install --user -r requirements.txt
```

O instala una por una:
```bash
pip3.10 install --user Flask PyMySQL flask_mail werkzeug openpyxl google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 🔐 PASO 4: CONFIGURAR OAUTH PARA HTTPS

### 4.1 Subir archivos de credenciales manualmente

**Los archivos sensibles NO deben estar en Git. Súbelos manualmente:**

1. En PythonAnywhere, ve a **"Files"**
2. Navega a tu carpeta del proyecto
3. Sube estos archivos:
   - `oauth_config.json`
   - `robot-cuestionarios-0c0d91bed8ea.json` (si lo sigues usando)

### 4.2 Modificar `app.py` para HTTPS

Busca esta línea en `app.py`:
```python
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
```

**COMÉNTALA o ELIMÍNALA** (solo era para desarrollo local):
```python
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo desarrollo local
```

### 4.3 Actualizar redirect URIs en Google Cloud Console

1. Ve a [Google Cloud Console - Credenciales](https://console.cloud.google.com/apis/credentials?project=robot-cuestionarios)

2. Edita **"Cuestionarios OAuth Client"**

3. En **"URIs de redirección autorizados"**, agrega:
   ```
   https://tuusuario.pythonanywhere.com/oauth2callback
   ```
   
   Por ejemplo, si tu usuario es `valentinoandca`:
   ```
   https://valentinoandca.pythonanywhere.com/oauth2callback
   ```

4. **GUARDA** los cambios

---

## ⚙️ PASO 5: CONFIGURAR WSGI EN PYTHONANYWHERE

1. Ve a **"Web"** en el dashboard
2. Si no tienes una app, crea una nueva web app (Flask)
3. Edita el archivo WSGI (botón "WSGI configuration file")

### Configuración del archivo WSGI:

```python
import sys
import os

# Agregar el path de tu proyecto
path = '/home/tuusuario/tu-proyecto/Kahoot'
if path not in sys.path:
    sys.path.insert(0, path)

# Cambiar al directorio del proyecto
os.chdir(path)

# Importar la app de Flask
from app import app as application
```

**Reemplaza:**
- `tuusuario` → Tu usuario de PythonAnywhere
- `tu-proyecto` → Nombre de tu carpeta del proyecto

---

## 📂 PASO 6: CONFIGURAR CARPETAS ESTÁTICAS

En la sección **"Web"** → **"Static files"**:

Agrega estas rutas:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/tuusuario/tu-proyecto/Kahoot/static/` |

---

## 🔄 PASO 7: RECARGAR LA APLICACIÓN

1. En la sección **"Web"**, haz clic en el botón verde:
   **"Reload tuusuario.pythonanywhere.com"**

2. Ve a tu URL:
   ```
   https://tuusuario.pythonanywhere.com
   ```

---

## 🔐 PASO 8: AUTORIZAR GOOGLE DRIVE EN PRODUCCIÓN

**IMPORTANTE:** Debes autorizar de nuevo en PythonAnywhere porque:
- El archivo `token.pickle` no se subió (está en `.gitignore`)
- Estás usando HTTPS ahora

### Pasos:

1. **Inicia sesión** en tu app de PythonAnywhere
2. Ve al **menú de perfil** → **"🔐 Autorizar Google Drive"**
3. Google te redirigirá a autorizar
4. **Selecciona:** `valentinoandca@gmail.com`
5. **Haz clic en "Permitir"**
6. Volverás a tu app y se creará `token.pickle` en el servidor

---

## 🧪 PASO 9: PROBAR EXPORTACIÓN

1. Juega un cuestionario
2. Exporta resultados
3. Verifica que:
   - ✅ Se descargue el Excel
   - ✅ Se guarde en Google Drive

---

## 📧 PASO 10: CONFIGURAR EMAIL (OPCIONAL)

Si usas el sistema de correos, actualiza las credenciales en `app.py`:

```python
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'tu-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'tu-contraseña-app')
```

**Mejor práctica:** Usa variables de entorno en lugar de hardcodear.

---

## ❓ PROBLEMAS COMUNES

### 1. **Error: "No module named 'pymysql'"**
```bash
pip3.10 install --user PyMySQL
```

### 2. **Error: "Access denied for user"**
- Verifica las credenciales en `bd.py`
- Asegúrate de usar el host correcto: `tuusuario.mysql.pythonanywhere-services.com`

### 3. **Error OAuth: "redirect_uri_mismatch"**
- Verifica que agregaste la URI correcta en Google Cloud Console
- Debe ser: `https://tuusuario.pythonanywhere.com/oauth2callback`
- **HTTPS**, no HTTP

### 4. **Archivos estáticos no cargan (CSS/JS/imágenes)**
- Configura "Static files" en la sección Web
- Recarga la aplicación

### 5. **Error: "insecure_transport"**
- Elimina o comenta: `os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'`
- Esta línea solo es para desarrollo local

### 6. **Token expira constantemente**
- Asegúrate de que `token.pickle` tenga permisos de escritura
- Verifica que el archivo se esté guardando correctamente

---

## 🔒 SEGURIDAD

### Archivos que NO deben estar en Git público:

- ❌ `token.pickle` (contiene credenciales de acceso)
- ❌ `oauth_config.json` (credenciales OAuth)
- ❌ `robot-cuestionarios-*.json` (Service Account keys)
- ❌ Contraseñas de base de datos
- ❌ Claves de API

### Usa `.gitignore`:

Ya creé el archivo `.gitignore` con las exclusiones necesarias.

---

## 📝 CHECKLIST FINAL

Antes de considerar que todo está listo:

- [ ] Archivos subidos a PythonAnywhere
- [ ] Base de datos configurada (credenciales correctas en `bd.py`)
- [ ] Script SQL ejecutado (`database_completo.sql`)
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Archivo WSGI configurado
- [ ] Static files configurados
- [ ] `OAUTHLIB_INSECURE_TRANSPORT` eliminado/comentado
- [ ] Redirect URI actualizado en Google Cloud Console (HTTPS)
- [ ] Aplicación recargada en PythonAnywhere
- [ ] Google Drive autorizado desde PythonAnywhere
- [ ] Exportación probada y funcionando

---

## 🆘 SI ALGO FALLA

1. **Revisa los logs de error:**
   - En PythonAnywhere: Web → Log files → Error log
   
2. **Revisa el log del servidor:**
   - Web → Log files → Server log

3. **Habilita el modo debug temporalmente:**
   ```python
   # En app.py, al final
   if __name__ == '__main__':
       app.run(debug=True)
   ```
   **⚠️ DESACTIVA DEBUG EN PRODUCCIÓN**

---

## 🎉 ¡LISTO!

Tu aplicación debería estar funcionando en:
```
https://tuusuario.pythonanywhere.com
```

Con exportación automática a Google Drive funcionando correctamente.

