# -*- coding: utf-8 -*-
"""Generuje fragmenty HTML galerii z manifest.json."""
import os, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG = os.path.join(ROOT, "scripts", "fragments")
os.makedirs(FRAG, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "scripts", "manifest.json"), encoding="utf-8"))

import re
def tidy(s):
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip(" ,.;")
    return s
def esc(s): return html.escape(tidy(s), quote=True)

def card(thumbs, images, title, meta, ba=False):
    """thumbs = lista 1-2 miniatur do kafelka; images = pelny zestaw do lightboxa."""
    data = "|".join(images)
    n = len(images)
    badge = f'<span class="gallery-item__badge">{n} zdjęć</span>' if n > 1 else ""
    if ba and len(thumbs) >= 2:
        pic = (f'<span class="ba"><img src="{thumbs[0]}" alt="{esc(title)} — 1" loading="lazy">'
               f'<img src="{thumbs[1]}" alt="{esc(title)} — 2" loading="lazy"></span>')
        cls = "gallery-item gallery-item--ba"
    else:
        pic = f'<img class="gallery-item__img" src="{thumbs[0]}" alt="{esc(title)}" loading="lazy">'
        cls = "gallery-item"
    return (f'        <button class="{cls}" data-images="{esc(data)}" '
            f'data-title="{esc(title)}" data-meta="{esc(meta)}">\n'
            f'          {pic}\n'
            f'          <span class="gallery-item__info"><span class="gallery-item__title">{esc(title)}</span>'
            f'<span class="gallery-item__meta">{esc(meta)}</span></span>\n'
            f'          {badge}\n'
            f'        </button>')

def write(name, content):
    open(os.path.join(FRAG, name), "w", encoding="utf-8").write(content)

# --- SLIDER (tla hero) ---
write("slider.html", "\n".join(
    f'      <div class="hero-slider__slide{" is-active" if i==0 else ""}" '
    f'style="background-image:url(\'{s["src"]}\')" role="img" aria-label="{esc(s["title"])}"></div>'
    for i, s in enumerate(M["slider"])))

# --- REALIZACJE (02) ---
write("realizacje.html", "\n".join(card([r["src"]], [r["src"]], r["title"], "Wybrana realizacja") for r in M["realizacje"]))
write("realizacje6.html", "\n".join(card([r["src"]], [r["src"]], r["title"], "Wybrana realizacja") for r in M["realizacje"][:6]))

# --- KOPIE (03): kafelek = thumb, lightbox = pelny zestaw ---
write("kopie.html", "\n".join(card([k["thumb"]], k["images"], k["title"], "Kopia malarska") for k in M["kopie"]))

# --- KONSERWACJE (04): kafelek 2-up (przed/po), lightbox = pelny zestaw ---
def kons_card(k):
    thumbs = [k["thumb"]] + ([k["thumb2"]] if k.get("thumb2") else [])
    meta = "Konserwacja — przed i po" if k["count"] >= 2 else "Konserwacja"
    return card(thumbs, k["images"], k["title"], meta, ba=(k["count"] >= 2))
write("konserwacje.html", "\n".join(kons_card(k) for k in M["konserwacje"]))

# --- O MNIE galeria ---
write("omnie.html", "\n".join(card([g["src"]], [g["src"]], g["title"], "Pracownia") for g in M["omnie"]["gallery"]))

print("OK. slider:%d realizacje:%d kopie:%d konserwacje:%d omnie:%d" % (
    len(M["slider"]), len(M["realizacje"]), len(M["kopie"]),
    len(M["konserwacje"]), len(M["omnie"]["gallery"])))
print("omnie.bg =", M["omnie"].get("bg"), "| omnie.portret =", M["omnie"].get("portret"))
