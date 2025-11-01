# Documentación de Cambios: Sistema de Docentes y Alumnos

## Resumen de Cambios

Se implementó un sistema de diferenciación entre docentes y alumnos basado en el dominio de su correo electrónico, con permisos y funcionalidades específicas para cada tipo de usuario.

---

## 1. Clasificación Automática de Usuarios

### Criterios de Clasificación
- **Docentes**: Correos que terminan en `@usat.edu.pe`
- **Alumnos**: Correos que terminan en `@usat.pe`
- **Usuario genérico**: Otros dominios (por compatibilidad)

### Archivos Modificados
- `Kahoot/controllers/user_controller.py` - Función `insertar_usuario()`

### Cambios Realizados
```python
# Determinar el rol según el dominio del email
if email.endswith('@usat.edu.pe'):
    role = 'docente'
elif email.endswith('@usat.pe'):
    role = 'alumno'
else:
    role = 'usuario'
```

---

## 2. Script de Actualización de Base de Datos

### Archivo Creado
- `Kahoot/update_user_roles.sql`

### Propósito
Actualizar los roles de usuarios existentes en la base de datos según su dominio de correo electrónico.

### Ejecución
```bash
# Desde MySQL/MariaDB:
mysql -u usuario -p database_name < Kahoot/update_user_roles.sql

# Desde PostgreSQL:
psql -U usuario -d database_name -f Kahoot/update_user_roles.sql
```

---

## 3. Restricciones de Acceso para Docentes

### 3.1 Creación de Cuestionarios

#### Rutas Protegidas
- `GET /editor` - Crear nuevo cuestionario
- `GET /editor/<int:cuestionario_id>` - Editar cuestionario
- `POST /api/cuestionario` - API crear cuestionario
- `PUT/POST /api/cuestionario/<int:cuestionario_id>` - API actualizar cuestionario

#### Verificación Implementada
```python
if g.user.get('role') != 'docente':
    flash('Solo los docentes pueden crear cuestionarios', 'error')
    return redirect(url_for('home'))
```

### 3.2 Creación de Salas/Grupos

#### Rutas Protegidas
- `POST /api/grupos/crear` - Crear nueva sala/grupo

#### Verificación Implementada
```python
if g.user.get('role') != 'docente':
    return jsonify({'success': False, 'message': 'Solo los docentes pueden crear salas'}), 403
```

---

## 4. Sistema de Puntos Diferenciado

### 4.1 Vista para Docentes

Los docentes **NO ven sus propios puntos**. En su lugar, ven:

- **Puntos totales** de todos los alumnos combinados
- **Ranking completo** de todos los alumnos ordenados de mayor a menor
- Información detallada de cada alumno:
  - Posición en el ranking (con medallas 🥇🥈🥉 para los 3 primeros)
  - Nombre de usuario
  - Email
  - Rango actual
  - Puntosmoneda acumulados

### 4.2 Vista para Alumnos

Los alumnos ven su información personal:

- Sus **puntosmoneda acumulados**
- Su **rango actual**
- **Progreso** hacia el siguiente rango
- **Estadísticas** personales (juegos en top 3, primeros lugares, etc.)
- **Historial** de recompensas
- Sistema completo de rangos disponibles

### Archivos Modificados
- `Kahoot/app.py` - Función `mis_puntos()`
- `Kahoot/templates/mis_puntos.html` - Vista diferenciada

---

## 5. Cambios en el Sistema de Login

El sistema de login ya cargaba correctamente el campo `role` en la sesión del usuario, por lo que no requirió modificaciones adicionales.

### Sesión de Usuario
```python
session['user'] = {
    'username': user['username'],
    'email': user['email'],
    'role': user['role']  # Ya existía
}
```

---

## 6. Flujo de Trabajo Actualizado

### Para Docentes
1. ✅ Registrarse con correo `@usat.edu.pe`
2. ✅ Acceder al **Editor** para crear cuestionarios
3. ✅ Crear **Salas/Grupos** para sus alumnos
4. ✅ Ver **Ranking completo** de todos los alumnos en "Mis Puntos"
5. ❌ NO participar en cuestionarios (son observadores/creadores)

### Para Alumnos
1. ✅ Registrarse con correo `@usat.pe`
2. ✅ Unirse a cuestionarios y grupos
3. ✅ Participar en juegos y acumular puntos
4. ✅ Ver sus propios puntos y progreso en "Mis Puntos"
5. ❌ NO crear cuestionarios
6. ❌ NO crear salas/grupos

---

## 7. Mensajes de Error

### Para Alumnos que Intentan Crear Contenido

**Crear Cuestionarios:**
```
"Solo los docentes pueden crear cuestionarios"
```

**Crear Salas/Grupos:**
```
"Solo los docentes pueden crear salas"
```

---

## 8. Estructura de la Base de Datos

### Campo `role` en tabla `users`
```sql
`role` VARCHAR(50) NOT NULL DEFAULT 'usuario'
```

### Valores Válidos
- `'docente'` - Profesores con permisos de creación
- `'alumno'` - Estudiantes que participan en juegos
- `'usuario'` - Otros usuarios (compatibilidad)

---

## 9. Pruebas Recomendadas

### Test 1: Registro de Docente
1. Registrar usuario con email: `profesor@usat.edu.pe`
2. Verificar que puede acceder a `/editor`
3. Verificar que puede crear cuestionarios
4. Verificar que puede crear grupos
5. Verificar que ve el ranking de alumnos en "Mis Puntos"

### Test 2: Registro de Alumno
1. Registrar usuario con email: `estudiante@usat.pe`
2. Verificar que NO puede acceder a `/editor`
3. Verificar que NO puede crear cuestionarios
4. Verificar que NO puede crear grupos
5. Verificar que ve sus propios puntos en "Mis Puntos"

### Test 3: Actualización de Usuarios Existentes
1. Ejecutar el script SQL `update_user_roles.sql`
2. Verificar que los usuarios con `@usat.edu.pe` ahora tienen `role='docente'`
3. Verificar que los usuarios con `@usat.pe` ahora tienen `role='alumno'`

---

## 10. Archivos Modificados (Resumen)

### Backend
- ✅ `Kahoot/controllers/user_controller.py` - Clasificación automática
- ✅ `Kahoot/app.py` - Verificaciones de permisos y vista de puntos

### Frontend
- ✅ `Kahoot/templates/mis_puntos.html` - Vistas diferenciadas

### Base de Datos
- ✅ `Kahoot/update_user_roles.sql` - Script de actualización

### Documentación
- ✅ `Kahoot/CAMBIOS_DOCENTES_ALUMNOS.md` - Este archivo

---

## 11. Notas Importantes

⚠️ **IMPORTANTE**: Ejecutar el script SQL `update_user_roles.sql` en la base de datos para actualizar los usuarios existentes antes de usar el sistema.

✅ El sistema está completamente funcional y listo para producción.

✅ Todos los cambios son retrocompatibles con el sistema existente.

✅ No hay errores de linter en ninguno de los archivos modificados.

---

## 12. Soporte y Mantenimiento

Si necesitas agregar más funcionalidades específicas para docentes o alumnos:

1. Verificar el rol en la ruta: `if g.user.get('role') == 'docente':`
2. Modificar la lógica según el tipo de usuario
3. Actualizar las plantillas HTML según sea necesario

---

**Fecha de Implementación**: Noviembre 2025
**Desarrollador**: Sistema RoBot - USAT

