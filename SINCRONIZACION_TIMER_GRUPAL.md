# Documentación: Sistema de Timer Sincronizado para Juegos Grupales

## 🎯 Objetivo

Implementar un sistema donde **solo el tiempo del docente/creador controla** cuándo todos los jugadores avanzan a la siguiente pregunta, y que el tiempo se mantenga sincronizado incluso al recargar la página.

---

## 📝 Cambios Realizados

### 1. **Modificaciones en Base de Datos**

**Archivo: `Kahoot/add_timer_sync_columns.sql`**

Se agregaron 3 columnas a la tabla `sesiones_grupo`:

```sql
ALTER TABLE sesiones_grupo 
ADD COLUMN pregunta_actual_id INT DEFAULT NULL,
ADD COLUMN pregunta_inicio_time TIMESTAMP NULL DEFAULT NULL,
ADD COLUMN pregunta_tiempo_limite INT DEFAULT 30;
```

- **`pregunta_actual_id`**: ID de la pregunta que está siendo mostrada
- **`pregunta_inicio_time`**: Timestamp cuando el docente inició la pregunta
- **`pregunta_tiempo_limite`**: Tiempo límite en segundos para esa pregunta

**⚠️ IMPORTANTE: Ejecutar este script antes de usar el sistema actualizado**

---

### 2. **Nuevos Endpoints en Backend**

**Archivo: `Kahoot/app.py`**

#### A) `/api/grupo/timer-sync/<sesion_id>` (GET)
- **Propósito**: Devolver el tiempo restante de la pregunta actual
- **Uso**: Todos los jugadores hacen polling cada 2 segundos
- **Respuesta**:
```json
{
  "success": true,
  "tiempo_restante": 25,
  "pregunta_id": 123,
  "tiempo_limite": 30
}
```

#### B) `/api/grupo/set-pregunta-actual` (POST)
- **Propósito**: El docente registra cuando inicia una nueva pregunta
- **Uso**: Solo el creador/docente cuando muestra una pregunta
- **Parámetros**:
```json
{
  "sesion_id": 1,
  "pregunta_id": 123,
  "tiempo_limite": 30
}
```

---

### 3. **Modificaciones en Frontend**

**Archivo: `Kahoot/templates/juego_grupo.html`**

#### Cambios Clave:

1. **Timer Sincronizado**
   - Cada 2 segundos hace polling a `/api/grupo/timer-sync`
   - Actualiza `timeLeft` con el valor del servidor
   - Todos los jugadores ven el mismo tiempo

2. **Registro de Inicio (solo docente)**
   - Cuando el docente muestra una pregunta, llama a `/api/grupo/set-pregunta-actual`
   - Esto guarda el timestamp en el servidor

3. **Los jugadores NO detienen el timer**
   - Cuando responden, el timer sigue corriendo
   - Solo avanza cuando el tiempo del servidor llega a 0

4. **Soporte para Recarga de Página**
   - Al recargar, obtiene el tiempo restante del servidor
   - Se sincroniza automáticamente con el tiempo actual

---

## 🎮 Flujo de Funcionamiento

### Inicio de Pregunta

```
1. Docente muestra pregunta
   ↓
2. Frontend llama a /api/grupo/set-pregunta-actual
   ↓
3. Servidor guarda timestamp actual en pregunta_inicio_time
   ↓
4. Todos los clientes inician timer local
   ↓
5. Todos hacen polling cada 2 segundos a /api/grupo/timer-sync
```

### Durante la Pregunta

```
Cada 2 segundos:
1. Cliente: "¿Cuánto tiempo queda?"
   ↓
2. Servidor: Calcula (tiempo_limite - tiempo_transcurrido)
   ↓
3. Cliente: Actualiza timeLeft = tiempo_restante
```

### Al Recargar Página

```
1. Cliente recarga la página
   ↓
2. Frontend llama a /api/grupo/obtener-pregunta-actual
   ↓
3. Frontend obtiene pregunta_id actual
   ↓
4. Muestra la pregunta correcta
   ↓
5. Inicia polling de timer
   ↓
6. Se sincroniza con el tiempo del servidor
   ↓
7. ✅ Usuario ve el tiempo correcto
```

### Fin de Tiempo

```
Cuando tiempo_restante llega a 0:
1. Todos los clientes detectan timeLeft <= 0
   ↓
2. Detienen el timer local
   ↓
3. Muestran pantalla de transición
   ↓
4. Avanzan a la siguiente pregunta
   ↓
5. El docente vuelve a registrar inicio de nueva pregunta
```

---

## ✅ Comportamiento Esperado

### ✔️ **Timer Sincronizado**
- Todos los jugadores ven el mismo tiempo
- El tiempo es controlado por el servidor (docente)
- No hay desincronización entre clientes

### ✔️ **Recarga de Página**
- Al recargar, el jugador ve el tiempo correcto
- Se mantiene en la pregunta correcta
- Se sincroniza automáticamente

### ✔️ **Respuestas Anticipadas**
- Jugadores pueden responder antes del tiempo
- El timer NO se detiene
- Esperan a que termine el tiempo del docente

### ✔️ **Control del Docente**
- Solo el docente controla el avance
- Su timer es el "master timer"
- Todos avanzan cuando su tiempo termina

---

## 🔧 Instalación y Configuración

### Paso 1: Actualizar Base de Datos
```bash
# Ejecutar el script SQL
mysql -u usuario -p database_name < Kahoot/add_timer_sync_columns.sql
# o
psql -U usuario -d database_name -f Kahoot/add_timer_sync_columns.sql
```

### Paso 2: Reiniciar Aplicación
```bash
# Reiniciar Flask
# Los cambios en app.py ya están aplicados
```

### Paso 3: Probar
1. Docente crea una sala
2. Alumnos se unen
3. Docente inicia el juego
4. Verificar que todos ven el mismo tiempo
5. Probar recargar página en un jugador
6. Verificar que se sincroniza correctamente

---

## 🐛 Solución de Problemas

### Problema: Los jugadores se quedan trabados
**Causa**: No ejecutaste el script SQL
**Solución**: Ejecuta `add_timer_sync_columns.sql`

### Problema: Los tiempos no coinciden
**Causa**: El servidor y los clientes tienen diferencias de hora
**Solución**: Sincroniza el reloj del servidor con NTP

### Problema: Al recargar se pierde el progreso
**Causa**: Los endpoints no están respondiendo correctamente
**Solución**: Verifica que `/api/grupo/timer-sync` y `/api/grupo/obtener-pregunta-actual` funcionan

---

## 📊 Monitoreo

Para verificar que todo funciona, revisa la consola del navegador:

```
✅ Mensajes esperados:
- "⏰ Timer sincronizado iniciado en servidor"
- "🔄 Timer sincronizado: 25s restantes"
- "📍 Sincronizando con pregunta X"

❌ Mensajes de error:
- "Error al sincronizar timer"
- "Error al registrar inicio de pregunta"
```

---

## 📈 Mejoras Futuras (Opcionales)

1. **WebSocket**: Reemplazar polling por WebSocket para sincronización en tiempo real
2. **Compensación de Latencia**: Ajustar tiempo basándose en latencia de red
3. **Reconexión Automática**: Si pierde conexión, intentar reconectar automáticamente
4. **Animación de Sincronización**: Mostrar un indicador visual cuando se sincroniza

---

**Fecha de Implementación**: Noviembre 2025
**Desarrollador**: Sistema RoBot - USAT
**Estado**: ✅ Completado y Probado

