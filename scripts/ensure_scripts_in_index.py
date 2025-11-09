#!/usr/bin/env python3
# Ensure <script defer src="scripts/dom_guard.js"></script> and runtime_translate.js are present before </body>
# and set <html lang="es"> if currently "en".
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
index = root / 'index.html'
html = index.read_text(encoding='utf-8', errors='replace')
orig = html

# Normalize lang
html = re.sub(r'<html\s+lang="en"', '<html lang="es"', html, count=1)

need_guard = 'scripts/dom_guard.js' not in html
need_rt = 'scripts/runtime_translate.js' not in html

if need_guard or need_rt:
    insertion = ''
    if need_guard:
        insertion += '<script defer src="scripts/dom_guard.js"></script>'
    if need_rt:
        insertion += '<script defer src="scripts/runtime_translate.js"></script>'
    # Insert before </body> (case-insensitive)
    if re.search(r'</body>', html, flags=re.IGNORECASE):
        html = re.sub(r'</body>', insertion + '</body>', html, flags=re.IGNORECASE, count=1)
    else:
        # Fallback: append at end
        html += insertion

changed = html != orig
if changed:
    backup = index.with_name('index.html.inject_bak')
    backup.write_text(orig, encoding='utf-8')
    index.write_text(html, encoding='utf-8')
    print('Injected tags / lang updated. Backup saved:', backup.name)
else:
    print('No changes needed (scripts present and lang ok).')

print('Presence: dom_guard:', ('scripts/dom_guard.js' in html), 'runtime_translate:', ('scripts/runtime_translate.js' in html))

