import bd

db = bd.obtener_conexion()
cursor = db.cursor()
cursor.execute('SELECT id, titulo, estado, pin FROM cuestionarios ORDER BY id DESC LIMIT 5')
results = cursor.fetchall()

print("\n=== Estado actual de los cuestionarios ===")
for r in results:
    print(f"ID: {r['id']:3} | Título: {r['titulo']:20} | Estado: {r['estado']:8} | PIN: {r['pin']}")

cursor.close()
db.close()
