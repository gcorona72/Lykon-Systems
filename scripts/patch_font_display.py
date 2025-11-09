#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
css_path = root / 'styles.css'
css = css_path.read_text(encoding='utf-8')

# Add font-display: swap; to @font-face blocks for Space Mono when missing

def add_font_display_to_space_mono(css_text: str) -> str:
    def repl(match: re.Match) -> str:
        block = match.group(0)
        # If font-display present already, return block unchanged
        if re.search(r"font-display\s*:\s*swap\s*;", block):
            return block
        # Insert font-display after font-weight line if exists, else after font-style
        block2 = re.sub(r"(font-weight\s*:\s*\d+\s*;)",
                        r"\1\n  font-display: swap;",
                        block,
                        count=1)
        if block2 == block:
            block2 = re.sub(r"(font-style\s*:\s*[^;]+\s*;)",
                            r"\1\n  font-display: swap;",
                            block,
                            count=1)
        return block2

    pattern = re.compile(r"@font-face\s*\{[^}]*font-family\s*:\s*['\"]Space Mono['\"][^}]*}\s*", re.IGNORECASE | re.DOTALL)
    return pattern.sub(repl, css_text)

new_css = add_font_display_to_space_mono(css)
if new_css != css:
    backup = css_path.with_name(css_path.name + '.perf_bak')
    backup.write_text(css, encoding='utf-8')
    css_path.write_text(new_css, encoding='utf-8')
    print('Patched Space Mono @font-face with font-display: swap; backup:', backup.name)
else:
    print('No changes needed (font-display already present for Space Mono).')

