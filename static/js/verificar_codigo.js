// Función para alternar visibilidad de contraseña
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
        // Cambiar a icono de ojo cerrado (original)
        svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
    }
}

// Validación del formulario
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    const newPassword = document.getElementById('new-password');
    const confirmPassword = document.getElementById('confirm-password');

    form.addEventListener('submit', function(e) {
        // Verificar que las contraseñas coincidan
        if (newPassword.value !== confirmPassword.value) {
            e.preventDefault();
            alert('Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales.');
            confirmPassword.focus();
            return false;
        }

        // Verificar longitud mínima
        if (newPassword.value.length < 8) {
            e.preventDefault();
            alert('La contraseña debe tener al menos 8 caracteres.');
            newPassword.focus();
            return false;
        }

        return true;
    });

    // Validación en tiempo real al escribir en confirmar contraseña
    confirmPassword.addEventListener('input', function() {
        if (this.value && newPassword.value !== this.value) {
            this.setCustomValidity('Las contraseñas no coinciden');
            this.style.borderColor = '#f88';
        } else {
            this.setCustomValidity('');
            this.style.borderColor = '';
        }
    });

    // Actualizar validación cuando cambia la nueva contraseña
    newPassword.addEventListener('input', function() {
        if (confirmPassword.value) {
            confirmPassword.dispatchEvent(new Event('input'));
        }
    });
});
