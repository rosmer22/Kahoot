import pymysql
from contextlib import contextmanager

def obtener_conexion():
    """Obtiene una conexión a la base de datos de PythonAnywhere"""
    return pymysql.connect(
        host='Grupo2dawb.mysql.pythonanywhere-services.com',
        user='Grupo2dawb',
        password='clavegrupo2',  # ¡ADVERTENCIA DE SEGURIDAD!
        db='Grupo2dawb$Kahoot',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False  # Importante para que el rollback funcione
    )

@contextmanager
def obtener_conexion_segura():
    """Context manager que garantiza que la conexión se cierre siempre"""
    conexion = None
    try:
        conexion = obtener_conexion()
        yield conexion
    except Exception as e:
        if conexion:
            try:
                conexion.rollback()  # Deshace cambios si hay error
            except:
                pass  # Ignora errores durante el rollback
        raise e  # Vuelve a lanzar la excepción original
    finally:
        if conexion:
            try:
                conexion.close()  # Cierra la conexión siempre
            except:
                pass  # Ignora errores durante el cierre