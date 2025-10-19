import pymysql

# Conectar a la base de datos
conn = pymysql.connect(
    host='localhost',
    port=3327,
    user='root',
    password='',
    db='robot',
    charset='utf8mb4'
)

cur = conn.cursor()

print('🔄 Actualizando tabla cuestionarios...\n')

try:
    # PASO 1: Modificar la columna para incluir temporalmente todos los valores
    print('Paso 1: Expandiendo el ENUM...')
    cur.execute("""
        ALTER TABLE cuestionarios 
        MODIFY COLUMN estado ENUM('borrador', 'publicado', 'archivado', 'publico', 'privado') 
        DEFAULT 'publico'
    """)
    print('✅ ENUM expandido\n')
    
    # PASO 2: Migrar datos existentes
    print('Paso 2: Migrando datos existentes...')
    cur.execute("UPDATE cuestionarios SET estado = 'publico' WHERE estado IN ('publicado', 'borrador', '')")
    rows_updated = cur.rowcount
    print(f'✅ {rows_updated} registros actualizados a "publico"\n')
    
    cur.execute("UPDATE cuestionarios SET estado = 'privado' WHERE estado = 'archivado'")
    rows_updated = cur.rowcount
    print(f'✅ {rows_updated} registros actualizados a "privado"\n')
    
    # PASO 3: Modificar la columna para tener solo los valores finales
    print('Paso 3: Reduciendo el ENUM a valores finales...')
    cur.execute("""
        ALTER TABLE cuestionarios 
        MODIFY COLUMN estado ENUM('publico', 'privado') 
        DEFAULT 'publico'
    """)
    print('✅ ENUM actualizado a solo "publico" y "privado"\n')
    
    conn.commit()
    
    # Verificar el resultado
    print('📊 Verificando resultados:')
    print('-' * 60)
    cur.execute('SELECT id, titulo, estado, pin FROM cuestionarios')
    results = cur.fetchall()
    
    if results:
        for row in results:
            print(f'ID: {row[0]:3} | Título: {row[1]:30} | Estado: {row[2]:8} | PIN: {row[3]}')
    else:
        print('No hay cuestionarios en la base de datos')
    
    print('-' * 60)
    print(f'\n✅ ¡Actualización completada exitosamente!')
    print(f'   Total de cuestionarios: {len(results)}')
    
except Exception as e:
    conn.rollback()
    print(f'\n❌ Error durante la actualización: {e}')
    raise

finally:
    cur.close()
    conn.close()
