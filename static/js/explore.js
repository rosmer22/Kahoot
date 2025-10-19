// Búsqueda dinámica por nombre o PIN usando el input del header
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-container input[name="q"]');
    const searchForm = document.querySelector('.search-container');
    const resultsGrid = document.getElementById('resultsGrid');
    const noResults = document.getElementById('noResults');
    const noResultsInitial = document.getElementById('noResultsInitial');

    console.log('🔍 Inicializando búsqueda...');
    console.log('Input encontrado:', !!searchInput);
    console.log('Form encontrado:', !!searchForm);
    console.log('Grid encontrado:', !!resultsGrid);

    if (!searchInput || !searchForm || !resultsGrid) {
        console.warn('❌ Elementos de búsqueda no encontrados');
        return;
    }

    const allResults = resultsGrid.querySelectorAll('.result');
    console.log('📊 Total de resultados:', allResults.length);

    if (allResults.length === 0) {
        console.warn('⚠️ No hay resultados para buscar');
        return;
    }

    // Limpiar el input al cargar la página
    searchInput.value = '';

    // Prevenir el envío del formulario
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Formulario submit prevenido');
    });

    // Función de búsqueda
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        console.log('🔎 Buscando:', searchTerm);
        let visibleCount = 0;

        // Si no hay término de búsqueda, mostrar todos
        if (searchTerm === '') {
            console.log('✅ Mostrando todos los resultados');
            allResults.forEach(result => {
                result.style.display = '';
                visibleCount++;
            });
            
            if (noResults) {
                noResults.classList.add('hidden');
            }
            if (noResultsInitial) {
                noResultsInitial.classList.add('hidden');
            }
            resultsGrid.style.display = 'grid';
            return;
        }

        // Buscar en los resultados
        allResults.forEach(result => {
            const name = (result.getAttribute('data-name') || '').toLowerCase();
            const pin = (result.getAttribute('data-pin') || '').toLowerCase();

            console.log(`Comparando: "${name}" / "${pin}" con "${searchTerm}"`);

            // Buscar por nombre o PIN
            if (name.includes(searchTerm) || pin.includes(searchTerm)) {
                result.style.display = '';
                visibleCount++;
                console.log('✅ Coincidencia encontrada');
            } else {
                result.style.display = 'none';
                console.log('❌ No coincide');
            }
        });

        console.log(`📊 Resultados visibles: ${visibleCount}`);

        // Mostrar mensaje si no hay resultados
        if (visibleCount === 0) {
            if (noResults) {
                noResults.classList.remove('hidden');
            }
            resultsGrid.style.display = 'none';
        } else {
            if (noResults) {
                noResults.classList.add('hidden');
            }
            resultsGrid.style.display = 'grid';
        }
    }

    // Eventos de búsqueda
    searchInput.addEventListener('input', performSearch);
    searchInput.addEventListener('keyup', performSearch);

    // Click en las cards para ver detalles
    allResults.forEach(result => {
        result.addEventListener('click', function() {
            const quizId = this.getAttribute('data-quiz-id');
            if (quizId) {
                window.location.href = `/quiz/${quizId}`;
            }
        });
        
        // Añadir cursor pointer
        result.style.cursor = 'pointer';
    });

    console.log('✅ Búsqueda inicializada correctamente');
});
