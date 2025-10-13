import pymysql

def obtener_conexion():
    return pymysql.connect(host='localhost',
                                port=3327,
                                user='root',
                                password='',
                                db='kahoot',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)