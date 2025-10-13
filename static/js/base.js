
(() => {
  const avatarBtn = document.getElementById('avatarBtn');
  const menuList = document.getElementById('menuList');
  if (avatarBtn && menuList){
    avatarBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = menuList.classList.toggle('open');
      avatarBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    
    // Cerrar menú al hacer clic fuera, pero NO dentro del menú
    document.addEventListener('click', (e) => {
      if (!menuList.contains(e.target) && e.target !== avatarBtn) {
        menuList.classList.remove('open');
        avatarBtn && avatarBtn.setAttribute('aria-expanded', 'false');
      }
    });
    
    // Permitir que los enlaces funcionen normalmente
    menuList.addEventListener('click', (e) => {
      if (e.target.tagName === 'A') {
        // Dejar que el navegador siga el enlace normalmente
        e.stopPropagation();
      }
    });
  }

  // Auto-close flash messages after 5 seconds
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach(msg => {
    setTimeout(() => {
      msg.style.animation = 'slideOut 0.3s ease-in';
      setTimeout(() => msg.remove(), 300);
    }, 5000);
  });
})();

