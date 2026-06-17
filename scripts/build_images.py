# -*- coding: utf-8 -*-
"""
Pipeline obrazow dla strony Zofia Siek-Mlicka (mm2).
Przetwarza katalogi "WWW Lukasz/01..05" na zoptymalizowane pliki web + manifest.json
+ gotowe fragmenty HTML galerii.
"""
import os, json, re, unicodedata
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "WWW Łukasz")
IMG  = os.path.join(ROOT, "img")
FRAG = os.path.join(ROOT, "scripts", "fragments")
os.makedirs(FRAG, exist_ok=True)

MAX_PER_SET = 8          # ile zdjec maksymalnie na obraz/obiekt w podgalerii
Q_FULL, Q_THUMB, Q_HERO = 80, 82, 85

def slugify(s):
    s = s.replace("ł", "l").replace("Ł", "L")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s

def clean_title(s):
    s = re.sub(r"^\s*\d+\s+", "", s)        # wiodacy numer "01 "
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(" ,.;")
    return s

def is_img(f):
    return os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png", ".tif", ".tiff")

def sort_key(name):
    # "00 ..." na poczatek; potem naturalnie
    m = re.match(r"^\s*(\d+)", name)
    return (0, int(m.group(1)), name.lower()) if m else (1, 0, name.lower())

def save_web(src_path, dst_path, max_edge, quality):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB",):
            im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, max_edge / float(max(w, h)))
        if scale < 1.0:
            im = im.resize((max(1, round(w*scale)), max(1, round(h*scale))), Image.LANCZOS)
        im.save(dst_path, "JPEG", quality=quality, optimize=True, progressive=True)
    return os.path.getsize(dst_path)

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

manifest = {}
src_bytes = [0]
out_bytes = [0]
def track_src(p): src_bytes[0] += os.path.getsize(p)

# ---------------------------------------------------------------- 01 SLIDER
print("== 01 Slider ==")
sl_dir = os.path.join(SRC, "01 Zdjecia do slajdera")
slides = []
files = sorted([f for f in os.listdir(sl_dir) if is_img(f) and f.lower() != "tlo.jpg"], key=sort_key)
for i, f in enumerate(files, 1):
    sp = os.path.join(sl_dir, f); track_src(sp)
    dp = os.path.join(IMG, "slider", f"slide-{i:02d}.jpg")
    out_bytes[0] += save_web(sp, dp, 1920, Q_HERO)
    slides.append({"src": rel(dp), "title": clean_title(os.path.splitext(f)[0])})
    print("  ", rel(dp))
# tekstura tla
tp = os.path.join(sl_dir, "tlo.jpg")
if os.path.exists(tp):
    track_src(tp)
    out_bytes[0] += save_web(tp, os.path.join(IMG, "tlo.jpg"), 600, 80)
manifest["slider"] = slides

# ---------------------------------------------------------------- 02 REALIZACJE
print("== 02 Wybrane realizacje ==")
re_dir = os.path.join(SRC, "02 Wybrane realizacje")
realizacje = []
for f in sorted([f for f in os.listdir(re_dir) if is_img(f)], key=sort_key):
    sp = os.path.join(re_dir, f); track_src(sp)
    slug = slugify(os.path.splitext(f)[0])
    full = os.path.join(IMG, "realizacje", slug + ".jpg")
    out_bytes[0] += save_web(sp, full, 1600, Q_FULL)
    realizacje.append({"src": rel(full), "title": clean_title(os.path.splitext(f)[0])})
print("   %d zdjec" % len(realizacje))
manifest["realizacje"] = realizacje

# ---------------------------------------------------------------- 03 / 04 zestawy
def process_sets(folder, out_sub, exclude_substr=()):
    base = os.path.join(SRC, folder)
    out = []
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        sl = slugify(name)
        if any(x in sl for x in exclude_substr):
            print("   POMINIETO:", name); continue
        imgs = sorted([f for f in os.listdir(d) if is_img(f)], key=sort_key)[:MAX_PER_SET]
        if not imgs:
            continue
        web = []
        for j, f in enumerate(imgs):
            sp = os.path.join(d, f); track_src(sp)
            dp = os.path.join(IMG, out_sub, sl, f"{j:02d}.jpg")
            out_bytes[0] += save_web(sp, dp, 1600, Q_FULL)
            web.append(rel(dp))
        # miniatura z glownego (kafelek siatki)
        thumb = os.path.join(IMG, out_sub, sl, "thumb.jpg")
        out_bytes[0] += save_web(os.path.join(d, imgs[0]), thumb, 900, Q_THUMB)
        # druga miniatura (uklad przed/po przy konserwacji)
        thumb2 = None
        if len(imgs) >= 2:
            t2 = os.path.join(IMG, out_sub, sl, "thumb-b.jpg")
            out_bytes[0] += save_web(os.path.join(d, imgs[1]), t2, 900, Q_THUMB)
            thumb2 = rel(t2)
        out.append({"slug": sl, "title": clean_title(name),
                    "thumb": rel(thumb), "thumb2": thumb2,
                    "images": web, "count": len(web)})
        print("   %-45s %d zdjec" % (name[:45], len(web)))
    return out

print("== 03 Kopie obrazow ==")
manifest["kopie"] = process_sets("03 Kopie obrazów", "kopie")
print("== 04 Konserwacje ==")
manifest["konserwacje"] = process_sets("04 Konserwacje", "konserwacje",
                                       exclude_substr=("zloc", "globus"))

# ---------------------------------------------------------------- 05 O MNIE
print("== 05 O mnie ==")
om_dir = os.path.join(SRC, "05 O mnie")
def find(sub):
    for f in os.listdir(om_dir):
        if sub.lower() in f.lower() and is_img(f):
            return os.path.join(om_dir, f)
    return None
omnie = {}
bg = find("Pracownia w Siedlcu")
if bg: track_src(bg); out_bytes[0] += save_web(bg, os.path.join(IMG, "omnie", "tlo-omnie.jpg"), 1920, Q_HERO); omnie["bg"] = rel(os.path.join(IMG,"omnie","tlo-omnie.jpg"))
por = find("Zofia")
if por: track_src(por); out_bytes[0] += save_web(por, os.path.join(IMG, "omnie", "portret.jpg"), 1100, Q_HERO); omnie["portret"] = rel(os.path.join(IMG,"omnie","portret.jpg"))
gal = []
for f in sorted([f for f in os.listdir(om_dir) if is_img(f)]):
    sp = os.path.join(om_dir, f); track_src(sp)
    slug = slugify(os.path.splitext(f)[0])
    dp = os.path.join(IMG, "omnie", slug + ".jpg")
    out_bytes[0] += save_web(sp, dp, 1400, Q_FULL)
    gal.append({"src": rel(dp), "title": clean_title(os.path.splitext(f)[0])})
omnie["gallery"] = gal
manifest["omnie"] = omnie

# ---------------------------------------------------------------- ZAPIS
with open(os.path.join(ROOT, "scripts", "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("\n== PODSUMOWANIE ==")
print("Zrodlo:  %.0f MB" % (src_bytes[0]/1048576))
print("Wynik :  %.1f MB" % (out_bytes[0]/1048576))
print("Slider: %d | Realizacje: %d | Kopie: %d | Konserwacje: %d | O mnie galeria: %d" % (
    len(manifest["slider"]), len(manifest["realizacje"]),
    len(manifest["kopie"]), len(manifest["konserwacje"]), len(omnie["gallery"])))
