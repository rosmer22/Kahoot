// === Validación de registro USAT ===

// Reglas RegEx
const RE_EMAIL   = /^[0-9]{8}@usat\.pe$/i;
const RE_LENGTH  = /^.{12,}$/;
const RE_UPPER   = /[A-Z]/;
const RE_LOWER   = /[a-z]/;
const RE_DIGIT   = /\d/;
const RE_SPECIAL = /[^A-Za-z0-9]/;

// Elementos
const form = document.querySelector('.auth-form');
const email = document.getElementById('remail');
const username = document.getElementById('ruser');
const pwd = document.getElementById('rpass');
const terms = document.getElementById('terms');
const submitBtn = document.querySelector('.submit-btn');

// Crear feedback dinámico para la contraseña
const feedback = document.createElement('div');
feedback.id = 'passwordFeedback';
feedback.style.marginTop = '0.5rem';
feedback.style.fontSize = '0.9rem';
feedback.style.lineHeight = '1.4';
feedback.style.color = '#000'; // ← texto negro
pwd.parentElement.insertAdjacentElement('afterend', feedback);

// Reglas de contraseña
const rules = [
  { text: 'Mínimo 12 caracteres', test: p => RE_LENGTH.test(p) },
  { text: 'Al menos 1 mayúscula (A–Z)', test: p => RE_UPPER.test(p) },
  { text: 'Al menos 1 minúscula (a–z)', test: p => RE_LOWER.test(p) },
  { text: 'Al menos 1 número (0–9)', test: p => RE_DIGIT.test(p) },
  { text: 'Al menos 1 carácter especial (!@#$%^&*)', test: p => RE_SPECIAL.test(p) },
];

// Renderizar solo los requisitos que faltan
function renderRules(pwdVal) {
  if (!pwdVal) {
    feedback.innerHTML = ''; // vacío si no hay input
    return false;
  }
  const missing = rules.filter(rule => !rule.test(pwdVal));
  if (missing.length === 0) {
    feedback.innerHTML = ''; // todo cumplido → se borra el cuadro
    return true;
  }
  let html = '<p style="margin:0 0 0.3rem 0;">Tu contraseña debe contener:</p><ul style="margin:0; padding-left:1.2rem;">';
  for (const rule of missing) {
    html += `<li>${rule.text}</li>`;
  }
  feedback.innerHTML = html + '</ul>';
  return false;
}

// Validación general del formulario
function validateForm() {
  const passwordValid = renderRules(pwd.value);
  const emailValid = RE_EMAIL.test(email.value);
  const allValid = passwordValid && emailValid && username.value.trim() && terms.checked;

  if (allValid) {
    submitBtn.disabled = false;
    submitBtn.style.backgroundColor = 'var(--color-secundario-amarillo)';
    submitBtn.style.cursor = 'pointer';
  } else {
    submitBtn.disabled = true;
    submitBtn.style.backgroundColor = 'var(--color-gris-boton)';
    submitBtn.style.cursor = 'not-allowed';
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
  feedback.innerHTML = '';
  submitBtn.style.backgroundColor = 'var(--color-gris-boton)';
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