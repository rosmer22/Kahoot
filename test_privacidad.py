import bd

# Actualizar algunos cuestionarios para tener estados diferentes
db = bd.obtener_conexion()
cursor = db.cursor()

# Cambiar el cuestionario ID 12 a privado para pruebas
cursor.execute("UPDATE cuestionarios SET estado = 'privado' WHERE id = 12")
db.commit()

# Mostrar el estado actualizado
cursor.execute('SELECT id, titulo, estado, pin FROM cuestionarios ORDER BY id DESC')
results = cursor.fetchall()

print("\n=== Estado actualizado de los cuestionarios ===")
print("(El cuestionario ID 12 'manuel' ahora está en modo PRIVADO)")
print()
for r in results:
    emoji = "🔒" if r['estado'] == 'privado' else "🌐"
    print(f"{emoji} ID: {r['id']:3} | Título: {r['titulo']:20} | Estado: {r['estado']:8} | PIN: {r['pin']}")

cursor.close()
db.close()

print("\n✅ Listo! Ahora puedes:")
print("1. Ir a /explore y verificar que el cuestionario 'manuel' NO aparece")
print("2. Crear un nuevo cuestionario y seleccionar 'Privado' en Configuración")
print("3. Guardar y verificar que se guarda correctamente como privado")
