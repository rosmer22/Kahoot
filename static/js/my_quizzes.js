(() => {
  // Manejar clic en botón Editar
  document.querySelectorAll('.btn-edit').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const quizId = btn.getAttribute('data-quiz-id');
      if (quizId) {
        window.location.href = `/editor/${quizId}`;
      }
    });
  });

  // Manejar clic en botón Eliminar
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const quizId = btn.getAttribute('data-quiz-id');
      
      if (!quizId) return;
      
      if (confirm('¿Estás seguro de que deseas eliminar este cuestionario?\n\nEsta acción no se puede deshacer.')) {
        // Deshabilitar botón mientras se elimina
        btn.disabled = true;
        btn.textContent = 'Eliminando...';
        
        fetch(`/api/cuestionario/${quizId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(response => response.json())
        .then(result => {
          if (result.success) {
            // Eliminar la card del DOM con animación
            const card = btn.closest('.card');
            card.style.transition = 'opacity 0.3s, transform 0.3s';
            card.style.opacity = '0';
            card.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
              card.remove();
              
              // Si no quedan más cards, mostrar mensaje de estado vacío
              const cardsContainer = document.querySelector('.cards');
              if (cardsContainer && cardsContainer.children.length === 0) {
                location.reload();
              }
            }, 300);
            
            alert(result.message || 'Cuestionario eliminado exitosamente');
          } else {
            alert('Error: ' + (result.error || 'No se pudo eliminar el cuestionario'));
            btn.disabled = false;
            btn.textContent = '🗑️ Eliminar';
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Error al eliminar el cuestionario. Por favor, intenta de nuevo.');
          btn.disabled = false;
          btn.textContent = '🗑️ Eliminar';
        });
      }
    });
  });

  // Hacer que solo las cards de "Completados" sean clickeables
  // Las cards de "Creados por mí" solo deben usar los botones Editar/Eliminar
  document.querySelectorAll('.cards.soft .card').forEach(card => {
    card.addEventListener('click', (e) => {
      const quizId = card.getAttribute('data-quiz-id');
      if (quizId) {
        window.location.href = `/quiz/${quizId}`;
      }
    });
    
    // Añadir cursor pointer solo a las cards de completados
    card.style.cursor = 'pointer';
  });
})();
