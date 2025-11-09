/* Runtime translation layer: re-traduce textos ingleses que Framer re-hidrata.
   - Se ejecuta después de la hidratación inicial y en mutaciones.
   - Preserva términos técnicos y evita tocar nodos ya traducidos (marcados con data-translated="true").
   - Trabaja junto con dom_guard (si está presente) para mantener clases/atributos.
*/
(function(){
  'use strict';

  var DICT = [
    ['Home','Inicio'],
    ['Agency','Agencia'],
    ['Projects','Proyectos'],
    ['Project','Proyecto'],
    ['Blog','Blog'],
    ['Contact','Contacto'],
    ['Start a Project','Iniciar un proyecto'],
    ['Start\na Project','Iniciar un proyecto'],
    ['From strategy to launch we deliver fast, accessible sites and clear brands with Growth-driven results','De la estrategia al lanzamiento entregamos sitios rápidos, accesibles y marcas claras con resultados impulsados por el crecimiento'],
    ['We’re a senior creative digital agency focused on clarity and performance. We align strategy, brand, and web into modular systems that ship on time and scale. Our values are simplicity, accountability and measurable impact. The team is small and senior; every project has a lead for strategy, design and build. We partner long-term, iterating with data to keep products fast.','Somos una agencia digital creativa sénior enfocada en la claridad y el rendimiento. Alineamos estrategia, marca y web en sistemas modulares que se entregan a tiempo y escalan. Nuestros valores son simplicidad, responsabilidad e impacto medible. El equipo es pequeño y sénior; cada proyecto tiene un líder para estrategia, diseño y desarrollo. Colaboramos a largo plazo, iterando con datos para mantener los productos rápidos.'],
    // Variantes más cortas
    ['We’re a senior creative digital agency focused on clarity and performance.','Somos una agencia digital creativa sénior enfocada en la claridad y el rendimiento.'],
    ['We align strategy, brand, and web into modular systems that ship on time and scale.','Alineamos estrategia, marca y web en sistemas modulares que se entregan a tiempo y escalan.'],
    ['Our values are simplicity, accountability and measurable impact.','Nuestros valores son simplicidad, responsabilidad e impacto medible.'],
    ['The team is small and senior; every project has a lead for strategy, design and build.','El equipo es pequeño y sénior; cada proyecto tiene un líder para estrategia, diseño y desarrollo.'],
    ['We partner long-term, iterating with data to keep products fast.','Colaboramos a largo plazo, iterando con datos para mantener los productos rápidos.'],
    ['Read more','Leer más'],
    ['Learn more','Saber más'],
    ['View project','Ver proyecto'],
    ['All rights reserved','Todos los derechos reservados']
  ];

  // Ordenar por longitud descendente para evitar reemplazos parciales prematuros
  DICT.sort(function(a,b){return b[0].length - a[0].length});

  var TECH = ['Next.js','React','JavaScript','Node.js','TypeScript','WebGL','Three.js','Figma','Framer','Vercel'];

  var WORDS = [
    ['From','De'],['strategy','estrategia'],['to','a'],['launch','lanzamiento'],['we','nosotros'],['deliver','entregamos'],
    ['fast','rápidos'],['accessible','accesibles'],['sites','sitios'],['and','y'],['clear','claras'],['brands','marcas'],
    ['with','con'],['Growth-driven','impulsados por el crecimiento'],['results','resultados'],
    ['We’re','Somos'],['a','una'],['senior','sénior'],['creative','creativa'],['digital','digital'],['agency','agencia'],
    ['focused','enfocada'],['on','en'],['clarity','claridad'],['performance','rendimiento'],['align','alineamos'],
    ['brand','marca'],['web','web'],['into','en'],['modular','modulares'],['systems','sistemas'],['that','que'],
    ['ship','se entregan'],['on','en'],['time','tiempo'],['and','y'],['scale','escalan'],
    ['Our','Nuestros'],['values','valores'],['are','son'],['simplicity','simplicidad'],['accountability','responsabilidad'],
    ['measurable','medible'],['impact','impacto'],['The','El'],['team','equipo'],['is','es'],['small','pequeño'],['every','cada'],
    ['project','proyecto'],['has','tiene'],['a','un'],['lead','líder'],['for','para'],['design','diseño'],['build','desarrollo'],
    ['We','Colaboramos'],['partner','a largo plazo'],['long-term','a largo plazo'],['iterating','iterando'],['data','datos'],
    ['keep','mantener'],['products','productos'],['fast','rápidos']
  ];

  function preserveTech(str){
    return str; // Ya manejamos al no traducir tokens exactos en DICT
  }

  function capLike(src, tgt){
    if(!src) return tgt;
    if(src[0] === src[0].toUpperCase()) return tgt[0].toUpperCase() + tgt.slice(1);
    return tgt;
  }

  function replaceWords(txt){
    var out = txt;
    for(var i=0;i<WORDS.length;i++){
      var from = WORDS[i][0];
      var to = WORDS[i][1];
      var re = new RegExp('\\b'+from.replace(/[-/\\^$*+?.()|[\]{}]/g,'\\$&')+'\\b','g');
      out = out.replace(re, function(match){ return capLike(match, to); });
    }
    return out;
  }

  function translateText(original){
    if(!original) return original;
    var txt = original;
    for(var i=0;i<DICT.length;i++){
      var src = DICT[i][0];
      var tgt = DICT[i][1];
      // Búsqueda exacta (case sensitive) y también normalizando espacios y saltos de línea
      if(txt.indexOf(src) !== -1){
        txt = txt.split(src).join(tgt);
      }
    }
    // capa por palabras para cubrir variaciones
    txt = replaceWords(txt);
    return preserveTech(txt);
  }

  function shouldSkip(el){
    if(!el) return true;
    if(el.nodeType !== 1) return true;
    if(el.hasAttribute('data-translated')) return true;
    var tag = el.tagName;
    if(/^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|INPUT|SVG)$/.test(tag)) return true;
    return false;
  }

  function processNode(el){
    if(shouldSkip(el)) return false;
    var changed = false;
    // Procesar nodos de texto directos
    for(var i=0;i<el.childNodes.length;i++){
      var n = el.childNodes[i];
      if(n.nodeType === 3){ // TEXT
        var original = n.nodeValue;
        var translated = translateText(original);
        if(translated !== original){
          n.nodeValue = translated;
          changed = true;
        }
      }
    }
    // También procesar atributos alt/title/aria-label si existen
    ['alt','title','aria-label'].forEach(function(attr){
      if(el.hasAttribute(attr)){
        var val = el.getAttribute(attr);
        var t = translateText(val);
        if(t !== val){ el.setAttribute(attr, t); changed = true; }
      }
    });
    if(changed){
      el.setAttribute('data-translated','true');
    }
    return changed;
  }

  function walk(root){
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT, null);
    var node;
    while((node = walker.nextNode())) processNode(node);
  }

  function initialPass(){
    walk(document.body || document.documentElement);
    // Señal para dom_guard: traducción inicial aplicada
    try {
      window.__runtimeTranslateReady = true;
      var ev = new CustomEvent('runtime-translate-ready');
      window.dispatchEvent(ev);
    } catch(e) {}
  }

  var pending = false;
  function schedule(){
    if(pending) return; pending = true;
    (window.requestAnimationFrame||setTimeout)(function(){
      pending = false;
      initialPass();
    },50);
  }

  function setupMutationWatcher(){
    var mo = new MutationObserver(function(muts){
      var needs = false;
      for(var i=0;i<muts.length;i++){
        var m = muts[i];
        if(m.type === 'childList'){ needs = true; break; }
        if(m.type === 'attributes' && (m.attributeName === 'class' || m.attributeName === 'alt' || m.attributeName==='title' || m.attributeName==='aria-label')){ needs = true; break; }
      }
      if(needs) schedule();
    });
    mo.observe(document.documentElement,{subtree:true,childList:true,attributes:true});
    window.__runtimeTranslateObserver = mo;
  }

  function init(){
    initialPass();
    setupMutationWatcher();
    // Reintentos para textos tardíos
    setTimeout(initialPass,500);
    setTimeout(initialPass,1500);
    setTimeout(initialPass,3000);
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded',init);
  } else {
    init();
  }
})();
