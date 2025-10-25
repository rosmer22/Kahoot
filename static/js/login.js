document.addEventListener('DOMContentLoaded', function() {
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const submitBtn = document.querySelector('.submit-btn');

    function validateFields() {
        if (email.value.trim() && password.value.trim()) {
            submitBtn.disabled = false;
            submitBtn.classList.add('enabled');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.remove('enabled');
        }
    }

    email.addEventListener('input', validateFields);
    password.addEventListener('input', validateFields);

    // Inicialmente bloqueado
    submitBtn.disabled = true;
    submitBtn.classList.remove('enabled');
});

// Función toggle para mostrar/ocultar contraseña
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.toggle-password');
    const svg = button.querySelector('svg');

    if (input.type === 'password') {
        input.type = 'text';
        svg.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
    } else {
        input.type = 'password';
        svg.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
    }
}