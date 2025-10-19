// ===== Sistema de Gestión de Preguntas =====
let questions = []; // Array para almacenar todas las preguntas
let currentQuestionIndex = 0; // Índice de la pregunta actual

// ===== Panel Lateral de Preguntas =====
(function(){
  const sidebar = document.getElementById('questionsSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const toggleBtn = document.getElementById('toggleSidebarBtn');
  const closeBtn = document.getElementById('closeSidebarBtn');
  const sidebarContent = document.querySelector('.sidebar-content');
  const sidebarHeader = document.querySelector('.sidebar-header h3');
  const addQuestionBtn = document.getElementById('addQuestionBtn');

  function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('active');
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  }

  // Crear tarjeta de pregunta para el sidebar
  function createQuestionCard(question, index) {
    const card = document.createElement('div');
    card.className = 'question-card';
    if (index === currentQuestionIndex) {
      card.classList.add('active');
    }
    card.dataset.index = index;

    // Badge de puntos
    const pointsBadge = document.createElement('div');
    pointsBadge.className = 'question-points';
    pointsBadge.innerHTML = `✔ ${question.points} ${question.points === 1 ? 'punto' : 'puntos'}`;

    // Crear preview del texto de la pregunta
    const previewText = document.createElement('div');
    previewText.className = 'question-preview-text';
    previewText.textContent = question.text || '';

    // Crear preview de las respuestas
    const previewAnswers = document.createElement('div');
    previewAnswers.className = 'question-preview-answers';
    
    question.answers.forEach(answer => {
      const answerDiv = document.createElement('div');
      answerDiv.className = 'preview-answer';
      if (answer.isCorrect) {
        answerDiv.classList.add('correct');
      }
      previewAnswers.appendChild(answerDiv);
    });

    // Preview container
    const preview = document.createElement('div');
    preview.className = 'question-preview';
    preview.appendChild(previewText);
    preview.appendChild(previewAnswers);

    // Botón de eliminar
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-question-btn';
    deleteBtn.title = 'Eliminar pregunta';
    deleteBtn.textContent = '🗑';
    deleteBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      deleteQuestion(index);
    });

    card.appendChild(pointsBadge);
    card.appendChild(preview);
    card.appendChild(deleteBtn);

    // Click para cambiar a esta pregunta
    card.addEventListener('click', function() {
      switchToQuestion(index);
    });

    return card;
  }

  // Renderizar todas las preguntas en el sidebar
  function renderSidebar() {
    sidebarContent.innerHTML = '';
    
    questions.forEach((question, index) => {
      const card = createQuestionCard(question, index);
      sidebarContent.appendChild(card);
    });

    // Actualizar el título con el número de preguntas
    const count = questions.length;
    sidebarHeader.textContent = count === 1 ? '1 Pregunta' : `${count} Preguntas`;
  }

  // Agregar nueva pregunta
  function addNewQuestion() {
    // Primero guardar la pregunta actual
    saveCurrentQuestion();
    
    const newQuestion = {
      text: '',
      type: 'multiple',
      answers: [
        { text: '', isCorrect: false },
        { text: '', isCorrect: false },
        { text: '', isCorrect: false },
        { text: '', isCorrect: false }
      ],
      points: 1,
      time: 30
    };

    questions.push(newQuestion);
    currentQuestionIndex = questions.length - 1;
    renderSidebar();
    loadQuestion(currentQuestionIndex);
  }

  // Eliminar pregunta
  function deleteQuestion(index) {
    if (questions.length <= 1) {
      alert('Debe haber al menos 1 pregunta en el cuestionario');
      return;
    }

    questions.splice(index, 1);
    
    // Ajustar el índice actual si es necesario
    if (currentQuestionIndex >= questions.length) {
      currentQuestionIndex = questions.length - 1;
    }
    
    renderSidebar();
    loadQuestion(currentQuestionIndex);
  }

  // Cambiar a una pregunta específica
  function switchToQuestion(index) {
    saveCurrentQuestion();
    currentQuestionIndex = index;
    loadQuestion(index);
    renderSidebar();
    closeSidebar();
  }

  // Guardar la pregunta actual antes de cambiar
  window.saveCurrentQuestion = function() {
    if (questions.length === 0) return;

    const questionText = document.querySelector('.question-text');
    const questionTypeSelect = document.querySelector('.select-question-type');
    const pointsSelect = document.querySelector('.select-points');
    const timeSelect = document.querySelector('.select-time');
    const answersContainer = document.getElementById('answersContainer');
    const answerElements = answersContainer.querySelectorAll('.answer');

    const currentQuestion = questions[currentQuestionIndex];
    currentQuestion.text = questionText ? questionText.value : '';
    currentQuestion.type = questionTypeSelect ? questionTypeSelect.value : 'multiple';
    currentQuestion.points = pointsSelect ? parseInt(pointsSelect.value) : 1;
    currentQuestion.time = timeSelect ? parseInt(timeSelect.value) : 30;
    currentQuestion.answers = [];

    answerElements.forEach(answerEl => {
      const input = answerEl.querySelector('.answer-input');
      const isCorrect = answerEl.classList.contains('selected');
      currentQuestion.answers.push({
        text: input ? input.value : '',
        isCorrect: isCorrect
      });
    });
  };

  // Cargar una pregunta en el editor
  window.loadQuestion = function(index) {
    if (index < 0 || index >= questions.length) return;

    const question = questions[index];
    const questionText = document.querySelector('.question-text');
    const questionTypeSelect = document.querySelector('.select-question-type');
    const pointsSelect = document.querySelector('.select-points');
    const timeSelect = document.querySelector('.select-time');
    const answersContainer = document.getElementById('answersContainer');

    // Limpiar completamente el texto de la pregunta
    if (questionText) questionText.value = question.text || '';
    if (pointsSelect) pointsSelect.value = question.points;
    if (timeSelect) timeSelect.value = question.time;
    
    // Limpiar el contenedor de respuestas completamente
    answersContainer.innerHTML = '';
    
    // Actualizar el tipo de pregunta
    if (questionTypeSelect) questionTypeSelect.value = question.type;

    // Recrear las alternativas según el tipo
    const answerCount = question.answers.length;
    
    if (question.type === 'verdadero-falso') {
      // Crear alternativas de Verdadero/Falso
      const verdadero = document.createElement('div');
      verdadero.className = 'answer pink';
      verdadero.innerHTML = `
        <div class="answer-head">
          <button class="tiny-btn delete-answer-btn" title="Eliminar" style="display:none;">🗑</button>
          <span class="check">✔</span>
        </div>
        <input class="answer-input" placeholder="Escriba la alternativa aqui" value="Verdadero" readonly>
      `;
      
      const falso = document.createElement('div');
      falso.className = 'answer pink';
      falso.innerHTML = `
        <div class="answer-head">
          <button class="tiny-btn delete-answer-btn" title="Eliminar" style="display:none;">🗑</button>
          <span class="check">✔</span>
        </div>
        <input class="answer-input" placeholder="Escriba la alternativa aqui" value="Falso" readonly>
      `;
      
      answersContainer.appendChild(verdadero);
      answersContainer.appendChild(falso);
      
      // Marcar la correcta
      if (question.answers[0] && question.answers[0].isCorrect) {
        verdadero.classList.add('selected');
      }
      if (question.answers[1] && question.answers[1].isCorrect) {
        falso.classList.add('selected');
      }
    } else {
      // Crear alternativas normales
      for (let i = 0; i < answerCount; i++) {
        const answer = document.createElement('div');
        answer.className = 'answer pink';
        answer.innerHTML = `
          <div class="answer-head">
            <button class="tiny-btn delete-answer-btn" title="Eliminar">🗑</button>
            <span class="check">✔</span>
          </div>
          <input class="answer-input" placeholder="Escriba la alternativa aqui" value="">
        `;
        
        // Establecer el texto y si es correcta
        const input = answer.querySelector('.answer-input');
        if (input && question.answers[i]) {
          input.value = question.answers[i].text || '';
        }
        
        if (question.answers[i] && question.answers[i].isCorrect) {
          answer.classList.add('selected');
        }
        
        answersContainer.appendChild(answer);
      }
    }
    
    // Re-adjuntar eventos a todas las alternativas
    const allAnswers = answersContainer.querySelectorAll('.answer');
    allAnswers.forEach(answer => {
      // Evento de clic para seleccionar
      answer.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-answer-btn') || 
            e.target.classList.contains('answer-input') ||
            e.target.tagName === 'INPUT') {
          return;
        }
        
        const isSelected = this.classList.contains('selected');
        const currentMode = questionTypeSelect ? questionTypeSelect.value : 'multiple';
        
        if (currentMode === 'multiple') {
          // Opción Múltiple: Se pueden seleccionar varias
          if (isSelected) {
            this.classList.remove('selected');
          } else {
            this.classList.add('selected');
          }
        } else {
          // Selección Simple o Verdadero/Falso: Solo una
          allAnswers.forEach(ans => ans.classList.remove('selected'));
          this.classList.add('selected');
        }
      });

      // Evento de eliminar (solo para alternativas normales)
      const deleteBtn = answer.querySelector('.delete-answer-btn');
      if (deleteBtn && question.type !== 'verdadero-falso') {
        deleteBtn.addEventListener('click', function(e) {
          e.stopPropagation();
          const currentCount = answersContainer.querySelectorAll('.answer').length;
          if (currentCount <= 2) {
            alert('Debe haber al menos 2 alternativas');
            return;
          }
          answer.remove();
        });
      }
    });
  };

  // Event listeners
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        saveCurrentQuestion();
        renderSidebar();
        openSidebar();
      }
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', closeSidebar);
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  if (addQuestionBtn) {
    addQuestionBtn.addEventListener('click', function() {
      addNewQuestion();
      closeSidebar();
    });
  }

  // Inicializar con una pregunta por defecto
  if (window.cuestionarioData && window.cuestionarioData.preguntas && window.cuestionarioData.preguntas.length > 0) {
    // Cargar preguntas existentes
    questions = window.cuestionarioData.preguntas;
    currentQuestionIndex = 0;
    renderSidebar();
    loadQuestion(0);
  } else {
    // Agregar una pregunta por defecto
    addNewQuestion();
  }
})();

// ===== Generador de PIN =====
(function(){
  const pinInput = document.querySelector('.pin-input');
  const refreshBtn = document.querySelector('.refresh-button');

  // Generar PIN aleatorio de 4 caracteres (números y letras)
  function generatePIN() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let pin = '';
    for (let i = 0; i < 4; i++) {
      pin += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return pin;
  }

  // Establecer PIN inicial
  if (pinInput) {
    pinInput.value = generatePIN();
  }

  // Refrescar PIN al hacer clic
  if (refreshBtn) {
    refreshBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (pinInput) {
        pinInput.value = generatePIN();
      }
    });
  }
})();

// ===== Modal de Configuración =====
(function(){
  const modal = document.getElementById('config-modal');
  const backdrop = document.getElementById('config-backdrop');
  const btnCancel = document.getElementById('cfgCancel');
  const btnDone = document.getElementById('cfgDone');
  const tabs = document.querySelectorAll('.cfg-tab');
  const panels = document.querySelectorAll('.tab-panel');
  const titleInputEditor = document.querySelector('.title-input-editor'); // Input del header (readonly)
  const cfgTitleInput = document.getElementById('cfgTitleInput'); // Input del modal
  const cfgDescInput = document.getElementById('cfgDescInput');
  const drop = document.getElementById('cfgDrop');
  const file = document.getElementById('cfgFile');
  const cuestionarioIdInput = document.getElementById('cuestionario_id');

  function open(){ modal.classList.remove('hidden'); backdrop.classList.remove('hidden'); }
  function close(){ modal.classList.add('hidden'); backdrop.classList.add('hidden'); }

  // Validar que el título esté completo
  function validateForm() {
    const title = cfgTitleInput.value.trim();
    
    if (!title) {
      alert('Por favor, ingresa un título para el cuestionario.');
      cfgTitleInput.focus();
      return false;
    }
    
    return true;
  }

  // Tab switching
  tabs.forEach(t => t.addEventListener('click', () => {
    tabs.forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    const key = t.getAttribute('data-tab');
    panels.forEach(p => p.classList.toggle('hidden', p.getAttribute('data-panel') !== key));
  }));

  // Done/Cancel - Solo sincroniza el título, NO guarda en base de datos
  btnCancel && btnCancel.addEventListener('click', () => { 
    close(); 
  });
  
  btnDone && btnDone.addEventListener('click', () => {
    if (!validateForm()) {
      return;
    }
    // Sincronizar el título del modal al input del header
    if (cfgTitleInput && titleInputEditor) {
      titleInputEditor.value = cfgTitleInput.value;
    }
    
    // Solo cierra el modal, NO guarda en base de datos
    close();
  });

  // Drag & drop for cover
  ;['dragenter','dragover'].forEach(ev => drop && drop.addEventListener(ev, (e)=>{e.preventDefault(); drop.style.background='#f4f4f4';}));
  ;['dragleave','drop'].forEach(ev => drop && drop.addEventListener(ev, (e)=>{e.preventDefault(); drop.style.background='';}));
  drop && drop.addEventListener('drop', (e)=>{
    const f = e.dataTransfer.files[0]; if (!f) return;
    file.files = e.dataTransfer.files;
    drop.querySelector('.drop-inner').innerHTML = '<div class="drop-icon">✅</div><div>'+f.name+'</div>';
  });
  drop && drop.addEventListener('click', ()=> file && file.click());
  file && file.addEventListener('change', ()=>{
    const f = file.files[0]; if (f) drop.querySelector('.drop-inner').innerHTML = '<div class="drop-icon">✅</div><div>'+f.name+'</div>';
  });

  // Auto-open on editor load solo si es un nuevo cuestionario
  if (!window.cuestionarioData) {
    open();
  }

  // Cargar datos del cuestionario si existen
  if (window.cuestionarioData) {
    const data = window.cuestionarioData;
    if (cfgTitleInput) cfgTitleInput.value = data.titulo || '';
    if (cfgDescInput) cfgDescInput.value = data.descripcion || '';
    if (titleInputEditor) titleInputEditor.value = data.titulo || '';
    
    // Cargar el PIN en el header
    const pinInput = document.querySelector('.pin-input');
    if (pinInput && data.pin) {
      pinInput.value = data.pin;
    }
    
    // Cargar el estado de privacidad
    const cfgPublico = document.getElementById('cfgPublico');
    const cfgPrivado = document.getElementById('cfgPrivado');
    if (data.estado === 'privado' && cfgPrivado) {
      cfgPrivado.checked = true;
    } else if (cfgPublico) {
      cfgPublico.checked = true;
    }
  }

  // Make "Configuración" button reopen modal
  document.querySelectorAll('.pill, .btn-config-inline, .btn-dark').forEach(btn => {
    if (btn.textContent.trim().toLowerCase().includes('configuracion')) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        open();
      });
    }
  });
})();

// ===== Control de Selección de Respuestas =====
(function(){
  const questionTypeSelect = document.querySelector('.select-question-type');
  const answersContainer = document.getElementById('answersContainer');
  const addAnswerBtn = document.getElementById('addAnswerBtn');
  let currentMode = 'multiple'; // Por defecto: opción múltiple
  const MAX_ANSWERS = 5;
  const MIN_ANSWERS = 2;

  // Crear una alternativa
  function createAnswer(text = '') {
    const answer = document.createElement('div');
    answer.className = 'answer pink';
    answer.innerHTML = `
      <div class="answer-head">
        <button class="tiny-btn delete-answer-btn" title="Eliminar">🗑</button>
        <span class="check">✔</span>
      </div>
      <input class="answer-input" placeholder="Escriba la alternativa aqui" value="${text}">
    `;
    return answer;
  }

  // Actualizar el estado del botón agregar
  function updateAddButton() {
    const currentCount = answersContainer.querySelectorAll('.answer').length;
    
    // Si es verdadero/falso, ocultar el botón
    if (currentMode === 'verdadero-falso') {
      addAnswerBtn.style.display = 'none';
      return;
    }
    
    addAnswerBtn.style.display = 'inline-block';
    
    if (currentCount >= MAX_ANSWERS) {
      addAnswerBtn.disabled = true;
      addAnswerBtn.textContent = `Máximo ${MAX_ANSWERS} alternativas`;
      addAnswerBtn.style.opacity = '0.5';
      addAnswerBtn.style.cursor = 'not-allowed';
    } else {
      addAnswerBtn.disabled = false;
      addAnswerBtn.textContent = '+ Agregar Alternativa';
      addAnswerBtn.style.opacity = '1';
      addAnswerBtn.style.cursor = 'pointer';
    }
  }

  // Inicializar con 4 alternativas
  function initializeAnswers() {
    for (let i = 0; i < 4; i++) {
      answersContainer.appendChild(createAnswer());
    }
    attachAllEvents();
    updateAddButton();
  }

  // Crear alternativas de Verdadero/Falso
  function createTrueFalseAnswers() {
    // Limpiar alternativas existentes
    answersContainer.innerHTML = '';
    
    // Crear exactamente 2 alternativas
    const verdadero = createAnswer('Verdadero');
    const falso = createAnswer('Falso');
    
    // Deshabilitar inputs para que no se puedan editar
    verdadero.querySelector('.answer-input').setAttribute('readonly', 'readonly');
    falso.querySelector('.answer-input').setAttribute('readonly', 'readonly');
    
    answersContainer.appendChild(verdadero);
    answersContainer.appendChild(falso);
    
    attachAllEvents();
    
    // Ocultar botones de eliminar en modo verdadero/falso
    const deleteButtons = answersContainer.querySelectorAll('.delete-answer-btn');
    deleteButtons.forEach(btn => {
      btn.style.display = 'none';
    });
  }

  // Restaurar alternativas normales
  function restoreNormalAnswers() {
    answersContainer.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      answersContainer.appendChild(createAnswer());
    }
    attachAllEvents();
  }

  // Función para manejar el clic en una respuesta
  function handleAnswerClick(answerElement) {
    const isSelected = answerElement.classList.contains('selected');
    
    if (currentMode === 'multiple') {
      // Opción Múltiple: Se pueden seleccionar varias
      if (isSelected) {
        answerElement.classList.remove('selected');
      } else {
        answerElement.classList.add('selected');
      }
    } else {
      // Selección Simple o Verdadero/Falso: Solo una
      const allAnswers = answersContainer.querySelectorAll('.answer');
      allAnswers.forEach(ans => ans.classList.remove('selected'));
      answerElement.classList.add('selected');
    }
  }

  // Eliminar una alternativa
  function deleteAnswer(answerElement) {
    // No permitir eliminar en modo verdadero/falso
    if (currentMode === 'verdadero-falso') {
      return;
    }
    
    const currentCount = answersContainer.querySelectorAll('.answer').length;
    
    if (currentCount <= MIN_ANSWERS) {
      alert(`Debe haber al menos ${MIN_ANSWERS} alternativas`);
      return;
    }
    
    answerElement.remove();
    updateAddButton();
  }

  // Adjuntar eventos a TODAS las alternativas
  function attachAllEvents() {
    // Remover todos los event listeners existentes clonando el contenedor
    const answers = answersContainer.querySelectorAll('.answer');
    
    answers.forEach(answer => {
      // Clonar para eliminar listeners antiguos
      const newAnswer = answer.cloneNode(true);
      answer.parentNode.replaceChild(newAnswer, answer);
    });

    // Ahora agregar eventos a todas las alternativas
    const freshAnswers = answersContainer.querySelectorAll('.answer');
    
    freshAnswers.forEach(answer => {
      // Evento de clic para seleccionar
      answer.addEventListener('click', function(e) {
        // No seleccionar si se hizo clic en el botón de eliminar o en el input
        if (e.target.classList.contains('delete-answer-btn') || 
            e.target.classList.contains('answer-input') ||
            e.target.tagName === 'INPUT') {
          return;
        }
        handleAnswerClick(this);
      });

      // Evento de eliminar
      const deleteBtn = answer.querySelector('.delete-answer-btn');
      if (deleteBtn && currentMode !== 'verdadero-falso') {
        deleteBtn.addEventListener('click', function(e) {
          e.stopPropagation();
          deleteAnswer(answer);
        });
      }
    });
  }

  // Agregar nueva alternativa
  if (addAnswerBtn) {
    addAnswerBtn.addEventListener('click', function() {
      const currentCount = answersContainer.querySelectorAll('.answer').length;
      
      if (currentCount < MAX_ANSWERS && currentMode !== 'verdadero-falso') {
        const newAnswer = createAnswer();
        answersContainer.appendChild(newAnswer);
        attachAllEvents(); // Re-adjuntar eventos a TODAS las alternativas
        updateAddButton();
      }
    });
  }

  // Cambiar modo según el tipo de pregunta seleccionado
  if (questionTypeSelect) {
    questionTypeSelect.addEventListener('change', function() {
      const previousMode = currentMode;
      currentMode = this.value;
      
      // Si cambió a verdadero/falso
      if (currentMode === 'verdadero-falso') {
        createTrueFalseAnswers();
      } else if (previousMode === 'verdadero-falso') {
        // Si salió del modo verdadero/falso, restaurar alternativas normales
        restoreNormalAnswers();
      } else {
        // Limpiar todas las selecciones al cambiar de tipo
        const allAnswers = answersContainer.querySelectorAll('.answer');
        allAnswers.forEach(ans => ans.classList.remove('selected'));
      }
      
      updateAddButton();
      
      // Guardar cambios automáticamente
      if (typeof saveCurrentQuestion === 'function') {
        saveCurrentQuestion();
      }
    });
  }

  // NO inicializar alternativas aquí - lo hace loadQuestion()
})();

// Auto-guardar al escribir en la pregunta
document.addEventListener('DOMContentLoaded', function() {
  const questionText = document.querySelector('.question-text');
  if (questionText) {
    questionText.addEventListener('blur', function() {
      if (typeof saveCurrentQuestion === 'function') {
        saveCurrentQuestion();
      }
    });
  }

  // Conectar el botón Guardar del header
  const saveBtn = document.getElementById('saveQuizBtn');
  if (saveBtn) {
    saveBtn.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Guardar la pregunta actual
      if (typeof saveCurrentQuestion === 'function') {
        saveCurrentQuestion();
      }
      
      // Validar que haya título
      const cfgTitleInput = document.getElementById('cfgTitleInput');
      const titulo = cfgTitleInput ? cfgTitleInput.value.trim() : '';
      
      if (!titulo) {
        alert('Por favor, configura el título del cuestionario primero.\nHaz clic en "Configuración".');
        // Abrir el modal de configuración
        const modal = document.getElementById('config-modal');
        const backdrop = document.getElementById('config-backdrop');
        if (modal && backdrop) {
          modal.classList.remove('hidden');
          backdrop.classList.remove('hidden');
          cfgTitleInput.focus();
        }
        return;
      }
      
      // Guardar el cuestionario
      guardarCuestionario();
    });
  }
});

// ===== Función para Guardar el Cuestionario =====
function guardarCuestionario() {
  // Guardar la pregunta actual antes de enviar
  if (typeof saveCurrentQuestion === 'function') {
    saveCurrentQuestion();
  }

  // Obtener datos del modal de configuración
  const titulo = document.getElementById('cfgTitleInput').value.trim();
  const descripcion = document.getElementById('cfgDescInput').value.trim();
  const imagenFile = document.getElementById('cfgFile').files[0];
  const cuestionarioId = document.getElementById('cuestionario_id').value;
  
  // Obtener configuración de privacidad - verificar cuál radio está seleccionado
  const radioPrivacidad = document.querySelector('input[name="privacy"]:checked');
  const estado = radioPrivacidad ? radioPrivacidad.value : 'publico';

  // Validar que haya un título
  if (!titulo) {
    alert('Por favor, ingresa un título para el cuestionario.');
    return;
  }

  // Validar que haya al menos una pregunta
  if (questions.length === 0) {
    alert('Debes agregar al menos una pregunta.');
    return;
  }

  // Validar que todas las preguntas tengan texto
  for (let i = 0; i < questions.length; i++) {
    if (!questions[i].text || questions[i].text.trim() === '') {
      alert(`La pregunta ${i + 1} está vacía. Por favor, complétala.`);
      return;
    }

    // Validar que haya al menos una respuesta correcta
    const hasCorrectAnswer = questions[i].answers.some(answer => answer.isCorrect);
    if (!hasCorrectAnswer) {
      alert(`La pregunta ${i + 1} no tiene ninguna respuesta marcada como correcta.`);
      return;
    }

    // Validar que las respuestas tengan texto
    for (let j = 0; j < questions[i].answers.length; j++) {
      if (!questions[i].answers[j].text || questions[i].answers[j].text.trim() === '') {
        alert(`La pregunta ${i + 1} tiene una alternativa vacía.`);
        return;
      }
    }
  }

  // Obtener el PIN del encabezado
  const pinInput = document.querySelector('.pin-input');
  const pin = pinInput ? pinInput.value : '';

  // Preparar datos para enviar
  const data = {
    titulo: titulo,
    descripcion: descripcion,
    preguntas: questions,
    pin: pin,  // Incluir el PIN del encabezado
    estado: estado  // Incluir el estado de privacidad
  };

  // Determinar si es creación o actualización
  const isUpdate = cuestionarioId && cuestionarioId !== '';
  const url = isUpdate 
    ? `/api/cuestionario/${cuestionarioId}` 
    : '/api/cuestionario';
  const method = isUpdate ? 'PUT' : 'POST';

  // Crear FormData si hay imagen, sino enviar JSON
  let requestData;
  let headers = {};

  if (imagenFile) {
    requestData = new FormData();
    requestData.append('titulo', titulo);
    requestData.append('descripcion', descripcion);
    requestData.append('preguntas', JSON.stringify(questions));
    requestData.append('pin', pin);  // Incluir el PIN del encabezado
    requestData.append('estado', estado);  // Incluir el estado de privacidad
    requestData.append('imagen_portada', imagenFile);
  } else {
    requestData = JSON.stringify(data);
    headers['Content-Type'] = 'application/json';
  }

  // Mostrar indicador de carga solo en el botón Guardar del header
  const btnSave = document.getElementById('saveQuizBtn');
  const originalTextSave = btnSave ? btnSave.textContent : '';
  
  if (btnSave) {
    btnSave.textContent = 'Guardando...';
    btnSave.disabled = true;
  }

  // Enviar al servidor
  fetch(url, {
    method: method,
    headers: headers,
    body: requestData
  })
  .then(response => response.json())
  .then(result => {
    if (btnSave) {
      btnSave.textContent = originalTextSave;
      btnSave.disabled = false;
    }

    if (result.success) {
      // Mensaje de éxito simple
      alert('Cuestionario registrado correctamente');
      
      // Si se creó un nuevo cuestionario, actualizar el ID
      if (!isUpdate && result.cuestionario_id) {
        document.getElementById('cuestionario_id').value = result.cuestionario_id;
      }

      // Redirigir a Mis Cuestionarios
      window.location.href = '/my-quizzes';
    } else {
      alert('Error: ' + (result.error || result.message || 'No se pudo guardar el cuestionario'));
    }
  })
  .catch(error => {
    if (btnSave) {
      btnSave.textContent = originalTextSave;
      btnSave.disabled = false;
    }
    console.error('Error:', error);
    alert('Error al guardar el cuestionario. Por favor, intenta de nuevo.');
  });
}
