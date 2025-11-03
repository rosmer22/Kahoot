// Gestión de Grupos - JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Elementos del DOM
    const createGroupBtn = document.getElementById('createGroupBtn');
    const joinGroupBtn = document.getElementById('joinGroupBtn');
    const createGroupModal = document.getElementById('createGroupModal');
    const joinGroupModal = document.getElementById('joinGroupModal');
    const selectQuizModal = document.getElementById('selectQuizModal');
    const createGroupForm = document.getElementById('createGroupForm');
    const joinGroupForm = document.getElementById('joinGroupForm');
    const quizSearch = document.getElementById('quizSearch');
    const quizList = document.getElementById('quizList');

    // Variables globales
    let currentGroupId = null;
    let availableQuizzes = [];

    // Event Listeners
    createGroupBtn.addEventListener('click', () => openModal('createGroupModal'));
    joinGroupBtn.addEventListener('click', () => openModal('joinGroupModal'));

    createGroupForm.addEventListener('submit', handleCreateGroup);
    joinGroupForm.addEventListener('submit', handleJoinGroup);

    if (quizSearch) {
        quizSearch.addEventListener('input', filterQuizzes);
    }

    // Event listeners para botones de cerrar
    document.addEventListener('click', function (e) {
        // Botones de cerrar (X)
        if (e.target.closest('.close-btn')) {
            e.preventDefault();
            e.stopPropagation();
            const modal = e.target.closest('.modal');
            if (modal) {
                console.log('🔴 Cerrando modal:', modal.id);
                closeModal(modal.id);
            }
        }

        // Botones de cancelar
        if (e.target.textContent === 'Cancelar' && e.target.type === 'button') {
            e.preventDefault();
            e.stopPropagation();
            const modal = e.target.closest('.modal');
            if (modal) {
                console.log('🔴 Cerrando modal (cancelar):', modal.id);
                closeModal(modal.id);
            }
        }
    });

    // Funciones de Modal
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';

        // Limpiar formularios
        if (modalId === 'createGroupModal') {
            createGroupForm.reset();
        } else if (modalId === 'joinGroupModal') {
            joinGroupForm.reset();
        } else if (modalId === 'selectQuizModal') {
            quizSearch.value = '';
            quizList.innerHTML = '';
        }
    }

    // Hacer closeModal disponible globalmente para los onclick inline
    window.closeModal = closeModal;

    // Debug: verificar que los modales se abren y cierran correctamente
    console.log('✅ Event listeners de modales configurados correctamente');

    // Cerrar modal al hacer clic fuera (solo en el fondo, no en los botones)
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('modal') && !e.target.closest('.modal-content')) {
            const modalId = e.target.id;
            closeModal(modalId);
        }
    });

    // Cerrar modal con Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal.id);
            }
        }
    });

    // Crear Grupo
    async function handleCreateGroup(e) {
        e.preventDefault();

        const formData = new FormData(createGroupForm);
        const data = {
            nombre: formData.get('nombre'),
            descripcion: formData.get('descripcion'),
            es_publico: formData.get('es_publico') === 'on'
        };

        try {
            const response = await fetch('/api/grupos/crear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Grupo creado exitosamente', 'success');
                closeModal('createGroupModal');
                // Recargar la página para mostrar el nuevo grupo
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(result.message || 'Error al crear el grupo', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Unirse a Grupo
    async function handleJoinGroup(e) {
        e.preventDefault();

        const formData = new FormData(joinGroupForm);
        const codigo = formData.get('codigo').trim().toUpperCase();

        if (codigo.length !== 8) {
            showNotification('El código debe tener 8 caracteres', 'error');
            return;
        }

        try {
            const response = await fetch('/api/grupos/unirse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ codigo: codigo })
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Te has unido al grupo exitosamente', 'success');
                closeModal('joinGroupModal');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(result.message || 'Error al unirse al grupo', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Iniciar Cuestionario en Grupo
    window.startGroupQuiz = function (groupId) {
        currentGroupId = groupId;
        openModal('selectQuizModal');
        loadAvailableQuizzes();
    };

    // Cargar Cuestionarios Disponibles
    async function loadAvailableQuizzes() {
        try {
            const response = await fetch('/api/grupos/cuestionarios');
            const result = await response.json();

            if (result.success) {
                availableQuizzes = result.quizzes;
                displayQuizzes(availableQuizzes);
            } else {
                showNotification('Error al cargar cuestionarios', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Mostrar Cuestionarios
    function displayQuizzes(quizzes) {
        quizList.innerHTML = '';

        if (quizzes.length === 0) {
            quizList.innerHTML = `
                <div class="empty-state">
                    <p>No hay cuestionarios disponibles</p>
                </div>
            `;
            return;
        }

        quizzes.forEach(quiz => {
            const quizItem = document.createElement('div');
            quizItem.className = 'quiz-item';
            quizItem.dataset.quizId = quiz.id;

            quizItem.innerHTML = `
                <div class="quiz-item-info">
                    <h4>${quiz.titulo || 'Sin título'}</h4>
                    <p>PIN: ${quiz.pin} | ${quiz.preguntas_count || 0} preguntas</p>
                </div>
            `;

            quizItem.addEventListener('click', () => selectQuiz(quiz.id));
            quizList.appendChild(quizItem);
        });
    }

    // Filtrar Cuestionarios
    function filterQuizzes() {
        const searchTerm = quizSearch.value.toLowerCase();
        const filtered = availableQuizzes.filter(quiz =>
            (quiz.titulo && quiz.titulo.toLowerCase().includes(searchTerm)) ||
            quiz.pin.toString().includes(searchTerm)
        );
        displayQuizzes(filtered);
    }

    // Seleccionar Cuestionario
    function selectQuiz(quizId) {
        // Remover selección anterior
        document.querySelectorAll('.quiz-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Seleccionar actual
        const selectedItem = document.querySelector(`[data-quiz-id="${quizId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('selected');
        }

        // Confirmar selección después de un breve delay
        setTimeout(() => {
            startGroupQuizSession(quizId);
        }, 500);
    }

    // Iniciar Sesión de Cuestionario en Grupo
    async function startGroupQuizSession(quizId) {
        try {
            const response = await fetch('/api/grupos/iniciar-cuestionario', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    grupo_id: currentGroupId,
                    cuestionario_id: quizId
                })
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Cuestionario iniciado en el grupo', 'success');
                closeModal('selectQuizModal');
                // Redirigir a la página del cuestionario en grupo
                window.location.href = `/grupo/quiz/${result.sesion_id}`;
            } else {
                showNotification(result.message || 'Error al iniciar el cuestionario', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Salir de Grupo
    window.leaveGroup = function (groupId) {
        if (confirm('¿Estás seguro de que quieres salir de este grupo?')) {
            leaveGroupRequest(groupId);
        }
    };

    async function leaveGroupRequest(groupId) {
        try {
            const response = await fetch('/api/grupos/salir', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ grupo_id: groupId })
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Has salido del grupo', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(result.message || 'Error al salir del grupo', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Mostrar Notificaciones
    function showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        `;

        // Agregar estilos si no existen
        if (!document.getElementById('notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    max-width: 400px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    animation: slideInRight 0.3s ease;
                }
                .notification-success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .notification-error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .notification-info {
                    background: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
                .notification-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 1rem;
                }
                .notification-close {
                    background: none;
                    border: none;
                    cursor: pointer;
                    padding: 0.25rem;
                    margin-left: 0.5rem;
                }
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(styles);
        }

        // Agregar al DOM
        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Copiar código del grupo
    window.copyGroupCode = function (code) {
        navigator.clipboard.writeText(code).then(() => {
            showNotification('Código copiado al portapapeles', 'success');
        }).catch(() => {
            showNotification('Error al copiar el código', 'error');
        });
    };

    // Configurar grupo (solo para administradores)
    window.configureGroup = function (groupId) {
        // Implementar configuración del grupo
        showNotification('Función de configuración próximamente', 'info');
    };

    // Unirse a grupo público
    window.joinPublicGroup = function (codigo) {
        // Simular el proceso de unirse usando el código
        const joinForm = document.getElementById('joinGroupForm');
        const codeInput = document.getElementById('groupCode');

        if (codeInput && joinForm) {
            codeInput.value = codigo;
            // Simular el envío del formulario
            const formData = new FormData(joinForm);
            const data = {
                codigo: codigo
            };

            // Llamar directamente a la función de unirse
            handleJoinGroupDirect(data);
        }
    };

    // Función directa para unirse a grupo
    async function handleJoinGroupDirect(data) {
        try {
            const response = await fetch('/api/grupos/unirse', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                showNotification('Te has unido al grupo exitosamente', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showNotification(result.message || 'Error al unirse al grupo', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        }
    }

    // Función para refrescar grupos públicos
    window.refreshPublicGroups = function () {
        // Recargar la página para obtener grupos públicos actualizados
        window.location.reload();
    };

    // Auto-refresh cada 30 segundos para mostrar nuevos grupos públicos
    setInterval(() => {
        // Solo refrescar si no hay modales abiertos
        const openModal = document.querySelector('.modal.show');
        if (!openModal) {
            refreshPublicGroups();
        }
    }, 30000);

    console.log('✅ Módulo de Grupos cargado correctamente');
    console.log('🔄 Auto-refresh de grupos públicos cada 30 segundos');
});

document.addEventListener('click', function (e) {
    const leaveBtn = e.target.closest('.btn-icon[title="Salir del grupo"]');
    if (leaveBtn) {
        const groupCard = leaveBtn.closest('.group-card');
        const groupId = groupCard ? groupCard.dataset.groupId : null;
        if (groupId) {
            leaveGroup(groupId);
        }
    }
});