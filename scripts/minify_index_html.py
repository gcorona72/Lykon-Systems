#!/usr/bin/env python3
"""
Minifica index.html de forma segura para reducir tamaño sin cambiar funcionalidad.
- Crea un backup con timestamp: index.html.minifybak_YYYYMMDD_HHMMSS
- Usa htmlmin con opciones conservadoras.
Uso: python3 scripts/minify_index_html.py
"""
from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'

if not INDEX.exists():
    print('index.html no encontrado en', INDEX)
    sys.exit(1)

try:
    import htmlmin
except Exception:
    print('El paquete htmlmin no está instalado. Instálalo con: pip3 install --user htmlmin')
    sys.exit(2)

orig = INDEX.read_text(encoding='utf-8', errors='replace')
orig_size = len(orig.encode('utf-8'))

# Backup
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
backup = INDEX.with_name(f'index.html.minifybak_{ts}')
backup.write_bytes(INDEX.read_bytes())

# Minify (conservador):
# - remove_comments True
# - reduce_empty_attributes False
# - remove_optional_attribute_quotes False
# - keep_pre True (no tocar <pre>)
# - Minificar espacios entre tags y líneas
minified = htmlmin.minify(
    orig,
    remove_comments=True,
    remove_empty_space=True,
    reduce_empty_attributes=False,
    remove_optional_attribute_quotes=False,
    keep_pre=True
)

INDEX.write_text(minified, encoding='utf-8')
new_size = INDEX.stat().st_size

print('Backup creado:', backup.name)
print('Tamaño antes:', orig_size, 'bytes')
print('Tamaño después:', new_size, 'bytes', 'ahorro:', orig_size - new_size)

# Comprobaciones de sanidad
import re
style_attr_count = len(re.findall(r"\bstyle\s*=", minified))
extracted_refs = len(re.findall(r"extracted-style-\d+", minified))
print('style= en index (post-min):', style_attr_count)
print('refs extracted-style- en index (post-min):', extracted_refs)
print('Minificación completada.')

