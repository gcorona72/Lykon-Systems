(function() {
  'use strict';

  // Función para eliminar el badge "Buy Template" (LemonSqueezy)
  function removeBuyTemplateBadge() {
    let removed = false;

    // Buscar por contenedor específico
    const container = document.querySelector('.framer-60pafq-container');
    if (container && container.parentElement) {
      container.remove();
      removed = true;
    }

    // Buscar por enlace a lemonsqueezy
    document.querySelectorAll('a[href*="lemonsqueezy"]').forEach(function(link) {
      const text = (link.textContent || '').trim().toLowerCase();
      if (text.includes('buy') || text.includes('template')) {
        // Buscar el contenedor padre más cercano
        let parent = link.closest('.framer-60pafq-container');
        if (!parent) parent = link.closest('div[class*="container"]');
        if (!parent) parent = link.parentElement;

        if (parent) {
          parent.remove();
          removed = true;
        }
      }
    });

    // Buscar por clase específica del badge
    document.querySelectorAll('.framer-Dqd5S, .framer-m90iev, .framer-g8apuh').forEach(function(el) {
      const href = el.getAttribute('href');
      if (href && href.includes('lemonsqueezy')) {
        let parent = el.closest('div[class*="container"]');
        if (!parent) parent = el.parentElement;
        if (parent) {
          parent.remove();
          removed = true;
        }
      }
    });

    return removed;
  }

  // Función para eliminar el badge "Made in Framer"
  function removeFramerBadge() {
    let removed = false;

    // Buscar por ID del contenedor
    const badgeContainer = document.getElementById('__framer-badge-container');
    if (badgeContainer && badgeContainer.parentElement) {
      badgeContainer.remove();
      removed = true;
    }

    // Buscar por clase del badge
    document.querySelectorAll('.__framer-badge, .framer-6jWyo, .framer-n0ccwk').forEach(function(badge) {
      if (badge.parentElement) {
        const container = badge.closest('#__framer-badge-container') || badge.parentElement;
        container.remove();
        removed = true;
      }
    });

    // Buscar por enlace a framer.com con data-nosnippet
    document.querySelectorAll('a[href*="framer.com"][data-nosnippet="true"]').forEach(function(link) {
      const container = link.closest('div') || link.parentElement;
      if (container) {
        container.remove();
        removed = true;
      }
    });

    // Buscar por clase específica del backdrop
    document.querySelectorAll('.framer-13yxzio').forEach(function(el) {
      const badge = el.closest('a.__framer-badge');
      if (badge) {
        const container = badge.parentElement;
        if (container) {
          container.remove();
          removed = true;
        }
      }
    });

    return removed;
  }

  // Función principal que elimina ambos badges
  function removeBadges() {
    const buyRemoved = removeBuyTemplateBadge();
    const framerRemoved = removeFramerBadge();
    return buyRemoved || framerRemoved;
  }

  // Función para observar cambios en el DOM
  function observeAndRemove(duration) {
    const endTime = Date.now() + duration;
    let attempts = 0;
    const maxAttempts = 40;

    // MutationObserver para detectar cambios en el DOM
    const observer = new MutationObserver(function() {
      removeBadges();
      if (Date.now() > endTime) {
        observer.disconnect();
      }
    });

    // Observar cambios en todo el documento
    observer.observe(document.documentElement, {
      subtree: true,
      childList: true,
      attributes: false
    });

    // Reintentos rápidos adicionales
    const intervalId = setInterval(function() {
      attempts++;
      const removed = removeBadges();

      if (attempts >= maxAttempts || Date.now() > endTime) {
        clearInterval(intervalId);
      }
    }, 150);

    // Desconectar el observer después del tiempo especificado
    setTimeout(function() {
      observer.disconnect();
      clearInterval(intervalId);
    }, duration);
  }

  // Inicializar la eliminación
  function init() {
    // Eliminar inmediatamente
    removeBadges();

    // Observar cambios durante 10 segundos para resistir la rehidratación
    observeAndRemove(10000);

    // Reintentos adicionales en momentos clave
    setTimeout(removeBadges, 500);
    setTimeout(removeBadges, 1000);
    setTimeout(removeBadges, 2000);
  }

  // Ejecutar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // También ejecutar en el evento load por si acaso
  window.addEventListener('load', function() {
    removeBadges();
    observeAndRemove(5000);
  });

})();

