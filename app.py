from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g, send_file
from controllers import user_controller, quiz_controller
from werkzeug.security import check_password_hash
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from io import BytesIO
from datetime import datetime
from werkzeug.exceptions import HTTPException
from flask_mail import Mail, Message
import random
import bd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import logging
import os
import re
from pathlib import Path  # ✅ agregado para rutas absolutas seguras
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'dev-secret-change-me'

# === Config generales (MODIFICADO: usar rutas absolutas y crear carpeta en carga) ===
BASE_DIR = Path(__file__).resolve().parent               # /home/usuario/mysite
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)            # crea si no existe (funciona en WSGI)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)            # ruta ABSOLUTA para guardar archivos

# === Config Google Drive ===
GOOGLE_DRIVE_CREDENTIALS_FILE = str(BASE_DIR / 'robot-cuestionarios-0c0d91bed8ea.json')
GOOGLE_DRIVE_FOLDER_ID = '1v1lgL9bQQMNPcfFFmvkHHo0KDpk5MOiV'

# === Helper: Subir archivo a Google Drive ===
def subir_a_google_drive(file_stream, filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
    """
    Sube un archivo a Google Drive
    
    Args:
        file_stream: BytesIO con el contenido del archivo
        filename: Nombre del archivo
        mimetype: Tipo MIME del archivo
        
    Returns:
        dict: {'success': bool, 'file_id': str, 'file_url': str} o error
    """
    try:
        # Autenticación con Service Account
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_DRIVE_CREDENTIALS_FILE,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Crear servicio de Drive
        service = build('drive', 'v3', credentials=credentials)
        
        # Metadata del archivo
        file_metadata = {
            'name': filename,
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
        }
        
        # Subir archivo
        media = MediaIoBaseUpload(file_stream, mimetype=mimetype, resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink',
            supportsAllDrives=True  # Permite guardar en carpetas compartidas
        ).execute()
        
        return {
            'success': True,
            'file_id': file.get('id'),
            'file_url': file.get('webViewLink'),
            'message': 'Archivo subido exitosamente a Google Drive'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Error al subir a Google Drive: {str(e)}'
        }

# === Config de correo (Gmail SMTP) ===
# Sugerencia: usar variables de entorno para no exponer credenciales en código
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'valentinoandca@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'gcdl wgwf lego lmin')  # contraseña de aplicación
mail = Mail(app)

# Configuración básica de logging para registrar errores en la consola
logging.basicConfig(level=logging.ERROR)

# Almacén temporal de usuarios pendientes de verificación
# {email: {"username": str, "password": str, "codigo": int, "expira": datetime}}
usuarios_pendientes = {}
codigos = {}



# =====================
#  Hooks / Helpers
# =====================
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = user_controller.obtener_usuario_por_id(user_id)

def is_auth():
    return g.user is not None

@app.context_processor
def inject_globals():
    return dict(is_auth=is_auth(), user=g.user)


# =====================
#  Rutas públicas
# =====================
@app.route('/')
def home():
    """Página de inicio que muestra los cuestionarios públicos más recientes."""
    db = bd.obtener_conexion()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT
            c.id,
            COALESCE(c.titulo, 'Sin título') as titulo,
            c.pin,
            c.imagen_portada,
            (SELECT COUNT(*) FROM preguntas p WHERE p.cuestionario_id = c.id) as question_count
        FROM cuestionarios c
        WHERE c.estado = 'publico'
        ORDER BY c.created_at DESC
        LIMIT 6
        """
    )
    quizzes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('home.html', title='RoBot', quizzes=quizzes)



@app.errorhandler(404)
def page_not_found(e):
    """Maneja errores 404 (Página no encontrada)."""
    return render_template('error.html', title='Página no encontrada'), 404

@app.errorhandler(Exception)

def handle_exception(e):
    """Maneja excepciones no capturadas para evitar que la aplicación se caiga."""
    # Si es una excepción HTTP estándar (como 404, 401, etc.), deja que Flask la maneje.
    if isinstance(e, HTTPException):
        return e

    # Para cualquier otra excepción (errores 500), regístrala y muestra la página de error.
    app.logger.error(f"Error no manejado: {e}", exc_info=True)
    flash("Ha ocurrido un error inesperado en el servidor. Nuestro equipo ha sido notificado.", "error")
    return render_template('error.html', title='Error del Sistema'), 500


@app.route('/empezar', methods=['GET'])
def empezar():
     return render_template('empezar.html', title='Empezar')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_controller.obtener_usuario_por_email(email)

        if not user:
            flash('No existe una cuenta con ese usuario o correo. Por favor, regístrate.', 'error')
            return redirect(url_for('login'))

        if check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = {
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
            flash('¡Bienvenido de nuevo!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html', title='Iniciar Sesión')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# =====================
#  Registro con verificación por correo
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        username = request.form.get('username').strip()
        password = request.form.get('password')

        # Validaciones previas
        if user_controller.obtener_usuario_por_username(username):
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))

        if user_controller.obtener_usuario_por_email(email):
            flash('El correo electrónico ya está en uso', 'error')
            return redirect(url_for('register'))

        if not (email.endswith('@usat.edu.pe') or email.endswith('@usat.pe')):
            flash('El correo debe pertenecer al dominio usat.edu.pe o usat.pe', 'error')
            return redirect(url_for('register'))
        # validación de minuscula, mayuscula, numero y caracter
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&._-])[A-Za-z\d@$!%*?&._-]{8,}$'

        if not re.match(pattern, password):
            flash('La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, una minúscula, un número y un carácter especial.', 'error')
            return redirect(url_for('register'))

        # Generar código de verificación
        codigo = random.randint(100000, 999999)
        expira = datetime.datetime.now() + datetime.timedelta(minutes=10)

        usuarios_pendientes[email] = {
            'username': username,
            'password': password,
            'codigo': codigo,
            'expira': expira,
        }

        # Enviar correo con el código (si hay credenciales válidas)
        try:
            msg = Message(
                'Código de confirmación - RoBot',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Tu código de confirmación es: {codigo}\nVálido por 10 minutos."
            mail.send(msg)
            session['email_verificacion'] = email
            flash('Se ha enviado un código de verificación a tu correo. Revisa tu bandeja.', 'info')
            return redirect(url_for('verify_email'))
        except Exception as e:
            # Si el correo falla, se puede permitir registro directo o mostrar error.
            # Aquí optamos por mostrar error para no crear cuentas sin verificación.
            flash(f'No se pudo enviar el correo de verificación: {e}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html', title='Registrarme')

@app.route('/codigo_recuperacion', methods=['GET', 'POST'])
def codigo_recuperacion():
    if request.method == 'POST':
        email = request.form.get('email').strip()

        if user_controller.obtener_usuario_por_email(email):
            # Generar código de verificación
            codigo = random.randint(100000, 999999)

            codigos[email] = {
                'codigo': codigo,
                'expira': datetime.datetime.now() + datetime.timedelta(minutes=10)
            }

            try:
                msg = Message(
                    'Código de confirmación - RoBot',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email]
                )
                msg.body = f"Tu código de confirmación es: {codigo}\nVálido por 10 minutos."
                mail.send(msg)
                session['email_verificacion'] = email
                flash('Se ha enviado un código de verificación a tu correo. Revisa tu bandeja.', 'info')
                return redirect(url_for('verificar_recuperar_cuenta'))
            except Exception as e:
                # Si el correo falla, se puede permitir registro directo o mostrar error.
                # Aquí optamos por mostrar error para no crear cuentas sin verificación.
                flash(f'No se pudo enviar el correo de verificación: {e}', 'error')
                return redirect(url_for('verificar_codigo'))
        else:
            flash('El correo electrónico no existe', 'error')
            return redirect(url_for('recuperar_cuenta'))

@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    email = session.get('email_verificacion')
    if not email:
        return redirect(url_for('register'))

    # Validar si el correo ya pertenece a un usuario registrado
    if user_controller.obtener_usuario_por_email(email):
        session.pop('email_verificacion', None)
        flash('Ya tienes una cuenta con este correo. Por favor, inicia sesión.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo')
        datos = usuarios_pendientes.get(email)

        if datos and str(datos['codigo']) == codigo_ingresado and datetime.datetime.now() < datos['expira']:
            # Crear usuario definitivo
            user_controller.insertar_usuario(datos['username'], email, datos['password'])

            # Recuperar el usuario recién creado
            nuevo_usuario = user_controller.obtener_usuario_por_email(email)

            # Eliminar datos temporales
            usuarios_pendientes.pop(email, None)
            session.pop('email_verificacion', None)

            flash('Cuenta verificada y creada correctamente ✅', 'success')

            # Iniciar sesión automáticamente con la nueva cuenta
            if nuevo_usuario:
                session['user_id'] = nuevo_usuario['id']
                session['user'] = {
                    'username': nuevo_usuario['username'],
                    'email': nuevo_usuario['email'],
                    'role': nuevo_usuario['role']
                }

                flash('¡Bienvenido!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Error al iniciar sesión automáticamente. Intenta iniciar sesión manualmente.', 'warning')
                return redirect(url_for('login'))
        else:
            flash('Código inválido o expirado ❌', 'error')

    return render_template('emailverificacion.html', title='Verificar correo')

@app.route('/verificar_codigo_recuperacion', methods=['GET', 'POST'])
def verificar_codigo_recuperacion():
    email = session.get('email_verificacion')
    if not email:
        return redirect(url_for('recuperar_cuenta'))

    if request.method == 'POST':
        codigo_ingresado = request.form.get('codigo')
        datos = codigos.get(email)

        if datos and str(datos['codigo']) == codigo_ingresado and datetime.datetime.now() < datos['expira']:
            # Código válido → redirige al formulario de cambio de contraseña
            codigos.pop(email, None)
            return redirect(url_for('cambiar_contra'))  # 👈 ajusta este nombre si tu función de cambio de contraseña tiene otro nombre
        else:
            flash('Código inválido o expirado', 'error')

    return render_template('verificar_codigo.html', title='Verificar código')

@app.route('/cambiar_contra', methods=['GET'])
def cambiar_contra():
     return render_template('cambiar_contra.html', title='Empezar')

@app.route('/resend_code', methods=['POST'])
def resend_verification_code():
    """Reenvía un nuevo código de verificación al correo en sesión."""
    email = session.get('email_verificacion')
    if not email or email not in usuarios_pendientes:
        return jsonify({'success': False, 'message': 'No hay una verificación pendiente o la sesión ha expirado.'}), 400

    # Generar nuevo código y actualizar datos
    codigo = random.randint(100000, 999999)
    expira = datetime.datetime.now() + datetime.timedelta(minutes=10)

    usuarios_pendientes[email]['codigo'] = codigo
    usuarios_pendientes[email]['expira'] = expira

    # Enviar correo con el nuevo código
    try:
        msg = Message(
            'Nuevo Código de confirmación - RoBot',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"Tu nuevo código de confirmación es: {codigo}\nVálido por 10 minutos."
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Se ha enviado un nuevo código a tu correo.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'No se pudo reenviar el correo: {e}'}), 500


# =====================
#  Perfil y seguridad
# =====================
@app.route('/settings')
def settings():
    if g.user is None:
        return redirect(url_for('login'))
    return render_template('settings.html', title='Configuración', user=g.user)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if g.user is None:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json()
    user_id = g.user['id']

    try:
        # Actualizar username si se proporcionó
        if 'username' in data:
            success, message = user_controller.actualizar_username(user_id, data['username'])
            if not success:
                return jsonify({'success': False, 'message': message}), 400

        # Actualizar email si se proporcionó
        if 'email' in data:
            success, message = user_controller.actualizar_email(user_id, data['email'])
            if not success:
                return jsonify({'success': False, 'message': message}), 400

        return jsonify({'success': True, 'message': 'Perfil actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/change_password', methods=['POST'])
def change_password():
    if g.user is None:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json()
    user_id = g.user['id']
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    try:
        success, message = user_controller.actualizar_password(user_id, old_password, new_password)
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================
#  Vistas de cuestionarios
# =====================
@app.route('/my-quizzes')
def my_quizzes():
    if g.user is None:
        return redirect(url_for('login'))

    db = bd.obtener_conexion()
    created = quiz_controller.listar_cuestionarios_usuario(db, g.user['id'])
    db.close()

    # Por ahora, completados está vacío (se implementará en el futuro)
    completed = []

    return render_template('my_quizzes.html', title='Mis cuestionarios', created=created, completed=completed)

@app.route('/lobby/<int:cuestionario_id>')
def lobby(cuestionario_id):
    """Muestra el lobby de espera para un cuestionario."""
    if not g.user:
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('login'))

    modo = request.args.get('modo', 'individual')

    db = bd.obtener_conexion()
    cursor = db.cursor()

    # Obtener detalles del cuestionario
    cursor.execute("SELECT id, titulo, pin FROM cuestionarios WHERE id = %s", (cuestionario_id,))
    quiz = cursor.fetchone()

    if not quiz:
        flash('Cuestionario no encontrado.', 'error')
        return redirect(url_for('my_quizzes'))

    # Si el modo es grupal, redirigir a la página de grupos por ahora
    if modo == 'grupal':
        # This is a temporary solution, as the group flow from here is not clear.
        flash('La función de iniciar un quiz grupal desde aquí no está implementada. Por favor, inicia el quiz desde la página del grupo.', 'info')
        return redirect(url_for('grupos'))

    cursor.close()
    db.close()

    return render_template('lobby.html', quiz=quiz, pin=quiz['pin'], modo=modo)

@app.route('/cuestionario/<pin>/espera')
def espera_cuestionario(pin):
    """Página de espera para un jugador que se une a un cuestionario."""
    db = bd.obtener_conexion()
    cursor = db.cursor()

    # Buscar el cuestionario por PIN
    cursor.execute("SELECT id, titulo FROM cuestionarios WHERE pin = %s", (pin,))
    quiz = cursor.fetchone()

    cursor.close()
    db.close()

    if not quiz:
        flash('El PIN del cuestionario no es válido o ha expirado.', 'error')
        return redirect(url_for('join_quiz'))

    return render_template('lobby.html', quiz=quiz, pin=pin, modo='individual')

@app.route('/api/participantes')
def api_participantes():
    """Devuelve la lista de participantes para un PIN de cuestionario."""
    pin = request.args.get('pin')
    if not pin:
        return jsonify({'error': 'PIN no proporcionado'}), 400

    # TODO: Replace with a real database query
    participantes = [
        {'nombre': g.user['username'] if g.user else 'Jugador Anonimo', 'puntaje': 0},
    ]

    return jsonify({'participantes': participantes})

@app.route('/api/iniciar_sesion/<pin>', methods=['POST'])
def api_iniciar_sesion(pin):
    """Marca una sesión de cuestionario como iniciada."""
    if not g.user:
        return jsonify({'error': 'No autorizado'}), 401

    # TODO: Update the session status in the database

    return jsonify({'success': True, 'message': 'Cuestionario iniciado'})

@app.route('/sesion/<pin>/pregunta/', defaults={'num_pregunta': 1})
@app.route('/sesion/<pin>/pregunta/<int:num_pregunta>')
def sesion_pregunta(pin, num_pregunta):
    """Muestra una pregunta de un cuestionario en una sesión de juego."""
    if not g.user:
        flash('Debes iniciar sesión para jugar.', 'warning')
        return redirect(url_for('login'))

    db = None
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()

        # Obtener el cuestionario a partir del PIN
        cursor.execute("SELECT id, titulo FROM cuestionarios WHERE pin = %s", (pin,))
        quiz = cursor.fetchone()

        if not quiz:
            cursor.close(); db.close()
            flash('El PIN del cuestionario no es válido o ha expirado.', 'error')
            return redirect(url_for('join_quiz'))

        cuestionario_id = quiz['id']

        # Obtener todas las preguntas con opciones
        cursor.execute("""
            SELECT p.id, p.texto_pregunta, p.tiempo_limite
            FROM preguntas p
            WHERE p.cuestionario_id = %s
            ORDER BY p.orden ASC
        """, (cuestionario_id,))
        preguntas_db = cursor.fetchall()

        preguntas_list = []
        for p in preguntas_db:
            cursor.execute("""
                SELECT id, texto_opcion, es_correcta, orden
                FROM opciones_respuesta
                WHERE pregunta_id = %s
                ORDER BY orden ASC
            """, (p['id'],))
            opciones = cursor.fetchall()
            preguntas_list.append({
                'id': p['id'],
                'texto_pregunta': p['texto_pregunta'],
                'tiempo_limite': p.get('tiempo_limite', 30),
                'opciones': [
                    {'id': o['id'], 'texto_opcion': o['texto_opcion'], 'es_correcta': bool(o['es_correcta'])}
                    for o in opciones
                ]
            })

        cursor.close()

        if not preguntas_list:
            db.close()
            flash('Este cuestionario no tiene preguntas.', 'error')
            return redirect(url_for('my_quizzes'))

        # Si el número de pregunta solicitado es mayor que el total, el quiz ha terminado.
        if num_pregunta > len(preguntas_list):
            db.close()
            return redirect(url_for('resultados_quiz', pin=pin))

        pregunta_actual = preguntas_list[num_pregunta - 1]

        resp = render_template(
            'juego_pregunta.html',
            pin=pin,
            quiz=quiz,
            preguntas=preguntas_list,
            preguntas_json=preguntas_list, # Pasa la lista de Python directamente
            num_pregunta=num_pregunta,
            puntaje_inicial=0,
            tiempo_limite=pregunta_actual['tiempo_limite']
        )
        db.close()
        return resp

    except Exception as e:
        if db:
            try: db.close()
            except: pass
        flash(f'Error al cargar la pregunta: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/api/sesion/responder', methods=['POST'])
def api_responder_pregunta():
    """API para que un usuario individual guarde su respuesta."""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    data = request.get_json()
    pin = data.get('pin')
    pregunta_id = data.get('pregunta_id')
    opcion_id = data.get('opcion_id')
    tiempo_respuesta = data.get('tiempo_respuesta')

    if not all([pin, pregunta_id, opcion_id, tiempo_respuesta is not None]):
        return jsonify({'success': False, 'message': 'Faltan datos en la solicitud'}), 400

    db = None
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()

        # 1. Obtener la sesión de juego y el cuestionario
        cursor.execute("""
            SELECT sj.id as sesion_id
            FROM sesiones_juego sj JOIN cuestionarios c ON sj.cuestionario_id = c.id
            WHERE c.pin = %s AND sj.user_id = %s AND sj.estado = 'en_progreso'
            LIMIT 1
        """, (pin, g.user['id']))
        sesion_info = cursor.fetchone()

        if not sesion_info:
            # Si no existe, la creamos
            cursor.execute("SELECT id FROM cuestionarios WHERE pin = %s", (pin,))
            quiz = cursor.fetchone()
            if not quiz:
                return jsonify({'success': False, 'message': 'PIN no válido'}), 404
            
            # Usamos la nueva columna user_id y la columna created_by para el creador
            cursor.execute("""
                INSERT INTO sesiones_juego (cuestionario_id, user_id, estado, fecha_inicio, created_by)
                VALUES (%s, %s, 'en_progreso', NOW(), %s)
            """, (quiz['id'], g.user['id'], g.user['id']))
            sesion_id = cursor.lastrowid
        else:
            sesion_id = sesion_info['sesion_id']

        # 2. Verificar si la respuesta es correcta y calcular puntos
        cursor.execute("SELECT es_correcta FROM opciones_respuesta WHERE id = %s", (opcion_id,))
        opcion = cursor.fetchone()
        es_correcta = opcion['es_correcta'] if opcion else False

        cursor.execute("SELECT tiempo_limite, puntos FROM preguntas WHERE id = %s", (pregunta_id,))
        pregunta = cursor.fetchone()
        puntos_base = pregunta['puntos'] if pregunta else 1000

        puntos_obtenidos = 0
        if es_correcta:
            # Fórmula de puntos: (1 - (tiempo_respuesta / tiempo_limite / 2)) * puntos_base
            tiempo_limite = pregunta['tiempo_limite'] if pregunta else 30
            puntos_obtenidos = round((1 - (float(tiempo_respuesta) / tiempo_limite / 2)) * puntos_base)

        # 3. Guardar la respuesta
        cursor.execute("""
            INSERT INTO respuestas_participantes (sesion_juego_id, user_id, pregunta_id, opcion_id, es_correcta, puntos_obtenidos, tiempo_respuesta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (sesion_id, g.user['id'], pregunta_id, opcion_id, es_correcta, puntos_obtenidos, tiempo_respuesta))

        db.commit()
        return jsonify({'success': True, 'correct': bool(es_correcta), 'points': puntos_obtenidos})

    except Exception as e:
        if db: db.rollback()
        return jsonify({'success': False, 'message': f'Error al guardar respuesta: {str(e)}'}), 500

@app.route('/explore')
def explore():
    """Explorar cuestionarios públicos (versión que consulta BD)."""
    search_query = request.args.get('q', '').strip()
    
    db = bd.obtener_conexion()
    cursor = db.cursor()
    
    if search_query:
        # Búsqueda por título o PIN
        cursor.execute(
            """
            SELECT id,
                   COALESCE(titulo, 'Sin título') as titulo,
                   pin,
                   COALESCE(descripcion, '') as descripcion,
                   imagen_portada
            FROM cuestionarios
            WHERE estado = 'publico' 
            AND (LOWER(titulo) LIKE LOWER(%s) OR CAST(pin AS CHAR) LIKE %s)
            ORDER BY created_at DESC
            """,
            (f'%{search_query}%', f'%{search_query}%')
        )
    else:
        # Sin búsqueda, mostrar todos
        cursor.execute(
            """
            SELECT id,
                   COALESCE(titulo, 'Sin título') as titulo,
                   pin,
                   COALESCE(descripcion, '') as descripcion,
                   imagen_portada
            FROM cuestionarios
            WHERE estado = 'publico'
            ORDER BY created_at DESC
            """
        )
    
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('explore.html', title='Explorar', items=items, search_query=search_query)


@app.route('/join')
def join_quiz():
    """Página para unirse a un cuestionario usando un PIN."""
    return render_template('join.html', title='Unirse a Cuestionario')


@app.route('/editor')
def editor():
    return render_template('editor.html', title='Editor', creating_quiz=True)


@app.route('/quiz/<int:cuestionario_id>')
def quiz_details(cuestionario_id):
    """Ver detalles de un cuestionario público o del usuario actual"""
    db = bd.obtener_conexion()
    cursor = db.cursor()

    # Obtener cuestionario
    cursor.execute("""
        SELECT c.id, c.user_id, c.titulo, c.descripcion, c.imagen_portada, c.pin, c.estado, c.created_at,
               u.username as creator_username
        FROM cuestionarios c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.id = %s
    """, (cuestionario_id,))

    cuestionario = cursor.fetchone()

    if not cuestionario:
        cursor.close()
        db.close()
        flash('Cuestionario no encontrado', 'error')
        return redirect(url_for('explore'))

    # Verificar permisos:
    # - Si es público, todos pueden verlo
    # - Si es privado, solo el creador puede verlo en esta vista
    if cuestionario['estado'] == 'privado':
        if not g.user or g.user['id'] != cuestionario['user_id']:
            cursor.close()
            db.close()
            flash('Este cuestionario es privado. Usa el PIN para acceder.', 'warning')
            return redirect(url_for('join_quiz'))

    # Obtener preguntas
    cursor.execute("""
        SELECT id, tipo_pregunta, texto_pregunta, orden, tiempo_limite, puntos
        FROM preguntas
        WHERE cuestionario_id = %s
        ORDER BY orden ASC
    """, (cuestionario_id,))

    preguntas = cursor.fetchall()

    # Obtener opciones para cada pregunta
    preguntas_con_opciones = []
    for pregunta in preguntas:
        cursor.execute("""
            SELECT id, texto_opcion, es_correcta, orden
            FROM opciones_respuesta
            WHERE pregunta_id = %s
            ORDER BY orden ASC
        """, (pregunta['id'],))

        opciones = cursor.fetchall()

        preguntas_con_opciones.append({
            'id': pregunta['id'],
            'texto': pregunta['texto_pregunta'],
            'answers': [{'texto': op['texto_opcion'], 'is_correct': bool(op['es_correcta'])} for op in opciones]
        })

    cursor.close()
    db.close()

    # Construir URL completa de la imagen
    if cuestionario['imagen_portada'] and cuestionario['imagen_portada'].strip():
        image_url = url_for('static', filename='uploads/' + cuestionario['imagen_portada'])
    else:
        image_url = url_for('static', filename='img/sinimagenes.jpeg')

    quiz_data = {
        'id': cuestionario['id'],
        'titulo': cuestionario['titulo'],
        'descripcion': cuestionario['descripcion'],
        'image_url': image_url,
        'pin': cuestionario['pin'],
        'creator_username': cuestionario['creator_username'],
        'questions': preguntas_con_opciones
    }

    return render_template('quiz_details.html', title=quiz_data['titulo'], quiz=quiz_data)


@app.route('/editor/<int:cuestionario_id>')
def editor_edit(cuestionario_id):
    """Editar un cuestionario existente"""
    if g.user is None:
        return redirect(url_for('login'))

    db = bd.obtener_conexion()
    response = quiz_controller.obtener_cuestionario(db, cuestionario_id)
    db.close()

    # Si hay error, redirigir a my_quizzes
    if response[1] != 200:
        flash('Cuestionario no encontrado', 'error')
        return redirect(url_for('my_quizzes'))

    cuestionario = response[0].get_json()['cuestionario']
    return render_template('editor.html', title='Editor', creating_quiz=False, cuestionario=cuestionario)


# =====================
#  API de cuestionarios
# =====================
@app.route('/api/cuestionario', methods=['POST'])
def crear_cuestionario():
    """Crear un nuevo cuestionario"""
    if g.user is None:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = {}

        if request.is_json:
            json_data = request.get_json()
            data['titulo'] = json_data.get('titulo')
            data['descripcion'] = json_data.get('descripcion')
            data['preguntas'] = json_data.get('preguntas', [])
            data['pin'] = json_data.get('pin', '')
            data['estado'] = json_data.get('estado', 'publico')
        else:
            data['titulo'] = request.form.get('titulo')
            data['descripcion'] = request.form.get('descripcion')
            data['pin'] = request.form.get('pin', '')
            data['estado'] = request.form.get('estado', 'publico')

            import json
            preguntas_str = request.form.get('preguntas', '[]')
            try:
                data['preguntas'] = json.loads(preguntas_str) if preguntas_str else []
            except Exception:
                data['preguntas'] = []

        db = bd.obtener_conexion()
        response = quiz_controller.crear_cuestionario(db, data, request.files, app.config['UPLOAD_FOLDER'])
        db.close()
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cuestionario/<int:cuestionario_id>', methods=['PUT', 'POST'])
def actualizar_cuestionario(cuestionario_id):
    """Actualizar un cuestionario existente"""
    if g.user is None:
        return jsonify({'error': 'No autorizado'}), 401

    try:
        data = {}

        if request.is_json:
            json_data = request.get_json()
            data['titulo'] = json_data.get('titulo')
            data['descripcion'] = json_data.get('descripcion')
            data['preguntas'] = json_data.get('preguntas', [])
            data['pin'] = json_data.get('pin', '')
            data['estado'] = json_data.get('estado', 'publico')
        else:
            data['titulo'] = request.form.get('titulo')
            data['descripcion'] = request.form.get('descripcion')
            data['pin'] = request.form.get('pin', '')
            data['estado'] = request.form.get('estado', 'publico')

            import json
            preguntas_str = request.form.get('preguntas', '[]')
            try:
                data['preguntas'] = json.loads(preguntas_str) if preguntas_str else []
            except Exception:
                data['preguntas'] = []

        db = bd.obtener_conexion()
        response = quiz_controller.actualizar_cuestionario(
            db, cuestionario_id, data, request.files, app.config['UPLOAD_FOLDER']
        )
        db.close()
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cuestionario/<int:cuestionario_id>', methods=['GET'])
def obtener_cuestionario(cuestionario_id):
    """Obtener un cuestionario con todas sus preguntas"""
    if g.user is None:
        return jsonify({'error': 'No autorizado'}), 401

    db = bd.obtener_conexion()
    response = quiz_controller.obtener_cuestionario(db, cuestionario_id)
    db.close()
    return response


@app.route('/api/cuestionario/<int:cuestionario_id>', methods=['DELETE'])
def eliminar_cuestionario(cuestionario_id):
    """Eliminar un cuestionario"""
    if g.user is None:
        return jsonify({'error': 'No autorizado'}), 401

    db = bd.obtener_conexion()
    response = quiz_controller.eliminar_cuestionario(db, cuestionario_id)
    db.close()
    return response

@app.route('/Contactanos')
def Contactanos():
    return render_template('contact.html')

@app.route('/Nosotros')
def Nosotros():
    return render_template('about_us.html')

@app.route('/Desarrolladores')
def Desarrolladores():
    return render_template('developers.html')

@app.route('/Preguntas_Frecuentes')
def Preguntas_Frecuentes():
    return render_template('faq.html')

@app.route('/Soporte_Tecnico')
def Soporte_Tecnico():
    return render_template('technical_support.html')
# =====================
#  Main
# =====================

@app.route('/delete_account', methods=['POST'])
def delete_account():
    """Eliminar la cuenta del usuario actual"""
    if g.user is None:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401

    user_id = g.user['id']

    try:
        db = bd.obtener_conexion()
        success, message = user_controller.eliminar_usuario(db, user_id)
        db.close()

        if success:
            session.clear()  # cerrar sesión tras eliminar cuenta
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        print("Error al eliminar cuenta:", e)
        return jsonify({'success': False, 'message': 'Error interno al eliminar cuenta'}), 500

@app.route('/recuperar_cuenta')
def recuperar_cuenta():
    return render_template('recuperar_cuenta.html')

@app.route('/verificar_recuperar_cuenta')
def verificar_recuperar_cuenta():
    return render_template('verificar_recuperar_cuenta.html')

@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    if request.method == 'POST':
        nueva = request.form['new-password']
        confirmar = request.form['confirm-password']
        email = session.get('email_verificacion')  # el correo que guardaste tras verificar el código

        if nueva != confirmar:
            return render_template('cambiar_contra.html', mensaje="Las contraseñas no coinciden")

        if email:
            user_controller.actualizar_password_por_email(email, nueva)
            session.pop('email_verificacion', None)  # limpia la sesión
            return redirect(url_for('login'))  # redirige al inicio o login

        return render_template('cambiar_contra.html', mensaje="Sesión inválida o expirada")

    return render_template('cambiar_contra.html')

# === RUTAS PARA GRUPOS ===

@app.route('/grupos')
def grupos():
    """Página principal de gestión de grupos"""
    if not g.user:
        flash('Debes iniciar sesión para acceder a los grupos', 'warning')
        return redirect(url_for('login'))
    
    # Obtener grupos del usuario
    db = bd.obtener_conexion()
    cursor = db.cursor()
    
    # Grupos donde el usuario es miembro
    cursor.execute("""
        SELECT g.id, g.nombre, g.descripcion, g.codigo, g.es_publico, g.created_at,
               CASE WHEN g.admin_id = %s THEN true ELSE false END as es_admin,
               COUNT(gm.user_id) as miembros_count
        FROM grupos g
        LEFT JOIN grupo_miembros gm ON g.id = gm.grupo_id
        WHERE g.id IN (
            SELECT grupo_id FROM grupo_miembros WHERE user_id = %s
        )
        GROUP BY g.id, g.nombre, g.descripcion, g.codigo, g.es_publico, g.created_at, g.admin_id
        ORDER BY g.created_at DESC
    """, (g.user['id'], g.user['id']))
    
    mis_grupos = cursor.fetchall()
    
    # Grupos públicos disponibles (donde el usuario NO es miembro)
    cursor.execute("""
        SELECT g.id, g.nombre, g.descripcion, g.codigo, g.es_publico, g.created_at,
               false as es_admin,
               COUNT(gm.user_id) as miembros_count
        FROM grupos g
        LEFT JOIN grupo_miembros gm ON g.id = gm.grupo_id
        WHERE g.es_publico = true 
        AND g.id NOT IN (
            SELECT grupo_id FROM grupo_miembros WHERE user_id = %s
        )
        GROUP BY g.id, g.nombre, g.descripcion, g.codigo, g.es_publico, g.created_at
        ORDER BY g.created_at DESC
    """, (g.user['id'],))
    
    grupos_publicos = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('grupos.html', 
                         title='Grupos', 
                         grupos=mis_grupos, 
                         grupos_publicos=grupos_publicos)

@app.route('/api/grupos/crear', methods=['POST'])
def api_crear_grupo():
    """API para crear un nuevo grupo"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    descripcion = data.get('descripcion', '').strip()
    es_publico = data.get('es_publico', False)
    
    if not nombre:
        return jsonify({'success': False, 'message': 'El nombre del grupo es requerido'})
    
    # Generar código único de 8 caracteres
    import string
    import random
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Crear grupo
        cursor.execute("""
            INSERT INTO grupos (nombre, descripcion, codigo, es_publico, admin_id, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (nombre, descripcion, codigo, es_publico, g.user['id']))
        
        grupo_id = cursor.lastrowid
        
        # Agregar admin como miembro
        cursor.execute("""
            INSERT INTO grupo_miembros (grupo_id, user_id, joined_at)
            VALUES (%s, %s, NOW())
        """, (grupo_id, g.user['id']))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True, 
            'message': 'Grupo creado exitosamente',
            'grupo_id': grupo_id,
            'codigo': codigo
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al crear grupo: {str(e)}'})

@app.route('/api/grupos/unirse', methods=['POST'])
def api_unirse_grupo():
    """API para unirse a un grupo por código"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    codigo = data.get('codigo', '').strip().upper()
    
    if len(codigo) != 8:
        return jsonify({'success': False, 'message': 'El código debe tener 8 caracteres'})
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Buscar grupo por código
        cursor.execute("SELECT id, nombre FROM grupos WHERE codigo = %s", (codigo,))
        grupo = cursor.fetchone()
        
        if not grupo:
            return jsonify({'success': False, 'message': 'Grupo no encontrado'})
        
        # Verificar si ya es miembro
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (grupo['id'], g.user['id']))
        
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'Ya eres miembro de este grupo'})
        
        # Agregar como miembro
        cursor.execute("""
            INSERT INTO grupo_miembros (grupo_id, user_id, joined_at)
            VALUES (%s, %s, NOW())
        """, (grupo['id'], g.user['id']))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True, 
            'message': f'Te has unido al grupo "{grupo["nombre"]}"'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al unirse al grupo: {str(e)}'})

@app.route('/api/grupos/salir', methods=['POST'])
def api_salir_grupo():
    """API para salir de un grupo"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    grupo_id = data.get('grupo_id')
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Verificar si es miembro
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (grupo_id, g.user['id']))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'No eres miembro de este grupo'})
        
        # Remover del grupo
        cursor.execute("""
            DELETE FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (grupo_id, g.user['id']))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True, 'message': 'Has salido del grupo'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al salir del grupo: {str(e)}'})

@app.route('/api/grupos/cuestionarios')
def api_grupos_cuestionarios():
    """API para obtener cuestionarios disponibles para grupos"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener cuestionarios públicos y del usuario
        cursor.execute("""
            SELECT c.id, c.titulo, c.descripcion, c.pin, c.imagen_portada,
                   COUNT(p.id) as preguntas_count
            FROM cuestionarios c
            LEFT JOIN preguntas p ON c.id = p.cuestionario_id
            WHERE c.estado = 'publico' OR c.user_id = %s
            GROUP BY c.id, c.titulo, c.descripcion, c.pin, c.imagen_portada
            ORDER BY c.created_at DESC
        """, (g.user['id'],))
        
        cuestionarios = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'quizzes': cuestionarios
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al cargar cuestionarios: {str(e)}'})

@app.route('/api/grupos/iniciar-cuestionario', methods=['POST'])
def api_iniciar_cuestionario_grupo():
    """API para iniciar un cuestionario en grupo"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    grupo_id = data.get('grupo_id')
    cuestionario_id = data.get('cuestionario_id')
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Verificar que el usuario es miembro del grupo
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (grupo_id, g.user['id']))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'No eres miembro de este grupo'})
        
        # Generar un session_code único
        import string
        import random
        while True:
            session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            cursor.execute("SELECT id FROM sesiones_grupo WHERE session_code = %s", (session_code,))
            if not cursor.fetchone():
                break

        # Crear sesión de cuestionario en grupo
        cursor.execute("""
            INSERT INTO sesiones_grupo (grupo_id, cuestionario_id, iniciado_por, created_at, session_code)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (grupo_id, cuestionario_id, g.user['id'], session_code))
        
        sesion_id = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'message': 'Cuestionario iniciado en el grupo'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al iniciar cuestionario: {str(e)}'})

@app.route('/grupo/quiz/<int:sesion_id>')
def grupo_quiz(sesion_id):
    """Página para rendir cuestionario en grupo"""
    if not g.user:
        flash('Debes iniciar sesión para participar', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT sg.id, sg.grupo_id, sg.cuestionario_id, sg.estado, sg.session_code,
                   g.nombre as grupo_nombre, c.titulo, c.pin, c.descripcion
            FROM sesiones_grupo sg
            JOIN grupos g ON sg.grupo_id = g.id
            JOIN cuestionarios c ON sg.cuestionario_id = c.id
            WHERE sg.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('grupos'))
        
        # Verificar que el usuario es miembro del grupo
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (sesion['grupo_id'], g.user['id']))
        
        if not cursor.fetchone():
            flash('No eres miembro de este grupo', 'error')
            return redirect(url_for('grupos'))
        
        # Registrar automáticamente al usuario en la sesión si no está ya
        cursor.execute("""
            INSERT INTO usuario_estado_grupo (sesion_id, user_id, esta_listo)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (sesion_id, g.user['id']))
        
        db.commit()
        
        # Obtener SOLO los miembros que se han unido a esta sesión (están en usuario_estado_grupo)
        cursor.execute("""
            SELECT u.id, u.username, ues.esta_listo
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            WHERE ues.sesion_id = %s
        """, (sesion_id,))
        
        miembros = cursor.fetchall()
        
        # Obtener preguntas del cuestionario
        cursor.execute("""
            SELECT p.id, p.texto_pregunta, p.tiempo_limite, p.puntos
            FROM preguntas p
            WHERE p.cuestionario_id = %s
            ORDER BY p.orden ASC
        """, (sesion['cuestionario_id'],))
        
        preguntas = cursor.fetchall()

        # Obtener opciones para cada pregunta
        preguntas_con_opciones = []
        for pregunta in preguntas:
            cursor.execute("""
                SELECT id, texto_opcion, es_correcta
                FROM opciones_respuesta
                WHERE pregunta_id = %s
                ORDER BY orden ASC
            """, (pregunta['id'],))
            opciones = cursor.fetchall()
            preguntas_con_opciones.append({
                'id': pregunta['id'],
                'text': pregunta['texto_pregunta'],
                'time_limit': pregunta['tiempo_limite'],
                'options': [{'id': o['id'], 'text': o['texto_opcion'], 'is_correct': bool(o['es_correcta'])} for o in opciones]
            })
        
        cursor.close()
        db.close()
        
        return render_template('grupo_quiz.html', 
                             sesion_id=sesion_id,
                             session_code=sesion['session_code'],
                             grupo={'nombre': sesion['grupo_nombre']},
                             cuestionario={
                                 'titulo': sesion['titulo'],
                                 'pin': sesion['pin'],
                                 'preguntas_count': len(preguntas)
                             },
                             miembros=miembros,
                             preguntas_json=json.dumps(preguntas_con_opciones))
        
    except Exception as e:
        flash(f'Error al cargar el cuestionario: {str(e)}', 'error')
        return redirect(url_for('grupos'))

@app.route('/api/grupo/unirse-sesion', methods=['POST'])
def api_unirse_sesion_grupo():
    """API para unirse a una sesión de grupo usando el código de sala"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    session_code = data.get('session_code', '').strip().upper()
    
    if not session_code or len(session_code) != 6:
        return jsonify({'success': False, 'message': 'Código de sala inválido'}), 400
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # 1. Buscar la sesión por código
        cursor.execute("""
            SELECT sg.id, sg.grupo_id, sg.estado, g.nombre as grupo_nombre
            FROM sesiones_grupo sg
            JOIN grupos g ON sg.grupo_id = g.id
            WHERE sg.session_code = %s
        """, (session_code,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            cursor.close(); db.close()
            return jsonify({'success': False, 'message': 'Código de sala no encontrado'}), 404
        
        # 2. Verificar que el usuario es miembro del grupo
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (sesion['grupo_id'], g.user['id']))
        
        if not cursor.fetchone():
            cursor.close(); db.close()
            return jsonify({'success': False, 'message': 'No eres miembro de este grupo'}), 403
        
        # 3. Verificar el estado de la sesión
        if sesion['estado'] == 'finalizado':
            cursor.close(); db.close()
            return jsonify({'success': False, 'message': 'Esta sesión ya ha finalizado'}), 400
        
        # 4. Registrar al usuario en la sesión si no está ya
        cursor.execute("""
            INSERT INTO usuario_estado_grupo (sesion_id, user_id, esta_listo)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (sesion['id'], g.user['id']))
        
        db.commit()
        cursor.close(); db.close()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion['id'],
            'grupo_nombre': sesion['grupo_nombre'],
            'message': f'Te has unido a la sala del grupo {sesion["grupo_nombre"]}'
        })
        
    except Exception as e:
        if db:
            try: db.close()
            except: pass
        return jsonify({'success': False, 'message': f'Error al unirse a la sesión: {str(e)}'}), 500

@app.route('/api/grupo/ready', methods=['POST'])
def api_grupo_ready():
    """API para marcar usuario como listo y, si todos los que están en la sala están listos, iniciar la sesión."""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    ready = bool(data.get('ready', False))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # 1) Upsert del estado del usuario en la sesión
        cursor.execute("""
            INSERT INTO usuario_estado_grupo (sesion_id, user_id, esta_listo)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE esta_listo = VALUES(esta_listo)
        """, (sesion_id, g.user['id'], ready))
        
        # 2) Obtener grupo de la sesión
        cursor.execute("SELECT grupo_id FROM sesiones_grupo WHERE id = %s", (sesion_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close(); db.close()
            return jsonify({'success': False, 'message': 'Sesión no encontrada'}), 404
        grupo_id = row['grupo_id']
        
        # 3) CAMBIO CLAVE: Contar usuarios que se UNIERON A LA SALA (están en usuario_estado_grupo)
        # en lugar de contar todos los miembros del grupo
        cursor.execute("""
            SELECT COUNT(*) AS total_en_sala
            FROM usuario_estado_grupo
            WHERE sesion_id = %s
        """, (sesion_id,))
        total_en_sala = cursor.fetchone()['total_en_sala']
        
        # 4) Contar cuántos están listos en esta sesión
        cursor.execute("""
            SELECT COUNT(*) AS listos
            FROM usuario_estado_grupo
            WHERE sesion_id = %s AND esta_listo = 1
        """, (sesion_id,))
        listos = cursor.fetchone()['listos']
        
        # 5) Todos están listos si hay al menos 1 persona en la sala y todos están listos
        all_ready = (total_en_sala > 0 and listos == total_en_sala)
        
        # 6) Si todos listos, pasar a 'en_progreso' y setear started_at
        if all_ready:
            cursor.execute("""
                UPDATE sesiones_grupo
                SET estado = 'en_progreso', started_at = NOW()
                WHERE id = %s
            """, (sesion_id,))
        
        # 7) Obtener la lista actualizada SOLO de usuarios que están en la sala
        cursor.execute("""
            SELECT u.id, u.username, ues.esta_listo as ready
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            WHERE ues.sesion_id = %s
        """, (sesion_id,))
        
        miembros_actualizados = cursor.fetchall()
        
        db.commit()
        cursor.close(); db.close()
        
        return jsonify({'success': True, 'all_ready': all_ready, 'members': miembros_actualizados})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500



@app.route('/grupo/juego/<int:sesion_id>')
def grupo_juego(sesion_id):
    """Página para jugar el cuestionario en grupo (solo cuando está en progreso)"""
    if not g.user:
        flash('Debes iniciar sesión para participar', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT sg.id, sg.grupo_id, sg.cuestionario_id, sg.estado, sg.session_code,
                   g.nombre as grupo_nombre, c.titulo, c.pin
            FROM sesiones_grupo sg
            JOIN grupos g ON sg.grupo_id = g.id
            JOIN cuestionarios c ON sg.cuestionario_id = c.id
            WHERE sg.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('grupos'))
        
        # Verificar que el usuario es miembro del grupo
        cursor.execute("""
            SELECT id FROM grupo_miembros 
            WHERE grupo_id = %s AND user_id = %s
        """, (sesion['grupo_id'], g.user['id']))
        
        if not cursor.fetchone():
            flash('No eres miembro de este grupo', 'error')
            return redirect(url_for('grupos'))
        
        # Verificar que el usuario está en la sesión
        cursor.execute("""
            SELECT id FROM usuario_estado_grupo
            WHERE sesion_id = %s AND user_id = %s
        """, (sesion_id, g.user['id']))
        
        if not cursor.fetchone():
            flash('No estás registrado en esta sesión', 'error')
            return redirect(url_for('grupo_quiz', sesion_id=sesion_id))
        
        # Verificar estado de la sesión
        if sesion['estado'] != 'en_progreso':
            if sesion['estado'] == 'esperando':
                return redirect(url_for('grupo_quiz', sesion_id=sesion_id))
            elif sesion['estado'] == 'finalizado':
                return redirect(url_for('grupo_resultados', sesion_id=sesion_id))
        
        # Obtener preguntas del cuestionario
        cursor.execute("""
            SELECT p.id, p.texto_pregunta, p.tiempo_limite, p.puntos, p.orden
            FROM preguntas p
            WHERE p.cuestionario_id = %s
            ORDER BY p.orden ASC
        """, (sesion['cuestionario_id'],))
        
        preguntas = cursor.fetchall()

        # Obtener opciones para cada pregunta
        preguntas_con_opciones = []
        for pregunta in preguntas:
            cursor.execute("""
                SELECT id, texto_opcion, es_correcta, orden
                FROM opciones_respuesta
                WHERE pregunta_id = %s
                ORDER BY orden ASC
            """, (pregunta['id'],))
            opciones = cursor.fetchall()
            preguntas_con_opciones.append({
                'id': pregunta['id'],
                'text': pregunta['texto_pregunta'],
                'time_limit': pregunta['tiempo_limite'],
                'points': pregunta['puntos'],
                'orden': pregunta['orden'],
                'options': [{'id': o['id'], 'text': o['texto_opcion'], 'is_correct': bool(o['es_correcta'])} for o in opciones]
            })
        
        # Obtener miembros en la sesión
        cursor.execute("""
            SELECT u.id, u.username
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            WHERE ues.sesion_id = %s
        """, (sesion_id,))
        
        miembros = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template('juego_grupo.html', 
                             sesion_id=sesion_id,
                             grupo={'nombre': sesion['grupo_nombre']},
                             cuestionario={'titulo': sesion['titulo']},
                             preguntas_json=json.dumps(preguntas_con_opciones),
                             total_preguntas=len(preguntas),
                             miembros=miembros)
        
    except Exception as e:
        flash(f'Error al cargar el juego: {str(e)}', 'error')
        return redirect(url_for('grupos'))

@app.route('/api/grupo/miembros/<int:sesion_id>')
def api_grupo_miembros(sesion_id):
    """API para obtener la lista actualizada de miembros en una sesión"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener miembros que están en la sesión
        cursor.execute("""
            SELECT u.id, u.username, ues.esta_listo as ready
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            WHERE ues.sesion_id = %s
            ORDER BY ues.created_at ASC
        """, (sesion_id,))
        
        miembros = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'members': miembros
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/grupo/status/<int:sesion_id>')
def api_grupo_status(sesion_id):
    """API para obtener el estado de la sesión"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        cursor.execute("SELECT estado FROM sesiones_grupo WHERE id = %s", (sesion_id,))
        sesion = cursor.fetchone()
        
        if not sesion:
            return jsonify({'success': False, 'message': 'Sesión no encontrada'})
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'status': sesion['estado']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/grupo/answer', methods=['POST'])
def api_grupo_answer():
    """API para enviar respuesta del usuario con cálculo de puntos"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    tiempo_respuesta = data.get('tiempo_respuesta', 0)
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la opción y la pregunta
        cursor.execute("""
            SELECT o.es_correcta, p.puntos, p.tiempo_limite
            FROM opciones_respuesta o
            JOIN preguntas p ON o.pregunta_id = p.id
            WHERE o.id = %s AND o.pregunta_id = %s
        """, (answer_id, question_id))
        
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({'success': False, 'message': 'Opción no encontrada'})
        
        # Calcular puntos (más rápido = más puntos)
        es_correcta = resultado['es_correcta']
        puntos = 0
        if es_correcta:
            puntos_base = resultado['puntos'] or 1000
            tiempo_limite = resultado['tiempo_limite'] or 30
            # Fórmula: puntaje = puntaje_base * (tiempo_restante / tiempo_total)
            tiempo_restante = max(0, tiempo_limite - tiempo_respuesta)
            factor_tiempo = tiempo_restante / tiempo_limite
            puntos = int(puntos_base * factor_tiempo)
        
        # Guardar respuesta
        cursor.execute("""
            INSERT INTO respuestas_grupo (sesion_id, user_id, pregunta_id, opcion_id, es_correcta, puntos, tiempo_respuesta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE opcion_id = %s, es_correcta = %s, puntos = %s, tiempo_respuesta = %s
        """, (sesion_id, g.user['id'], question_id, answer_id, es_correcta, puntos, tiempo_respuesta,
              answer_id, es_correcta, puntos, tiempo_respuesta))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'correct': bool(es_correcta),
            'points': puntos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/grupo/pregunta-estado/<int:sesion_id>/<int:pregunta_id>')
def api_grupo_pregunta_estado(sesion_id, pregunta_id):
    """API para verificar si todos respondieron una pregunta"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Contar total de usuarios en la sesión
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM usuario_estado_grupo
            WHERE sesion_id = %s
        """, (sesion_id,))
        total_usuarios = cursor.fetchone()['total']
        
        # Contar cuántos ya respondieron esta pregunta
        cursor.execute("""
            SELECT COUNT(*) as respondidos
            FROM respuestas_grupo
            WHERE sesion_id = %s AND pregunta_id = %s
        """, (sesion_id, pregunta_id))
        respondidos = cursor.fetchone()['respondidos']
        
        cursor.close()
        db.close()
        
        todos_respondieron = (total_usuarios > 0 and respondidos >= total_usuarios)
        
        return jsonify({
            'success': True,
            'all_answered': todos_respondieron,
            'total': total_usuarios,
            'answered': respondidos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/grupo/finalizar-sesion', methods=['POST'])
def api_finalizar_sesion():
    """API para marcar la sesión como finalizada"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Actualizar estado de la sesión
        cursor.execute("""
            UPDATE sesiones_grupo
            SET estado = 'finalizado', finished_at = NOW()
            WHERE id = %s
        """, (sesion_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/grupo/resultados/<int:sesion_id>')
def grupo_resultados(sesion_id):
    """Página de resultados finales de la sesión de grupo"""
    if not g.user:
        flash('Debes iniciar sesión para ver los resultados', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT sg.id, sg.grupo_id, sg.cuestionario_id,
                   g.nombre as grupo_nombre, c.titulo as cuestionario_titulo
            FROM sesiones_grupo sg
            JOIN grupos g ON sg.grupo_id = g.id
            JOIN cuestionarios c ON sg.cuestionario_id = c.id
            WHERE sg.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('grupos'))
        
        # Obtener el total de preguntas
        cursor.execute("""
            SELECT COUNT(p.id) as total_preguntas
            FROM preguntas p
            WHERE p.cuestionario_id = %s
        """, (sesion['cuestionario_id'],))
        total_preguntas = cursor.fetchone()['total_preguntas']

        # Obtener resultados de todos los participantes
        cursor.execute("""
            SELECT 
                u.id,
                u.username, 
                COALESCE(SUM(rg.puntos), 0) as score,
                COALESCE(SUM(rg.es_correcta), 0) as correct_answers,
                COUNT(DISTINCT rg.pregunta_id) as preguntas_respondidas
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            LEFT JOIN respuestas_grupo rg ON rg.user_id = u.id AND rg.sesion_id = %s
            WHERE ues.sesion_id = %s
            GROUP BY u.id, u.username
            ORDER BY score DESC, correct_answers DESC
        """, (sesion_id, sesion_id))
        resultados = cursor.fetchall()

        cursor.close()
        db.close()
        
        return render_template('grupo_resultados.html', 
                             sesion_id=sesion_id,
                             grupo_nombre=sesion['grupo_nombre'],
                             cuestionario_titulo=sesion['cuestionario_titulo'],
                             resultados=resultados,
                             total_preguntas=total_preguntas)
        
    except Exception as e:
        flash(f'Error al cargar resultados: {str(e)}', 'error')
        return redirect(url_for('grupos'))

@app.route('/api/grupo/results/<int:sesion_id>')
def api_grupo_results(sesion_id):
    """API para obtener resultados del grupo"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener el total de preguntas del cuestionario de esta sesión
        cursor.execute("""
            SELECT COUNT(p.id) as total_preguntas
            FROM sesiones_grupo sg
            JOIN preguntas p ON sg.cuestionario_id = p.cuestionario_id
            WHERE sg.id = %s
        """, (sesion_id,))
        total_preguntas_row = cursor.fetchone()
        total_preguntas = total_preguntas_row['total_preguntas'] if total_preguntas_row else 0

        # Obtener puntuaciones y aciertos de todos los usuarios
        cursor.execute("""
            SELECT 
                u.username, 
                SUM(rg.puntos) as score,
                SUM(rg.es_correcta) as correct_answers
            FROM respuestas_grupo rg
            JOIN users u ON rg.user_id = u.id
            WHERE rg.sesion_id = %s
            GROUP BY u.id, u.username
            ORDER BY score DESC
        """, (sesion_id,))
        resultados = cursor.fetchall()

        # Añadir el total de preguntas a cada resultado
        for r in resultados:
            r['total_questions'] = total_preguntas

        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'results': resultados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/resultados/<pin>')
def resultados_quiz(pin):
    """Página de resultados para una sesión de juego individual."""
    if not g.user:
        flash('Debes iniciar sesión para ver los resultados.', 'warning')
        return redirect(url_for('login'))

    db = None
    game_data = {
        "totalTime": 0,
        "questions": [],
        "participants": []
    }

    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()

        # 1. Obtener el cuestionario por PIN
        cursor.execute("""
            SELECT id, titulo, created_at FROM cuestionarios WHERE pin = %s
        """, (pin,))
        quiz_info = cursor.fetchone()

        if not quiz_info:
            flash('Cuestionario con ese PIN no encontrado.', 'error')
            return redirect(url_for('home'))

        cuestionario_id = quiz_info['id']

        # 2. Obtener todas las preguntas del cuestionario para el JSON
        cursor.execute("""
            SELECT id, texto_pregunta as text, orden
            FROM preguntas
            WHERE cuestionario_id = %s ORDER BY orden
        """, (cuestionario_id,))
        game_data['questions'] = cursor.fetchall()

        # 3. Obtener todas las sesiones de juego para este cuestionario
        cursor.execute("""
            SELECT id, user_id, fecha_inicio, fecha_fin FROM sesiones_juego
            WHERE cuestionario_id = %s AND user_id IS NOT NULL
        """, (cuestionario_id,))
        sesiones = cursor.fetchall()

        if not sesiones:
            flash('Aún no se ha jugado ninguna partida para este cuestionario.', 'info')
            return redirect(url_for('quiz_details', cuestionario_id=cuestionario_id))

        # 4. Procesar los resultados de todas las sesiones
        participants_map = {}
        total_game_duration = 0

        for sesion in sesiones:
            # Calcular duración total del juego
            if sesion.get('fecha_inicio') and sesion.get('fecha_fin'):
                duration = (sesion['fecha_fin'] - sesion['fecha_inicio']).total_seconds()
                total_game_duration = max(total_game_duration, duration)

            # Obtener respuestas de esta sesión
            cursor.execute("""
                SELECT
                    rp.user_id,
                    u.username,
                    rp.pregunta_id,
                    rp.es_correcta,
                    rp.puntos_obtenidos,
                    rp.tiempo_respuesta,
                    op.texto_opcion as choice
                FROM respuestas_participantes rp
                JOIN users u ON rp.user_id = u.id
                LEFT JOIN opciones_respuesta op ON rp.opcion_id = op.id
                WHERE rp.sesion_juego_id = %s
            """, (sesion['id'],))
            respuestas = cursor.fetchall()

            for r in respuestas:
                user_id = r['user_id']
                if user_id not in participants_map:
                    participants_map[user_id] = {
                        "id": user_id,
                        "name": r['username'],
                        "answers": []
                    }
                
                participants_map[user_id]['answers'].append({
                    "questionId": r['pregunta_id'],
                    "correct": bool(r['es_correcta']),
                    "points": r['puntos_obtenidos'],
                    "time": float(r['tiempo_respuesta']) if r['tiempo_respuesta'] is not None else 0,
                    "choice": r['choice'] or "N/A"
                })

        game_data['participants'] = list(participants_map.values())
        game_data['totalTime'] = total_game_duration

        return render_template('resultados_quiz.html',
                               title=f"Resultados de {quiz_info['titulo']}",
                               game_data_json=json.dumps(game_data, default=str))

    except Exception as e:
        flash(f'Error al cargar los resultados: {str(e)}', 'error')
        return redirect(url_for('home'))

# =====================
#  Sesiones Individuales (Sistema similar a grupos)
# =====================

@app.route('/api/individual/iniciar-cuestionario', methods=['POST'])
def api_iniciar_cuestionario_individual():
    """API para iniciar un cuestionario individual con sistema de sala"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    cuestionario_id = data.get('cuestionario_id')
    
    if not cuestionario_id:
        return jsonify({'success': False, 'message': 'ID de cuestionario requerido'}), 400
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Verificar que el cuestionario existe
        cursor.execute("SELECT id, titulo FROM cuestionarios WHERE id = %s", (cuestionario_id,))
        cuestionario = cursor.fetchone()
        
        if not cuestionario:
            return jsonify({'success': False, 'message': 'Cuestionario no encontrado'})
        
        # Generar un session_code único de 6 caracteres
        import string
        import random
        while True:
            session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Verificar que no exista en sesiones_grupo ni sesiones_individual
            cursor.execute("SELECT id FROM sesiones_grupo WHERE session_code = %s", (session_code,))
            if cursor.fetchone():
                continue
            cursor.execute("SELECT id FROM sesiones_individual WHERE session_code = %s", (session_code,))
            if not cursor.fetchone():
                break

        # Crear sesión individual
        cursor.execute("""
            INSERT INTO sesiones_individual (cuestionario_id, iniciado_por, session_code, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (cuestionario_id, g.user['id'], session_code))
        
        sesion_id = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion_id,
            'session_code': session_code,
            'message': 'Sesión creada exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al iniciar cuestionario: {str(e)}'})

@app.route('/individual/quiz/<int:sesion_id>')
def individual_quiz(sesion_id):
    """Página de sala de espera para cuestionario individual"""
    if not g.user:
        flash('Debes iniciar sesión para participar', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT si.id, si.cuestionario_id, si.estado, si.session_code,
                   c.titulo, c.pin, c.descripcion
            FROM sesiones_individual si
            JOIN cuestionarios c ON si.cuestionario_id = c.id
            WHERE si.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('my_quizzes'))
        
        # Si la sesión ya finalizó, redirigir
        if sesion['estado'] == 'finalizado':
            flash('Esta sesión ya ha finalizado', 'info')
            return redirect(url_for('my_quizzes'))
        
        # Registrar automáticamente al usuario en la sesión si no está ya
        cursor.execute("""
            INSERT INTO usuario_estado_individual (sesion_id, user_id, esta_listo)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (sesion_id, g.user['id']))
        
        db.commit()
        
        # Obtener todos los usuarios en la sala
        cursor.execute("""
            SELECT u.id, u.username, uei.esta_listo
            FROM usuario_estado_individual uei
            JOIN users u ON uei.user_id = u.id
            WHERE uei.sesion_id = %s
            ORDER BY uei.created_at ASC
        """, (sesion_id,))
        
        participantes = cursor.fetchall()
        
        # Obtener el número de preguntas
        cursor.execute("""
            SELECT COUNT(*) as count FROM preguntas WHERE cuestionario_id = %s
        """, (sesion['cuestionario_id'],))
        
        preguntas_count = cursor.fetchone()['count']
        
        cursor.close()
        db.close()
        
        cuestionario_info = {
            'titulo': sesion['titulo'],
            'pin': sesion['pin'],
            'descripcion': sesion['descripcion'],
            'preguntas_count': preguntas_count
        }
        
        return render_template('individual_quiz.html',
                             sesion_id=sesion_id,
                             session_code=sesion['session_code'],
                             cuestionario=cuestionario_info,
                             participantes=participantes,
                             user_id=g.user['id'])
        
    except Exception as e:
        flash(f'Error al cargar la sala: {str(e)}', 'error')
        return redirect(url_for('my_quizzes'))

@app.route('/api/individual/unirse-sesion', methods=['POST'])
def api_unirse_sesion_individual():
    """API para unirse a una sesión individual usando el código de sala"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    session_code = data.get('session_code', '').strip().upper()
    
    if len(session_code) != 6:
        return jsonify({'success': False, 'message': 'El código debe tener 6 caracteres'})
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Buscar sesión por código
        cursor.execute("""
            SELECT id, estado FROM sesiones_individual 
            WHERE session_code = %s
        """, (session_code,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            return jsonify({'success': False, 'message': 'Código de sala inválido'})
        
        if sesion['estado'] == 'finalizado':
            return jsonify({'success': False, 'message': 'Esta sesión ya ha finalizado'})
        
        # Registrar al usuario en la sesión
        cursor.execute("""
            INSERT INTO usuario_estado_individual (sesion_id, user_id, esta_listo)
            VALUES (%s, %s, 0)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (sesion['id'], g.user['id']))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'sesion_id': sesion['id'],
            'message': 'Te has unido a la sesión'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al unirse: {str(e)}'})

@app.route('/api/individual/ready', methods=['POST'])
def api_individual_ready():
    """API para marcar al usuario como listo en sesión individual"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Verificar que el usuario está en la sesión
        cursor.execute("""
            SELECT id FROM usuario_estado_individual
            WHERE sesion_id = %s AND user_id = %s
        """, (sesion_id, g.user['id']))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'No estás en esta sesión'})
        
        # Marcar como listo
        cursor.execute("""
            UPDATE usuario_estado_individual
            SET esta_listo = 1
            WHERE sesion_id = %s AND user_id = %s
        """, (sesion_id, g.user['id']))
        
        db.commit()
        
        # Verificar si todos están listos
        cursor.execute("""
            SELECT COUNT(*) AS total_en_sala
            FROM usuario_estado_individual
            WHERE sesion_id = %s
        """, (sesion_id,))
        
        total_en_sala = cursor.fetchone()['total_en_sala']
        
        cursor.execute("""
            SELECT COUNT(*) AS listos
            FROM usuario_estado_individual
            WHERE sesion_id = %s AND esta_listo = 1
        """, (sesion_id,))
        
        listos = cursor.fetchone()['listos']
        
        all_ready = (total_en_sala > 0 and listos == total_en_sala)
        
        if all_ready:
            # Actualizar estado de la sesión a 'en_progreso'
            cursor.execute("""
                UPDATE sesiones_individual
                SET estado = 'en_progreso', started_at = NOW()
                WHERE id = %s
            """, (sesion_id,))
            db.commit()
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'all_ready': all_ready,
            'ready_count': listos,
            'total_count': total_en_sala,
            'message': 'Marcado como listo' if not all_ready else '¡Todos listos! Iniciando...'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/individual/juego/<int:sesion_id>')
def individual_juego(sesion_id):
    """Página para jugar el cuestionario individual (solo cuando está en progreso)"""
    if not g.user:
        flash('Debes iniciar sesión para participar', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT si.id, si.cuestionario_id, si.estado, si.session_code,
                   c.titulo, c.pin
            FROM sesiones_individual si
            JOIN cuestionarios c ON si.cuestionario_id = c.id
            WHERE si.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('my_quizzes'))
        
        # Verificar que el usuario está en la sesión
        cursor.execute("""
            SELECT id FROM usuario_estado_individual
            WHERE sesion_id = %s AND user_id = %s
        """, (sesion_id, g.user['id']))
        
        if not cursor.fetchone():
            flash('No estás registrado en esta sesión', 'error')
            return redirect(url_for('individual_quiz', sesion_id=sesion_id))
        
        # Verificar estado de la sesión
        if sesion['estado'] != 'en_progreso':
            flash('El juego aún no ha comenzado o ya finalizó', 'info')
            return redirect(url_for('individual_quiz', sesion_id=sesion_id))
        
        # Obtener preguntas del cuestionario
        cursor.execute("""
            SELECT id, texto_pregunta, tiempo_limite, puntos, orden
            FROM preguntas
            WHERE cuestionario_id = %s
            ORDER BY orden ASC
        """, (sesion['cuestionario_id'],))
        
        preguntas = cursor.fetchall()
        
        # Obtener opciones para cada pregunta
        preguntas_con_opciones = []
        for pregunta in preguntas:
            cursor.execute("""
                SELECT id, texto_opcion, es_correcta
                FROM opciones_respuesta
                WHERE pregunta_id = %s
                ORDER BY orden ASC
            """, (pregunta['id'],))
            
            opciones = cursor.fetchall()
            
            pregunta_dict = dict(pregunta)
            pregunta_dict['opciones'] = opciones
            preguntas_con_opciones.append(pregunta_dict)
        
        # Obtener participantes en la sala
        cursor.execute("""
            SELECT u.id, u.username
            FROM usuario_estado_individual uei
            JOIN users u ON uei.user_id = u.id
            WHERE uei.sesion_id = %s
        """, (sesion_id,))
        
        participantes = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template('juego_individual.html', 
                             sesion_id=sesion_id,
                             cuestionario={'titulo': sesion['titulo']},
                             preguntas_json=json.dumps(preguntas_con_opciones),
                             total_preguntas=len(preguntas),
                             participantes=participantes)
        
    except Exception as e:
        flash(f'Error al cargar el juego: {str(e)}', 'error')
        return redirect(url_for('my_quizzes'))

@app.route('/api/individual/participantes/<int:sesion_id>')
def api_individual_participantes(sesion_id):
    """API para obtener la lista actualizada de participantes en una sesión"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, uei.esta_listo as ready
            FROM usuario_estado_individual uei
            JOIN users u ON uei.user_id = u.id
            WHERE uei.sesion_id = %s
            ORDER BY uei.created_at ASC
        """, (sesion_id,))
        
        participantes = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'participants': participantes
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/individual/status/<int:sesion_id>')
def api_individual_status(sesion_id):
    """API para obtener el estado de la sesión"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        cursor.execute("SELECT estado FROM sesiones_individual WHERE id = %s", (sesion_id,))
        sesion = cursor.fetchone()
        
        if not sesion:
            return jsonify({'success': False, 'message': 'Sesión no encontrada'})
        
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'status': sesion['estado']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/individual/answer', methods=['POST'])
def api_individual_answer():
    """API para enviar respuesta en sesión individual (igual que grupos)"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    tiempo_respuesta = data.get('tiempo_respuesta', 0)
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la opción y la pregunta
        cursor.execute("""
            SELECT o.es_correcta, p.puntos, p.tiempo_limite
            FROM opciones_respuesta o
            JOIN preguntas p ON o.pregunta_id = p.id
            WHERE o.id = %s AND o.pregunta_id = %s
        """, (answer_id, question_id))
        
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({'success': False, 'message': 'Opción no encontrada'})
        
        # Calcular puntos (fórmula igual que grupos)
        es_correcta = resultado['es_correcta']
        puntos = 0
        if es_correcta:
            puntos_base = resultado['puntos'] or 1000
            tiempo_limite = resultado['tiempo_limite'] or 30
            # Más rápido = más puntos
            tiempo_restante = max(0, tiempo_limite - tiempo_respuesta)
            factor_tiempo = tiempo_restante / tiempo_limite
            puntos = int(puntos_base * factor_tiempo)
        
        # Guardar respuesta en la tabla correcta
        cursor.execute("""
            INSERT INTO respuestas_individual (sesion_id, user_id, pregunta_id, opcion_id, es_correcta, puntos, tiempo_respuesta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE opcion_id = %s, es_correcta = %s, puntos = %s, tiempo_respuesta = %s
        """, (sesion_id, g.user['id'], question_id, answer_id, es_correcta, puntos, tiempo_respuesta,
              answer_id, es_correcta, puntos, tiempo_respuesta))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            'success': True,
            'correct': bool(es_correcta),
            'points': puntos
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/individual/finalizar-sesion', methods=['POST'])
def api_finalizar_sesion_individual():
    """API para marcar sesión individual como finalizada"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    data = request.get_json()
    sesion_id = data.get('sesion_id')
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE sesiones_individual
            SET estado = 'finalizado', finished_at = NOW()
            WHERE id = %s
        """, (sesion_id,))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/individual/resultados/<int:sesion_id>')
def individual_resultados(sesion_id):
    """Página de resultados finales de la sesión individual"""
    if not g.user:
        flash('Debes iniciar sesión para ver los resultados', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT si.id, si.cuestionario_id, c.titulo as cuestionario_titulo
            FROM sesiones_individual si
            JOIN cuestionarios c ON si.cuestionario_id = c.id
            WHERE si.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('my_quizzes'))
        
        # Obtener el total de preguntas
        cursor.execute("""
            SELECT COUNT(p.id) as total_preguntas
            FROM preguntas p
            WHERE p.cuestionario_id = %s
        """, (sesion['cuestionario_id'],))
        total_preguntas = cursor.fetchone()['total_preguntas']

        # Obtener resultados de todos los participantes
        cursor.execute("""
            SELECT 
                u.id,
                u.username, 
                COALESCE(SUM(ri.puntos), 0) as score,
                COALESCE(SUM(ri.es_correcta), 0) as correct_answers,
                COUNT(DISTINCT ri.pregunta_id) as preguntas_respondidas
            FROM usuario_estado_individual uei
            JOIN users u ON uei.user_id = u.id
            LEFT JOIN respuestas_individual ri ON ri.user_id = u.id AND ri.sesion_id = %s
            WHERE uei.sesion_id = %s
            GROUP BY u.id, u.username
            ORDER BY score DESC, correct_answers DESC
        """, (sesion_id, sesion_id))
        resultados = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        return render_template('individual_resultados.html',
                             sesion_id=sesion_id,
                             cuestionario_titulo=sesion['cuestionario_titulo'],
                             total_preguntas=total_preguntas,
                             resultados=resultados)
        
    except Exception as e:
        flash(f'Error al cargar resultados: {str(e)}', 'error')
        return redirect(url_for('my_quizzes'))

# =====================
#  Exportar Resultados a Excel
# =====================

@app.route('/grupo/resultados/<int:sesion_id>/exportar-excel')
def exportar_resultados_grupo_excel(sesion_id):
    """Exportar resultados de grupo a Excel"""
    if not g.user:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT sg.id, sg.grupo_id, sg.cuestionario_id,
                   g.nombre as grupo_nombre, c.titulo as cuestionario_titulo
            FROM sesiones_grupo sg
            JOIN grupos g ON sg.grupo_id = g.id
            JOIN cuestionarios c ON sg.cuestionario_id = c.id
            WHERE sg.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('grupos'))
        
        # Obtener el total de preguntas
        cursor.execute("""
            SELECT COUNT(p.id) as total_preguntas
            FROM preguntas p
            WHERE p.cuestionario_id = %s
        """, (sesion['cuestionario_id'],))
        total_preguntas = cursor.fetchone()['total_preguntas']

        # Obtener resultados de todos los participantes
        cursor.execute("""
            SELECT 
                u.username, 
                COALESCE(SUM(rg.puntos), 0) as score,
                COALESCE(SUM(rg.es_correcta), 0) as correct_answers,
                COUNT(DISTINCT rg.pregunta_id) as preguntas_respondidas
            FROM usuario_estado_grupo ues
            JOIN users u ON ues.user_id = u.id
            LEFT JOIN respuestas_grupo rg ON rg.user_id = u.id AND rg.sesion_id = %s
            WHERE ues.sesion_id = %s
            GROUP BY u.id, u.username
            ORDER BY score DESC, correct_answers DESC
        """, (sesion_id, sesion_id))
        resultados = cursor.fetchall()

        cursor.close()
        db.close()
        
        # Crear libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados"
        
        # Estilos
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Título
        ws.merge_cells('A1:E1')
        title_cell = ws['A1']
        title_cell.value = f"Resultados - {sesion['cuestionario_titulo']}"
        title_cell.font = Font(bold=True, size=16)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.merge_cells('A2:E2')
        subtitle_cell = ws['A2']
        subtitle_cell.value = f"Grupo: {sesion['grupo_nombre']}"
        subtitle_cell.font = Font(size=12)
        subtitle_cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.merge_cells('A3:E3')
        date_cell = ws['A3']
        date_cell.value = f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        date_cell.alignment = Alignment(horizontal='center')
        
        # Headers
        headers = ['Posición', 'Jugador', 'Puntaje', 'Respuestas Correctas', 'Preguntas Respondidas']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=5, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border
        
        # Datos
        for idx, resultado in enumerate(resultados, start=1):
            row = idx + 5
            ws.cell(row=row, column=1, value=idx).border = border
            ws.cell(row=row, column=2, value=resultado['username']).border = border
            ws.cell(row=row, column=3, value=resultado['score']).border = border
            ws.cell(row=row, column=4, value=f"{resultado['correct_answers']}/{total_preguntas}").border = border
            ws.cell(row=row, column=5, value=resultado['preguntas_respondidas']).border = border
            
            # Alineación
            for col in range(1, 6):
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='center', vertical='center')
        
        # Ajustar anchos de columna
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 22
        ws.column_dimensions['E'].width = 25
        
        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"Resultados_{sesion['grupo_nombre']}_{sesion['cuestionario_titulo']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # ✅ SUBIR AUTOMÁTICAMENTE A GOOGLE DRIVE
        output_copy = BytesIO(output.getvalue())  # Copia para Drive
        drive_result = subir_a_google_drive(output_copy, filename)
        
        if drive_result['success']:
            flash(f'✅ Resultados guardados en Google Drive', 'success')
        else:
            flash(f'⚠️ Descarga lista, pero hubo un error al guardar en Drive: {drive_result.get("error", "Error desconocido")}', 'warning')
        
        # Resetear el puntero para la descarga
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error al exportar resultados: {str(e)}', 'error')
        return redirect(url_for('grupo_resultados', sesion_id=sesion_id))

@app.route('/individual/resultados/<int:sesion_id>/exportar-excel')
def exportar_resultados_individual_excel(sesion_id):
    """Exportar resultados individuales a Excel"""
    if not g.user:
        flash('Debes iniciar sesión', 'warning')
        return redirect(url_for('login'))
    
    try:
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        # Obtener información de la sesión
        cursor.execute("""
            SELECT si.id, si.cuestionario_id, c.titulo as cuestionario_titulo
            FROM sesiones_individual si
            JOIN cuestionarios c ON si.cuestionario_id = c.id
            WHERE si.id = %s
        """, (sesion_id,))
        
        sesion = cursor.fetchone()
        
        if not sesion:
            flash('Sesión no encontrada', 'error')
            return redirect(url_for('my_quizzes'))
        
        # Obtener el total de preguntas
        cursor.execute("""
            SELECT COUNT(p.id) as total_preguntas
            FROM preguntas p
            WHERE p.cuestionario_id = %s
        """, (sesion['cuestionario_id'],))
        total_preguntas = cursor.fetchone()['total_preguntas']

        # Obtener resultados de todos los participantes
        cursor.execute("""
            SELECT 
                u.username, 
                COALESCE(SUM(ri.puntos), 0) as score,
                COALESCE(SUM(ri.es_correcta), 0) as correct_answers,
                COUNT(DISTINCT ri.pregunta_id) as preguntas_respondidas
            FROM usuario_estado_individual uei
            JOIN users u ON uei.user_id = u.id
            LEFT JOIN respuestas_individual ri ON ri.user_id = u.id AND ri.sesion_id = %s
            WHERE uei.sesion_id = %s
            GROUP BY u.id, u.username
            ORDER BY score DESC, correct_answers DESC
        """, (sesion_id, sesion_id))
        resultados = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        # Crear libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Resultados"
        
        # Estilos
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Título
        ws.merge_cells('A1:E1')
        title_cell = ws['A1']
        title_cell.value = f"Resultados - {sesion['cuestionario_titulo']}"
        title_cell.font = Font(bold=True, size=16)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.merge_cells('A2:E2')
        subtitle_cell = ws['A2']
        subtitle_cell.value = "Sesión Individual"
        subtitle_cell.font = Font(size=12)
        subtitle_cell.alignment = Alignment(horizontal='center', vertical='center')
        
        ws.merge_cells('A3:E3')
        date_cell = ws['A3']
        date_cell.value = f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        date_cell.alignment = Alignment(horizontal='center')
        
        # Headers
        headers = ['Posición', 'Jugador', 'Puntaje', 'Respuestas Correctas', 'Preguntas Respondidas']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=5, column=col)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border
        
        # Datos
        for idx, resultado in enumerate(resultados, start=1):
            row = idx + 5
            ws.cell(row=row, column=1, value=idx).border = border
            ws.cell(row=row, column=2, value=resultado['username']).border = border
            ws.cell(row=row, column=3, value=resultado['score']).border = border
            ws.cell(row=row, column=4, value=f"{resultado['correct_answers']}/{total_preguntas}").border = border
            ws.cell(row=row, column=5, value=resultado['preguntas_respondidas']).border = border
            
            # Alineación
            for col in range(1, 6):
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='center', vertical='center')
        
        # Ajustar anchos de columna
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 22
        ws.column_dimensions['E'].width = 25
        
        # Guardar en memoria
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"Resultados_{sesion['cuestionario_titulo']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # ✅ SUBIR AUTOMÁTICAMENTE A GOOGLE DRIVE
        output_copy = BytesIO(output.getvalue())  # Copia para Drive
        drive_result = subir_a_google_drive(output_copy, filename)
        
        if drive_result['success']:
            flash(f'✅ Resultados guardados en Google Drive', 'success')
        else:
            flash(f'⚠️ Descarga lista, pero hubo un error al guardar en Drive: {drive_result.get("error", "Error desconocido")}', 'warning')
        
        # Resetear el puntero para la descarga
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error al exportar resultados: {str(e)}', 'error')
        return redirect(url_for('individual_resultados', sesion_id=sesion_id))

if __name__ == '__main__':
    # Ya no es necesario crear la carpeta aquí; se crea arriba en tiempo de carga.
    app.run(debug=True)
