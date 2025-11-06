#!/usr/bin/env python3
"""
Script para extraer todo el CSS del index.html y organizarlo en archivos separados.
"""

import re
import os

def extraer_css_del_html(archivo_html):
    print(f"📖 Leyendo {archivo_html}...")

    with open(archivo_html, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Buscar todas las etiquetas <style>
    patron_style = r'<style[^>]*>(.*?)</style>'
    estilos_encontrados = re.findall(patron_style, contenido, re.DOTALL)

    print(f"✅ Encontrados {len(estilos_encontrados)} bloques <style>")

    # Crear el archivo CSS principal
    css_completo = []

    for i, estilo in enumerate(estilos_encontrados, 1):
        print(f"   📝 Bloque {i}: {len(estilo)} caracteres")
        css_completo.append(f"/* ========== Bloque de estilos {i} ========== */\n")
        css_completo.append(estilo.strip())
        css_completo.append("\n\n")

    # Guardar todo el CSS en un archivo
    archivo_css = 'styles.css'
    with open(archivo_css, 'w', encoding='utf-8') as f:
        f.write(''.join(css_completo))

    print(f"💾 CSS guardado en {archivo_css}")

    # Crear respaldo del HTML original
    backup_html = archivo_html + '.backup'
    with open(backup_html, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"💾 Backup creado: {backup_html}")

    # Reemplazar los bloques <style> con un link al CSS externo
    html_limpio = contenido

    # Eliminar todos los bloques style
    html_limpio = re.sub(patron_style, '', html_limpio, flags=re.DOTALL)

    # Insertar el link al CSS en el <head>
    link_css = '    <link rel="stylesheet" href="styles.css">\n'

    # Buscar el </head> e insertar el link antes
    if '</head>' in html_limpio:
        html_limpio = html_limpio.replace('</head>', f'{link_css}</head>', 1)
    else:
        print("⚠️  No se encontró </head>, agregando al inicio del body")
        html_limpio = html_limpio.replace('<body', f'{link_css}<body', 1)

    # Guardar el HTML limpio
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html_limpio)

    print(f"✅ HTML actualizado: {archivo_html}")
    print(f"\n📊 Resumen:")
    print(f"   - Bloques CSS extraídos: {len(estilos_encontrados)}")
    print(f"   - Tamaño total del CSS: {len(''.join(css_completo))} caracteres")
    print(f"   - Archivo CSS creado: {archivo_css}")
    print(f"   - Backup del HTML: {backup_html}")

if __name__ == "__main__":
    extraer_css_del_html('index.html')
    print("\n✨ ¡Proceso completado!")

