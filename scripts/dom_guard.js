/*
  DOM Guard: protege tus clases personalizadas (prefijo custom-) y elimina badges/promos
  sin interferir con el runtime principal de Framer (animaciones/variantes siguen).

  Convención recomendada:
  - Marca las clases tuyas con prefijo `custom-` (p. ej. custom-hero, custom-titulo).
  - (Opcional) En elementos críticos añade data-custom-classes="custom-uno custom-dos" para reforzar.
*/
(function () {
  'use strict';

  var CUSTOM_PREFIX = 'custom-';
  var running = false; // para evitar reentradas
  // --- NUEVO: Configuración de atributos protegidos ---
  var PROTECTED_ATTR_PREFIXES = ['data-custom-', 'data-protect-'];
  var EXACT_PROTECTED_ATTRS = ['data-locked']; // puedes añadir más aquí
  var protectedAttrSnapshot = new WeakMap(); // element -> { attrName: value }
  var debug = false; // activar con window.domGuard.debug = true;
  var mutationQueue = [];
  var scheduled = false;

  function log() { if (debug) console.log.apply(console, ['[dom-guard]'].concat([].slice.call(arguments))); }

  function isCustomClass(cls) {
    return typeof cls === 'string' && cls.indexOf(CUSTOM_PREFIX) === 0;
  }

  function parseCustomDataset(el) {
    var list = (el && el.getAttribute && el.getAttribute('data-custom-classes')) || '';
    if (!list) return [];
    return list.split(/\s+/).filter(Boolean).filter(isCustomClass);
  }

  function desiredCustomClasses(el) {
    // 1) dataset explícito
    var fromData = parseCustomDataset(el);
    if (fromData.length) return fromData;
    // 2) fallback: las que ya tenga el elemento con prefijo custom-
    var have = [];
    if (el && el.classList) {
      el.classList.forEach(function (c) { if (isCustomClass(c)) have.push(c); });
    }
    return have;
  }

  function ensureCustom(el) {
    if (!el || !el.classList) return false;
    var desired = desiredCustomClasses(el);
    if (!desired.length) return false;
    var changed = false;
    for (var i = 0; i < desired.length; i++) {
      var cls = desired[i];
      if (!el.classList.contains(cls)) {
        el.classList.add(cls);
        changed = true;
        log('Reañadida clase custom:', cls, 'en', el);
      }
    }
    return changed;
  }

  function applyOverrides(root) {
    if (!root) root = document;
    // Para rendimiento, solo tocamos nodos que ya declaran dataset o tienen clases custom-
    var sel = '[data-custom-classes], [class*="' + CUSTOM_PREFIX + '"]';
    var list = root.querySelectorAll(sel);
    for (var i = 0; i < list.length; i++) ensureCustom(list[i]);
  }

  // --- NUEVO: Protección de atributos ---
  function isProtectedAttribute(name) {
    if (!name) return false;
    if (EXACT_PROTECTED_ATTRS.indexOf(name) !== -1) return true;
    for (var i = 0; i < PROTECTED_ATTR_PREFIXES.length; i++) {
      if (name.indexOf(PROTECTED_ATTR_PREFIXES[i]) === 0) return true;
    }
    return false;
  }

  function snapshotProtectedAttributes(el) {
    if (!el || el.nodeType !== 1) return; // ELEMENT_NODE
    var record = protectedAttrSnapshot.get(el) || {};
    // Guardar atributos que cumplan criterio
    for (var i = 0; i < el.attributes.length; i++) {
      var attr = el.attributes[i];
      if (isProtectedAttribute(attr.name)) {
        record[attr.name] = attr.value;
      }
    }
    if (Object.keys(record).length) protectedAttrSnapshot.set(el, record);
  }

  function restoreProtectedAttributes(el) {
    var record = protectedAttrSnapshot.get(el);
    if (!record) return false;
    var changed = false;
    Object.keys(record).forEach(function (attrName) {
      var current = el.getAttribute(attrName);
      if (current !== record[attrName]) {
        el.setAttribute(attrName, record[attrName]);
        changed = true;
        log('Restaurado atributo protegido', attrName, '->', record[attrName]);
      }
    });
    return changed;
  }

  function snapshotTree(root) {
    var all = root.querySelectorAll('[data-custom-classes], [class*="' + CUSTOM_PREFIX + '"], *');
    for (var i = 0; i < all.length; i++) snapshotProtectedAttributes(all[i]);
    // añadir snapshot de texto visible
    snapshotTextTree(root);
  }

  // Badges / Promos: eliminar si aparecen
  function removeBadgesOnce() {
    var removed = false;
    var badgeContainer = document.getElementById('__framer-badge-container');
    if (badgeContainer && badgeContainer.parentElement) {
      badgeContainer.remove();
      removed = true;
      log('Badge container eliminado');
    }
    var badgeAny = document.querySelectorAll('.__framer-badge, .framer-6jWyo, .framer-n0ccwk');
    badgeAny.forEach(function (b) { if (b && b.parentElement) { b.parentElement.remove(); removed = true; log('Badge eliminado'); } });

    var buyBtn = document.querySelectorAll('.framer-60pafq-container, a[href*="lemonsqueezy"]');
    buyBtn.forEach(function (n) {
      var parent = n.closest('.framer-60pafq-container') || n.closest('div[class*="container"]') || n.parentElement;
      if (parent && parent.parentElement) { parent.remove(); removed = true; log('Elemento promocional eliminado'); }
    });
    return removed;
  }

  // --- NUEVO: Protección de texto visible ---
  var TEXT_PROTECT_ENABLED = true;
  var textSnapshot = new WeakMap(); // element -> original textContent
  var SKIP_TEXT_TAGS = { SCRIPT:1, STYLE:1, NOSCRIPT:1, TEXTAREA:1, INPUT:1, SVG:0 };

  function isTextBearingElement(el) {
    if (!el || el.nodeType !== 1) return false;
    if (SKIP_TEXT_TAGS[el.tagName]) return false;
    if (el.hasAttribute('data-allow-text-change')) return false; // opt-out explícito
    // Heurística: tags típicos y/o si contiene algún nodo de texto no vacío
    var tag = el.tagName;
    if (/^(H1|H2|H3|H4|H5|H6|P|SPAN|A|LI|BUTTON|STRONG|EM|SMALL|LABEL|DIV)$/i.test(tag)) return true;
    for (var i = 0; i < el.childNodes.length; i++) {
      var n = el.childNodes[i];
      if (n.nodeType === 3 && /\S/.test(n.nodeValue)) return true; // text node con no-espacio
    }
    return false;
  }

  function snapshotText(el) {
    if (!TEXT_PROTECT_ENABLED) return;
    if (!isTextBearingElement(el)) return;
    try { textSnapshot.set(el, el.textContent); } catch (e) { /* ignore */ }
  }

  function restoreText(el) {
    if (!TEXT_PROTECT_ENABLED) return false;
    if (!isTextBearingElement(el)) return false;
    var orig = textSnapshot.get(el);
    if (typeof orig !== 'string') return false;
    var now = el.textContent;
    if (now !== orig) {
      el.textContent = orig;
      log('Restaurado texto en', el);
      return true;
    }
    return false;
  }

  function snapshotTextTree(root) {
    if (!TEXT_PROTECT_ENABLED) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null);
    var node;
    while ((node = walker.nextNode())) snapshotText(node);
  }

  // --- THROTTLE de mutaciones ---
  function scheduleProcess() {
    if (scheduled) return;
    scheduled = true;
    // usar requestAnimationFrame si disponible para agrupar
    var runner = function () {
      try { processMutationBatch(mutationQueue.splice(0)); } finally { scheduled = false; }
    };
    (window.requestAnimationFrame || setTimeout)(runner, 30);
  }

  function processMutationBatch(mutations) {
    if (!mutations.length) return;
    if (running) return; // evitar recursión
    running = true;
    try {
      var touched = false;
      for (var i = 0; i < mutations.length; i++) {
        var m = mutations[i];
        if (m.type === 'attributes') {
          if (m.attributeName === 'class' && m.target) {
            touched = ensureCustom(m.target) || touched;
          } else if (isProtectedAttribute(m.attributeName)) {
            touched = restoreProtectedAttributes(m.target) || touched;
          }
        } else if (m.type === 'characterData') {
          // Restaurar texto si fue alterado
          var host = m.target && m.target.parentNode && m.target.parentNode.nodeType === 1 ? m.target.parentNode : null;
          if (host) touched = restoreText(host) || touched;
        } else if (m.type === 'childList') {
          if (m.addedNodes && m.addedNodes.length) {
            for (var j = 0; j < m.addedNodes.length; j++) {
              var node = m.addedNodes[j];
              if (node && node.nodeType === 1) { // Element
                snapshotProtectedAttributes(node);
                ensureCustom(node);
                try { applyOverrides(node); } catch (e) {}
                // capturar texto inicial del nuevo subárbol
                snapshotTextTree(node);
              }
            }
          }
        }
      }
      if (touched) log('Mutaciones procesadas. Correcciones aplicadas.');
      removeBadgesOnce();
    } finally { running = false; }
  }

  function startObserver() {
    var mo = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) mutationQueue.push(muts[i]);
      scheduleProcess();
    });
    mo.observe(document.documentElement, {
      subtree: true,
      childList: true,
      attributes: true,
      characterData: true,
      characterDataOldValue: false
    });
    window.__domGuardObserver = mo;
  }

  function init() {
    setTimeout(function () {
      try {
        snapshotTree(document);
        applyOverrides(document);
        removeBadgesOnce();
        startObserver();
        // Re-snapshot de texto cuando el traductor runtime termine su primera pasada
        try {
          window.addEventListener('runtime-translate-ready', function(){
            log('evento runtime-translate-ready recibido, snapshot de texto');
            snapshotTextTree(document);
          });
        } catch (e) {}
        // Fallback: si no hay evento, intentar re-snapshot pasado un tiempo
        setTimeout(function(){ snapshotTextTree(document); }, 800);
        window.domGuard = {
          applyOverrides: function () { applyOverrides(document); },
          removeBadges: removeBadgesOnce,
          CUSTOM_PREFIX: CUSTOM_PREFIX,
          debug: false, // activar manualmente: window.domGuard.debug = true;
          resnapshot: function () { snapshotTree(document); log('Re-snapshot completo'); },
          restoreAll: function () {
            var els = document.querySelectorAll('*');
            els.forEach(restoreProtectedAttributes);
            applyOverrides(document);
            log('Restauración masiva completada');
          }
        };
        Object.defineProperty(window.domGuard, 'debug', {
          get: function () { return debug; },
          set: function (v) { debug = !!v; log('Debug:', debug); }
        });
        log('DOM Guard inicializado');
      } catch (e) { if (debug) console.error('[dom-guard] init error', e); }
    }, 0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
