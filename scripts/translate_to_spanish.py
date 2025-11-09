#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traduce contenido de texto visible en archivos HTML del proyecto al español, de forma selectiva:
- Preserva términos técnicos (Next.js, React, JavaScript, Node.js, etc.).
- No toca <script>, <style>, ni atributos tipo class/href.
- Traduce texto en nodos (incluye enlaces y títulos visibles) y alt/title de imágenes si se desea.
- Crea backups por archivo: <nombre>.trans_bak_YYYYMMDD_HHMMSS
Uso:
  python3 scripts/translate_to_spanish.py
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_DIRS = [ROOT]
# También recorrer subdirectorios típicos
for sub in ["blog", "projects", "agency", "contact"]:
    p = ROOT / sub
    if p.exists():
        INCLUDE_DIRS.append(p)

TECH_TERMS = {
    'next.js', 'react', 'node.js', 'javascript', 'typescript', 'webgl', 'three.js',
    'figma', 'framer', 'vercel', 'github', 'css', 'html', 'api', 'ux', 'ui', 'npm', 'yarn', 'pnpm'
}
# Normalizar a minúsculas al comparar

def is_tech_term(token: str) -> bool:
    t = token.strip()
    if not t:
        return False
    low = t.lower()
    # Coincidencia exacta o con puntuación adyacente
    for term in TECH_TERMS:
        if low == term:
            return True
        if low.strip('.,;:!¿?()[]{}"\'“”') == term:
            return True
    # Tokens como "Next" solos no se consideran término
    return False

# Diccionario de frases comunes (case-insensitive) -> traducción
PHRASES = {
    # navegación y secciones
    "home": "Inicio",
    "agency": "Agencia",
    "projects": "Proyectos",
    "blog": "Blog",
    "contact": "Contacto",
    # CTAs
    "start": "Comenzar",
    "start a project": "Iniciar un proyecto",
    "buy template": "Comprar plantilla",
    # mensajes
    "let's book & talk with our manager.": "Reservemos y hablemos con nuestro gerente.",
    "we’re a senior creative digital agency focused on clarity and performance.": "Somos una agencia digital creativa sénior centrada en la claridad y el rendimiento.",
    "we align strategy, brand, and web into modular systems that ship on time and scale.": "Alineamos estrategia, marca y web en sistemas modulares que se entregan a tiempo y escalan.",
    "our values are simplicity, accountability and measurable impact.": "Nuestros valores son la simplicidad, la responsabilidad y el impacto medible.",
    "the team is small and senior; every project has a lead for strategy, design and build.": "El equipo es pequeño y sénior; cada proyecto tiene un responsable de estrategia, diseño y desarrollo.",
    "we partner long-term, iterating with data to keep products fast.": "Colaboramos a largo plazo, iterando con datos para mantener productos rápidos.",
    # genérico
    "learn more": "Saber más",
    "read more": "Leer más",
    "view more": "Ver más",
    "view project": "Ver proyecto",
    "all rights reserved": "Todos los derechos reservados",
}

# Palabras sueltas comunes
WORDS = {
    "and": "y",
    "or": "o",
    "with": "con",
    "to": "a",
    "for": "para",
    "by": "por",
    "of": "de",
    "in": "en",
    "on": "en",
    "from": "de",
    "at": "en",
    "about": "sobre",
    "we": "nosotros",
    "our": "nuestro",
    "you": "tú",
    "your": "tu",
    "team": "equipo",
    "design": "diseño",
    "strategy": "estrategia",
    "performance": "rendimiento",
    "clarity": "claridad",
    "impact": "impacto",
    "simple": "simple",
    "simplicity": "simplicidad",
    "accountability": "responsabilidad",
}

SPLIT_RE = re.compile(r"(\s+)")
ALNUM_RE = re.compile(r"^[A-Za-z]+(?:[\-\']?[A-Za-z]+)*$")

# Traducción básica con preservación de términos técnicos y capitalización aproximada

def translate_chunk(chunk: str) -> str:
    if not chunk or chunk.strip() == "":
        return chunk
    # Frases completas conocidas (case-insensitive)
    low = chunk.strip().lower()
    if low in PHRASES:
        translated = PHRASES[low]
        # Conservar puntuación inicial/final si aplica
        prefix = ''
        suffix = ''
        m = re.match(r"^([\"'“”()\[\]¿¡!?.]*)", chunk)
        if m:
            prefix = m.group(1)
        m2 = re.search(r"([\"'“”()\[\]¿¡!?.]*)$", chunk)
        if m2:
            suffix = m2.group(1)
        core = translated
        return prefix + core + suffix

    # Palabras separadas por espacios
    parts = SPLIT_RE.split(chunk)
    out = []
    for p in parts:
        if SPLIT_RE.fullmatch(p):
            out.append(p)
            continue
        token = p
        # Preservar si parece término técnico
        if is_tech_term(token):
            out.append(token)
            continue
        # No traducir si parece identificador/código (CamelCase, snake_case, etc.)
        if not ALNUM_RE.match(token):
            out.append(token)
            continue
        lowt = token.lower()
        if lowt in WORDS:
            trans = WORDS[lowt]
            # Capitalización simple si original arranca en mayúscula
            if token[0].isupper():
                trans = trans[0].upper() + trans[1:]
            out.append(trans)
        else:
            # fallback: dejar tal cual si no está en diccionario
            out.append(token)
    return ''.join(out)

# ¿Debemos traducir el string? Evitar nodos dentro de etiquetas que no son visibles
SKIP_TAGS = {'script', 'style', 'noscript'}

# Atributos alternativos que podemos traducir (opc): alt y title
ALT_ATTRS = {'alt', 'title', 'aria-label'}


def translate_html(path: Path) -> tuple[int,int]:
    html = path.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')

    # Recorrer nodos de texto visibles
    changed_nodes = 0
    total_nodes = 0
    for el in soup.find_all(True):
        if el.name in SKIP_TAGS:
            continue
        # traducir atributos alternativos
        for attr in list(el.attrs.keys()):
            if attr in ALT_ATTRS:
                val = el.get(attr)
                if isinstance(val, str) and val.strip():
                    total_nodes += 1
                    new = translate_chunk(val)
                    if new != val:
                        el[attr] = new
                        changed_nodes += 1
        # traducir nodos de texto directos
        for child in list(el.children):
            if isinstance(child, NavigableString):
                text = str(child)
                if text.strip():
                    total_nodes += 1
                    new = translate_chunk(text)
                    if new != text:
                        child.replace_with(new)
                        changed_nodes += 1

    if changed_nodes:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = path.with_name(path.name + f'.trans_bak_{ts}')
        backup.write_text(html, encoding='utf-8')
        path.write_text(str(soup), encoding='utf-8')
    return changed_nodes, total_nodes


def is_html_file(fp: Path) -> bool:
    if fp.suffix.lower() == '.html':
        return True
    if fp.is_file() and fp.suffix == '':
        try:
            head = fp.read_bytes()[:2048].lower()
            return b'<html' in head or b'<!doctype html' in head
        except Exception:
            return False
    return False


def main():
    files = []
    for base in INCLUDE_DIRS:
        if not base.exists():
            continue
        for fp in base.rglob('*'):
            if fp.is_file() and is_html_file(fp):
                files.append(fp)
    # Evitar tocar backups
    files = [f for f in files if '.bak_' not in f.name and '.trans_bak_' not in f.name and not f.name.endswith('.bak')]

    if not files:
        print('No se encontraron archivos HTML para traducir.')
        return 0

    total_changed = 0
    total_nodes = 0
    for f in files:
        ch, tn = translate_html(f)
        total_changed += ch
        total_nodes += tn
        print(f"{f.relative_to(ROOT)}: nodos traducidos {ch}/{tn}")

    print(f"Resumen: traducidos {total_changed} de {total_nodes} nodos de texto/alt/title")
    return 0

if __name__ == '__main__':
    sys.exit(main())

