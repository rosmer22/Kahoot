# 🎮 Sistema de Cuestionarios Individuales con Salas

## 📋 Descripción

Se ha implementado un nuevo sistema para jugar cuestionarios individuales que replica el flujo de juego de los grupos. Ahora, cuando inicias un cuestionario (ya sea desde "Mis Cuestionarios" o desde la búsqueda de cuestionarios), se crea una sala con un código único de 6 caracteres que otros usuarios pueden usar para unirse y jugar juntos.

---

## 🎯 Características Principales

### ✅ Sistema de Salas
- **Código único de 6 caracteres**: Al iniciar un cuestionario, se genera automáticamente un código de sala (ej: "A1B2C3")
- **Compartir código**: El código se puede copiar fácilmente para compartir con otros jugadores
- **Unirse con código**: Otros usuarios pueden unirse usando el botón "Unirse" en el header

### ✅ Sala de Espera
- **Lista de participantes**: Muestra todos los usuarios que se han unido a la sala
- **Estado "Listo"**: Cada participante debe marcar que está listo antes de comenzar
- **Inicio automático**: El juego comienza automáticamente cuando todos están listos
- **Cuenta regresiva**: Después de que todos están listos, hay una cuenta regresiva de 3 segundos

### ✅ Juego Sincronizado
- **Mismo flujo que grupos**: Usa el mismo HTML dedicado para el juego (`juego_individual.html`)
- **Preguntas secuenciales**: Los participantes avanzan por las preguntas automáticamente
- **Temporizador por pregunta**: Cada pregunta tiene su propio temporizador
- **Feedback inmediato**: Muestra si la respuesta fue correcta o incorrecta
- **Transiciones animadas**: Pantallas de transición entre preguntas

---

## 🔧 Cambios Implementados

### 1. **Base de Datos** ✅

#### Nuevas Tablas:

**`sesiones_individual`**
```sql
CREATE TABLE sesiones_individual (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cuestionario_id INT NOT NULL,
  iniciado_por INT NOT NULL,
  session_code VARCHAR(6) UNIQUE NOT NULL,
  estado ENUM('esperando', 'en_progreso', 'finalizado'),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP NULL,
  finished_at TIMESTAMP NULL
);
```

**`usuario_estado_individual`**
```sql
CREATE TABLE usuario_estado_individual (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sesion_id INT NOT NULL,
  user_id INT NOT NULL,
  esta_listo TINYINT(1) DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_session (sesion_id, user_id)
);
```

**Script SQL**: `update_sesiones_individual.sql`

---

### 2. **Backend (app.py)** ✅

#### Nuevos Endpoints:

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/individual/iniciar-cuestionario` | Crea una nueva sesión individual con código |
| GET | `/individual/quiz/<sesion_id>` | Sala de espera para cuestionario individual |
| POST | `/api/individual/unirse-sesion` | Unirse a una sesión con código de 6 caracteres |
| POST | `/api/individual/ready` | Marcar usuario como listo |
| GET | `/individual/juego/<sesion_id>` | Página para jugar el cuestionario |
| GET | `/api/individual/participantes/<sesion_id>` | Lista actualizada de participantes |
| GET | `/api/individual/status/<sesion_id>` | Estado actual de la sesión |
| POST | `/api/individual/answer` | Enviar respuesta de un participante |

**Ubicación**: Líneas 2024-2494 en `app.py`

---

### 3. **Templates** ✅

#### **individual_quiz.html**
- Sala de espera para cuestionarios individuales
- Muestra el código de sala con botón para copiar
- Lista de participantes con indicador de "listo"
- Botón "Estoy Listo"
- Polling en tiempo real para actualizaciones
- Reutiliza los estilos de `grupo_quiz.css`

#### **juego_individual.html**
- Página dedicada para jugar cuestionarios individuales
- Interfaz similar a `juego_grupo.html`
- Temporizador circular por pregunta
- Transiciones animadas entre preguntas
- Feedback inmediato de respuestas
- Barra de progreso
- Reutiliza los estilos de `juego_grupo.css`

---

### 4. **Frontend** ✅

#### **my_quizzes.html**
- Botón "Empezar" modificado para usar el nuevo flujo
- Ahora llama a `startIndividualQuiz(quizId)` en lugar de redirigir directamente

#### **my_quizzes.js**
- Nueva función `startIndividualQuiz(quizId)`
- Llama al endpoint `/api/individual/iniciar-cuestionario`
- Redirige a la sala de espera con el `sesion_id`

#### **quiz_details.html**
- Botón "Iniciar ahora" modificado para usar el nuevo flujo
- Incluye función JavaScript inline para iniciar la sesión

#### **join.html**
- Actualizada la lógica para detectar códigos de sesiones individuales
- Cuando se ingresa un código de 6 caracteres:
  1. Intenta unirse a sesión de grupo
  2. Si falla, intenta unirse a sesión individual
  3. Si ambos fallan, muestra error

---

## 🔄 Flujo Completo del Usuario

### 📝 Escenario 1: Usuario Crea una Sesión

1. Usuario va a **"Mis Cuestionarios"** o encuentra un cuestionario en **"Explorar"**
2. Hace clic en **"Empezar"** o **"Iniciar ahora"**
3. El sistema:
   - Crea una sesión en `sesiones_individual`
   - Genera un `session_code` único (ej: "A1B2C3")
   - Redirige a `/individual/quiz/<sesion_id>`
   - Registra automáticamente al usuario en `usuario_estado_individual`
4. El usuario ve:
   - Código de sala con botón para copiar
   - Lista de participantes (solo él por ahora)
   - Botón "Estoy Listo"

### 🚪 Escenario 2: Otro Usuario se Une

1. Usuario recibe el código de sala (ej: "A1B2C3")
2. Va al botón **"Unirse"** en el header
3. Ingresa el código "A1B2C3"
4. El sistema:
   - Detecta que tiene 6 caracteres
   - Llama a `/api/individual/unirse-sesion`
   - Registra al usuario en `usuario_estado_individual`
   - Redirige a `/individual/quiz/<sesion_id>`
5. El usuario ve la sala de espera con todos los participantes

### ▶️ Escenario 3: Inicio del Juego

1. Usuarios están en la sala esperando
2. Cada uno presiona **"Estoy Listo"**
3. El sistema:
   - Actualiza `esta_listo = 1` en `usuario_estado_individual`
   - Cuenta cuántos usuarios hay EN LA SALA
   - Cuenta cuántos están listos
   - Si `listos == total_en_sala`: inicia el juego
   - Actualiza `estado = 'en_progreso'` en `sesiones_individual`
4. Muestra cuenta regresiva de 3 segundos
5. Redirige a `/individual/juego/<sesion_id>`

### 🎮 Escenario 4: Jugando el Cuestionario

1. Se muestra la primera pregunta con temporizador
2. Usuarios seleccionan sus respuestas
3. El sistema:
   - Guarda la respuesta en `respuestas_usuarios`
   - Calcula puntos basados en tiempo y corrección
   - Muestra feedback (correcta/incorrecta)
4. Después de 2 segundos, pasa a la siguiente pregunta
5. Se repite hasta terminar todas las preguntas
6. Redirige a `/my-quizzes` (puede implementarse página de resultados)

---

## 🆚 Diferencias con el Sistema de Grupos

| Característica | Grupos | Individual |
|---------------|--------|------------|
| **Requisito** | Ser miembro del grupo | Ninguno, cualquiera con el código |
| **Acceso** | Solo miembros del grupo | Abierto con código |
| **Inicio de sesión** | Desde página del grupo | Desde "Mis Cuestionarios" o "Explorar" |
| **Endpoint de sesión** | `/api/grupo/...` | `/api/individual/...` |
| **Tabla de sesiones** | `sesiones_grupo` | `sesiones_individual` |
| **Tabla de estado** | `usuario_estado_grupo` | `usuario_estado_individual` |
| **Sincronización** | Espera a que todos respondan | Avance automático después de responder |

---

## ✅ Validaciones Implementadas

### Seguridad:
- ✅ Usuario debe estar autenticado para crear o unirse a sesiones
- ✅ Código de sala debe existir y ser válido
- ✅ Sesión no debe estar finalizada
- ✅ No se permiten duplicados en `usuario_estado_individual` (UNIQUE constraint)
- ✅ Validación de respuestas en el servidor

### UX:
- ✅ Feedback visual al copiar código
- ✅ Mensajes de error claros
- ✅ Detección automática del tipo de código (6 caracteres = sala, otro = PIN)
- ✅ Lista actualizada de participantes en tiempo real (polling cada 2 segundos)
- ✅ Contador visible de quién está listo
- ✅ Transiciones suaves y animadas
- ✅ Temporizador visual circular
- ✅ Barra de progreso del cuestionario

---

## 📦 Archivos Modificados/Creados

### Creados:
- `update_sesiones_individual.sql` - Script para crear las tablas
- `templates/individual_quiz.html` - Sala de espera
- `templates/juego_individual.html` - Página de juego
- `SISTEMA_CUESTIONARIOS_INDIVIDUALES.md` - Esta documentación

### Modificados:
- `app.py` - Nuevos endpoints (líneas 2024-2494)
- `templates/my_quizzes.html` - Botón "Empezar"
- `static/js/my_quizzes.js` - Función `startIndividualQuiz()`
- `templates/quiz_details.html` - Botón "Iniciar ahora"
- `templates/join.html` - Detección de códigos individuales

---

## 🚀 Instrucciones de Instalación

### 1. Ejecutar Script SQL
```bash
# Conectar a MySQL
mysql -u root -p

# Usar la base de datos
USE robot;

# Ejecutar el script
source update_sesiones_individual.sql;
```

O ejecutar manualmente:
```bash
mysql -u root -p robot < update_sesiones_individual.sql
```

### 2. Verificar Tablas
```sql
-- Verificar que las tablas se crearon correctamente
SHOW TABLES LIKE 'sesiones_individual';
SHOW TABLES LIKE 'usuario_estado_individual';

-- Ver estructura de las tablas
DESCRIBE sesiones_individual;
DESCRIBE usuario_estado_individual;
```

### 3. Reiniciar la Aplicación
```bash
# Si estás en desarrollo
python app.py
```

---

## 🧪 Pruebas Recomendadas

### Prueba 1: Crear Sesión Individual
1. Ir a "Mis Cuestionarios"
2. Hacer clic en "Empezar" en cualquier cuestionario
3. Verificar que se crea la sala con código de 6 caracteres
4. Verificar que apareces en la lista de participantes

### Prueba 2: Unirse a Sesión
1. Copiar el código de sala
2. En otra pestaña/navegador, iniciar sesión con otro usuario
3. Ir a "Unirse" en el header
4. Ingresar el código
5. Verificar que ambos usuarios aparecen en la sala

### Prueba 3: Sistema de "Listo"
1. Con 2 usuarios en la sala
2. Usuario 1 marca "Estoy Listo"
3. Verificar que el indicador cambia
4. Usuario 2 marca "Estoy Listo"
5. Verificar que comienza la cuenta regresiva
6. Verificar que inicia el juego

### Prueba 4: Jugar Cuestionario
1. Responder preguntas
2. Verificar temporizador
3. Verificar feedback de respuestas
4. Verificar transiciones entre preguntas
5. Verificar que finaliza correctamente

---

## 🐛 Posibles Problemas y Soluciones

### Error: Tabla no existe
**Solución**: Ejecutar el script SQL `update_sesiones_individual.sql`

### Error: Código de sala no funciona
**Solución**: Verificar que:
- El código tiene exactamente 6 caracteres
- La sesión existe en la base de datos
- El estado de la sesión no es 'finalizado'

### Error: No se puede unir a la sesión
**Solución**: Verificar que:
- El usuario está autenticado
- La sesión está activa (estado = 'esperando')

### Error: No inicia el juego
**Solución**: Verificar que:
- Todos los usuarios en la sala están marcados como "listo"
- El polling está funcionando (revisar consola del navegador)
- El estado de la sesión se actualiza correctamente

---

## 🔮 Mejoras Futuras Sugeridas

1. **Página de Resultados Individual**
   - Mostrar ranking de participantes
   - Mostrar puntajes individuales
   - Mostrar estadísticas del juego

2. **Chat en la Sala**
   - Permitir comunicación entre participantes
   - Usar WebSockets para tiempo real

3. **Configuraciones de Sala**
   - Límite de participantes
   - Modo privado/público
   - Tiempo límite de espera

4. **Historial de Sesiones**
   - Ver sesiones anteriores
   - Reanudar sesiones interrumpidas
   - Estadísticas por sesión

5. **Compartir en Redes Sociales**
   - Botón para compartir código de sala
   - Link directo para unirse

---

## 📞 Contacto

Si tienes preguntas o encuentras algún problema, por favor documenta:
- Qué estabas intentando hacer
- Qué error apareció (captura de pantalla)
- Logs de la consola del navegador (F12)
- Logs del servidor (terminal donde corre Flask)

---

## ✨ Resumen

El nuevo sistema de cuestionarios individuales replica exitosamente el flujo de juego de los grupos, proporcionando:

✅ **Salas con códigos únicos** para compartir  
✅ **Sistema de "listo"** para sincronización  
✅ **Juego fluido** con transiciones animadas  
✅ **Polling en tiempo real** para actualizaciones  
✅ **Compatibilidad** con el sistema existente  
✅ **Experiencia unificada** entre grupos e individuales  

El sistema está completamente funcional y listo para usar. ¡Disfruta jugando! 🎉

