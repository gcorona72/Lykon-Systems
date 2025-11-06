#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script automático para insertar el código de eliminación de badges en index.html
Ejecuta este script con: python3 instalar-badges.py
"""

import os
import shutil
from datetime import datetime

def main():
    print("=" * 60)
    print("🚀 INSTALADOR AUTOMÁTICO - Eliminación de Badges de Framer")
    print("=" * 60)
    print()

    # Verificar que estamos en el directorio correcto
    if not os.path.exists('index.html'):
        print("❌ ERROR: No se encuentra index.html en este directorio")
        print("   Por favor, ejecuta este script desde la carpeta del proyecto")
        return

    if not os.path.exists('codigo-para-insertar.html'):
        print("❌ ERROR: No se encuentra codigo-para-insertar.html")
        print("   Asegúrate de que todos los archivos estén en la carpeta")
        return

    print("✅ Archivos encontrados correctamente")
    print()

    # Crear backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"index.html.backup_{timestamp}"

    print(f"📦 Creando backup: {backup_name}")
    try:
        shutil.copy2('index.html', backup_name)
        print(f"✅ Backup creado exitosamente")
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return

    print()

    # Leer archivos
    print("📖 Leyendo archivos...")

    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            contenido_html = f.read()
        print("✅ index.html leído")
    except Exception as e:
        print(f"❌ Error al leer index.html: {e}")
        return

    try:
        with open('codigo-para-insertar.html', 'r', encoding='utf-8') as f:
            codigo_badges = f.read()
        print("✅ codigo-para-insertar.html leído")
    except Exception as e:
        print(f"❌ Error al leer codigo-para-insertar.html: {e}")
        return

    print()

    # Insertar el código
    print("📝 Insertando código de eliminación de badges...")

    # Estrategia 1: Buscar <!-- Start of bodyEnd -->
    if '<!-- Start of bodyEnd -->' in contenido_html and '<!-- End of bodyEnd -->' in contenido_html:
        print("   Método: Reemplazando sección bodyEnd")
        # Reemplazar toda la sección bodyEnd
        inicio = contenido_html.find('<!-- Start of bodyEnd -->')
        fin = contenido_html.find('<!-- End of bodyEnd -->') + len('<!-- End of bodyEnd -->')

        nuevo_contenido = (
            contenido_html[:inicio] +
            codigo_badges +
            contenido_html[fin:]
        )

    # Estrategia 2: Buscar </body>
    elif '</body>' in contenido_html:
        print("   Método: Insertando antes de </body>")
        nuevo_contenido = contenido_html.replace(
            '</body>',
            '\n' + codigo_badges + '\n</body>'
        )

    # Estrategia 3: Buscar </html>
    elif '</html>' in contenido_html:
        print("   Método: Insertando antes de </html>")
        nuevo_contenido = contenido_html.replace(
            '</html>',
            '\n' + codigo_badges + '\n</html>'
        )

    # Estrategia 4: Añadir al final
    else:
        print("   Método: Añadiendo al final del archivo")
        nuevo_contenido = contenido_html + '\n' + codigo_badges

    # Guardar el archivo modificado
    try:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        print("✅ Código insertado correctamente en index.html")
    except Exception as e:
        print(f"❌ Error al guardar index.html: {e}")
        print(f"   Restaurando desde backup...")
        try:
            shutil.copy2(backup_name, 'index.html')
            print("✅ Backup restaurado")
        except:
            print("❌ Error al restaurar backup")
        return

    print()
    print("=" * 60)
    print("🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print()
    print("📋 Resumen de cambios:")
    print(f"   ✅ Backup guardado como: {backup_name}")
    print("   ✅ Código insertado en: index.html")
    print("   ✅ Badges eliminados:")
    print("      • Badge 'Buy Template' (LemonSqueezy)")
    print("      • Badge 'Made in Framer'")
    print()
    print("🌐 Próximos pasos:")
    print("   1. Abre index.html en tu navegador")
    print("   2. Verifica que los badges hayan desaparecido")
    print("   3. Si algo sale mal, restaura con:")
    print(f"      cp {backup_name} index.html")
    print()
    print("💡 Para aplicar a otras páginas (agency, contact, etc.):")
    print("   Ejecuta este script desde cada carpeta de página")
    print()

if __name__ == '__main__':
    main()

