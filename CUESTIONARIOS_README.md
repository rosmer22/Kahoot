# Sistema de Cuestionarios - Documentación

## 📋 Descripción General

Sistema completo para crear, editar y gestionar cuestionarios con preguntas de opción múltiple, selección simple y verdadero/falso.

## 🗄️ Estructura de Base de Datos

### Tabla: `cuestionarios`
Almacena la información principal de cada cuestionario.

```sql
- id: INT (PRIMARY KEY)
- user_id: INT (FOREIGN KEY -> users.id)
- titulo: VARCHAR(255)
- descripcion: TEXT
- imagen_portada: VARCHAR(500)
- pin: VARCHAR(10) UNIQUE
- estado: ENUM('borrador', 'publicado', 'archivado')
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Tabla: `preguntas`
Almacena las preguntas de cada cuestionario.

```sql
- id: INT (PRIMARY KEY)
- cuestionario_id: INT (FOREIGN KEY -> cuestionarios.id)
- tipo_pregunta: ENUM('opcion_multiple', 'seleccion_simple', 'verdadero_falso')
- texto_pregunta: TEXT
- imagen_pregunta: VARCHAR(500)
- orden: INT
- tiempo_limite: INT (segundos)
- puntos: INT
- created_at: TIMESTAMP
```

### Tabla: `opciones_respuesta`
Almacena las opciones de respuesta para cada pregunta.

```sql
- id: INT (PRIMARY KEY)
- pregunta_id: INT (FOREIGN KEY -> preguntas.id)
- texto_opcion: TEXT
- es_correcta: BOOLEAN
- orden: INT
- created_at: TIMESTAMP
```

## 🔌 API Endpoints

### 1. Crear Cuestionario
**POST** `/api/cuestionario`

**Request Body (JSON):**
```json
{
  "titulo": "Matemática 1° Básico",
  "descripcion": "Cuestionario de suma y resta",
  "preguntas": [
    {
      "text": "¿Cuánto es 2 + 2?",
      "type": "simple",
      "time": 30,
      "points": 1,
      "answers": [
        {"text": "3", "isCorrect": false},
        {"text": "4", "isCorrect": true},
        {"text": "5", "isCorrect": false}
      ]
    }
  ]
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Cuestionario creado exitosamente",
  "cuestionario_id": 1,
  "pin": "ABC123"
}
```

### 2. Actualizar Cuestionario
**PUT** `/api/cuestionario/<cuestionario_id>`

**Request Body:** Mismo formato que crear cuestionario

**Response (200):**
```json
{
  "success": true,
  "message": "Cuestionario actualizado exitosamente",
  "cuestionario_id": 1
}
```

### 3. Obtener Cuestionario
**GET** `/api/cuestionario/<cuestionario_id>`

**Response (200):**
```json
{
  "success": true,
  "cuestionario": {
    "id": 1,
    "titulo": "Matemática 1° Básico",
    "descripcion": "Cuestionario de suma y resta",
    "imagen_portada": "portada_123456.jpg",
    "pin": "ABC123",
    "estado": "borrador",
    "created_at": "2025-01-01T10:00:00",
    "preguntas": [...]
  }
}
```

## 📂 Archivos Implementados

### Backend (Python/Flask)
1. **controllers/quiz_controller.py** - Controlador con la lógica de negocio
   - `crear_cuestionario()` - Crea un nuevo cuestionario
   - `actualizar_cuestionario()` - Actualiza un cuestionario existente
   - `obtener_cuestionario()` - Obtiene un cuestionario completo
   - `generate_pin()` - Genera PIN único
   - `save_cover_image()` - Guarda imagen de portada

2. **app.py** - Rutas añadidas:
   - `/editor` - Vista del editor (crear nuevo)
   - `/editor/<id>` - Vista del editor (editar existente)
   - `/api/cuestionario` [POST] - Crear cuestionario
   - `/api/cuestionario/<id>` [PUT/POST] - Actualizar cuestionario
   - `/api/cuestionario/<id>` [GET] - Obtener cuestionario

### Frontend (JavaScript)
3. **static/js/editor.js** - Lógica del editor actualizada:
   - Sistema de gestión de múltiples preguntas
   - Panel lateral con preview de preguntas
   - Función `guardarCuestionario()` - Envía datos al servidor
   - Validaciones de formulario
   - Carga de cuestionarios existentes

### Templates
4. **templates/editor.html** - Vista actualizada:
   - Input hidden para `cuestionario_id`
   - Script para cargar datos de cuestionario existente

## 🔄 Flujo de Trabajo

### Crear Nuevo Cuestionario
1. Usuario navega a `/editor`
2. Se abre modal de configuración automáticamente
3. Usuario ingresa título y descripción
4. Usuario crea preguntas con sus opciones
5. Al hacer clic en "Listo", se ejecuta `guardarCuestionario()`
6. Datos se envían a `/api/cuestionario` vía POST
7. Sistema valida y guarda en base de datos
8. Redirige a "Mis Cuestionarios"

### Editar Cuestionario Existente
1. Usuario navega a `/editor/<id>`
2. Sistema carga cuestionario desde base de datos
3. Se llenan campos del modal y preguntas
4. Usuario modifica lo necesario
5. Al hacer clic en "Listo", se ejecuta `guardarCuestionario()`
6. Datos se envían a `/api/cuestionario/<id>` vía PUT
7. Sistema actualiza en base de datos
8. Redirige a "Mis Cuestionarios"

## 🔐 Validaciones

### Backend
- Usuario autenticado (usando `g.user`)
- Título obligatorio
- Al menos 1 pregunta
- Verificación de propiedad del cuestionario (solo el creador puede editar)

### Frontend
- Título no vacío
- Pregunta con texto
- Al menos una respuesta correcta por pregunta
- Todas las respuestas con texto

## 📦 Tipos de Pregunta

### 1. Opción Múltiple (`multiple`)
- Permite seleccionar varias respuestas correctas
- Mínimo 2, máximo 5 alternativas

### 2. Selección Simple (`simple`)
- Solo una respuesta correcta
- Mínimo 2, máximo 5 alternativas

### 3. Verdadero/Falso (`verdadero-falso`)
- Exactamente 2 opciones: "Verdadero" y "Falso"
- Opciones no editables

## 🎯 Características Implementadas

✅ Crear cuestionarios con título, descripción e imagen de portada
✅ Agregar múltiples preguntas con diferentes tipos
✅ Configurar tiempo límite y puntos por pregunta
✅ Panel lateral con preview de todas las preguntas
✅ Eliminar y reordenar preguntas
✅ Validaciones completas en frontend y backend
✅ Generación automática de PIN único
✅ Guardar en base de datos con relaciones correctas
✅ Editar cuestionarios existentes
✅ Protección por autenticación de usuario

## 🚀 Próximas Funcionalidades

- [ ] Listar cuestionarios en "Mis Cuestionarios"
- [ ] Eliminar cuestionarios
- [ ] Publicar/Archivar cuestionarios
- [ ] Sistema de juego en vivo con PIN
- [ ] Estadísticas y resultados
- [ ] Compartir cuestionarios

## 💡 Uso

### En el Editor:

1. **Botón "Guardar" en el Header**: 
   - ✅ **GUARDA en la base de datos**
   - Valida que haya título configurado
   - Si no hay título, abre el modal de configuración
   - Muestra el PIN generado al crear un cuestionario nuevo
   - Redirige a "Mis Cuestionarios" después de guardar

2. **Botón "Listo" en el Modal de Configuración**:
   - ❌ **NO guarda en base de datos**
   - Solo sincroniza el título al header
   - Cierra el modal de configuración
   - Úsalo para cambiar el título/descripción temporalmente

3. **Botón "Cancelar" en el Modal de Configuración**:
   - Cierra el modal sin validar
   - No realiza ninguna acción de guardado

### Estructura de datos en JavaScript:
```javascript
// En el editor, las preguntas se guardan automáticamente en el array:
questions = [
  {
    text: "¿Pregunta?",
    type: "multiple|simple|verdadero-falso",
    time: 30, // segundos
    points: 1,
    answers: [
      {text: "Opción 1", isCorrect: true},
      {text: "Opción 2", isCorrect: false}
    ]
  }
]
```

## ⚠️ Notas Importantes

- Las imágenes de portada se guardan en `static/uploads/`
- Los PIN son únicos de 6 caracteres (letras mayúsculas y números)
- Las preguntas se eliminan en cascada al eliminar un cuestionario
- El estado por defecto es 'borrador'
