#!/usr/bin/env python3
"""
Script para ejecutar la actualización de las tablas con campos de timestamp de pregunta.
Esto permite que el tiempo no se reinicie al recargar la página.
"""
import bd

def ejecutar_update():
    try:
        print("🔧 Conectando a la base de datos...")
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        print("📝 Leyendo script SQL...")
        with open('update_add_pregunta_timestamp.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Dividir por punto y coma y ejecutar cada sentencia
        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"⚙️  Ejecutando sentencia {i}/{len(statements)}...")
                cursor.execute(statement)
                db.commit()
                print(f"   ✅ Sentencia {i} ejecutada correctamente")
        
        cursor.close()
        db.close()
        
        print("\n✅ ¡Actualización completada exitosamente!")
        print("📊 Se agregaron los campos:")
        print("   - pregunta_actual (INT)")
        print("   - pregunta_inicio_timestamp (BIGINT)")
        print("   a las tablas usuario_estado_grupo y usuario_estado_individual")
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar la actualización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    ejecutar_update()

