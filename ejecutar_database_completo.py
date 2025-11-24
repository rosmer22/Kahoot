"""
Script para ejecutar database_completo.sql en tu base de datos
"""
import pymysql
from pathlib import Path

# ====== CONFIGURACIÓN ======
# MODIFICA ESTOS VALORES CON TUS CREDENCIALES
DB_CONFIG = {
    'host': 'localhost',  # o tu host de base de datos
    'user': 'tu_usuario',  # tu usuario de MySQL
    'password': 'tu_contraseña',  # tu contraseña
    'database': 'nombre_de_tu_bd',  # nombre de tu base de datos
    'charset': 'utf8mb4'
}

def ejecutar_script_sql():
    """Ejecuta el script SQL completo"""
    
    # Leer el archivo SQL
    sql_file = Path(__file__).parent / 'database_completo.sql'
    
    if not sql_file.exists():
        print(f"❌ ERROR: No se encuentra el archivo {sql_file}")
        return False
    
    print(f"📂 Leyendo archivo: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Separar por comandos (cada comando termina con ;)
    # Nota: Este es un enfoque simple, puede necesitar ajustes para scripts complejos
    comandos = []
    comando_actual = []
    
    for linea in sql_content.split('\n'):
        linea = linea.strip()
        
        # Saltar comentarios y líneas vacías
        if linea.startswith('--') or linea.startswith('/*') or linea.startswith('*') or not linea:
            continue
        
        comando_actual.append(linea)
        
        # Si termina con ;, es el final del comando
        if linea.endswith(';'):
            comandos.append(' '.join(comando_actual))
            comando_actual = []
    
    print(f"📊 Se encontraron {len(comandos)} comandos SQL")
    
    # Conectar a la base de datos
    try:
        print(f"\n🔌 Conectando a la base de datos...")
        conexion = pymysql.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        print(f"✅ Conexión exitosa\n")
        
        # Ejecutar cada comando
        exitosos = 0
        errores = 0
        
        for i, comando in enumerate(comandos, 1):
            # Mostrar progreso cada 10 comandos
            if i % 10 == 0:
                print(f"⏳ Ejecutando comando {i}/{len(comandos)}...")
            
            try:
                cursor.execute(comando)
                exitosos += 1
            except Exception as e:
                errores += 1
                # Solo mostrar primeros 100 caracteres del comando con error
                cmd_preview = comando[:100] + '...' if len(comando) > 100 else comando
                print(f"\n⚠️ Error en comando {i}: {str(e)}")
                print(f"   Comando: {cmd_preview}\n")
        
        # Confirmar cambios
        conexion.commit()
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DE EJECUCIÓN")
        print("="*60)
        print(f"✅ Comandos exitosos: {exitosos}")
        print(f"❌ Comandos con error: {errores}")
        print(f"📊 Total: {len(comandos)}")
        
        if errores == 0:
            print("\n🎉 ¡SCRIPT EJECUTADO COMPLETAMENTE!")
        else:
            print(f"\n⚠️ Hubo {errores} errores. Revisa los mensajes arriba.")
        
        # Verificar tablas creadas
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        
        print(f"\n📋 Tablas en la base de datos ({len(tablas)}):")
        for tabla in tablas:
            print(f"   - {tabla[0]}")
        
        cursor.close()
        conexion.close()
        
        return errores == 0
        
    except pymysql.Error as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
        print("\n🔧 Verifica:")
        print("   - Host correcto")
        print("   - Usuario y contraseña correctos")
        print("   - Nombre de base de datos correcto")
        print("   - Que el servidor MySQL esté corriendo")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🗄️  EJECUTOR DE SCRIPT DATABASE_COMPLETO.SQL")
    print("="*60)
    print()
    print("⚠️  IMPORTANTE: Asegúrate de haber hecho un BACKUP primero")
    print()
    
    respuesta = input("¿Has hecho un backup de tu base de datos? (si/no): ").lower()
    
    if respuesta != 'si' and respuesta != 's':
        print("\n❌ Por favor, haz un backup primero antes de continuar.")
        print("   Ejecuta: mysqldump -u usuario -p nombre_bd > backup.sql")
        exit()
    
    print("\n🚀 Iniciando ejecución...\n")
    
    exito = ejecutar_script_sql()
    
    if exito:
        print("\n✅ Base de datos actualizada correctamente")
    else:
        print("\n⚠️ Hubo problemas durante la ejecución")
        print("   Si necesitas restaurar el backup:")
        print("   mysql -u usuario -p nombre_bd < backup.sql")

