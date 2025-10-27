# 📂 CONFIGURACIÓN GOOGLE DRIVE CON OAUTH (GRATIS)

## ✅ CONFIGURACIÓN COMPLETADA

Tu aplicación ahora está configurada para usar **OAuth 2.0** con Google Drive, lo que significa:

- ✅ **100% GRATIS** - No necesitas pagar Google Workspace
- ✅ Funciona con tu **cuenta personal** de Gmail
- ✅ Los archivos se guardan en **tu Google Drive personal**
- ✅ La autorización se hace **una sola vez** y dura meses

---

## 🚀 CÓMO USAR

### **PASO 1: REINICIAR EL SERVIDOR FLASK**

**MUY IMPORTANTE:** Debes reiniciar Flask para que cargue los cambios.

1. Si Flask está corriendo, presiona `Ctrl + C` para detenerlo
2. Vuelve a iniciar:
   ```bash
   cd Kahoot
   python app.py
   ```

---

### **PASO 2: AUTORIZAR GOOGLE DRIVE (SOLO LA PRIMERA VEZ)**

Tienes **2 formas** de autorizar:

#### **Opción A: Desde el menú de usuario**

1. Inicia sesión en tu aplicación
2. Haz clic en tu **ícono de perfil** (arriba a la derecha)
3. Selecciona **"🔐 Autorizar Google Drive"**
4. Se abrirá una ventana de Google
5. **Selecciona tu cuenta de Gmail**
6. Haz clic en **"Permitir"** o **"Allow"**
7. ¡Listo! Volverás a tu aplicación

#### **Opción B: Cuando intentes exportar por primera vez**

1. Juega un cuestionario
2. Al terminar, ve a **Resultados**
3. Haz clic en **"Exportar a Excel"**
4. Si no estás autorizado, verás un mensaje:
   ```
   ⚠️ Para guardar en Drive, necesitas autorizar primero.
   ```
5. Ve al menú de usuario → **"🔐 Autorizar Google Drive"**
6. Autoriza como se explicó arriba

---

### **PASO 3: EXPORTAR RESULTADOS**

Después de autorizar:

1. Juega cualquier cuestionario (individual o de grupo)
2. Al terminar, haz clic en **"Exportar a Excel"**
3. Verás el mensaje:
   ```
   ✅ Resultados guardados en Google Drive
   ```
4. El archivo se:
   - ✅ **Descargará** automáticamente a tu navegador
   - ✅ **Guardará** en tu Google Drive en la carpeta: `1v1lgL9bQQMNPcfFFmvkHHo0KDpk5MOiV`

---

## 🔑 ARCHIVOS IMPORTANTES

### **Archivos de configuración creados:**

- `oauth_config.json` - Credenciales OAuth de Google
- `token.pickle` - Token de acceso (se crea automáticamente después de autorizar)

⚠️ **IMPORTANTE:** NO subas estos archivos a repositorios públicos (GitHub, etc.)

---

## 🔄 REFRESCAR LA AUTORIZACIÓN

El token de acceso:
- ✅ Se **refresca automáticamente** cuando expira
- ✅ Dura **varios meses** sin necesidad de reautorizar
- ⚠️ Si ves error de autenticación, simplemente vuelve a autorizar

---

## 📂 CARPETA DE GOOGLE DRIVE

Los archivos se guardan en la carpeta con ID:
```
1v1lgL9bQQMNPcfFFmvkHHo0KDpk5MOiV
```

Para acceder a tus archivos:
1. Ve a [Google Drive](https://drive.google.com)
2. Busca la carpeta por ID o nombre
3. Ahí estarán todos los Excel exportados

---

## ❓ PROBLEMAS COMUNES

### **"Error: redirect_uri_mismatch"**

Si ves este error:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Ve a **"Credenciales"**
3. Edita tu **"ID de cliente de OAuth"**
4. Asegúrate de que esté esta URI exacta:
   ```
   http://localhost:5000/oauth2callback
   ```
5. Si tu Flask corre en otro puerto, cámbiala a: `http://localhost:PUERTO/oauth2callback`

### **"Error: access_denied"**

- Significa que denegaste el acceso
- Vuelve a autorizar desde el menú de usuario

### **"Error: invalid_grant"**

- El token expiró o fue revocado
- Elimina `token.pickle` y vuelve a autorizar:
  ```bash
  rm Kahoot/token.pickle
  ```

### **No se guarda en Drive pero sí se descarga**

- Verifica que hayas autorizado primero
- Ve al menú de usuario → **"🔐 Autorizar Google Drive"**

---

## 🎯 VENTAJAS DE ESTA SOLUCIÓN

✅ **Gratis** - No necesitas pagar nada  
✅ **Simple** - Solo autorizas una vez  
✅ **Seguro** - Solo tu cuenta tiene acceso  
✅ **Automático** - El token se refresca solo  
✅ **Personal** - Los archivos van a TU Drive  

---

## 🆘 SOPORTE

Si tienes problemas:
1. Revisa el error en la consola de Flask
2. Verifica que `oauth_config.json` exista
3. Verifica que los URIs de redirección sean correctos
4. Intenta eliminar `token.pickle` y reautorizar

---

## 🎉 ¡TODO LISTO!

Tu aplicación está configurada y lista para usar. Solo falta:
1. Reiniciar Flask
2. Autorizar Google Drive
3. ¡Exportar resultados!

**¡Disfruta de tu aplicación! 🚀**

