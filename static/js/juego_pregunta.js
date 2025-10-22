document.addEventListener('DOMContentLoaded', () => {
    let currentQuestionIndex = num_pregunta - 1;
    let score = puntaje_inicial;
    let timerInterval;

    const questionTextEl = document.getElementById('question-text');
    const optionsContainerEl = document.getElementById('options-container');
    const timerValueEl = document.getElementById('timer-value');
    const scoreEl = document.getElementById('score-value');
    const questionCounterEl = document.getElementById('question-counter');
    const feedbackEl = document.getElementById('feedback');
    const nextButton = document.getElementById('next-question-btn');

    function showQuestion(index) {
        // Si el índice es mayor o igual al número de preguntas, el quiz ha terminado.
        if (index >= preguntas.length) {
            // Finalizar la sesión de juego y redirigir a la página de resultados
            fetch(`/api/sesion/finalizar`, { // Necesitarás crear esta ruta si quieres marcar la sesión como finalizada
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: pin })
            }).finally(() => {
                window.location.href = `/resultados/${pin}`;
            });
            return;
        }

        const question = preguntas[index];
        
        // Actualizar UI
        questionTextEl.textContent = question.texto_pregunta;
        questionCounterEl.textContent = `Pregunta ${index + 1} de ${preguntas.length}`;
        optionsContainerEl.innerHTML = '';
        optionsContainerEl.classList.remove('answered');
        feedbackEl.style.display = 'none';
        nextButton.style.display = 'none';

        // Crear opciones de respuesta
        question.opciones.forEach(opcion => {
            const button = document.createElement('button');
            button.className = 'option-btn';
            button.dataset.optionId = opcion.id;
            button.dataset.correct = opcion.es_correcta;
            button.innerHTML = `<span>${opcion.texto_opcion}</span>`;
            button.onclick = () => handleAnswer(button, question.id);
            optionsContainerEl.appendChild(button);
        });

        // Iniciar temporizador
        startTimer(question.tiempo_limite);
    }

    function startTimer(duration) {
        let timeLeft = duration;
        timerValueEl.textContent = timeLeft;
        clearInterval(timerInterval);

        timerInterval = setInterval(() => {
            timeLeft--;
            timerValueEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                handleTimeUp();
            }
        }, 1000);
    }

    function handleAnswer(selectedButton, questionId) {
        clearInterval(timerInterval);
        const timeRemaining = parseInt(timerValueEl.textContent, 10);
        const timeTaken = preguntas[currentQuestionIndex].tiempo_limite - timeRemaining;

        const optionId = selectedButton.dataset.optionId;
        const isCorrect = selectedButton.dataset.correct === 'true';

        // Deshabilitar todos los botones
        optionsContainerEl.classList.add('answered');

        // Enviar respuesta al backend
        fetch('/api/sesion/responder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pin: pin,
                pregunta_id: questionId,
                opcion_id: optionId,
                tiempo_respuesta: timeTaken
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (data.correct) {
                    score += data.points;
                    scoreEl.textContent = score;
                    showFeedback(true, `¡Correcto! +${data.points} puntos`);
                } else {
                    showFeedback(false, 'Respuesta incorrecta');
                }
            } else {
                showFeedback(false, data.message || 'Error al guardar respuesta');
            }
            highlightAnswers(optionId);
            nextButton.style.display = 'block';
        })
        .catch(() => {
            showFeedback(false, 'Error de conexión');
            highlightAnswers(optionId);
            nextButton.style.display = 'block';
        });
    }

    function handleTimeUp() {
        optionsContainerEl.classList.add('answered');
        showFeedback(false, '¡Se acabó el tiempo!');
        highlightAnswers(null); // Resaltar solo la correcta
        nextButton.style.display = 'block';
    }

    function showFeedback(isCorrect, message) {
        feedbackEl.textContent = message;
        feedbackEl.className = `feedback ${isCorrect ? 'correct' : 'incorrect'}`;
        feedbackEl.style.display = 'block';
    }

    function highlightAnswers(selectedOptionId) {
        const buttons = optionsContainerEl.querySelectorAll('.option-btn');
        buttons.forEach(btn => {
            const isCorrect = btn.dataset.correct === 'true';
            const isSelected = btn.dataset.optionId === selectedOptionId;

            if (isCorrect) {
                btn.classList.add('correct');
            } else if (isSelected && !isCorrect) {
                btn.classList.add('incorrect');
            } else {
                btn.classList.add('disabled');
            }
        });
    }

    function goToNextQuestion() {
        currentQuestionIndex++;
        showQuestion(currentQuestionIndex);
    }

    // Asignar evento al botón "Siguiente"
    nextButton.addEventListener('click', goToNextQuestion);

    // Iniciar el juego mostrando la primera pregunta
    showQuestion(currentQuestionIndex);
});

// Ruta para finalizar sesión (opcional, pero recomendado)
// En app.py, podrías añadir:
/*
@app.route('/api/sesion/finalizar', methods=['POST'])
def api_finalizar_sesion():
    if not g.user:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    pin = request.get_json().get('pin')
    db = bd.obtener_conexion()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE sesiones_juego 
        SET estado = 'finalizado', finished_at = NOW() 
        WHERE pin_sesion = %s AND user_id = %s
    """, (pin, g.user['id']))
    db.commit()
    return jsonify({'success': True})
*/