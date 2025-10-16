document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.carousel-cards');
    if (!slider) return;

    let isDown = false;
    let startX;
    let scrollLeft;
    let walk = 0;

    const end = () => {
        if (!isDown) return;
        isDown = false;
        slider.classList.remove('active');

        // Lógica de "snap"
        const card = slider.querySelector('.card');
        if (!card) return;

        const cardWidth = card.offsetWidth;
        const snapThreshold = cardWidth * 0.3; // 30% del ancho de la tarjeta

        // Determinar la tarjeta más cercana
        const currentScroll = slider.scrollLeft;
        let targetIndex;

        if (walk < -snapThreshold) { // Deslizó hacia la izquierda (ver siguiente)
            targetIndex = Math.ceil(currentScroll / cardWidth);
        } else if (walk > snapThreshold) { // Deslizó hacia la derecha (ver anterior)
            targetIndex = Math.floor(currentScroll / cardWidth);
        } else {
            targetIndex = Math.round(currentScroll / cardWidth);
        }

        const targetScroll = targetIndex * cardWidth;
        slider.scrollTo({
            left: targetScroll,
            behavior: 'smooth'
        });
    };

    const start = (e) => {
        isDown = true;
        slider.classList.add('active');
        startX = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
        scrollLeft = slider.scrollLeft;
        walk = 0; // Resetear el recorrido en cada inicio
    };

    const move = (e) => {
        if (!isDown) return;
        e.preventDefault(); // Evita la selección de texto
        const x = (e.pageX || e.touches[0].pageX) - slider.offsetLeft;
        walk = (x - startX); // Distancia total del arrastre
        slider.scrollLeft = scrollLeft - walk;
    };

    // Eventos de Mouse
    slider.addEventListener('mousedown', start);
    slider.addEventListener('mouseleave', end);
    slider.addEventListener('mouseup', end);
    slider.addEventListener('mousemove', move);

    // Eventos Táctiles
    slider.addEventListener('touchstart', start, { passive: false });
    slider.addEventListener('touchend', end);
    slider.addEventListener('touchcancel', end);
    slider.addEventListener('touchmove', move, { passive: false });

    // Flechas de navegación (opcional, pero buena práctica mantenerlas funcionales)
    const prevArrow = document.querySelector('.carousel-arrow:first-of-type');
    const nextArrow = document.querySelector('.carousel-arrow:last-of-type');

    prevArrow?.addEventListener('click', () => slider.scrollBy({ left: -slider.clientWidth, behavior: 'smooth' }));
    nextArrow?.addEventListener('click', () => slider.scrollBy({ left: slider.clientWidth, behavior: 'smooth' }));
});