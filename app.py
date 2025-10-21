from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from controllers import user_controller, quiz_controller, grupo_controller, quiz_grupo_controller
from werkzeug.security import check_password_hash
from werkzeug.exceptions import HTTPException
from flask_mail import Mail, Message
import random
import datetime
import bd
import logging
import os
import re
from pathlib import Path
from bd import obtener_conexion

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'dev-secret-change-me'

# === Config generales (MODIFICADO: usar rutas absolutas) ===
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)

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


@app.route('/explore')
def explore():
    """Explorar cuestionarios públicos (versión que consulta BD)."""
    db = bd.obtener_conexion()
    cursor = db.cursor()
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
    return render_template('explore.html', title='Explorar', items=items)


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
    
    quiz_data = {
        'id': cuestionario['id'],
        'titulo': cuestionario['titulo'],
        'descripcion': cuestionario['descripcion'],
        'image_url': cuestionario['imagen_portada'],
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
    

# app.py
@app.route('/grupos', methods=['GET', 'POST'])
def grupos():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        action = request.form.get('action')
        grupo_id = request.form.get('grupo_id')

        try:
            if action == 'crear':
                nombre = request.form['nombre']
                grupo_id = grupo_controller.crear_grupo(nombre, user_id)
                grupo_controller.unirse_a_grupo(grupo_id, user_id)
                flash('✅ Grupo creado con éxito', 'success')

            elif action == 'unirse' and grupo_id:
                exito = grupo_controller.unirse_a_grupo(grupo_id, user_id)
                if exito:
                    flash('✅ Te has unido al grupo', 'success')
                else:
                    flash('⚠️ Ya eres miembro de este grupo', 'info')

        except Exception as e:
            app.logger.error(f"Error al procesar POST en /grupos: {e}")
            flash(f"Hubo un error: {str(e)}", 'danger')

        return redirect(url_for('grupos'))

    # GET: cargar grupos y miembros
    try:
        grupos_usuario = grupo_controller.obtener_grupos_por_usuario(user_id)

        # Agregar miembros de cada grupo
        for grupo in grupos_usuario:
            grupo['miembros'] = grupo_controller.obtener_miembros_por_grupo(grupo['id'])

    except Exception as e:
        app.logger.error(f"Error al obtener grupos del usuario: {e}")
        grupos_usuario = []
        flash("No se pudieron cargar tus grupos", "danger")

    return render_template('grupos_unificado.html', grupos=grupos_usuario)


# ==============================
# Endpoint para obtener miembros de un grupo
# ==============================
@app.route('/miembros/<int:grupo_id>')
def obtener_miembros(grupo_id):
    try:
        miembros = grupo_controller.obtener_miembros_grupo(grupo_id)
        return render_template('miembros.html', miembros=miembros, grupo_id=grupo_id)
    except Exception as e:
        app.logger.error(f"Error no manejado: {e}")
        flash("Hubo un error al obtener los miembros del grupo", "danger")
        return redirect(url_for('grupos.grupos'))  # Volvemos a la lista de grupos

@app.route('/grupo/<int:grupo_id>/cuestionario/<pin>', methods=['GET', 'POST'])
def rendir_cuestionario_grupo(grupo_id, pin):
    """
    Vista para rendir un cuestionario en grupo usando el PIN del cuestionario (no el ID).
    """
    db = obtener_conexion()
    cursor = db.cursor()

    # 🔹 Buscar el cuestionario por su PIN
    cursor.execute("SELECT id, titulo FROM cuestionarios WHERE pin = %s", (pin,))
    cuestionario = cursor.fetchone()

    if not cuestionario:
        cursor.close()
        db.close()
        flash('❌ Código de cuestionario no válido.', 'error')
        return redirect(url_for('grupos'))

    cuestionario_id = cuestionario['id']

    if request.method == 'POST':
        sesion_id = request.form.get('sesion_id')
        sesion_grupo_id = quiz_grupo_controller.crear_sesion_grupal(grupo_id, sesion_id)

        for key, value in request.form.items():
            if key.startswith('pregunta_'):
                pregunta_id = int(key.split('_')[1])
                opcion_id = int(value)
                quiz_grupo_controller.guardar_respuesta_grupal(
                    sesion_grupo_id, pregunta_id, opcion_id, True, 1
                )

        cursor.close()
        db.close()
        flash('✅ Cuestionario rendido en grupo con éxito', 'success')
        return redirect(url_for('resultado_grupo', grupo_id=grupo_id))

    # 🔹 Obtener preguntas asociadas al cuestionario encontrado
    preguntas = quiz_grupo_controller.obtener_preguntas_por_cuestionario(cuestionario_id)
    cursor.close()
    db.close()

    return render_template(
        'rendir_cuestionario_grupo.html',
        grupo_id=grupo_id,
        cuestionario_pin=pin,
        cuestionario_titulo=cuestionario['titulo'],
        preguntas=preguntas
    )


@app.route('/grupo/<int:grupo_id>/resultado')
def resultado_grupo(grupo_id):
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute("""
        SELECT g.nombre AS nombre_grupo, c.titulo, c.pin
        FROM grupos g
        LEFT JOIN sesiones_grupo sg ON sg.grupo_id = g.id
        LEFT JOIN sesiones_juego sj ON sj.id = sg.sesion_id
        LEFT JOIN cuestionarios c ON c.id = sj.cuestionario_id
        WHERE g.id = %s
        LIMIT 1
    """, (grupo_id,))
    quiz_info = cursor.fetchone()

    # 🔹 Simulación de resultados (puedes reemplazar por query real)
    ranking = [
        {"nombre": "Usuario1", "puntaje_obtenido": 80, "respuestas_correctas": 8, "total_preguntas": 10, "tiempo_total": 90},
        {"nombre": "Usuario2", "puntaje_obtenido": 70, "respuestas_correctas": 7, "total_preguntas": 10, "tiempo_total": 110},
    ]

    data = {
        "grupo_id": grupo_id,
        "nombre_grupo": quiz_info["nombre_grupo"] if quiz_info else "Grupo Desconocido",
        "quiz": quiz_info or {},
        "puntaje_total": sum(r["puntaje_obtenido"] for r in ranking),
        "respuestas_correctas": sum(r["respuestas_correctas"] for r in ranking),
        "total_preguntas": ranking[0]["total_preguntas"] if ranking else 0,
        "tiempo_total": sum(r["tiempo_total"] for r in ranking),
        "ranking": ranking,
    }

    cursor.close()
    db.close()

    return render_template('resultado_grupo.html', **data)


@app.route('/cuestionario/<int:cuestionario_id>/lobby')
def lobby(cuestionario_id):
    """Pantalla donde el profesor espera jugadores (modo individual o grupal)."""
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute("SELECT id, titulo, pin FROM cuestionarios WHERE id=%s", (cuestionario_id,))
    quiz = cursor.fetchone()
    cursor.close()
    db.close()

    if not quiz:
        return "Cuestionario no encontrado", 404

    # modo puede venir desde query ?modo=grupal o ?modo=individual
    modo = request.args.get('modo', 'individual')

    # simulamos PIN desde el cuestionario
    pin = quiz['pin']

    return render_template(
        'lobby.html',
        quiz=quiz,
        modo=modo,
        pin=pin,
        grupo=None  # opcional
    )

@app.route('/api/participantes')
def api_participantes():
    """Devuelve la lista de jugadores conectados al PIN (según pin_sesion de sesiones_juego)."""
    pin = request.args.get('pin')
    if not pin:
        return jsonify({'participantes': []})

    db = obtener_conexion()
    cursor = db.cursor()

    cursor.execute("""
        SELECT p.nombre_participante AS nombre, p.puntaje_total AS puntaje
        FROM participantes p
        INNER JOIN sesiones_juego s ON p.sesion_id = s.id
        WHERE s.pin_sesion = %s
    """, (pin,))
    
    data = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({'participantes': data})


@app.route('/api/iniciar_sesion/<pin>', methods=['POST'])
def api_iniciar_sesion(pin):
    """El profesor inicia el cuestionario (crea registro en sesiones_juego)."""
    db = obtener_conexion()
    cursor = db.cursor()

    # Crear una sesión de juego (usando pin_sesion correcto)
    cursor.execute("""
        INSERT INTO sesiones_juego (pin_sesion, fecha_inicio, estado, cuestionario_id, created_by)
        VALUES (%s, NOW(), 'en_progreso', 
                (SELECT id FROM cuestionarios WHERE pin = %s LIMIT 1),
                %s)
    """, (pin, pin, session.get('user_id', 1)))

    sesion_id = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()

    return jsonify({'success': True, 'sesion_id': sesion_id})


@app.route('/sesion/<pin>/pregunta/<int:num>')
def mostrar_pregunta(pin, num):
    """Carga la pregunta N° num del cuestionario identificado por el pin."""
    db = obtener_conexion()
    cursor = db.cursor()

    # Obtener cuestionario por PIN
    cursor.execute("SELECT id, titulo FROM cuestionarios WHERE pin=%s", (pin,))
    quiz = cursor.fetchone()
    if not quiz:
        return "Cuestionario no encontrado", 404

    # Obtener todas las preguntas del cuestionario
    cursor.execute("""
        SELECT p.id, p.texto_pregunta, p.tiempo_limite
        FROM preguntas p
        WHERE p.cuestionario_id = %s
        ORDER BY p.orden ASC
    """, (quiz['id'],))
    preguntas = cursor.fetchall()

    if num < 1 or num > len(preguntas):
        return redirect(f"/resultado/{pin}")

    pregunta_actual = preguntas[num - 1]
    pregunta_id = pregunta_actual['id']

    # Obtener opciones
    cursor.execute("""
        SELECT id, texto_opcion, es_correcta
        FROM opciones_respuesta
        WHERE pregunta_id=%s
        ORDER BY orden ASC
    """, (pregunta_id,))
    opciones = cursor.fetchall()
    cursor.close()
    db.close()

    # Estructura compatible con tu template
    pregunta_actual['opciones'] = opciones

    return render_template(
        'juego_pregunta.html',
        quiz=quiz,
        preguntas=[pregunta_actual],  # el template ya itera
        pin=pin,
        puntaje_inicial=0
    )

@app.route('/resultado/<pin>')
def resultado_final(pin):
    """Muestra el resumen final del juego."""
    db = obtener_conexion()
    cursor = db.cursor()

    cursor.execute("SELECT id, titulo FROM cuestionarios WHERE pin=%s", (pin,))
    quiz = cursor.fetchone()
    cursor.close()
    db.close()

    # Simulación: más adelante traeremos estos datos reales de la BD
    data_resultado = {
        'quiz': quiz,
        'puntaje_obtenido': 80,
        'puntaje_maximo': 100,
        'respuestas_correctas': 8,
        'total_preguntas': 10,
        'tiempo_total': 120,
        'modo': 'individual',
        'ranking': []
    }

    return render_template('resultado.html', **data_resultado)

@app.route('/cuestionario/<pin>/espera')
def esperar_cuestionario(pin):
    """Vista donde el alumno espera a que el profesor inicie el juego."""
    db = obtener_conexion()
    cursor = db.cursor()
    cursor.execute("SELECT id, titulo, pin FROM cuestionarios WHERE pin=%s", (pin,))
    quiz = cursor.fetchone()
    cursor.close()
    db.close()

    if not quiz:
        flash('❌ Código de participación no válido', 'error')
        return redirect(url_for('join_quiz'))

    return render_template('espera.html', quiz=quiz, pin=pin)








if __name__ == '__main__':
    app.run(debug=True)
