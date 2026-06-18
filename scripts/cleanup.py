# -*- coding: utf-8 -*-
"""Usuwa nieużywane obrazy w img/ (skanuje HTML + CSS). Bezpieczne — kasuje tylko to,
do czego nigdzie nie ma odwołań."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

used = set()
def add(ref, base):
    if not ref or ref.startswith(("http", "data:", "mailto:", "tel:", "#")):
        return
    used.add(os.path.normpath(os.path.join(base, ref.split("#")[0])))

# HTML (z katalogu glownego)
for page in glob.glob(os.path.join(ROOT, "*.html")):
    s = open(page, encoding="utf-8").read()
    for m in re.findall(r'(?:src|href)="([^"]+)"', s): add(m, ROOT)
    for m in re.findall(r'data-images="([^"]+)"', s):
        for one in m.split("|"): add(one, ROOT)
    for m in re.findall(r"url\('([^']+)'\)", s): add(m, ROOT)

# CSS (sciezki wzgledne do katalogu css/)
for css in glob.glob(os.path.join(ROOT, "css", "*.css")):
    s = open(css, encoding="utf-8").read()
    for m in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", s):
        add(m, os.path.join(ROOT, "css"))

all_imgs = [p for p in glob.glob(os.path.join(ROOT, "img", "**", "*"), recursive=True) if os.path.isfile(p)]
freed = 0
removed = 0
for p in all_imgs:
    if os.path.normpath(p) not in used:
        freed += os.path.getsize(p)
        os.remove(p)
        removed += 1
        print("  usunięto:", os.path.relpath(p, ROOT).replace("\\", "/"))

print(f"\nUsunięto {removed} plików, zwolniono {freed/1048576:.1f} MB")
print("Zachowano (przykłady): tlo.jpg, logo.png, favicon.svg, konserwacja-tetmajer.jpg jeśli używane")
