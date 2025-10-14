// Búsqueda dinámica por nombre o PIN usando el input del header
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-container input[name="q"]');
    const searchForm = document.querySelector('.search-container');
    const resultsGrid = document.getElementById('resultsGrid');
    const noResults = document.getElementById('noResults');
    const allResults = resultsGrid.querySelectorAll('.result');

    if (searchInput && searchForm) {
        // Prevenir el envío del formulario
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });

        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let visibleCount = 0;

            allResults.forEach(result => {
                const name = result.getAttribute('data-name').toLowerCase();
                const pin = result.getAttribute('data-pin').toLowerCase();

                // Buscar por nombre o PIN
                if (name.includes(searchTerm) || pin.includes(searchTerm)) {
                    result.style.display = 'block';
                    visibleCount++;
                } else {
                    result.style.display = 'none';
                }
            });

            // Mostrar mensaje si no hay resultados
            if (visibleCount === 0 && searchTerm !== '') {
                noResults.classList.remove('hidden');
                resultsGrid.style.display = 'none';
            } else {
                noResults.classList.add('hidden');
                resultsGrid.style.display = 'grid';
            }
        });
    }
});
