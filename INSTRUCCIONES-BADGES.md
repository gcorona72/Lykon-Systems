# Solución para eliminar badges de Framer de forma permanente

## Problema
Framer rehidrata el DOM al cargar y restaura los badges:
1. **Badge "Buy Template"** (LemonSqueezy) - clase `.framer-60pafq-container`
2. **Badge "Made in Framer"** - ID `#__framer-badge-container`

## Solución implementada

Se han creado dos archivos:
- `remove-badges.js` - Script JavaScript que elimina los badges resistiendo la rehidratación
- `hide-badges.css` - CSS de respaldo para ocultar los badges

## Cómo aplicar la solución

### Opción 1: Editar manualmente el index.html (RECOMENDADO)

Abre el archivo `index.html` y busca la sección que dice:

```html
<!-- Start of bodyEnd -->

<!-- End of bodyEnd -->
```

Reemplázala con:

```html
<!-- Start of bodyEnd -->

<!-- CSS de respaldo para ocultar badges -->
<link rel="stylesheet" href="./hide-badges.css">

<!-- Script para eliminar badges de forma permanente -->
<script src="./remove-badges.js"></script>

<!-- End of bodyEnd -->
```

### Opción 2: Insertar el código directamente (sin archivos externos)

Si prefieres no usar archivos externos, busca la misma sección y reemplázala con:

```html
<!-- Start of bodyEnd -->

<!-- CSS de respaldo para ocultar badges -->
<style>
  /* Badge Buy Template (LemonSqueezy) */
  .framer-60pafq-container,
  .framer-Dqd5S[href*="lemonsqueezy"],
  a[href*="lemonsqueezy"][href*="buy"] {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
  }
  
  /* Badge Made in Framer */
  .__framer-badge,
  #__framer-badge-container,
  a[href*="framer.com"][data-nosnippet="true"] {
    display: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
  }
</style>

<!-- Script para eliminar badges -->
<script src="./remove-badges.js"></script>

<!-- End of bodyEnd -->
```

## Cómo funciona

### El script JavaScript:

1. **Detección múltiple**: Busca los badges por:
   - Clases CSS específicas (`.framer-60pafq-container`, `.__framer-badge`)
   - IDs (`#__framer-badge-container`)
   - Enlaces a LemonSqueezy y Framer.com
   - Contenido de texto ("Buy Template", "Made in Framer")

2. **Eliminación idempotente**: Elimina de forma segura sin duplicar esfuerzos

3. **Resistencia a rehidratación**:
   - MutationObserver que observa cambios en el DOM durante 10 segundos
   - Reintentos cada 150ms durante 40 intentos
   - Ejecución adicional en eventos clave (DOMContentLoaded, load)

4. **Fallbacks**: Múltiples estrategias de detección por si Framer cambia las clases

### El CSS:

- Oculta los badges inmediatamente con `display: none !important`
- Respaldo por si el JavaScript tarda en ejecutarse
- Múltiples selectores para cubrir todas las variantes

## Ventajas de esta solución

✅ **Permanente**: Sobrevive a la rehidratación de Framer
✅ **Robusta**: Múltiples métodos de detección
✅ **Rápida**: CSS oculta inmediatamente, JS elimina definitivamente
✅ **Sin efectos secundarios**: Solo elimina los badges específicos
✅ **Reutilizable**: Funciona en todas las páginas del sitio

## Aplicar a todas las páginas

Para aplicar la solución a todas las páginas del sitio, debes añadir las mismas líneas en:

- `index.html` ✓
- `agency` (si es un HTML)
- `blog.1` (si es un HTML)
- `contact` (si es un HTML)
- `projects.1` (si es un HTML)
- Y cualquier otra página HTML del sitio

Busca siempre la sección `<!-- Start of bodyEnd -->` en cada archivo.

## Verificación

Para verificar que funciona:

1. Abre el sitio en un navegador
2. Abre las DevTools (F12)
3. Ve a la pestaña Elements/Elementos
4. Busca `.framer-60pafq-container` o `#__framer-badge-container`
5. Si no los encuentras, ¡funciona correctamente! ✓

También puedes buscar en la consola errores de carga de los archivos.

## Notas importantes

⚠️ **Atención**: Si Framer actualiza el sitio desde su editor, estos cambios pueden sobrescribirse. Guarda copias de los archivos `remove-badges.js` y `hide-badges.css` para poder volver a aplicarlos.

💡 **Tip**: Considera hacer esta modificación en tu flujo de build/deploy automático si usas uno.

## Patrón reutilizable

Este mismo patrón se puede usar para eliminar cualquier otro elemento molesto:

1. Identifica las clases/IDs del elemento
2. Añádelas al CSS
3. Crea funciones de detección en el JS
4. Usa MutationObserver para resistir cambios dinámicos

---

**Fecha de creación**: Noviembre 2025
**Autor**: Solución basada en el patrón de rehidratación de Framer

