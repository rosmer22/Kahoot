// Quiz Details JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Botón de iniciar quiz
  const btnStartQuiz = document.querySelector('.btn-start-quiz');
  if (btnStartQuiz) {
    btnStartQuiz.addEventListener('click', function() {
      // Aquí puedes agregar la lógica para iniciar el quiz
      console.log('Iniciando quiz...');
      // Por ejemplo: window.location.href = '/play/' + quizId;
    });
  }

  // Botón de editar
  const btnEdit = document.querySelector('.btn-edit');
  if (btnEdit) {
    btnEdit.addEventListener('click', function() {
      // Redirigir al editor
      console.log('Editando quiz...');
      // Por ejemplo: window.location.href = '/editor/' + quizId;
    });
  }

  // Botón de favorito
  const btnFavorite = document.querySelector('.btn-favorite');
  if (btnFavorite) {
    btnFavorite.addEventListener('click', function() {
      const icon = this.querySelector('i');
      if (icon.classList.contains('far')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        console.log('Añadido a favoritos');
        // Aquí puedes agregar la lógica para guardar en favoritos
      } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        console.log('Removido de favoritos');
        // Aquí puedes agregar la lógica para remover de favoritos
      }
    });
  }

  // Click en las tarjetas de preguntas
  const questionCards = document.querySelectorAll('.question-card:not(.placeholder)');
  questionCards.forEach((card, index) => {
    card.addEventListener('click', function() {
      console.log(`Pregunta ${index + 1} clickeada`);
      // Aquí puedes agregar la lógica para mostrar detalles de la pregunta
      // o navegar a una vista de edición de pregunta específica
    });
  });
});
