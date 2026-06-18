# -*- coding: utf-8 -*-
"""Wypełnia puste siatki <div class="gallery-grid" data-fill="NAZWA"></div> fragmentami."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG = os.path.join(ROOT, "scripts", "fragments")

frags = {}
for f in glob.glob(os.path.join(FRAG, "*.html")):
    frags[os.path.splitext(os.path.basename(f))[0]] = open(f, encoding="utf-8").read()

pat = re.compile(r'(<div class="gallery-grid[^"]*"[^>]*data-fill=")(\w+)("[^>]*>)\s*</div>')

def repl(m):
    name = m.group(2)
    frag = frags.get(name)
    if frag is None:
        print("  !! brak fragmentu:", name); return m.group(0)
    return f'{m.group(1)}{name}{m.group(3)}\n{frag}\n      </div>'

total = 0
for path in glob.glob(os.path.join(ROOT, "*.html")):
    s = open(path, encoding="utf-8").read()
    new, n = pat.subn(repl, s)
    if n:
        open(path, "w", encoding="utf-8").write(new)
        total += n
        print(f"  {os.path.basename(path)}: wypełniono {n} siatek")
print("Razem siatek:", total)
