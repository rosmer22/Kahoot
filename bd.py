import pymysql

def obtener_conexion():
    return pymysql.connect(host='localhost',
                                password='',
                                db='robot',
                                user='root',
                                port=3327,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)