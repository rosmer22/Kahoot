# 🎯 Fórmula de Puntajes Corregida

## 📊 Fórmula Implementada

### ✅ **Fórmula Correcta:**

```
puntaje_asignado = puntaje_base * (tiempo_restante / tiempo_total)
```

Donde:
- **`puntaje_base`** = Puntos configurados en la pregunta (ej: 1000)
- **`tiempo_restante`** = tiempo_total - tiempo_respuesta
- **`tiempo_total`** = Límite de tiempo de la pregunta (ej: 30 segundos)
- **`tiempo_respuesta`** = Segundos que tardó el usuario en responder

---

## 📐 Ejemplos Prácticos

### Ejemplo 1: Pregunta de 1000 puntos, 30 segundos

| Tiempo Respuesta | Tiempo Restante | Cálculo | Puntos Finales |
|------------------|-----------------|---------|----------------|
| **5 segundos** | 25 segundos | 1000 × (25/30) | **833 puntos** ✨ |
| **10 segundos** | 20 segundos | 1000 × (20/30) | **667 puntos** |
| **15 segundos** | 15 segundos | 1000 × (15/30) | **500 puntos** |
| **20 segundos** | 10 segundos | 1000 × (10/30) | **333 puntos** |
| **25 segundos** | 5 segundos | 1000 × (5/30) | **167 puntos** |
| **30 segundos** | 0 segundos | 1000 × (0/30) | **0 puntos** ⏱️ |

### Ejemplo 2: Pregunta de 500 puntos, 20 segundos

| Tiempo Respuesta | Tiempo Restante | Cálculo | Puntos Finales |
|------------------|-----------------|---------|----------------|
| **2 segundos** | 18 segundos | 500 × (18/20) | **450 puntos** ✨ |
| **5 segundos** | 15 segundos | 500 × (15/20) | **375 puntos** |
| **10 segundos** | 10 segundos | 500 × (10/20) | **250 puntos** |
| **15 segundos** | 5 segundos | 500 × (5/20) | **125 puntos** |
| **20 segundos** | 0 segundos | 500 × (0/20) | **0 puntos** ⏱️ |

---

## 💡 Comportamiento de la Fórmula

### ✅ Ventajas:

1. **Proporcional al tiempo restante**
   - Responder inmediatamente = casi 100% de puntos
   - Responder al final = 0 puntos

2. **Incentiva velocidad**
   - Cada segundo cuenta
   - Los más rápidos obtienen ventaja clara

3. **Justo y transparente**
   - Fácil de entender
   - Cálculo directo sin mínimos artificiales

### 📊 Gráfico Conceptual:

```
Puntos
  ↑
100%|●
    | \
 75%|  \
    |   \
 50%|    \
    |     \
 25%|      \
    |       \
  0%|________●
    0   15   30 → Tiempo (segundos)
    ↑           ↑
  Respuesta  Timeout
  inmediata
```

---

## 🔄 Cambios Realizados

### ❌ Fórmula Anterior (INCORRECTA):

```python
# ANTES (no funcionaba bien)
factor_tiempo = max(0.5, 1 - (tiempo_respuesta / tiempo_limite * 0.5))
puntos = int(puntos_base * factor_tiempo)

# Problema: 
# - Garantizaba mínimo 50% de puntos
# - No era proporcional al tiempo restante
# - Fórmula confusa
```

**Ejemplo con fórmula anterior:**
- Pregunta de 1000 puntos, 30 segundos
- Responder en 30 segundos → 500 puntos (50% garantizado) ❌
- No era justo, todos obtenían mínimo la mitad

### ✅ Fórmula Nueva (CORRECTA):

```python
# AHORA (correcto y justo)
tiempo_restante = max(0, tiempo_limite - tiempo_respuesta)
factor_tiempo = tiempo_restante / tiempo_limite
puntos = int(puntos_base * factor_tiempo)

# Ventajas:
# - Proporcional directo
# - Sin mínimos artificiales
# - Fórmula clara y simple
```

**Ejemplo con fórmula nueva:**
- Pregunta de 1000 puntos, 30 segundos
- Responder en 30 segundos → 0 puntos ✅
- Responder en 0 segundos → 1000 puntos ✅
- Lineal y justo

---

## 🎮 Impacto en el Juego

### Estrategias de Jugadores:

#### 🚀 Jugador Rápido:
```
Responde en 3 segundos de 30
→ 1000 × (27/30) = 900 puntos
✨ Recompensa alta por velocidad
```

#### 🤔 Jugador Pensativo:
```
Responde en 20 segundos de 30
→ 1000 × (10/30) = 333 puntos
⚠️ Pierde muchos puntos por pensar mucho
```

#### ⏱️ Jugador Lento:
```
Responde en 29 segundos de 30
→ 1000 × (1/30) = 33 puntos
💥 Casi sin puntos por tardanza
```

---

## 📝 Código Implementado

### Backend (app.py, líneas 1703-1712):

```python
# Calcular puntos (más rápido = más puntos)
es_correcta = resultado['es_correcta']
puntos = 0
if es_correcta:
    puntos_base = resultado['puntos'] or 1000
    tiempo_limite = resultado['tiempo_limite'] or 30
    # Fórmula: puntaje = puntaje_base * (tiempo_restante / tiempo_total)
    tiempo_restante = max(0, tiempo_limite - tiempo_respuesta)
    factor_tiempo = tiempo_restante / tiempo_limite
    puntos = int(puntos_base * factor_tiempo)
```

### Frontend (juego_grupo.html):

El frontend calcula `tiempo_respuesta`:
```javascript
// Calcular tiempo de respuesta
const timeToAnswer = Math.floor((Date.now() - questionStartTime) / 1000);

// Enviar al backend
sendAnswer(currentQuestion.id, optionId, timeToAnswer);
```

---

## 🧪 Casos de Prueba

### Test 1: Respuesta Instantánea
```
Input:
  - puntaje_base = 1000
  - tiempo_limite = 30
  - tiempo_respuesta = 0

Cálculo:
  - tiempo_restante = 30 - 0 = 30
  - factor = 30/30 = 1.0
  - puntos = 1000 × 1.0 = 1000

Output: 1000 puntos ✅
```

### Test 2: Respuesta a la Mitad
```
Input:
  - puntaje_base = 1000
  - tiempo_limite = 30
  - tiempo_respuesta = 15

Cálculo:
  - tiempo_restante = 30 - 15 = 15
  - factor = 15/30 = 0.5
  - puntos = 1000 × 0.5 = 500

Output: 500 puntos ✅
```

### Test 3: Respuesta al Final
```
Input:
  - puntaje_base = 1000
  - tiempo_limite = 30
  - tiempo_respuesta = 30

Cálculo:
  - tiempo_restante = 30 - 30 = 0
  - factor = 0/30 = 0
  - puntos = 1000 × 0 = 0

Output: 0 puntos ✅
```

### Test 4: Pregunta con Pocos Puntos
```
Input:
  - puntaje_base = 100
  - tiempo_limite = 15
  - tiempo_respuesta = 5

Cálculo:
  - tiempo_restante = 15 - 5 = 10
  - factor = 10/15 = 0.666...
  - puntos = 100 × 0.666 = 66 (redondeado)

Output: 66 puntos ✅
```

---

## 🔒 Protecciones

### Caso: Tiempo de Respuesta Mayor al Límite
```python
tiempo_restante = max(0, tiempo_limite - tiempo_respuesta)
```

Si por algún bug `tiempo_respuesta > tiempo_limite`:
- `tiempo_restante` será `0` (gracias al `max`)
- `puntos` será `0`
- ✅ No hay puntos negativos

---

## 📊 Comparativa Visual

### Distribución de Puntos en Pregunta de 1000pts/30seg:

```
Tiempo │ Anterior (50% mín) │ Nueva (proporcional)
───────┼────────────────────┼─────────────────────
  0s   │      1000 pts      │      1000 pts
  5s   │       917 pts      │       833 pts
 10s   │       833 pts      │       667 pts
 15s   │       750 pts      │       500 pts
 20s   │       667 pts      │       333 pts
 25s   │       583 pts      │       167 pts
 30s   │       500 pts ❌   │         0 pts ✅
```

**Ventaja de la nueva fórmula:**
- ✅ Más justa
- ✅ Incentiva mejor la velocidad
- ✅ Sin "colchón" artificial del 50%

---

## 🎯 Conclusión

La nueva fórmula es:
- ✅ **Más justa**: Proporcional directo
- ✅ **Más clara**: Fácil de entender
- ✅ **Más competitiva**: Cada segundo cuenta
- ✅ **Más simple**: Sin factores artificiales

---

## 👤 Cambios Realizados Por:
- Asistente IA
- Fecha: 26 de octubre de 2025
- Archivos modificados:
  - `app.py` (líneas 1703-1712)
  - `templates/juego_grupo.html` (eliminado beforeunload)

---

## 🐛 Problema del `beforeunload` Resuelto

### ❌ ANTES:
```javascript
window.addEventListener('beforeunload', function(e) {
    if (currentQuestionIndex < totalQuestions) {
        e.preventDefault();
        e.returnValue = '¿Seguro que quieres salir?';
    }
});
```
Esto causaba el mensaje molesto del navegador.

### ✅ AHORA:
```javascript
// Eliminado completamente
```
Ya no hay mensaje de confirmación al salir.

---

**¡Fórmula de puntajes corregida y mensaje molesto eliminado! 🎯✨**

