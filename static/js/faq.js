// Funcionalidad de acordeón para FAQ
document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => {
        const faqItem = button.parentElement;
        const isActive = faqItem.classList.contains('active');
        
        // Cerrar todos los items
        document.querySelectorAll('.faq-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Abrir el clickeado si no estaba activo
        if (!isActive) {
            faqItem.classList.add('active');
        }
    });
});
