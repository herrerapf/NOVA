// Control sencillo y robusto de modales (abrir, cerrar, overlay, escape).
document.addEventListener('DOMContentLoaded', function () {
  // Selectores
  const openCrear = document.getElementById('btn-crear');
  const openLogin = document.getElementById('btn-login');
  const modalOverlay = document.getElementById('modal-overlay');
  const modalRegistrar = document.getElementById('modal-registrar');
  const modalLogin = document.getElementById('modal-login');

  // Helper: abrir modal (elemento DOM)
  function openModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.remove('hidden');
    modalEl.setAttribute('aria-hidden', 'false');
    modalOverlay.classList.remove('hidden');
    document.body.classList.add('modal-open'); // evita scroll de fondo
    
    const firstInput = modalEl.querySelector('input, button, textarea, select');
    if (firstInput) firstInput.focus();
  }
  // static/js/home.js - manejo simple de modales (sin librerías)
document.addEventListener('DOMContentLoaded', function () {
  function openModal(id) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(id);
    if(!modal || !overlay) return;
    overlay.classList.remove('hidden');
    overlay.classList.add('active');
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
  }
  function closeModal(id) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(id);
    if(!modal || !overlay) return;
    overlay.classList.add('hidden');
    overlay.classList.remove('active');
    modal.classList.add('hidden');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
  }

  // botones
  const btnCrear = document.getElementById('btn-crear');
  const btnLogin = document.getElementById('btn-login');
  if(btnCrear) btnCrear.addEventListener('click', () => openModal('modal-registrar'));
  if(btnLogin) btnLogin.addEventListener('click', () => openModal('modal-login'));

  // cerrar modales desde los botones de cierre
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = btn.getAttribute('data-target');
      if(target) closeModal(target);
    });
  });

  // cerrar al tocar overlay
  const overlay = document.getElementById('modal-overlay');
  if(overlay) overlay.addEventListener('click', (e) => {
    // cerrar cualquier modal abierto
    document.querySelectorAll('.modal:not(.hidden)').forEach(m=>{
      m.classList.add('hidden');
      m.setAttribute('aria-hidden','true');
    });
    overlay.classList.add('hidden');
    overlay.classList.remove('active');
    document.body.classList.remove('modal-open');
  });

});


  // Helper: cerrar modal
  function closeModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.add('hidden');
    modalEl.setAttribute('aria-hidden', 'true');
    // verificar si hay otro modal abierto
    const anyOpen = document.querySelectorAll('.modal:not(.hidden)').length > 0;
    if (!anyOpen) {
      modalOverlay.classList.add('hidden');
      document.body.classList.remove('modal-open');
    }
  }

  // Abrir botones (si existen)
  if (openCrear) {
    openCrear.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(modalRegistrar);
    });
  }
  if (openLogin) {
    openLogin.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(modalLogin);
    });
  }

  // Overlay click cierra todos los modales
  if (modalOverlay) {
    modalOverlay.addEventListener('click', function () {
      document.querySelectorAll('.modal:not(.hidden)').forEach(function (m) {
        closeModal(m);
      });
    });
  }

  // Cerrar por botones con clase .modal-close (tienen data-target con id opcional)
  document.querySelectorAll('.modal-close').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const target = btn.getAttribute('data-target');
      if (target) {
        const m = document.getElementById(target);
        closeModal(m);
      } else {
        // si no tiene data-target, cierra el modal padre
        const parentModal = btn.closest('.modal');
        closeModal(parentModal);
      }
    });
  });

  // Cerrar con tecla Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal:not(.hidden)').forEach(function (m) {
        closeModal(m);
      });
    }
  });

  // Seguridad: si formularios tienen botones tipo=submit, permitir comportamiento normal.
  // Además: si en el markup se usa enlaces para abrir (a[href="#"]), prevenir navegación accidental
  document.querySelectorAll('a[href="#"]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
    });
  });

  // --- Optional: support for automatically opening modal via hash (#login, #register)
  if (window.location.hash) {
    const h = window.location.hash.replace('#', '');
    if (h === 'login') openModal(modalLogin);
    if (h === 'register' || h === 'signup') openModal(modalRegistrar);
  }
});
