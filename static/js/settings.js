// Variables de estado
let isEditingUsername = false;
let isEditingEmail = false;
let originalUsername = '';
let originalEmail = '';

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
  const usernameDisplay = document.getElementById('username-display');
  const emailDisplay = document.getElementById('email-display');
  
  if (usernameDisplay) originalUsername = usernameDisplay.textContent;
  if (emailDisplay) originalEmail = emailDisplay.textContent;
  
  // Event listener para el botón de logout
  const logoutBtn = document.querySelector('.btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', function() {
      const logoutUrl = this.getAttribute('data-logout-url');
      if (logoutUrl) {
        window.location.href = logoutUrl;
      }
    });
  }
});

// Editar nombre de usuario
function editUsername() {
  const display = document.getElementById('username-display');
  const input = document.getElementById('username');
  const saveBtn = document.getElementById('saveProfileBtn');
  
  if (!isEditingUsername) {
    // Activar modo edición
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
    input.select();
    isEditingUsername = true;
    saveBtn.style.display = 'inline-block';
  }
}

// Editar email
function editEmail() {
  const display = document.getElementById('email-display');
  const input = document.getElementById('email');
  const saveBtn = document.getElementById('saveProfileBtn');
  
  if (!isEditingEmail) {
    // Activar modo edición
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
    input.select();
    isEditingEmail = true;
    saveBtn.style.display = 'inline-block';
  }
}

// Verificar si hay campos en edición
function checkEditState() {
  const saveBtn = document.getElementById('saveProfileBtn');
  if (!isEditingUsername && !isEditingEmail) {
    saveBtn.style.display = 'none';
  }
}

// Validar username
function validateUsername(username) {
  if (!username || username.trim().length === 0) {
    return { valid: false, message: 'El nombre de usuario no puede estar vacío' };
  }
  if (username.length < 3) {
    return { valid: false, message: 'El nombre de usuario debe tener al menos 3 caracteres' };
  }
  if (username.length > 50) {
    return { valid: false, message: 'El nombre de usuario no puede exceder 50 caracteres' };
  }
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return { valid: false, message: 'El nombre de usuario solo puede contener letras, números y guiones bajos' };
  }
  return { valid: true };
}

// Validar email
function validateEmail(email) {
  if (!email || email.trim().length === 0) {
    return { valid: false, message: 'El correo electrónico no puede estar vacío' };
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: 'Por favor ingresa un correo electrónico válido' };
  }
  return { valid: true };
}

// Guardar perfil
async function saveProfile() {
  const usernameInput = document.getElementById('username');
  const emailInput = document.getElementById('email');
  const usernameDisplay = document.getElementById('username-display');
  const emailDisplay = document.getElementById('email-display');
  const saveBtn = document.getElementById('saveProfileBtn');
  
  const newUsername = usernameInput.value.trim();
  const newEmail = emailInput.value.trim();
  
  // Validar username si está siendo editado
  if (isEditingUsername) {
    const usernameValidation = validateUsername(newUsername);
    if (!usernameValidation.valid) {
      showAlert(usernameValidation.message, 'error');
      return;
    }
  }
  
  // Validar email si está siendo editado
  if (isEditingEmail) {
    const emailValidation = validateEmail(newEmail);
    if (!emailValidation.valid) {
      showAlert(emailValidation.message, 'error');
      return;
    }
  }
  
  // Preparar datos para enviar
  const data = {};
  if (isEditingUsername && newUsername !== originalUsername) {
    data.username = newUsername;
  }
  if (isEditingEmail && newEmail !== originalEmail) {
    data.email = newEmail;
  }
  
  // Si no hay cambios
  if (Object.keys(data).length === 0) {
    showAlert('No hay cambios para guardar', 'info');
    return;
  }
  
  // Deshabilitar botón mientras se procesa
  saveBtn.disabled = true;
  saveBtn.textContent = 'Guardando...';
  
  try {
    const response = await fetch('/update_profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    if (result.success) {
      showAlert(result.message, 'success');
      
      // Actualizar valores originales y displays
      if (data.username) {
        originalUsername = newUsername;
        usernameDisplay.textContent = newUsername;
      }
      if (data.email) {
        originalEmail = newEmail;
        emailDisplay.textContent = newEmail;
      }
      
      // Volver a modo vista
      if (isEditingUsername) {
        usernameInput.style.display = 'none';
        usernameDisplay.style.display = 'block';
        isEditingUsername = false;
      }
      if (isEditingEmail) {
        emailInput.style.display = 'none';
        emailDisplay.style.display = 'block';
        isEditingEmail = false;
      }
      
      saveBtn.style.display = 'none';
    } else {
      showAlert(result.message, 'error');
    }
  } catch (error) {
    showAlert('Error al guardar los cambios', 'error');
    console.error('Error:', error);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = 'Guardar Cambios';
  }
}

// Cambiar contraseña
async function changePassword(event) {
  event.preventDefault();
  
  const oldPassword = document.getElementById('oldPassword').value;
  const newPassword = document.getElementById('newPassword').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  // Validaciones
  if (!oldPassword || !newPassword || !confirmPassword) {
    showAlert('Por favor completa todos los campos', 'error');
    return false;
  }
  
  if (newPassword.length < 6) {
    showAlert('La nueva contraseña debe tener al menos 6 caracteres', 'error');
    return false;
  }
  
  if (newPassword !== confirmPassword) {
    showAlert('Las contraseñas no coinciden', 'error');
    return false;
  }
  
  if (oldPassword === newPassword) {
    showAlert('La nueva contraseña debe ser diferente a la anterior', 'error');
    return false;
  }
  
  const submitBtn = event.target.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Guardando...';
  
  try {
    const response = await fetch('/change_password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      showAlert(result.message, 'success');
      document.getElementById('passwordForm').reset();
    } else {
      showAlert(result.message, 'error');
    }
  } catch (error) {
    showAlert('Error al cambiar la contraseña. Por favor intenta de nuevo.', 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Guardar Contraseña';
  }
  
  return false;
}

// Mostrar/ocultar contraseña
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const button = input.parentElement.querySelector('.toggle-password');
  const svg = button.querySelector('svg');
  
  if (input.type === 'password') {
    input.type = 'text';
    // Cambiar a icono de ojo abierto
    svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
  } else {
    input.type = 'password';
    // Cambiar a icono de ojo cerrado
    svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
  }
}

// Mostrar alertas usando el sistema global de flash messages
function showAlert(message, type) {
  // Crear contenedor si no existe
  let flashContainer = document.querySelector('.flash-messages');
  if (!flashContainer) {
    flashContainer = document.createElement('div');
    flashContainer.className = 'flash-messages';
    document.body.appendChild(flashContainer);
  }
  
  // Crear alerta con el estilo del sistema global
  const alert = document.createElement('div');
  alert.className = `flash-message flash-${type}`;
  alert.innerHTML = `${message}<button class="flash-close" onclick="this.parentElement.remove()">&times;</button>`;
  
  // Agregar al contenedor
  flashContainer.appendChild(alert);
  
  // Auto-cerrar después de 5 segundos
  setTimeout(() => {
    alert.style.opacity = '0';
    setTimeout(() => alert.remove(), 300);
  }, 5000);
}
