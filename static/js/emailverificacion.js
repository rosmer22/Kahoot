document.addEventListener('DOMContentLoaded', function() {
    const codigoInput = document.getElementById('codigo');
    const submitBtn = document.querySelector('.submit-btn');
    const resendBtn = document.getElementById('resend-code-btn');
    const flashContainer = document.querySelector('.flash-messages-container');

    // Función para validar solo números y habilitar botón
    function validateCode() {
        // Eliminar cualquier carácter no numérico
        codigoInput.value = codigoInput.value.replace(/\D/g, '');

        if (codigoInput.value.length === 6) {
            submitBtn.disabled = false;
            submitBtn.classList.add('enabled');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.remove('enabled');
        }
    }

    codigoInput.addEventListener('input', validateCode);

    // Reenviar código
    resendBtn.addEventListener('click', function() {
        resendBtn.disabled = true;
        const originalText = resendBtn.textContent;
        resendBtn.textContent = 'Enviando...';

        fetch("{{ url_for('resend_verification_code') }}", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            flashContainer.innerHTML = '';
            const flashDiv = document.createElement('div');
            flashDiv.textContent = data.message;
            flashDiv.classList.add('flash-message');
            flashDiv.classList.add(data.success ? 'flash-info' : 'flash-error');
            flashContainer.appendChild(flashDiv);

            let countdown = 30;
            resendBtn.textContent = `Reenviar en ${countdown}s`;
            const interval = setInterval(() => {
                countdown--;
                if (countdown > 0) {
                    resendBtn.textContent = `Reenviar en ${countdown}s`;
                } else {
                    clearInterval(interval);
                    resendBtn.disabled = false;
                    resendBtn.textContent = originalText;
                }
            }, 1000);
        });
    });

    // Estado inicial del botón
    submitBtn.disabled = true;
});