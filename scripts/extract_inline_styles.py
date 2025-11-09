#!/usr/bin/env python3
"""
Extrae estilos inline repetidos de index.html y los mueve a styles.css como clases.
Crea backups de index.html y styles.css antes de modificar.

Uso: python3 scripts/extract_inline_styles.py

Reglas:
- Agrupa estilos inline idénticos.
- Para estilos que aparecen al menos MIN_OCCURRENCES veces se crea una clase .extracted-N.
- Reemplaza style="..." por class="... extracted-N" (conserva clases existentes).
- Añade las clases generadas al final de styles.css con un comentario con la fecha.

Advertencia: no convierte estilos únicos ni aquellos que aparecen pocas veces (configurable).
"""

import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

MIN_OCCURRENCES = 3
ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
STYLES = ROOT / 'styles.css'

if not INDEX.exists():
    print('index.html no encontrado en', INDEX)
    sys.exit(1)
if not STYLES.exists():
    print('styles.css no encontrado en', STYLES)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except Exception:
    print('BeautifulSoup (bs4) no está instalado. Por favor instala con: pip3 install beautifulsoup4')
    sys.exit(2)

# Leer index.html
orig_index = INDEX.read_bytes()
orig_index_size = len(orig_index)
html = orig_index.decode('utf-8', errors='replace')

soup = BeautifulSoup(html, 'html.parser')

# Recolectar estilos inline
style_counts = Counter()
style_nodes = defaultdict(list)  # style -> list of elements
for tag in soup.find_all(True):
    if tag.has_attr('style'):
        style_value = tag['style'].strip()
        # Normalize spaces
        style_norm = re.sub(r"\s+", ' ', style_value)
        style_counts[style_norm] += 1
        style_nodes[style_norm].append(tag)

print('Total estilos inline distintos encontrados:', len(style_counts))
print('Total ocurrencias de style=:', sum(style_counts.values()))

# Seleccionar estilos para extraer
extracted = {}
counter = 1
for style, count in style_counts.most_common():
    if count >= MIN_OCCURRENCES and style:
        class_name = f'extracted-style-{counter}'
        extracted[style] = (class_name, count)
        counter += 1

if not extracted:
    print('No se encontraron estilos repetidos suficientes (min=', MIN_OCCURRENCES, ') para extraer.')
    sys.exit(0)

print('Estilos a extraer (count >=', MIN_OCCURRENCES, '):', len(extracted))

# Crear backup de archivos
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
INDEX_backup = INDEX.with_name(f'index.html.bak_{timestamp}')
STYLES_backup = STYLES.with_name(f'styles.css.bak_{timestamp}')

INDEX_backup.write_bytes(orig_index)
STYLES_backup.write_bytes(STYLES.read_bytes())
print('Backups creados:', INDEX_backup.name, STYLES_backup.name)

# Reemplazar estilos inline por clases
replacements = 0
for style_norm, (class_name, count) in extracted.items():
    nodes = style_nodes[style_norm]
    for tag in nodes:
        # Remove style attribute if present
        if tag.has_attr('style'):
            try:
                del tag['style']
            except Exception:
                # ignore if removal fails for some reason
                pass
        # Append class preserving existing classes
        existing_classes = tag.get('class', [])
        # Avoid duplicate addition
        if class_name not in existing_classes:
            existing_classes.append(class_name)
        tag['class'] = existing_classes
        replacements += 1

# Escribir nuevo index.html
new_html = str(soup)
INDEX.write_text(new_html, encoding='utf-8')
new_index_size = INDEX.stat().st_size

# Generar CSS para las clases extraidas
css_lines = []
css_lines.append('\n/* Estilos extraidos desde index.html el %s */' % timestamp)
for style_norm, (class_name, count) in extracted.items():
    # Asegurar que el contenido termine con ; entre propiedades
    style_text = style_norm.rstrip().strip()
    if style_text and not style_text.endswith(';'):
        style_text += ';'
    css_lines.append(f'.{class_name} ' + '{ ' + style_text + ' } /* used: %d */' % count)

# Añadir al final de styles.css
try:
    STYLES.write_text(STYLES.read_text(encoding='utf-8') + '\n' + '\n'.join(css_lines), encoding='utf-8')
except Exception as e:
    print('Error al escribir styles.css:', e)
    # Restaurar index backup si algo falla
    INDEX_backup.write_bytes(INDEX_backup.read_bytes())
    sys.exit(3)

new_styles_size = STYLES.stat().st_size

print('\nReplacements realizados:', replacements)
print('index.html tamaño antes:', orig_index_size, 'después:', new_index_size, 'ahorro bytes:', orig_index_size - new_index_size)
print('styles.css tamaño antes:', STYLES_backup.stat().st_size, 'después:', new_styles_size)
print('Clases añadidas:', len(extracted))
print('Script finalizado. Revisar los backups y validar visualmente.')
