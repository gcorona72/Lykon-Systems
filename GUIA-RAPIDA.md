# 🎯 GUÍA RÁPIDA: Eliminar badges de Framer

## ✅ TODO ESTÁ LISTO - Solo falta insertar el código

---

## 📝 INSTRUCCIONES PASO A PASO

### Paso 1: Abre tu editor de código favorito
- VS Code, Sublime Text, o cualquier editor de texto
- Abre el archivo `index.html` del proyecto

### Paso 2: Busca esta sección (alrededor de la línea 551)

Usa Ctrl+F (o Cmd+F en Mac) para buscar:

```
<!-- Start of bodyEnd -->
```

Verás algo como esto:

```html
    <!-- Start of bodyEnd -->

    <!-- End of bodyEnd -->
```

### Paso 3: REEMPLAZA todo desde `<!-- Start of bodyEnd -->` hasta `<!-- End of bodyEnd -->`

Abre el archivo **`codigo-para-insertar.html`** que está en la misma carpeta.

**Copia TODO su contenido** y reemplaza las líneas del Paso 2.

El resultado final debe verse así:

```html
    <!-- Start of bodyEnd -->
    
    <!-- CSS de respaldo para ocultar badges de Framer -->
    <style>
      /* Badge "Buy Template" de LemonSqueezy */
      .framer-60pafq-container,
      .framer-Dqd5S[href*="lemonsqueezy"],
      a[href*="lemonsqueezy"][href*="buy"],
      div[class*="container"]:has(a[href*="lemonsqueezy"]) {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }
      
      /* Badge "Made in Framer" */
      .__framer-badge,
      #__framer-badge-container,
      .framer-6jWyo,
      .framer-n0ccwk,
      a[href*="framer.com"][data-nosnippet="true"] {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }
    </style>
    
    <!-- Script para eliminar badges de forma permanente -->
    <script>
    (function() {
      'use strict';
      
      function removeBuyTemplateBadge() {
        let removed = false;
        const container = document.querySelector('.framer-60pafq-container');
        if (container && container.parentElement) {
          container.remove();
          removed = true;
        }
        document.querySelectorAll('a[href*="lemonsqueezy"]').forEach(function(link) {
          const text = (link.textContent || '').trim().toLowerCase();
          if (text.includes('buy') || text.includes('template')) {
            let parent = link.closest('.framer-60pafq-container') || link.closest('div[class*="container"]') || link.parentElement;
            if (parent) {
              parent.remove();
              removed = true;
            }
          }
        });
        return removed;
      }
      
      function removeFramerBadge() {
        let removed = false;
        const badgeContainer = document.getElementById('__framer-badge-container');
        if (badgeContainer && badgeContainer.parentElement) {
          badgeContainer.remove();
          removed = true;
        }
        document.querySelectorAll('.__framer-badge, .framer-6jWyo, .framer-n0ccwk').forEach(function(badge) {
          if (badge.parentElement) {
            const container = badge.closest('#__framer-badge-container') || badge.parentElement;
            container.remove();
            removed = true;
          }
        });
        document.querySelectorAll('a[href*="framer.com"][data-nosnippet="true"]').forEach(function(link) {
          const container = link.closest('div') || link.parentElement;
          if (container) {
            container.remove();
            removed = true;
          }
        });
        return removed;
      }
      
      function removeBadges() {
        return removeBuyTemplateBadge() || removeFramerBadge();
      }
      
      function observeAndRemove(duration) {
        const endTime = Date.now() + duration;
        let attempts = 0;
        const observer = new MutationObserver(function() {
          removeBadges();
          if (Date.now() > endTime) observer.disconnect();
        });
        observer.observe(document.documentElement, { subtree: true, childList: true });
        const intervalId = setInterval(function() {
          attempts++;
          removeBadges();
          if (attempts >= 40 || Date.now() > endTime) clearInterval(intervalId);
        }, 150);
        setTimeout(function() {
          observer.disconnect();
          clearInterval(intervalId);
        }, duration);
      }
      
      function init() {
        removeBadges();
        observeAndRemove(10000);
        setTimeout(removeBadges, 500);
        setTimeout(removeBadges, 1000);
        setTimeout(removeBadges, 2000);
      }
      
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
      } else {
        init();
      }
      
      window.addEventListener('load', function() {
        removeBadges();
        observeAndRemove(5000);
      });
    })();
    </script>
    
    <!-- End of bodyEnd -->
```

### Paso 4: Guarda el archivo

- Ctrl+S (o Cmd+S en Mac)
- O Archivo → Guardar

### Paso 5: Prueba tu sitio

1. Abre `index.html` en un navegador
2. ¡Los badges deberían haber desaparecido! 🎉

---

## ❓ ¿Qué pasa si no encuentras `<!-- Start of bodyEnd -->`?

**Alternativa**: Busca el cierre de la etiqueta `</body>`

Inserta el código **justo ANTES** de `</body>`:

```html
    <!-- CSS y Script para eliminar badges -->
    <style>
      /* ... todo el CSS del archivo codigo-para-insertar.html ... */
    </style>
    <script>
      /* ... todo el JS del archivo codigo-para-insertar.html ... */
    </script>

  </body>
</html>
```

---

## 🔍 Verificación

### ¿Funcionó?

Abre tu navegador y presiona F12 (DevTools):

1. **Consola**: No debería haber errores
2. **Elements**: Busca (Ctrl+F):
   - `.framer-60pafq-container` → **No debe existir** ✅
   - `#__framer-badge-container` → **No debe existir** ✅

### ¿Sigues viendo los badges?

Revisa:
1. ¿Copiaste TODO el código de `codigo-para-insertar.html`?
2. ¿Guardaste el archivo index.html?
3. ¿Refrescaste el navegador (Ctrl+F5 o Cmd+Shift+R)?

---

## 📁 Archivos en tu proyecto

- ✅ `remove-badges.js` - Script independiente
- ✅ `hide-badges.css` - Estilos independientes
- ✅ `codigo-para-insertar.html` - **ESTE ES EL QUE NECESITAS COPIAR**
- ✅ `INSTRUCCIONES-BADGES.md` - Documentación completa
- ✅ `GUIA-RAPIDA.md` - Este archivo

---

## 🚨 IMPORTANTE

Si Framer regenera tu sitio, tendrás que volver a insertar el código.

**Solución**: Guarda una copia de `codigo-para-insertar.html` en un lugar seguro.

---

## ✅ Aplicar a otras páginas

Repite los pasos 1-4 en:
- `agency`
- `blog.1`
- `contact`
- `projects.1`

---

## 🎉 ¡Listo!

Tu sitio ahora está libre de badges molestos.

**¿Problemas?** Consulta `INSTRUCCIONES-BADGES.md` para más detalles.

