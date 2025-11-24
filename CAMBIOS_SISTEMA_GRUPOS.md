# 📋 Cambios en el Sistema de Grupos - Implementación de Código de Sala

## 🎯 Objetivo

Implementar un sistema donde:
1. Al crear un juego en grupo, se genera un **código de sala** de 6 caracteres
2. Otros usuarios pueden **unirse usando el botón "Unirse"** del header ingresando el código
3. **Solo los miembros del grupo** pueden unirse a la sesión
4. El juego **inicia cuando todos los que están en la sala estén listos** (no importa si son todos los del grupo o solo algunos)

---

## 🔧 Cambios Realizados

### 1. **templates/join.html** - Página de Unirse

#### Modificaciones:
- **Actualizado el título**: "Unirse a un Cuestionario o Sala"
- **Cambiado el placeholder** del input: "PIN o Código de Sala"
- **Aumentado maxlength** a 10 caracteres para aceptar diferentes formatos
- **Implementada lógica de detección automática**:
  - Si el código tiene **6 caracteres**: se intenta unir a sesión de grupo
  - Si tiene otra longitud: se trata como PIN de cuestionario individual

#### Código JavaScript nuevo:
```javascript
async function joinGroupSession(sessionCode, errorBox) {
  try {
    const response = await fetch('/api/grupo/unirse-sesion', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_code: sessionCode })
    });

    const result = await response.json();

    if (result.success) {
      window.location.href = `/grupo/quiz/${result.sesion_id}`;
    } else {
      errorBox.textContent = result.message || 'Código de sala inválido';
      errorBox.classList.remove("hidden");
    }
  } catch (error) {
    errorBox.textContent = 'Error de conexión. Intenta nuevamente.';
    errorBox.classList.remove("hidden");
  }
}
```

**Ubicación**: Líneas 173-219

---

### 2. **app.py** - Nuevo Endpoint para Unirse a Sesión

#### Nuevo Endpoint: `/api/grupo/unirse-sesion`

**Ubicación**: Líneas 1355-1421

**Funcionalidad**:
1. ✅ Valida que el código de sala tenga 6 caracteres
2. ✅ Busca la sesión por `session_code`
3. ✅ Verifica que el usuario sea miembro del grupo
4. ✅ Verifica que la sesión no esté finalizada
5. ✅ Registra al usuario en `usuario_estado_grupo` (sin duplicados)
6. ✅ Retorna el `sesion_id` para redirigir al usuario

**Validaciones de Seguridad**:
- Solo usuarios autenticados pueden unirse
- Solo miembros del grupo tienen acceso
- No se puede unir a sesiones finalizadas

```python
@app.route('/api/grupo/unirse-sesion', methods=['POST'])
def api_unirse_sesion_grupo():
    """API para unirse a una sesión de grupo usando el código de sala"""
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    # ... validaciones y lógica ...
```

---

### 3. **app.py** - Modificación de la Lógica "Ready"

#### Endpoint Modificado: `/api/grupo/ready`

**Ubicación**: Líneas 1423-1496

**Cambios Clave**:

**❌ ANTES**: Contaba todos los miembros del grupo
```sql
SELECT COUNT(*) AS total FROM grupo_miembros WHERE grupo_id = %s
```

**✅ AHORA**: Cuenta solo los usuarios que están en la sala
```sql
SELECT COUNT(*) AS total_en_sala
FROM usuario_estado_grupo
WHERE sesion_id = %s
```

**Impacto**:
- El juego **inicia cuando todos los que están EN LA SALA estén listos**
- No espera a todos los miembros del grupo
- Permite que grupos grandes jueguen con solo algunos miembros

**Nueva lógica de verificación**:
```python
# Todos están listos si hay al menos 1 persona en la sala y todos están listos
all_ready = (total_en_sala > 0 and listos == total_en_sala)
```

---

### 4. **app.py** - Ruta `/grupo/quiz/<sesion_id>`

#### Modificaciones:
**Ubicación**: Líneas 1262-1362

**Cambios**:
1. **Registro automático al entrar**: El usuario se registra automáticamente en `usuario_estado_grupo` al acceder
2. **Consulta modificada**: Solo muestra usuarios que están registrados en la sesión
3. **Se obtiene el `session_code`** para mostrarlo en la página

```python
# Registrar automáticamente al usuario en la sesión si no está ya
cursor.execute("""
    INSERT INTO usuario_estado_grupo (sesion_id, user_id, esta_listo)
    VALUES (%s, %s, 0)
    ON DUPLICATE KEY UPDATE user_id = user_id
""", (sesion_id, g.user['id']))

# Obtener SOLO los miembros que se han unido a esta sesión
cursor.execute("""
    SELECT u.id, u.username, ues.esta_listo
    FROM usuario_estado_grupo ues
    JOIN users u ON ues.user_id = u.id
    WHERE ues.sesion_id = %s
""", (sesion_id,))
```

---

### 5. **templates/grupo_quiz.html** - Visualización del Código

#### Nuevos Elementos UI:
**Ubicación**: Líneas 17-27

**Características**:
- 🎨 **Display visual atractivo** con gradiente morado
- 📋 **Botón para copiar** el código al portapapeles
- ℹ️ **Mensaje informativo** para compartir el código
- ✨ **Feedback visual** al copiar (cambio de ícono y color)

```html
<div class="session-code-display">
    <div class="code-label">Código de Sala:</div>
    <div class="code-value">{{ session_code }}</div>
    <button class="btn-copy-code" onclick="copySessionCode('{{ session_code }}')" title="Copiar código">
        <!-- SVG icon -->
    </button>
</div>
<p class="session-info">Comparte este código con los miembros del grupo para que se unan</p>
```

**JavaScript para copiar**:
```javascript
function copySessionCode(code) {
    navigator.clipboard.writeText(code).then(() => {
        // Cambiar ícono a checkmark
        // Cambiar color a verde
        // Revertir después de 2 segundos
    });
}
```

**Ubicación función JS**: Líneas 523-543

---

### 6. **static/css/grupo_quiz.css** - Estilos para Código de Sesión

#### Nuevos Estilos:
**Ubicación**: Líneas 64-112

**Elementos estilizados**:
- `.session-code-display`: Contenedor con gradiente morado
- `.code-label`: Etiqueta "Código de Sala"
- `.code-value`: Código en fuente monospace, grande y con espaciado
- `.btn-copy-code`: Botón de copiar con efectos hover
- `.session-info`: Texto informativo

**Características visuales**:
```css
.session-code-display {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: var(--radius-lg);
    color: white;
}

.code-value {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 0.2em;
    font-family: 'Courier New', monospace;
}
```

---

### 7. **Cambio de Títulos**

En `grupo_quiz.html` se cambió:
- **❌ Antes**: "Miembros del Grupo"
- **✅ Ahora**: "Miembros en la Sala"

**Ubicación**: Línea 30

Esto refleja que solo se muestran los usuarios que se han unido a la sesión específica.

---

## 📊 Base de Datos

### Tablas Utilizadas:

#### `sesiones_grupo`
```sql
CREATE TABLE `sesiones_grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `grupo_id` int NOT NULL,
  `cuestionario_id` int NOT NULL,
  `iniciado_por` int NOT NULL,
  `session_code` varchar(6) NOT NULL,  -- ⭐ Código de sala
  `estado` enum('esperando','en_progreso','finalizado'),
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `started_at` timestamp NULL DEFAULT NULL,
  `finished_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `session_code` (`session_code`)  -- ⭐ Debe ser único
);
```

#### `usuario_estado_grupo`
```sql
CREATE TABLE `usuario_estado_grupo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sesion_id` int NOT NULL,
  `user_id` int NOT NULL,
  `esta_listo` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_session` (`sesion_id`,`user_id`)  -- ⭐ Evita duplicados
);
```

**✅ No se requieren cambios en la estructura** si ya ejecutaste `database.sql` (todas las tablas ya tienen las columnas necesarias)

---

## 🔄 Flujo Completo del Usuario

### 📝 Escenario: Usuario crea una sesión

1. Usuario va a **"Mis Grupos"**
2. Hace clic en **"Rendir Cuestionario"**
3. Selecciona un cuestionario
4. El sistema:
   - Crea una sesión en `sesiones_grupo`
   - Genera un `session_code` único (ej: "A1B2C3")
   - Redirige a `/grupo/quiz/<sesion_id>`
   - Registra automáticamente al usuario en `usuario_estado_grupo`

### 🚪 Escenario: Otro usuario se une

1. Usuario ve el código de sala (ej: "A1B2C3")
2. Va al botón **"Unirse"** en el header
3. Ingresa el código "A1B2C3"
4. El sistema:
   - Detecta que tiene 6 caracteres → es código de sala
   - Llama a `/api/grupo/unirse-sesion`
   - Valida que el usuario sea miembro del grupo
   - Registra al usuario en `usuario_estado_grupo`
   - Redirige a `/grupo/quiz/<sesion_id>`

### ▶️ Escenario: Inicio del juego

1. Usuarios están en la sala esperando
2. Cada uno presiona **"Estoy Listo"**
3. El sistema:
   - Actualiza `esta_listo = 1` en `usuario_estado_grupo`
   - Cuenta cuántos usuarios hay EN LA SALA (no en el grupo)
   - Cuenta cuántos están listos
   - Si `listos == total_en_sala`: inicia el juego
   - Actualiza `estado = 'en_progreso'` en `sesiones_grupo`

---

## ✅ Validaciones Implementadas

### Seguridad:
- ✅ Usuario debe estar autenticado
- ✅ Usuario debe ser miembro del grupo
- ✅ Código de sala debe existir
- ✅ Sesión no debe estar finalizada
- ✅ No se permiten duplicados en `usuario_estado_grupo`

### UX:
- ✅ Feedback visual al copiar código
- ✅ Mensajes de error claros
- ✅ Detección automática del tipo de código
- ✅ Lista actualizada de miembros en tiempo real
- ✅ Contador visible de quién está listo

---

## 🆕 Endpoints Nuevos

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/grupo/unirse-sesion` | Unirse a sesión de grupo por código |

---

## 🔄 Endpoints Modificados

| Método | Ruta | Cambio Principal |
|--------|------|------------------|
| POST | `/api/grupo/ready` | Cuenta solo usuarios en la sala, no todos del grupo |
| GET | `/grupo/quiz/<sesion_id>` | Registro automático + consulta solo usuarios en sesión |

---

## 📁 Archivos Modificados

### Backend:
1. ✅ `app.py` (3 secciones modificadas + 1 endpoint nuevo)

### Frontend:
2. ✅ `templates/join.html` (JavaScript actualizado)
3. ✅ `templates/grupo_quiz.html` (UI código de sesión + función copiar)

### Estilos:
4. ✅ `static/css/grupo_quiz.css` (estilos para código de sesión)

### Documentación:
5. ✅ `update_sesiones_grupo.sql` (script de verificación BD)
6. ✅ `CAMBIOS_SISTEMA_GRUPOS.md` (este documento)

---

## 🧪 Cómo Probar

### Prueba 1: Crear y unirse a sesión
```
1. Login como Usuario A
2. Ir a /grupos
3. Crear un grupo o usar uno existente
4. Clic en "Rendir Cuestionario"
5. Seleccionar un cuestionario
6. Copiar el código de sala (6 caracteres)
7. Abrir navegador incógnito
8. Login como Usuario B (debe ser miembro del mismo grupo)
9. Clic en "Unirse" en el header
10. Pegar el código de sala
11. Verificar que Usuario B aparece en "Miembros en la Sala"
```

### Prueba 2: Inicio del juego con subset de miembros
```
1. Crear grupo con 5 miembros
2. Usuario A inicia sesión con cuestionario
3. Solo Usuario B y Usuario C se unen
4. Los 3 dan "Estoy Listo"
5. El juego debe iniciar (aunque faltan 2 miembros del grupo)
```

### Prueba 3: Validación de pertenencia
```
1. Usuario A crea sesión en Grupo X
2. Usuario B (NO miembro de Grupo X) intenta usar el código
3. Debe recibir error: "No eres miembro de este grupo"
```

---

## 🐛 Posibles Issues y Soluciones

### Issue: "Código de sala no encontrado"
**Causa**: El `session_code` no existe en la BD
**Solución**: Verificar que la sesión se creó correctamente y el código es correcto

### Issue: "No eres miembro de este grupo"
**Causa**: El usuario no está en `grupo_miembros`
**Solución**: Unirse primero al grupo usando el código del grupo

### Issue: Los miembros no se actualizan
**Causa**: El polling no está funcionando o el usuario no se registró
**Solución**: Verificar que existe el registro en `usuario_estado_grupo`

---

## 📝 Notas Importantes

1. **Códigos de sala son de 6 caracteres** (vs 8 del código de grupo)
2. **Los códigos son ÚNICOS** a nivel de base de datos
3. **El registro es automático** al entrar a la página
4. **No hay límite de tiempo** para las sesiones (se pueden implementar limpieza automática)
5. **Compatible con el flujo anterior** (acceso directo por URL sigue funcionando)

---

## 🎨 Mejoras Futuras Sugeridas

- [ ] Agregar expiración automática de sesiones después de X horas
- [ ] Notificaciones en tiempo real cuando alguien se une
- [ ] Historial de sesiones completadas
- [ ] Estadísticas de participación por grupo
- [ ] Modo "anfitrión" para controlar el inicio del juego
- [ ] Kick de usuarios de la sala (solo admin)
- [ ] Chat en la sala de espera

---

## 👤 Autor
Modificaciones realizadas por: Asistente IA
Fecha: 26 de octubre de 2025

---

## ✨ Resumen Ejecutivo

Se implementó exitosamente un **sistema de códigos de sala** para sesiones de grupo que permite:
- ✅ Generar códigos únicos de 6 caracteres
- ✅ Unirse desde el botón "Unirse" del header
- ✅ Validar membresía del grupo
- ✅ Iniciar juegos con subsets de miembros
- ✅ Interfaz intuitiva con feedback visual

**Todos los cambios son compatibles hacia atrás** y no requieren migraciones de base de datos.

