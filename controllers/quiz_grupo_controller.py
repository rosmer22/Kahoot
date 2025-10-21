from bd import obtener_conexion

def crear_sesion_grupal(grupo_id, sesion_id):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sesiones_grupo (grupo_id, sesion_id)
                VALUES (%s, %s)
            """, (grupo_id, sesion_id))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()


def obtener_preguntas_por_cuestionario(cuestionario_id):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.texto_pregunta, o.id AS opcion_id, o.texto_opcion
                FROM preguntas p
                JOIN opciones_respuesta o ON o.pregunta_id = p.id
                WHERE p.cuestionario_id = %s
                ORDER BY p.orden, o.orden
            """, (cuestionario_id,))
            rows = cursor.fetchall()
            preguntas = {}
            for r in rows:
                pid = r['id']
                if pid not in preguntas:
                    preguntas[pid] = {'texto': r['texto_pregunta'], 'opciones': []}
                preguntas[pid]['opciones'].append({'id': r['opcion_id'], 'texto': r['texto_opcion']})
            return preguntas
    finally:
        conn.close()


def guardar_respuesta_grupal(sesion_grupo_id, pregunta_id, opcion_seleccionada_id, es_correcta, puntos):
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO respuestas_grupo (sesion_grupo_id, pregunta_id, opcion_seleccionada_id, es_correcta, puntos_obtenidos)
                VALUES (%s, %s, %s, %s, %s)
            """, (sesion_grupo_id, pregunta_id, opcion_seleccionada_id, es_correcta, puntos))
            conn.commit()
    finally:
        conn.close()
