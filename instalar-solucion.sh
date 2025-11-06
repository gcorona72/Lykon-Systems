#!/bin/bash

# Script automático para insertar el código de eliminación de badges
# Este script hace TODO el trabajo por ti

echo "🚀 Iniciando instalación automática de eliminación de badges..."
echo ""

# Ruta al directorio del proyecto
PROYECTO="/Users/coronaoyono/Downloads/webs pro/mondragon.framer.website"

cd "$PROYECTO" || exit 1

# Crear un backup del index.html original
echo "📦 Creando backup de index.html..."
cp index.html index.html.backup
echo "✅ Backup creado: index.html.backup"
echo ""

# Leer el código a insertar
CODIGO_A_INSERTAR=$(cat codigo-para-insertar.html)

# Insertar el código ANTES del cierre de </body>
echo "📝 Insertando código en index.html..."

# Usar Python para hacer la inserción de forma segura
python3 << 'PYTHON_SCRIPT'
import re

# Leer el index.html
with open('index.html', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Leer el código a insertar
with open('codigo-para-insertar.html', 'r', encoding='utf-8') as f:
    codigo = f.read()

# Buscar el cierre de </body> o </html>
if '</body>' in contenido:
    # Insertar ANTES de </body>
    contenido = contenido.replace('</body>', codigo + '\n</body>')
    print("✅ Código insertado antes de </body>")
elif '</html>' in contenido:
    # Si no hay </body>, insertar antes de </html>
    contenido = contenido.replace('</html>', codigo + '\n</html>')
    print("✅ Código insertado antes de </html>")
else:
    # Si no encuentra ni </body> ni </html>, añadir al final
    contenido = contenido + '\n' + codigo
    print("✅ Código añadido al final del archivo")

# Guardar el archivo modificado
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(contenido)

print("✅ Archivo index.html modificado correctamente")
PYTHON_SCRIPT

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Resumen:"
echo "   ✅ Backup creado: index.html.backup"
echo "   ✅ Código insertado en: index.html"
echo "   ✅ Badges eliminados: Buy Template + Made in Framer"
echo ""
echo "🌐 Ahora abre tu sitio en un navegador para ver el resultado."
echo ""
echo "⚠️  Si algo sale mal, restaura el backup con:"
echo "   cp index.html.backup index.html"
echo ""

