from flask import jsonify, session, g
from werkzeug.utils import secure_filename
import os
import random
import string
import time

def generate_pin():
    """Genera un PIN único de 6 caracteres"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def save_cover_image(file, upload_folder):
    """Guarda la imagen de portada y retorna el nombre del archivo"""
    if not file:
        return None
    
    filename = secure_filename(file.filename)
    # Agregar timestamp para evitar colisiones
    timestamp = str(int(time.time()))
    name, ext = os.path.splitext(filename)
    filename = f"{name}_{timestamp}{ext}"
    
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filename

def crear_cuestionario(db, data, files, upload_folder):
    """Crea un nuevo cuestionario con sus preguntas y opciones"""
    try:
        # Validar que haya un usuario en sesión
        if not g.user:
            return jsonify({'error': 'No autorizado'}), 401
        
        user_id = g.user['id']
        
        # Extraer datos del cuestionario
        titulo = data.get('titulo', '').strip()
        descripcion = data.get('descripcion', '').strip()
        preguntas_data = data.get('preguntas', [])
        pin = data.get('pin', '').strip()  # Obtener PIN del frontend
        
        print(f"DEBUG: PIN recibido del frontend: '{pin}'")  # Debug
        
        # Validaciones
        if not titulo:
            return jsonify({'error': 'El título es obligatorio'}), 400
        
        if not preguntas_data or len(preguntas_data) == 0:
            return jsonify({'error': 'Debe haber al menos una pregunta'}), 400
        
        # Procesar imagen de portada
        imagen_portada = None
        if 'imagen_portada' in files:
            imagen_portada = save_cover_image(files['imagen_portada'], upload_folder)
        
        # Si no se proporciona PIN, generar uno
        if not pin:
            print("DEBUG: PIN vacío, generando uno nuevo")  # Debug
            pin = generate_pin()
        else:
            print(f"DEBUG: Usando PIN del frontend: '{pin}'")  # Debug
        
        cursor = db.cursor()
        
        # Verificar que el PIN no exista (solo si se generó uno nuevo)
        if not data.get('pin'):
            while True:
                cursor.execute("SELECT id FROM cuestionarios WHERE pin = %s", (pin,))
                if not cursor.fetchone():
                    break
                pin = generate_pin()
        
        # Insertar cuestionario
        query_cuestionario = """
            INSERT INTO cuestionarios 
            (user_id, titulo, descripcion, imagen_portada, pin, estado)
            VALUES (%s, %s, %s, %s, %s, 'borrador')
        """
        cursor.execute(query_cuestionario, (
            user_id,
            titulo,
            descripcion if descripcion else None,
            imagen_portada,
            pin
        ))
        cuestionario_id = cursor.lastrowid
        
        # Insertar preguntas
        for orden, pregunta in enumerate(preguntas_data):
            texto_pregunta = pregunta.get('text', '').strip()
            tipo_pregunta = pregunta.get('type', 'multiple')
            tiempo_limite = pregunta.get('time', 30)
            puntos = pregunta.get('points', 1)
            
            if not texto_pregunta:
                continue
            
            # Mapear tipos de pregunta
            tipo_map = {
                'multiple': 'opcion_multiple',
                'simple': 'seleccion_simple',
                'verdadero-falso': 'verdadero_falso'
            }
            tipo_db = tipo_map.get(tipo_pregunta, 'opcion_multiple')
            
            # Insertar pregunta
            query_pregunta = """
                INSERT INTO preguntas 
                (cuestionario_id, tipo_pregunta, texto_pregunta, orden, tiempo_limite, puntos)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_pregunta, (
                cuestionario_id,
                tipo_db,
                texto_pregunta,
                orden,
                tiempo_limite,
                puntos
            ))
            pregunta_id = cursor.lastrowid
            
            # Insertar opciones de respuesta
            answers = pregunta.get('answers', [])
            for orden_opcion, answer in enumerate(answers):
                texto_opcion = answer.get('text', '').strip()
                es_correcta = answer.get('isCorrect', False)
                
                if not texto_opcion:
                    continue
                
                query_opcion = """
                    INSERT INTO opciones_respuesta 
                    (pregunta_id, texto_opcion, es_correcta, orden)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_opcion, (
                    pregunta_id,
                    texto_opcion,
                    es_correcta,
                    orden_opcion
                ))
        
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Cuestionario creado exitosamente',
            'cuestionario_id': cuestionario_id,
            'pin': pin
        }), 201
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': f'Error al crear cuestionario: {str(e)}'}), 500

def actualizar_cuestionario(db, cuestionario_id, data, files, upload_folder):
    """Actualiza un cuestionario existente"""
    try:
        # Validar que haya un usuario en sesión
        if not g.user:
            return jsonify({'error': 'No autorizado'}), 401
        
        user_id = g.user['id']
        cursor = db.cursor()
        
        # Verificar que el cuestionario existe y pertenece al usuario
        cursor.execute(
            "SELECT id, imagen_portada FROM cuestionarios WHERE id = %s AND user_id = %s",
            (cuestionario_id, user_id)
        )
        cuestionario = cursor.fetchone()
        
        if not cuestionario:
            return jsonify({'error': 'Cuestionario no encontrado'}), 404
        
        # Extraer datos
        titulo = data.get('titulo', '').strip()
        descripcion = data.get('descripcion', '').strip()
        preguntas_data = data.get('preguntas', [])
        
        # Validaciones
        if not titulo:
            return jsonify({'error': 'El título es obligatorio'}), 400
        
        if not preguntas_data or len(preguntas_data) == 0:
            return jsonify({'error': 'Debe haber al menos una pregunta'}), 400
        
        # Procesar imagen de portada
        imagen_portada = cuestionario['imagen_portada']
        if 'imagen_portada' in files:
            nueva_imagen = save_cover_image(files['imagen_portada'], upload_folder)
            if nueva_imagen:
                # Eliminar imagen anterior si existe
                if imagen_portada:
                    old_path = os.path.join(upload_folder, imagen_portada)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                imagen_portada = nueva_imagen
        
        # Actualizar cuestionario
        query_update = """
            UPDATE cuestionarios 
            SET titulo = %s, descripcion = %s, imagen_portada = %s
            WHERE id = %s
        """
        cursor.execute(query_update, (
            titulo,
            descripcion if descripcion else None,
            imagen_portada,
            cuestionario_id
        ))
        
        # Eliminar preguntas y opciones antiguas
        cursor.execute("DELETE FROM preguntas WHERE cuestionario_id = %s", (cuestionario_id,))
        
        # Insertar preguntas actualizadas
        for orden, pregunta in enumerate(preguntas_data):
            texto_pregunta = pregunta.get('text', '').strip()
            tipo_pregunta = pregunta.get('type', 'multiple')
            tiempo_limite = pregunta.get('time', 30)
            puntos = pregunta.get('points', 1)
            
            if not texto_pregunta:
                continue
            
            # Mapear tipos de pregunta
            tipo_map = {
                'multiple': 'opcion_multiple',
                'simple': 'seleccion_simple',
                'verdadero-falso': 'verdadero_falso'
            }
            tipo_db = tipo_map.get(tipo_pregunta, 'opcion_multiple')
            
            # Insertar pregunta
            query_pregunta = """
                INSERT INTO preguntas 
                (cuestionario_id, tipo_pregunta, texto_pregunta, orden, tiempo_limite, puntos)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_pregunta, (
                cuestionario_id,
                tipo_db,
                texto_pregunta,
                orden,
                tiempo_limite,
                puntos
            ))
            pregunta_id = cursor.lastrowid
            
            # Insertar opciones de respuesta
            answers = pregunta.get('answers', [])
            for orden_opcion, answer in enumerate(answers):
                texto_opcion = answer.get('text', '').strip()
                es_correcta = answer.get('isCorrect', False)
                
                if not texto_opcion:
                    continue
                
                query_opcion = """
                    INSERT INTO opciones_respuesta 
                    (pregunta_id, texto_opcion, es_correcta, orden)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query_opcion, (
                    pregunta_id,
                    texto_opcion,
                    es_correcta,
                    orden_opcion
                ))
        
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Cuestionario actualizado exitosamente',
            'cuestionario_id': cuestionario_id
        }), 200
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': f'Error al actualizar cuestionario: {str(e)}'}), 500

def obtener_cuestionario(db, cuestionario_id):
    """Obtiene un cuestionario con todas sus preguntas y opciones"""
    try:
        # Validar que haya un usuario en sesión
        if not g.user:
            return jsonify({'error': 'No autorizado'}), 401
        
        user_id = g.user['id']
        cursor = db.cursor()
        
        # Obtener cuestionario
        cursor.execute("""
            SELECT id, titulo, descripcion, imagen_portada, pin, estado, created_at
            FROM cuestionarios 
            WHERE id = %s AND user_id = %s
        """, (cuestionario_id, user_id))
        
        cuestionario = cursor.fetchone()
        
        if not cuestionario:
            return jsonify({'error': 'Cuestionario no encontrado'}), 404
        
        # Obtener preguntas
        cursor.execute("""
            SELECT id, tipo_pregunta, texto_pregunta, imagen_pregunta, orden, tiempo_limite, puntos
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
            
            # Mapear tipos de pregunta de vuelta al frontend
            tipo_map = {
                'opcion_multiple': 'multiple',
                'seleccion_simple': 'simple',
                'verdadero_falso': 'verdadero-falso'
            }
            
            preguntas_con_opciones.append({
                'id': pregunta['id'],
                'text': pregunta['texto_pregunta'],
                'type': tipo_map.get(pregunta['tipo_pregunta'], 'multiple'),
                'time': pregunta['tiempo_limite'],
                'points': pregunta['puntos'],
                'answers': [
                    {
                        'id': op['id'],
                        'text': op['texto_opcion'],
                        'isCorrect': bool(op['es_correcta'])
                    }
                    for op in opciones
                ]
            })
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'cuestionario': {
                'id': cuestionario['id'],
                'titulo': cuestionario['titulo'],
                'descripcion': cuestionario['descripcion'],
                'imagen_portada': cuestionario['imagen_portada'],
                'pin': cuestionario['pin'],
                'estado': cuestionario['estado'],
                'created_at': cuestionario['created_at'].isoformat() if cuestionario['created_at'] else None,
                'preguntas': preguntas_con_opciones
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener cuestionario: {str(e)}'}), 500

def listar_cuestionarios_usuario(db, user_id):
    """Lista todos los cuestionarios creados por un usuario"""
    try:
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                c.id, 
                c.titulo, 
                c.descripcion, 
                c.imagen_portada, 
                c.pin, 
                c.estado, 
                c.created_at,
                COUNT(DISTINCT p.id) as num_preguntas
            FROM cuestionarios c
            LEFT JOIN preguntas p ON c.id = p.cuestionario_id
            WHERE c.user_id = %s
            GROUP BY c.id, c.titulo, c.descripcion, c.imagen_portada, c.pin, c.estado, c.created_at
            ORDER BY c.created_at DESC
        """, (user_id,))
        
        cuestionarios = cursor.fetchall()
        cursor.close()
        
        return cuestionarios
        
    except Exception as e:
        print(f"Error al listar cuestionarios: {str(e)}")
        return []

def eliminar_cuestionario(db, cuestionario_id):
    """Elimina un cuestionario y todas sus relaciones (preguntas, opciones)"""
    try:
        # Validar que haya un usuario en sesión
        if not g.user:
            return jsonify({'error': 'No autorizado'}), 401
        
        user_id = g.user['id']
        cursor = db.cursor()
        
        # Verificar que el cuestionario existe y pertenece al usuario
        cursor.execute(
            "SELECT id, imagen_portada FROM cuestionarios WHERE id = %s AND user_id = %s",
            (cuestionario_id, user_id)
        )
        cuestionario = cursor.fetchone()
        
        if not cuestionario:
            return jsonify({'error': 'Cuestionario no encontrado'}), 404
        
        # Eliminar imagen de portada si existe
        if cuestionario['imagen_portada']:
            import os
            from flask import current_app
            imagen_path = os.path.join(current_app.config['UPLOAD_FOLDER'], cuestionario['imagen_portada'])
            if os.path.exists(imagen_path):
                os.remove(imagen_path)
        
        # Eliminar cuestionario (las preguntas y opciones se eliminan en cascada)
        cursor.execute("DELETE FROM cuestionarios WHERE id = %s", (cuestionario_id,))
        
        db.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Cuestionario eliminado exitosamente'
        }), 200
        
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'error': f'Error al eliminar cuestionario: {str(e)}'}), 500
