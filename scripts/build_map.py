#!/usr/bin/env python3
"""
Generuje statyczne obrazki mapy (kafelki OpenStreetMap) dla strony Kontakt:
  - img/mapa-kontakt.png         (desktop, szeroki 1920x720)
  - img/mapa-kontakt-mobile.png  (mobile, 1280x720 16:9, wieksze podpisy)
oba z pinezkami + nazwami firm i nazwami ulic. Strona podmienia je przez <picture>.

Dane: scripts/pois.json (Google Maps przez scripts/scrape_pois.py) + Overpass (ulice).
Glowna (czerwona) pinezka = pracownia Siedlec 3, WYSRODKOWANA.

Uruchom: python scripts/build_map.py
"""
import io
import json
import math
import os
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "img", "mapa-kontakt.png")
OUT_M = os.path.join(ROOT, "img", "mapa-kontakt-mobile.png")
POIS_JSON = os.path.join(ROOT, "scripts", "pois.json")

CENTER = (50.143839, 19.678532)
CENTER_LABEL = "Pracownia — Siedlec 3"
SIEK = "Pracownie Artystyczne Siek ART"
MARGIN = 0.13
TILE = 256
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
OVERPASS = "https://overpass-api.de/api/interpreter"
UA = "mm2-static-map-builder/1.0 (https://guziczak.github.io/mm2; kontakt: zo.siek@interia.pl)"
RED = (211, 47, 47)
BLUE = (60, 90, 170)
ROAD_COL = (90, 90, 95)

DISPLAY = {
    "Szlachta - slusarsko-tokarskie": "Szlachta — ślusarstwo",
    "Uslugi spawalnicze": "Usługi spawalnicze",
    "Dom rekolekcyjny siostr": "Dom rekolekcyjny sióstr",
    "Pracownie Artystyczne Siek ART": "Pracownie Siek ART",
}


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read()


def gpx(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n * TILE
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n * TILE
    return x, y


def px_to_latlon(px, py, z):
    n = 2 ** z
    lon = px / (n * TILE) * 360.0 - 180.0
    ty = py / (n * TILE)
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ty))))
    return lat, lon


def choose_zoom(center, pts, w, h, margin):
    for z in range(18, 11, -1):
        cx, cy = gpx(center[0], center[1], z)
        if all(abs(gpx(la, lo, z)[0] - cx) <= w / 2 * (1 - margin) and
               abs(gpx(la, lo, z)[1] - cy) <= h / 2 * (1 - margin) for la, lo in pts):
            return z
    return 12


def fetch_tile(z, x, y):
    return Image.open(io.BytesIO(http_get(TILE_URL.format(z=z, x=x, y=y)))).convert("RGB")


def fetch_named_roads(bbox):
    q = ('[out:json][timeout:40];way["highway"]["name"](%f,%f,%f,%f);out geom;'
         % (bbox[0], bbox[1], bbox[2], bbox[3]))
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request(OVERPASS, data=data, headers={"User-Agent": UA})
    res = json.loads(urllib.request.urlopen(req, timeout=90).read())
    out = []
    for el in res.get("elements", []):
        nm = el.get("tags", {}).get("name")
        g = el.get("geometry")
        if nm and g:
            out.append((nm, [(p["lat"], p["lon"]) for p in g]))
    return out


def font(sz):
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def draw_label(img, x, y, text, fnt, anchor="right"):
    d = ImageDraw.Draw(img)
    try:
        tw = d.textlength(text, font=fnt)
    except Exception:
        tw = 8 * len(text)
    th = fnt.size
    if anchor == "right":
        tx, ty = x + 8, y - th // 2
    elif anchor == "left":
        tx, ty = x - 8 - tw, y - th // 2
    elif anchor == "above":
        tx, ty = x - tw // 2, y - th - 4
    else:
        tx, ty = x - tw // 2, y + 4
    sw = max(3, fnt.size // 6)
    d.text((tx, ty), text, fill=(30, 30, 30), font=fnt, stroke_width=sw, stroke_fill=(255, 255, 255))


def draw_rotated_text(img, xy, text, fnt, angle, fill=ROAD_COL):
    d0 = ImageDraw.Draw(img)
    try:
        tw = int(d0.textlength(text, font=fnt))
    except Exception:
        tw = 8 * len(text)
    th = fnt.size
    pad = 8
    tmp = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((pad, pad), text, font=fnt, fill=fill,
                             stroke_width=3, stroke_fill=(255, 255, 255, 255))
    tmp = tmp.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(xy[0] - tmp.width / 2), int(xy[1] - tmp.height / 2)), tmp)


def draw_pin(img, x, y, col, scale=1.0):
    d = ImageDraw.Draw(img)
    s = scale
    r = int(15 * s)
    hc = y - int(32 * s)
    d.polygon([(x - int(10*s), hc + int(5*s)), (x + int(10*s), hc + int(5*s)), (x, y)], fill=col)
    d.ellipse([x - r, hc - r, x + r, hc + r], fill=col, outline=(255, 255, 255), width=max(2, int(3*s)))
    d.ellipse([x - int(5*s), hc - int(5*s), x + int(5*s), hc + int(5*s)], fill=(255, 255, 255))


def pin_box(x, y, scale):
    r = int(15 * scale)
    return (x - r, y - int(47 * scale), x + r, y + 3)


def place_label(img, x, y, text, fnt, anchors, occ, W, H, clear=10, force=False):
    """Podpis w pierwszej pozycji, ktora MIESCI sie w kadrze i nie nachodzi na zajete
    prostokaty. `clear` = wysokosc pinezki nad szpicem (zeby 'above' bylo NAD glowka, nie na niej).
    force => gdy nic nie pasuje, bierze pierwsza pozycje w kadrze (ignoruje kolizje).
    Poza kadrem nie rysuje nigdy. Zwraca True, jesli narysowano."""
    d = ImageDraw.Draw(img)
    try:
        tw = int(d.textlength(text, font=fnt))
    except Exception:
        tw = 8 * len(text)
    th = fnt.size

    def box(an):
        if an == "right":
            tx, ty = x + 14, y - clear // 2 - th // 2
        elif an == "left":
            tx, ty = x - 14 - tw, y - clear // 2 - th // 2
        elif an == "above":
            tx, ty = x - tw // 2, y - clear - th
        else:  # below (szpic jest dolem pinezki)
            tx, ty = x - tw // 2, y + 8
        return tx, ty, (tx - 3, ty - 2, tx + tw + 3, ty + th + 2)

    def fits(bb):
        return bb[0] >= 4 and bb[1] >= 4 and bb[2] <= W - 4 and bb[3] <= H - 4

    def free(bb):
        return not any(not (bb[2] < o[0] or bb[0] > o[2] or bb[3] < o[1] or bb[1] > o[3]) for o in occ)

    def emit(tx, ty, bb):
        d.text((tx, ty), text, fill=(30, 30, 30), font=fnt,
               stroke_width=max(3, fnt.size // 6), stroke_fill=(255, 255, 255))
        occ.append(bb)

    for an in anchors:
        tx, ty, bb = box(an)
        if fits(bb) and free(bb):
            emit(tx, ty, bb)
            return True
    if force:
        for an in anchors:
            tx, ty, bb = box(an)
            if fits(bb):
                emit(tx, ty, bb)
                return True
    return False


def render(pois, W, H, out_path, fscale=1.0, zboost=0):
    z = min(18, choose_zoom(CENTER, list(pois.values()), W, H, MARGIN) + zboost)
    mx, my = gpx(CENTER[0], CENTER[1], z)
    left, top = mx - W / 2.0, my - H / 2.0

    x0, y0 = int(math.floor(left / TILE)), int(math.floor(top / TILE))
    x1, y1 = int(math.floor((left + W) / TILE)), int(math.floor((top + H) / TILE))
    canvas = Image.new("RGB", ((x1 - x0 + 1) * TILE, (y1 - y0 + 1) * TILE))
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            canvas.paste(fetch_tile(z, tx, ty), ((tx - x0) * TILE, (ty - y0) * TILE))
    ox, oy = int(round(left - x0 * TILE)), int(round(top - y0 * TILE))
    img = canvas.crop((ox, oy, ox + W, oy + H))

    def to_px(lat, lon):
        px, py = gpx(lat, lon, z)
        return int(round(px - left)), int(round(py - top))

    # nazwy ulic (pod pinezkami, wzdluz drogi)
    tl = px_to_latlon(left, top, z)
    br = px_to_latlon(left + W, top + H, z)
    rfnt = font(int(16 * fscale))
    try:
        roads = fetch_named_roads((br[0], tl[1], tl[0], br[1]))
    except Exception as e:
        roads = []
        print("  (drogi: blad %s)" % repr(e)[:60])
    M, STEP, nlab = 46, 470, 0
    for name, geom in roads:
        pts = [to_px(la, lo) for la, lo in geom]
        dense = []
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = max(1, int(math.hypot(bx - ax, by - ay) / 14))
            for s in range(n):
                t = s / n
                dense.append((ax + (bx - ax) * t, ay + (by - ay) * t))
        if pts:
            dense.append(pts[-1])
        runs, cur = [], []
        for p in dense:
            if M <= p[0] <= W - M and M <= p[1] <= H - M:
                cur.append(p)
            elif cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        for run in runs:
            if len(run) < 6:
                continue
            acc, target, placed = 0.0, STEP * 0.5, False
            for k in range(1, len(run) - 1):
                acc += math.hypot(run[k][0] - run[k-1][0], run[k][1] - run[k-1][1])
                if acc >= target:
                    (ax, ay), (bx, by) = run[k-1], run[k+1]
                    ang = math.degrees(math.atan2(-(by - ay), (bx - ax)))
                    ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
                    draw_rotated_text(img, run[k], name, rfnt, ang)
                    target += STEP
                    placed = True
                    nlab += 1
            if not placed:
                k = len(run) // 2
                (ax, ay), (bx, by) = run[max(0, k-1)], run[min(len(run)-1, k+1)]
                ang = math.degrees(math.atan2(-(by - ay), (bx - ax)))
                ang = ang - 180 if ang > 90 else (ang + 180 if ang < -90 else ang)
                draw_rotated_text(img, run[k], name, rfnt, ang)
                nlab += 1

    # pinezki tylko w kadrze (tip celuje w punkt); potem podpisy bez nakladania
    occ = []
    inframe = {}
    for name, (lat, lon) in pois.items():
        x, y = to_px(lat, lon)
        if 16 <= x <= W - 16 and 16 <= y <= H - 16:
            draw_pin(img, x, y, BLUE, scale=0.55)
            occ.append(pin_box(x, y, 0.55))
            inframe[name] = (x, y)
    cx, cy = to_px(*CENTER)
    draw_pin(img, cx, cy, RED, scale=1.05)
    occ.append(pin_box(cx, cy, 1.05))

    fnt = font(int(20 * fscale))
    place_label(img, cx, cy, CENTER_LABEL, font(int(25 * fscale)),
                ["above", "right", "left", "below"], occ, W, H, clear=int(47 * 1.05) + 4, force=True)
    if SIEK in inframe:
        x, y = inframe[SIEK]
        place_label(img, x, y, DISPLAY.get(SIEK, SIEK), fnt, ["below", "right", "left", "above"],
                    occ, W, H, clear=int(47 * 0.55) + 4, force=True)
    for name, (x, y) in inframe.items():
        if name == SIEK:
            continue
        anchors = ["above", "right", "left", "below"] if x < W * 0.55 else ["above", "left", "right", "below"]
        place_label(img, x, y, DISPLAY.get(name, name), fnt, anchors, occ, W, H, clear=int(47 * 0.55) + 4)

    d = ImageDraw.Draw(img)
    aff = font(13)
    txt = "(c) OpenStreetMap contributors"
    try:
        tw = d.textlength(txt, font=aff)
    except Exception:
        tw = 8 * len(txt)
    d.rectangle([W - tw - 12, H - 22, W, H], fill=(255, 255, 255))
    d.text((W - tw - 6, H - 19), txt, fill=(90, 90, 90), font=aff)

    img.save(out_path, "PNG", optimize=True)
    print("Zapisano %s (%dx%d, zoom %d, %d ulic)" % (out_path, W, H, z, nlab))


def main():
    pois = {}
    if os.path.exists(POIS_JSON):
        raw = json.load(open(POIS_JSON, encoding="utf-8"))
        pois = {k: tuple(v) for k, v in raw.items() if v}
    render(pois, 1920, 720, OUT, fscale=1.15)         # desktop (wieksze podpisy)
    render(pois, 1280, 720, OUT_M, fscale=0.92, zboost=1)  # mobile (mniejsze podpisy, blizej)


if __name__ == "__main__":
    main()
