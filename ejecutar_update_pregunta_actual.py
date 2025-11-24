#!/usr/bin/env python3
"""
Script para ejecutar el update de pregunta_actual en la base de datos
"""

import bd
import sys

def ejecutar_update():
    try:
        print("🔄 Conectando a la base de datos...")
        db = bd.obtener_conexion()
        cursor = db.cursor()
        
        print("📝 Leyendo script SQL...")
        with open('update_pregunta_actual.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar cada statement por separado
        statements = sql_script.split(';')
        
        for i, statement in enumerate(statements, 1):
            statement = statement.strip()
            if statement:
                print(f"⚙️ Ejecutando statement {i}...")
                try:
                    cursor.execute(statement)
                    db.commit()
                    print(f"   ✅ Statement {i} ejecutado correctamente")
                except Exception as e:
                    print(f"   ⚠️ Statement {i}: {str(e)}")
                    # Continuar con el siguiente statement
                    continue
        
        print("\n✅ Script ejecutado exitosamente!")
        print("📊 Verifica que las columnas pregunta_actual existan en:")
        print("   - usuario_estado_grupo")
        print("   - usuario_estado_individual")
        
        cursor.close()
        db.close()
        
        return True
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo update_pregunta_actual.sql")
        print("   Asegúrate de que el archivo esté en el mismo directorio.")
        return False
    except Exception as e:
        print(f"❌ Error al ejecutar el script: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("  ACTUALIZACIÓN DE TABLA - PREGUNTA ACTUAL")
    print("="*60)
    print()
    
    resultado = ejecutar_update()
    
    if resultado:
        print("\n✨ Actualización completada. Puedes probar la sincronización ahora.")
        sys.exit(0)
    else:
        print("\n❌ La actualización falló. Revisa los errores arriba.")
        sys.exit(1)

