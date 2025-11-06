#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para extraer y organizar el CSS del index.html
Separa el CSS en archivos externos para mejor organización
"""

import re
import os
from datetime import datetime

def extraer_css_inline(html_content):
    """Extrae todo el CSS de etiquetas <style> del HTML"""
    css_bloques = []

    # Patrón para encontrar etiquetas <style>...</style>
    pattern = r'<style[^>]*>(.*?)</style>'
    matches = re.finditer(pattern, html_content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        css_content = match.group(1).strip()
        if css_content:
            css_bloques.append({
                'css': css_content,
                'match': match.group(0),
                'start': match.start(),
                'end': match.end()
            })

    return css_bloques

def limpiar_html(html_content, css_bloques):
    """Elimina las etiquetas <style> del HTML"""
    html_limpio = html_content

    # Eliminar de atrás hacia adelante para no afectar las posiciones
    for bloque in reversed(css_bloques):
        html_limpio = html_limpio[:bloque['start']] + html_limpio[bloque['end']:]

    return html_limpio

def insertar_link_css(html_content, css_filename):
    """Inserta el link al archivo CSS en el <head>"""

    # Buscar el cierre de </head>
    head_close = re.search(r'</head>', html_content, re.IGNORECASE)

    if head_close:
        link_tag = f'    <link rel="stylesheet" href="./{css_filename}">\n'
        pos = head_close.start()
        html_nuevo = html_content[:pos] + link_tag + html_content[pos:]
        return html_nuevo

    return html_content

def main():
    print("=" * 70)
    print("🎨 ORGANIZADOR DE CSS - Extrayendo CSS del HTML")
    print("=" * 70)
    print()

    # Verificar que existe index.html
    if not os.path.exists('index.html'):
        print("❌ ERROR: No se encuentra index.html")
        return

    # Crear backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"index.html.backup_{timestamp}"

    print(f"📦 Creando backup: {backup_name}")
    with open('index.html', 'r', encoding='utf-8') as f:
        html_original = f.read()

    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(html_original)
    print("✅ Backup creado")
    print()

    # Extraer CSS
    print("🔍 Analizando HTML y extrayendo CSS...")
    css_bloques = extraer_css_inline(html_original)

    if not css_bloques:
        print("ℹ️  No se encontraron bloques <style> en el HTML")
        print("   El CSS puede estar ya en archivos externos")
        return

    print(f"✅ Encontrados {len(css_bloques)} bloques de CSS")
    print()

    # Separar CSS en categorías
    css_framer = []
    css_badges = []
    css_custom = []

    for i, bloque in enumerate(css_bloques, 1):
        css = bloque['css']

        # Detectar CSS de badges
        if 'framer-60pafq-container' in css or '__framer-badge' in css or 'Badge' in css:
            css_badges.append(css)
            print(f"   📌 Bloque {i}: CSS de eliminación de badges")
        # Detectar CSS de Framer
        elif 'framer-' in css or 'data-framer' in css:
            css_framer.append(css)
            print(f"   📌 Bloque {i}: CSS de Framer")
        # CSS custom
        else:
            css_custom.append(css)
            print(f"   📌 Bloque {i}: CSS personalizado")

    print()

    # Crear archivos CSS
    archivos_creados = []

    # 1. CSS de Framer (si existe)
    if css_framer:
        print("📝 Creando framer-styles.css...")
        with open('framer-styles.css', 'w', encoding='utf-8') as f:
            f.write("/* Estilos generados por Framer */\n")
            f.write("/* Extraído automáticamente del index.html */\n\n")
            f.write('\n\n'.join(css_framer))
        print("✅ framer-styles.css creado")
        archivos_creados.append('framer-styles.css')

    # 2. CSS de badges (ya existe hide-badges.css, pero por si acaso)
    if css_badges:
        print("📝 Actualizando hide-badges.css...")
        with open('hide-badges.css', 'w', encoding='utf-8') as f:
            f.write("/* CSS para ocultar badges de Framer */\n")
            f.write("/* Elimina: Buy Template + Made in Framer */\n\n")
            f.write('\n\n'.join(css_badges))
        print("✅ hide-badges.css actualizado")
        archivos_creados.append('hide-badges.css')

    # 3. CSS personalizado
    if css_custom:
        print("📝 Creando custom-styles.css...")
        with open('custom-styles.css', 'w', encoding='utf-8') as f:
            f.write("/* Estilos personalizados del sitio */\n\n")
            f.write('\n\n'.join(css_custom))
        print("✅ custom-styles.css creado")
        archivos_creados.append('custom-styles.css')

    print()

    # Limpiar HTML y añadir links
    print("🧹 Limpiando HTML y añadiendo links a CSS externos...")
    html_limpio = limpiar_html(html_original, css_bloques)

    # Añadir links a los archivos CSS
    for css_file in archivos_creados:
        html_limpio = insertar_link_css(html_limpio, css_file)

    # Guardar HTML limpio
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_limpio)

    print("✅ HTML actualizado con links a CSS externos")
    print()

    # Resumen
    print("=" * 70)
    print("🎉 ORGANIZACIÓN COMPLETADA")
    print("=" * 70)
    print()
    print("📋 Archivos CSS creados:")
    for archivo in archivos_creados:
        size = os.path.getsize(archivo)
        print(f"   ✅ {archivo} ({size} bytes)")

    print()
    print("📋 Cambios en index.html:")
    print(f"   • Eliminados {len(css_bloques)} bloques <style>")
    print(f"   • Añadidos {len(archivos_creados)} links <link rel='stylesheet'>")
    print()

    print("📁 Estructura ahora:")
    print("   index.html          → HTML limpio")
    if 'framer-styles.css' in archivos_creados:
        print("   framer-styles.css   → Estilos de Framer")
    if 'hide-badges.css' in archivos_creados:
        print("   hide-badges.css     → Ocultar badges")
    if 'custom-styles.css' in archivos_creados:
        print("   custom-styles.css   → Estilos personalizados")
    print()

    print("🆘 Si algo sale mal, restaura con:")
    print(f"   cp {backup_name} index.html")
    print()

    print("💡 Próximos pasos:")
    print("   1. Abre index.html en un navegador")
    print("   2. Verifica que todo se vea igual")
    print("   3. Los estilos ahora están organizados en archivos separados")
    print()

if __name__ == '__main__':
    main()

