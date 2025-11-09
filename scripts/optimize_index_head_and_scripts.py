#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'

head_inject = (
    '    <link rel="preconnect" href="https://framerusercontent.com" crossorigin>\n'
    '    <link rel="dns-prefetch" href="//framerusercontent.com">\n'
    '    <link rel="dns-prefetch" href="//events.framer.com">\n'
    '    <link rel="preload" as="font" type="font/woff2" href="https://fonts.gstatic.com/s/spacemono/v17/i7dPIFZifjKcF5UAWdDRYEF8RQ.woff2" crossorigin>\n'
)

if not INDEX.exists():
    raise SystemExit(f"index.html no encontrado en {INDEX}")

html = INDEX.read_text(encoding='utf-8', errors='replace')
orig_bytes = len(html.encode('utf-8'))
changed = False

# 1) Insertar preconnect/preload después del link de styles.css si no está
if '<link href="styles.css" rel="stylesheet">' in html and 'framerusercontent.com" crossorigin' not in html:
    html = html.replace('<link href="styles.css" rel="stylesheet">', '<link href="styles.css" rel="stylesheet">\n' + head_inject)
    changed = True

# 2) Deduplicar script removeBadges y ajustar timings
# Encontrar bloques <script> IIFE con removeBuyTemplateBadge
pattern = re.compile(r"<script>\s*\(function \(\) \{[\s\S]*?\}\)\(\);\s*</script>")
blocks = list(pattern.finditer(html))
removals = 0
if blocks:
    # Conservar el primer bloque que contenga la función, eliminar los demás que también la contengan
    keep_found = False
    new_html_parts = []
    last_idx = 0
    for m in blocks:
        block = html[m.start():m.end()]
        if 'removeBuyTemplateBadge' in block:
            if not keep_found:
                # Ajustar timings dentro de este
                block2 = block
                block2 = re.sub(r'observeAndRemove\(10000\)', 'observeAndRemove(4000)', block2)
                block2 = re.sub(r'\},\s*150\);', '}, 250);', block2)
                block2 = re.sub(r'if \(attempts >=\s*40', 'if (attempts >= 20', block2)
                block2 = re.sub(r"window.addEventListener\('load', function \(\) \) \{\s*removeBadges\(\);\s*observeAndRemove\(5000\);\s*\}\);",
                                 "window.addEventListener('load', function () { removeBadges(); observeAndRemove(3000); });",
                                 block2)
                new_html_parts.append(html[last_idx:m.start()])
                new_html_parts.append(block2)
                last_idx = m.end()
                keep_found = True
            else:
                # eliminar este bloque duplicado
                new_html_parts.append(html[last_idx:m.start()])
                last_idx = m.end()
                removals += 1
        else:
            # no es el script objetivo, mantener tal cual
            pass
    if removals > 0 or keep_found:
        new_html_parts.append(html[last_idx:])
        html = ''.join(new_html_parts)
        changed = True

if changed:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = INDEX.with_name(f'index.html.perf_bak_{ts}')
    backup.write_bytes(INDEX.read_bytes())
    INDEX.write_text(html, encoding='utf-8')
    print('Backup:', backup.name)
else:
    print('No hubo cambios aplicados (ya estaba optimizado).')

print('Heurística: removals =', removals)
print('Tamaño original:', orig_bytes, 'bytes, actual:', INDEX.stat().st_size, 'bytes')

