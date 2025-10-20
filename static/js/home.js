document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.carousel-cards');
    const heroSection = document.querySelector('.hero-section'); // Contenedor del carrusel
    if (!slider) return;

    // Obtener el ancho de una tarjeta y el espacio entre ellas para cálculos precisos
    const card = slider.querySelector('.card');
    const cardStyle = card ? getComputedStyle(card) : null;
    const cardWidth = card ? card.offsetWidth + parseFloat(cardStyle?.marginRight || 0) + parseFloat(cardStyle?.marginLeft || 0) : 0;

    let isDown = false;
    let startX;
    let scrollLeft;
    let walk = 0;

    const end = () => {
        if (!isDown) return; // Solo actuar si el arrastre se inició
        isDown = false;
        slider.classList.remove('active');

        // Lógica de "snap" mejorada
        if (!cardWidth) return;
        const snapThreshold = cardWidth * 0.2; // Umbral más pequeño para mayor sensibilidad

        // Determinar la tarjeta más cercana
        const currentScroll = slider.scrollLeft;
        const startIndex = Math.round(scrollLeft / cardWidth); // Tarjeta inicial antes del arrastre

        let targetIndex = startIndex;
        if (walk < -snapThreshold) { // Deslizó hacia la izquierda (ver siguiente tarjeta)
            targetIndex = startIndex + 1;
        } else if (walk > snapThreshold) { // Deslizó hacia la derecha (ver tarjeta anterior)
            targetIndex = startIndex - 1;
        } else {
            targetIndex = Math.round(currentScroll / cardWidth); // Si el arrastre es corto, ir a la más cercana
        }

        const targetScroll = targetIndex * cardWidth;
        slider.scrollTo({
            left: targetScroll,
            behavior: 'smooth'
        });
    };

    const start = (e) => {
        // IMPORTANTE: Solo iniciar el arrastre si el clic se origina en el carrusel o sus flechas.
        // Esto evita que el script bloquee otros enlaces como el botón "Empieza".
        if (!e.target.closest('.carousel-container')) {
            return;
        }

        isDown = true;
        slider.classList.add('active');
        startX = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
        walk = 0; // Resetear el recorrido en cada inicio
    };

    const move = (e) => {
        if (!isDown) return; // Si no se está arrastrando, no hacer nada.
        e.preventDefault(); // IMPORTANTE: Prevenir la acción por defecto SOLO cuando se está arrastrando.
        const x = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
        walk = (x - startX); // Distancia total del arrastre
        slider.scrollLeft = scrollLeft - walk;
    };

    // Eventos de Mouse
    heroSection.addEventListener('mousedown', start);
    heroSection.addEventListener('mouseleave', end);
    heroSection.addEventListener('mouseup', end);
    heroSection.addEventListener('mousemove', move);

    // Eventos Táctiles
    heroSection.addEventListener('touchstart', start, { passive: false });
    heroSection.addEventListener('touchend', end);
    heroSection.addEventListener('touchcancel', end);
    heroSection.addEventListener('touchmove', move, { passive: false });

    // Flechas de navegación mejoradas para usar el ancho de la tarjeta
    const prevArrow = document.querySelector('.carousel-arrow:first-of-type');
    const nextArrow = document.querySelector('.carousel-arrow:last-of-type');

    if (cardWidth > 0) {
        prevArrow?.addEventListener('click', () => slider.scrollBy({ left: -cardWidth, behavior: 'smooth' }));
        nextArrow?.addEventListener('click', () => slider.scrollBy({ left: cardWidth, behavior: 'smooth' }));
    }
});

// Lógica del nuevo carrusel con botones de navegación
document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('.carousel');
    if (!carousel) return;

    const track = carousel.querySelector('.track');
    const prevButton = carousel.querySelector('.nav.prev');
    const nextButton = carousel.querySelector('.nav.next');

    // --- Lógica de arrastre vs. clic ---
    let isDragging = false;
    let startX;
    let scrollLeft;
    let dragThreshold = 10; // Píxeles a mover para considerarlo un arrastre

    track.addEventListener('mousedown', (e) => {
        isDragging = false; // Reiniciar en cada clic
        startX = e.pageX - track.offsetLeft;
        scrollLeft = track.scrollLeft;
        track.style.cursor = 'grabbing';

        // Prevenir que un clic en un enlace inicie el arrastre
        if (e.target.tagName === 'A') {
            e.target.addEventListener('click', (ev) => {
                if (isDragging) {
                    ev.preventDefault();
                }
            }, { once: true });
        }
    });

    track.addEventListener('mousemove', (e) => {
        if (startX === undefined) return; // No se ha iniciado el mousedown
        const x = e.pageX - track.offsetLeft;
        const walk = x - startX;

        if (Math.abs(walk) > dragThreshold) {
            isDragging = true;
        }

        track.scrollLeft = scrollLeft - walk;
    });

    const stopDragging = () => {
        startX = undefined;
        track.style.cursor = 'grab';
    };

    track.addEventListener('mouseup', stopDragging);
    track.addEventListener('mouseleave', stopDragging);

    // --- Lógica de Navegación ---
    const updateNavButtons = () => {
        if (!track || !prevButton || !nextButton) return;
        // Un pequeño margen de 1px para evitar errores de redondeo
        const atStart = track.scrollLeft <= 1;
        const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 1;

        prevButton.setAttribute('aria-disabled', atStart);
        nextButton.setAttribute('aria-disabled', atEnd);
    };

    const navigate = (direction) => {
        const scrollAmount = track.clientWidth * direction;
        track.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    };

    prevButton.addEventListener('click', () => navigate(-1));
    nextButton.addEventListener('click', () => navigate(1));

    // Actualizar botones al hacer scroll (manual o con flechas)
    track.addEventListener('scroll', updateNavButtons);

    // --- Soporte de Teclado ---
    carousel.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            navigate(-1);
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            navigate(1);
        }
    });

    // --- Inicialización y Observadores ---

    // Usar ResizeObserver para actualizar los botones si el tamaño de la ventana cambia
    const resizeObserver = new ResizeObserver(entries => {
        // Se ejecuta cuando el tamaño del track cambia
        updateNavButtons();
    });

    resizeObserver.observe(track);

    // Llamada inicial para establecer el estado correcto de los botones
    // Se usa un pequeño timeout para asegurar que el layout esté completo
    setTimeout(updateNavButtons, 100);
});