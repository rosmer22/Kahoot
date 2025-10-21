import pymysql

def obtener_conexion():
    return pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='robot',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)