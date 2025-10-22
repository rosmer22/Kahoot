document.addEventListener('DOMContentLoaded', () => {
    // Los datos ahora vienen directamente del backend en la variable `gameData`.
    // Si no hay participantes, muestra un mensaje y detiene la ejecución.
    if (!gameData || !gameData.participants || gameData.participants.length === 0) {
        document.querySelector('.results-container').innerHTML = '<h1>No hay resultados para mostrar</h1><p>Parece que nadie ha completado este cuestionario todavía.</p>';
        return;
    }

    // 1. Procesar datos
    const processedData = processGameData(gameData);

    // 2. Renderizar componentes
    renderSummary(processedData);
    renderLeaderboard(processedData.leaderboard);
    renderHeatmap(processedData);
    renderDetailsAccordion(processedData);

    // 3. Adjuntar eventos
    setupEventListeners();
});

function processGameData(data) {
    const leaderboard = data.participants.map(p => {
        const totalPoints = p.answers.reduce((sum, a) => sum + a.points, 0);
        const correctAnswers = p.answers.filter(a => a.correct).length;
        const totalTime = p.answers.reduce((sum, a) => sum + a.time, 0);
        const processedParticipant = {
            id: p.id,
            name: p.name,
            totalPoints,
            correctAnswers,
            totalTime,
            totalQuestions: p.answers.length,
            avgTime: totalTime / p.answers.length,
            answers: p.answers,
        };

        // Asegurarse de que cada participante tenga una respuesta (aunque sea vacía) para cada pregunta del cuestionario
        const participantAnsweredQIds = new Set(p.answers.map(a => a.questionId));
        data.questions.forEach(q => {
            if (!participantAnsweredQIds.has(q.id)) {
                processedParticipant.answers.push({
                    questionId: q.id, correct: null, points: 0, time: 0, choice: "N/A"
                });
            }
        });

        return processedParticipant;
    }).sort((a, b) => {
        if (b.totalPoints !== a.totalPoints) {
            return b.totalPoints - a.totalPoints; // Mayor puntaje primero
        }
        return a.totalTime - b.totalTime; // Menor tiempo en caso de empate
    });

    const totalCorrect = leaderboard.reduce((sum, p) => sum + p.correctAnswers, 0);    
    const totalAnswered = leaderboard.reduce((sum, p) => sum + p.answers.length, 0);

    return {
        questions: data.questions,
        participants: data.participants,
        leaderboard,
        totalTime: data.totalTime,
        summary: {
            totalQuestions: data.questions.length,
            totalParticipants: data.participants.length,
            globalAccuracy: totalAnswered > 0 ? (totalCorrect / totalAnswered) * 100 : 0
        }
    };
}

function renderSummary(data) {
    document.getElementById('total-questions-chip').textContent = `${data.summary.totalQuestions} preguntas`;
    document.getElementById('total-participants-chip').textContent = `${data.summary.totalParticipants} participantes`;
    document.getElementById('total-time-chip').textContent = `${data.totalTime.toFixed(0)}s tiempo total`;

    const progressFill = document.getElementById('global-progress-fill');
    const progressText = document.getElementById('global-progress-text');
    progressFill.style.width = `${data.summary.globalAccuracy.toFixed(1)}%`;
    progressText.textContent = `${data.summary.globalAccuracy.toFixed(1)}% Aciertos Globales`;
}

function renderLeaderboard(leaderboard) {
    const tbody = document.querySelector('#leaderboard-table tbody');
    tbody.innerHTML = '';

    leaderboard.forEach((player, index) => {
        const rank = index + 1;
        const row = document.createElement('tr');
        
        let rankClass = '';
        if (rank === 1) rankClass = 'rank-1';
        else if (rank <= 3) rankClass = 'rank-2';

        row.innerHTML = `
            <td class="${rankClass}">${rank === 1 ? '🥇' : rank}</td>
            <td>${player.name}</td>
            <td><strong>${player.totalPoints}</strong></td>
            <td>${player.correctAnswers} / ${player.totalQuestions}</td>
            <td>${player.totalTime.toFixed(2)}s</td>
        `;
        tbody.appendChild(row);
    });
}

function renderHeatmap(data) {
    const container = document.getElementById('heatmap-container');
    if (!container) return;
    const table = document.createElement('table');
    table.className = 'heatmap-table';

    // Header (Preguntas)
    const thead = document.createElement('thead');
    let headerRow = '<tr><th class="user-name">Usuario</th>';
    data.questions.forEach(q => {
        headerRow += `<th>Q${q.order || q.id}</th>`;
    });
    headerRow += '</tr>';
    thead.innerHTML = headerRow;
    table.appendChild(thead);

    // Body (Usuarios y sus respuestas)
    const tbody = document.createElement('tbody');
    data.leaderboard.forEach(player => {
        let playerRow = `<tr><td class="user-name-cell">${player.name}</td>`;
        data.questions.forEach(q => {
            const answer = player.answers.find(a => a.questionId === q.id);
            let cellClass = 'heatmap-cell';
            let icon = '';
            let details = '';
            let fastestBadge = '';

            if (answer) {
                if (answer.correct === true) {
                    cellClass += ' correct';
                    icon = '✅';
                    details = `${answer.points} pts, ${answer.time.toFixed(1)}s`;
                    // Check for fastest correct answer
                    const fastest = findFastestCorrect(data.participants, q.id);
                    if (fastest && fastest.participantId === player.id) {
                        fastestBadge = '<span class="fastest-badge" title="Respuesta correcta más rápida">⚡</span>';
                    }
                } else if (answer.correct === false) {
                    cellClass += ' incorrect';
                    icon = '❌';
                    details = `0 pts, ${answer.time.toFixed(1)}s`;
                } else { // No respondió
                    cellClass += ' no-answer';
                    icon = '➖';
                    details = 'Sin respuesta';
                }
            }

            playerRow += `
                <td class="${cellClass}" data-question-id="${q.id}" data-player-id="${player.id}">
                    ${fastestBadge}
                    <span class="cell-icon">${icon}</span>
                    <span class="cell-details">${details}</span>
                </td>
            `;
        });
        playerRow += '</tr>';
        tbody.innerHTML += playerRow;
    });
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

function findFastestCorrect(participants, questionId) {
    let fastest = null;
    participants.forEach(p => {
        const answer = p.answers.find(a => a.questionId === questionId && a.correct);
        if (answer) {
            if (!fastest || answer.time < fastest.time) {
                fastest = { time: answer.time, participantId: p.id };
            }
        }
    });
    return fastest;
}

function renderDetailsAccordion(data) {
    const accordionContainer = document.getElementById('details-accordion');
    if (!accordionContainer) return;
    accordionContainer.innerHTML = '';

    data.leaderboard.forEach(player => {
        const item = document.createElement('div');
        item.className = 'accordion-item';
        item.innerHTML = `
            <div class="accordion-header" data-player-id="${player.id}">
                <span>${player.name}</span>
                <span>${player.totalPoints} Puntos</span>
            </div>
            <div class="accordion-content">
                <div class="user-summary-card">
                    <div class="summary-stat">
                        <div class="stat-value">${player.totalPoints}</div>
                        <div class="stat-label">Puntos Totales</div>
                    </div>
                    <div class="summary-stat">
                        <div class="stat-value">${player.correctAnswers}/${player.totalQuestions}</div>
                        <div class="stat-label">Aciertos</div>
                    </div>
                    <div class="summary-stat">
                        <div class="stat-value">${player.avgTime.toFixed(2)}s</div>
                        <div class="stat-label">Tiempo Promedio</div>
                    </div>
                </div>
                <ul class="user-questions-list">
                    ${player.answers.map(answer => {
                        const question = data.questions.find(q => q.id === answer.questionId);
                        if (!question) return '';
                        let statusClass = answer.correct === null ? 'no-answer' : '';
                        if (answer.correct === true) statusClass = 'correct';
                        if (answer.correct === false) statusClass = 'incorrect';
                        return `
                            <li class="user-question-item ${statusClass}">
                                <div class="question-text">Q${question.order || question.id}: ${question.text}</div>
                                <div class="question-details">
                                    <span>Tu respuesta: ${answer.choice}</span>
                                    <span>${answer.points} pts | ${answer.time.toFixed(1)}s</span>
                                </div>
                            </li>
                        `;
                    }).join('')}
                </ul>
                <div class="progress-chart-container">
                    <h4>Progreso de Puntos</h4>
                    <canvas id="chart-player-${player.id}" width="400" height="150"></canvas>
                </div>
            </div>
        `;
        accordionContainer.appendChild(item);

        // Render chart
        const ctx = document.getElementById(`chart-player-${player.id}`).getContext('2d');
        renderMiniChart(ctx, player.answers, data.questions);
    });
}

function renderMiniChart(ctx, playerAnswers, allQuestions) {
    const labels = allQuestions.map(q => `Q${q.order || q.id}`);
    const pointsData = [];
    let cumulativePoints = 0;

    allQuestions.forEach(q => {
        const answer = playerAnswers.find(a => a.questionId === q.id);
        if (answer) {
            cumulativePoints += answer.points;
        }
        pointsData.push(cumulativePoints);
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Puntos Acumulados',
                data: pointsData,
                borderColor: 'var(--color-accent)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: 'var(--color-accent)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0,0,0,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

function setupEventListeners() {
    const tooltip = document.getElementById('heatmap-tooltip');
    if (!tooltip) return;

    // Heatmap Tooltip
    document.querySelectorAll('.heatmap-cell').forEach(cell => {
        cell.addEventListener('mousemove', (e) => {
            const playerId = parseInt(cell.dataset.playerId, 10);
            const questionId = parseInt(cell.dataset.questionId, 10);

            const player = gameData.participants.find(p => p.id === playerId);
            const question = gameData.questions.find(q => q.id === questionId);
            const answer = player.answers.find(a => a.questionId === questionId);

            if (!answer || !question) return;

            let statusText = '';
            let statusClass = '';
            if (answer.correct === true) {
                statusText = 'Correcto';
                statusClass = 'correct';
            } else if (answer.correct === false) {
                statusText = 'Incorrecto';
                statusClass = 'incorrect';
            } else {
                statusText = 'Sin respuesta';
            }

            tooltip.innerHTML = `
                <div class="tooltip-question">${question.text}</div>
                <div>Respuesta: <span class="tooltip-answer ${statusClass}">${answer.choice} (${statusText})</span></div>
                <div>Puntos: ${answer.points}</div>
                <div>Tiempo: ${answer.time.toFixed(1)}s</div>
            `;

            tooltip.style.display = 'block';
            tooltip.style.left = `${e.pageX + 15}px`;
            tooltip.style.top = `${e.pageY + 15}px`;
        });

        cell.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    });

    // Accordion
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const item = header.parentElement;
            const content = header.nextElementSibling;

            if (item.classList.contains('open')) {
                item.classList.remove('open');
                content.style.maxHeight = '0px';
            } else {
                // Close other open accordions
                document.querySelectorAll('.accordion-item.open').forEach(openItem => {
                    openItem.classList.remove('open');
                    openItem.querySelector('.accordion-content').style.maxHeight = '0px';
                });

                item.classList.add('open');
                content.style.maxHeight = `${content.scrollHeight}px`;
            }
        });
    });
}