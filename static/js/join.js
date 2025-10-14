document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('joinForm');
  const pinInput = document.getElementById('pinInput');
  const errorMessage = document.getElementById('errorMessage');
  const submitBtn = form.querySelector('.btn-join-submit');

  // Convertir automáticamente a mayúsculas
  pinInput.addEventListener('input', function(e) {
    this.value = this.value.toUpperCase();
  });

  // Manejar el envío del formulario
  form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const pin = pinInput.value.trim();
    
    // Validar que el PIN tenga el formato correcto
    if (pin.length < 4) {
      showError('El PIN debe tener al menos 4 caracteres');
      return;
    }

    // Deshabilitar el botón mientras se procesa
    submitBtn.disabled = true;
    submitBtn.querySelector('span').textContent = 'Buscando...';
    hideError();

    // Aquí puedes hacer una llamada al servidor para verificar el PIN
    // Por ahora, simulamos una búsqueda
    setTimeout(() => {
      // Simular búsqueda del cuestionario
      // En producción, aquí harías fetch('/api/quiz/join', { method: 'POST', body: JSON.stringify({ pin }) })
      
      // Ejemplo de respuesta exitosa (comentado para implementar más tarde)
      /*
      fetch('/api/quiz/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ pin: pin })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Redirigir a la página del cuestionario
          window.location.href = `/quiz/${data.quiz_id}`;
        } else {
          showError(data.message || 'PIN no válido. Por favor, verifica e intenta nuevamente.');
          submitBtn.disabled = false;
          submitBtn.querySelector('span').textContent = 'Unirme Ahora';
        }
      })
      .catch(error => {
        showError('Error al conectar con el servidor. Por favor, intenta nuevamente.');
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Unirme Ahora';
      });
      */

      // Por ahora, solo mostrar un mensaje de error simulado
      showError('PIN no encontrado. Por favor, verifica el código e intenta nuevamente.');
      submitBtn.disabled = false;
      submitBtn.querySelector('span').textContent = 'Unirme Ahora';
    }, 1000);
  });

  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    pinInput.focus();
  }

  function hideError() {
    errorMessage.classList.add('hidden');
  }

  // Limpiar el error cuando el usuario empieza a escribir
  pinInput.addEventListener('input', hideError);

  // Enfocar automáticamente el input al cargar
  pinInput.focus();
});
