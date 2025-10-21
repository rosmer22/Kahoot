document.addEventListener('DOMContentLoaded', function() {
    const resendBtn = document.getElementById('resend-code-btn');
    const flashContainer = document.querySelector('.flash-messages-container');
    const codigoInput = document.getElementById('codigo');
    const submitBtn = document.querySelector('.submit-btn');

    // === VALIDACIÓN DINÁMICA DEL CÓDIGO ===
    function validarCodigo() {
        const value = codigoInput.value.trim();
        const isValid = /^\d{6}$/.test(value);

        if (isValid) {
            submitBtn.disabled = false;
            submitBtn.style.backgroundColor = 'var(--color-secundario-amarillo)';
            submitBtn.style.cursor = 'pointer';
        } else {
            submitBtn.disabled = true;
            submitBtn.style.backgroundColor = 'var(--color-gris-boton)';
            submitBtn.style.cursor = 'not-allowed';
        }
    }

    // Escuchar cambios en el campo
    codigoInput.addEventListener('input', validarCodigo);

    // Estado inicial
    submitBtn.disabled = true;
    submitBtn.style.backgroundColor = 'var(--color-gris-boton)';
    submitBtn.style.cursor = 'not-allowed';

    // === REENVÍO DE CÓDIGO (tu lógica existente) ===
    resendBtn.addEventListener('click', function() {
        // Deshabilitar el botón y mostrar estado de carga
        resendBtn.disabled = true;
        const originalText = resendBtn.textContent;
        resendBtn.textContent = 'Enviando...';

        fetch(resendVerificationCodeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Limpiar mensajes anteriores
            flashContainer.innerHTML = '';

            // Crear y mostrar el nuevo mensaje flash
            const flashDiv = document.createElement('div');
            flashDiv.textContent = data.message;
            flashDiv.classList.add('flash-message');
            if (data.success) {
                flashDiv.classList.add('flash-info'); // O 'flash-success'
            } else {
                flashDiv.classList.add('flash-error');
            }
            flashContainer.appendChild(flashDiv);

            // Iniciar un temporizador para reactivar el botón
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
});
