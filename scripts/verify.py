# -*- coding: utf-8 -*-
"""Audyt: czy wszystkie lokalne src/href istnieją; które obrazy są nieużywane."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_files = glob.glob(os.path.join(ROOT, "*.html"))

ref_re = re.compile(r'(?:src|href)="([^"]+)"')
data_re = re.compile(r'data-images="([^"]+)"')
bg_re = re.compile(r"url\('([^']+)'\)")

missing = []
used_imgs = set()

def check(page, ref):
    if not ref or ref.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
        return
    path = os.path.normpath(os.path.join(ROOT, ref.split("#")[0]))
    if ref.lower().endswith((".jpg", ".jpeg", ".png", ".svg", ".webp")):
        used_imgs.add(os.path.normpath(path))
    if not os.path.exists(path):
        missing.append((os.path.basename(page), ref))

for page in html_files:
    s = open(page, encoding="utf-8").read()
    for m in ref_re.findall(s):
        check(page, m)
    for m in data_re.findall(s):
        for one in m.split("|"):
            check(page, one)
    for m in bg_re.findall(s):
        check(page, m)

print("=== BRAKUJĄCE PLIKI (%d) ===" % len(missing))
for pg, ref in missing[:50]:
    print(f"  {pg}: {ref}")

# nieużywane obrazy w img/
all_imgs = set(os.path.normpath(p) for p in glob.glob(os.path.join(ROOT, "img", "**", "*"), recursive=True)
               if os.path.isfile(p))
unused = sorted(all_imgs - used_imgs)
print("\n=== NIEUŻYWANE pliki w img/ (%d) ===" % len(unused))
for p in unused:
    print("  ", os.path.relpath(p, ROOT).replace("\\", "/"))

print("\n=== STRONY (%d) ===" % len(html_files))
for p in sorted(html_files):
    print("  ", os.path.basename(p))
