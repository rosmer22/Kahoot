# 📚 Cómo Usar el Sistema de Cuestionarios

## 🚀 Inicio Rápido

### 1️⃣ Crear un Nuevo Cuestionario

1. **Inicia sesión** en tu cuenta
2. Haz clic en **"Editor"** o navega a `/editor`
3. Se abrirá automáticamente el **Modal de Configuración**

### 2️⃣ Configurar el Cuestionario

En el modal de configuración podrás:

#### Pestaña "Información Básica":
- ✍️ **Título** (obligatorio): Ej. "Matemática 1° Básico"
- 📝 **Descripción** (opcional): Breve descripción del cuestionario
- 🖼️ **Imagen de portada** (opcional): Arrastra una imagen o haz clic para seleccionar

#### Pestaña "Juego en Vivo":
- ⏱️ **Tiempo por pregunta**: 10, 20, 30, 45, 60 o 90 segundos
- ✔️ **Puntaje por pregunta**: 1, 2, 3, 4 o 5 puntos

### 3️⃣ Crear Preguntas

#### Usar el Panel de Edición:

**Tipo de Pregunta** (Selector superior):
- 📊 **Opción Múltiple**: Permite múltiples respuestas correctas
- ☝️ **Selección Simple**: Solo una respuesta correcta
- ✅ **Verdadero/Falso**: Opciones fijas de Verdadero o Falso

**Escribir la Pregunta**:
- Escribe en el área de texto grande (rosa)
- El texto se guarda automáticamente

**Agregar Alternativas**:
- Escribe las opciones de respuesta
- Haz clic en una alternativa para marcarla como correcta (✔ verde)
- Usa el botón **"+ Agregar Alternativa"** para más opciones (máx. 5)
- Usa el botón 🗑️ para eliminar alternativas (mín. 2)

#### Panel Lateral de Preguntas (☰):

- 📋 Ver todas las preguntas creadas
- 🎯 Ver qué pregunta estás editando (resaltada)
- ➕ Botón **"+ Añadir Pregunta"** para crear más preguntas
- 🗑️ Eliminar preguntas (mínimo 1 pregunta)
- 👆 Clic en una pregunta para editarla

### 4️⃣ Guardar el Cuestionario

#### 🔴 IMPORTANTE: Solo el botón "Guardar" guarda en la base de datos

#### Botón "Guardar" (Header) - ✅ GUARDA EN BASE DE DATOS
```
[☰] [Tipo de Pregunta] [Puntos] [Tiempo]     [Guardar] [Salir]
                                              ^^^^^^^^
                                              ¡Solo este guarda!
```
- Valida automáticamente que tengas título
- Si no hay título, abre el modal de configuración
- Guarda todo en la base de datos
- Muestra el PIN generado
- Redirige a "Mis Cuestionarios"

#### Botón "Listo" (Modal de Configuración) - ❌ NO GUARDA EN BASE DE DATOS
```
⚙ Configuración del Cuestionario        [Cancelar] [Listo]
                                                     ^^^^^^
                                                     Solo cierra el modal
```
- Solo cierra el modal de configuración
- Sincroniza el título al header
- **NO guarda en base de datos**
- Úsalo solo para cambiar el título o descripción temporalmente

#### Botón "Cancelar" (Modal de Configuración) - ❌ NO GUARDA
- Cierra el modal sin validar
- No guarda cambios
- No afecta la base de datos

## ✅ Validaciones Automáticas

El sistema valida:
- ✔️ Título obligatorio
- ✔️ Al menos 1 pregunta
- ✔️ Texto en cada pregunta
- ✔️ Al menos 1 respuesta correcta por pregunta
- ✔️ Texto en todas las alternativas

Si falta algo, te mostrará una alerta explicativa.

## 🔢 PIN del Cuestionario

- Se genera automáticamente al crear (6 caracteres)
- Se muestra en el header (campo deshabilitado)
- Botón 🔄 para regenerar (opcional)
- Se usa para que los estudiantes se unan al juego

## 📝 Editar un Cuestionario Existente

1. Ve a **"Mis Cuestionarios"**
2. Haz clic en **"Editar"** en el cuestionario deseado
3. Se abrirá el editor con todos los datos cargados
4. Modifica lo que necesites
5. Haz clic en **"Guardar"** para actualizar

## 🎮 Tipos de Preguntas Explicados

### 📊 Opción Múltiple
```
Pregunta: ¿Cuáles son números pares?
☑️ 2   ✅ (correcto)
☑️ 4   ✅ (correcto)
☐ 3   
☐ 5
```
- El jugador puede seleccionar varias opciones
- Útil para preguntas con múltiples respuestas válidas

### ☝️ Selección Simple
```
Pregunta: ¿Capital de Chile?
☐ Buenos Aires
☑️ Santiago   ✅ (correcto)
☐ Lima
☐ Bogotá
```
- El jugador solo puede seleccionar una opción
- Clásico "selección múltiple" tradicional

### ✅ Verdadero/Falso
```
Pregunta: La Tierra es plana
☐ Verdadero
☑️ Falso   ✅ (correcto)
```
- Solo dos opciones fijas
- No se pueden editar los textos
- Rápido para conceptos simples

## 💾 ¿Dónde se Guarda?

Los datos se guardan en **MySQL** en 3 tablas relacionadas:

```
cuestionarios (título, descripción, imagen, PIN)
    ↓
preguntas (texto, tipo, tiempo, puntos)
    ↓
opciones_respuesta (texto, es_correcta)
```

## 🔐 Seguridad

- ✅ Solo usuarios autenticados pueden crear cuestionarios
- ✅ Solo el creador puede editar sus propios cuestionarios
- ✅ Validaciones en frontend (JavaScript) y backend (Python)
- ✅ PIN único por cuestionario
- ✅ Protección contra inyección SQL (prepared statements)

## 📱 Próximos Pasos

Después de crear un cuestionario podrás:
- 👥 Compartir el PIN con estudiantes
- 🎮 Iniciar una sesión de juego en vivo
- 📊 Ver estadísticas y resultados
- 📂 Organizar en carpetas
- 🌐 Publicar o mantener como borrador

## ❓ Preguntas Frecuentes

**P: ¿Cuántas preguntas puedo crear?**
R: No hay límite, crea todas las que necesites.

**P: ¿Puedo cambiar el PIN?**
R: Sí, usa el botón 🔄 en el header del editor.

**P: ¿Se guardan automáticamente los cambios?**
R: No, debes hacer clic en "Guardar" para guardar en la base de datos.

**P: ¿Puedo agregar imágenes a las preguntas?**
R: Por ahora solo a la portada del cuestionario. Las imágenes en preguntas se agregarán próximamente.

**P: ¿Qué pasa si cierro el navegador sin guardar?**
R: Se perderán los cambios no guardados. ¡Recuerda hacer clic en Guardar!

## 🐛 Solución de Problemas

**Error: "El título es obligatorio"**
→ Abre el modal de configuración y completa el título

**Error: "Debe haber al menos 1 pregunta"**
→ Usa el botón "+ Añadir Pregunta" en el panel lateral

**Error: "La pregunta X no tiene respuesta correcta"**
→ Haz clic en la alternativa correcta para marcarla con ✔️

**No se guarda el cuestionario**
→ Revisa que estés conectado (sesión activa)
→ Verifica la consola del navegador (F12) para errores
→ Asegúrate que la base de datos esté activa

## 🎯 Consejos

- 💡 Da títulos descriptivos a tus cuestionarios
- 🎨 Agrega una imagen de portada atractiva
- ⚡ Ajusta el tiempo según la complejidad
- 🏆 Usa más puntos para preguntas difíciles
- 📝 Escribe preguntas claras y concisas
- ✅ Verifica las respuestas correctas antes de guardar

---

¡Listo! Ya estás preparado para crear cuestionarios increíbles 🚀
