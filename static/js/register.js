const form = document.querySelector('.auth-form');
const email = document.getElementById('remail');
const username = document.getElementById('ruser');
const pwd = document.getElementById('rpass');
const terms = document.getElementById('terms');
const submitBtn = document.querySelector('.submit-btn');
const feedback = document.getElementById('passwordFeedback');

// Regex
const RE_EMAIL = /^\d{8}@usat\.pe$/;
const RE_LENGTH = /^.{8,}$/;
const RE_UPPER = /[A-Z]/;
const RE_LOWER = /[a-z]/;
const RE_SPECIAL = /[^A-Za-z0-9]/;

// Reglas de contraseña
const rules = [
    { text: 'Mínimo 8 caracteres', test: p => RE_LENGTH.test(p) },
    { text: 'Al menos 1 mayúscula (A–Z)', test: p => RE_UPPER.test(p) },
    { text: 'Al menos 1 minúscula (a–z)', test: p => RE_LOWER.test(p) },
    { text: 'Al menos 1 carácter especial (!@#$%^&*)', test: p => RE_SPECIAL.test(p) },
];

// Render feedback con deslizamiento
function renderRules(pwdVal) {
    if (!pwdVal) {
        feedback.innerHTML = '';
        feedback.style.maxHeight = '0';
        return false;
    }
    const missing = rules.filter(r => !r.test(pwdVal));
    if (missing.length === 0) {
        feedback.innerHTML = '';
        feedback.style.maxHeight = '0';
        return true;
    }
    let html = '<ul>';
    missing.forEach(r => html += `<li>${r.text}</li>`);
    html += '</ul>';
    feedback.innerHTML = html;
    feedback.style.maxHeight = '200px';
    return false;
}

// Validación general
function validateForm() {
    const emailValid = RE_EMAIL.test(email.value.trim());
    const pwdValid = renderRules(pwd.value);
    const allValid = emailValid && pwdValid && username.value.trim() && terms.checked;

    if (allValid) {
        submitBtn.disabled = false;
        submitBtn.classList.add('enabled');
    } else {
        submitBtn.disabled = true;
        submitBtn.classList.remove('enabled');
    }
}

// Eventos
email.addEventListener('input', validateForm);
username.addEventListener('input', validateForm);
pwd.addEventListener('input', validateForm);
terms.addEventListener('change', validateForm);

// Estado inicial
window.addEventListener('DOMContentLoaded', () => {
    submitBtn.disabled = true;
    submitBtn.classList.remove('enabled');
    feedback.innerHTML = '';
    feedback.style.maxHeight = '0';
});

// Mostrar / ocultar contraseña
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