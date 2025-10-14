from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from controllers import user_controller, quiz_controller
from werkzeug.security import check_password_hash
import bd
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'dev-secret-change-me'  # replace in production

# DB Config
app.config['UPLOAD_FOLDER'] = 'static/uploads'

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

@app.route('/')
def home():
    return render_template('home.html', title='RoBot')

@app.route('/login', methods=['GET','POST'])
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
            session['user'] = {'username': user['username'], 'email': user['email'], 'role': user['role']}
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

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if user_controller.obtener_usuario_por_username(username):
            flash('El nombre de usuario ya existe', 'error')
        elif user_controller.obtener_usuario_por_email(email):
            flash('El correo electrónico ya está en uso', 'error')
        else:
            user_controller.insertar_usuario(username, email, password)
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Registrarme')

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
    # Obtener cuestionarios públicos de la base de datos
    db = bd.obtener_conexion()
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT id, titulo, pin, descripcion, imagen_portada 
        FROM cuestionarios 
        WHERE estado = 'publico'
        ORDER BY created_at DESC
    """)
    
    items = cursor.fetchall()
    cursor.close()
    db.close()
    
    return render_template('explore.html', title='Explorar', items=items)

@app.route('/join')
def join_quiz():
    """Página para unirse a un cuestionario usando un PIN"""
    return render_template('join.html', title='Unirse a Cuestionario')

@app.route('/editor')
def editor():
    return render_template('editor.html', title='Editor', creating_quiz=True)

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

@app.route('/api/cuestionario', methods=['POST'])
def crear_cuestionario():
    """Crear un nuevo cuestionario"""
    if g.user is None:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Obtener datos del formulario
        data = {}
        
        print("DEBUG app.py: Content-Type:", request.content_type)  # Debug
        print("DEBUG app.py: is_json:", request.is_json)  # Debug
        
        # Si los datos vienen como JSON (desde JavaScript)
        if request.is_json:
            json_data = request.get_json()
            data['titulo'] = json_data.get('titulo')
            data['descripcion'] = json_data.get('descripcion')
            data['preguntas'] = json_data.get('preguntas', [])
            data['pin'] = json_data.get('pin', '')
            print(f"DEBUG app.py: PIN desde JSON: '{data['pin']}'")  # Debug
        else:
            # Si vienen como FormData
            data['titulo'] = request.form.get('titulo')
            data['descripcion'] = request.form.get('descripcion')
            data['pin'] = request.form.get('pin', '')
            print(f"DEBUG app.py: PIN desde FormData: '{data['pin']}'")  # Debug
            
            # Parsear preguntas si vienen como string JSON
            import json
            preguntas_str = request.form.get('preguntas', '[]')
            try:
                data['preguntas'] = json.loads(preguntas_str) if preguntas_str else []
            except:
                data['preguntas'] = []
        
        print(f"DEBUG app.py: Data completa: {data.keys()}")  # Debug
        
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
        # Obtener datos
        data = {}
        
        # Si los datos vienen como JSON
        if request.is_json:
            json_data = request.get_json()
            data['titulo'] = json_data.get('titulo')
            data['descripcion'] = json_data.get('descripcion')
            data['preguntas'] = json_data.get('preguntas', [])
            data['pin'] = json_data.get('pin', '')
        else:
            # Si vienen como FormData
            data['titulo'] = request.form.get('titulo')
            data['descripcion'] = request.form.get('descripcion')
            data['pin'] = request.form.get('pin', '')
            
            # Parsear preguntas si vienen como string JSON
            import json
            preguntas_str = request.form.get('preguntas', '[]')
            try:
                data['preguntas'] = json.loads(preguntas_str) if preguntas_str else []
            except:
                data['preguntas'] = []
        
        db = bd.obtener_conexion()
        response = quiz_controller.actualizar_cuestionario(db, cuestionario_id, data, request.files, app.config['UPLOAD_FOLDER'])
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

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
