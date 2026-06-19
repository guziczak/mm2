#!/usr/bin/env python3
"""
Pobiera czcionki Google (Cormorant Garamond + Lato) i hostuje je lokalnie,
zeby strona nie wysylala IP odwiedzajacych do Google (zgodnosc z RODO).

Uruchom z katalogu glownego repo:  python scripts/fetch_fonts.py

Generuje:
  fonts/*.woff2   - pliki czcionek (podzbiory latin + latin-ext)
  css/fonts.css   - reguly @font-face wskazujace na pliki lokalne
"""
import os
import re
import urllib.request

CSS_URL = ("https://fonts.googleapis.com/css2?"
           "family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400"
           "&family=Lato:wght@300;400;700&display=swap")

# UA nowoczesnej przegladarki -> Google serwuje woff2 (najlepsza kompresja)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

KEEP_SUBSETS = {"latin", "latin-ext"}  # latin-ext = polskie znaki (l a e s z ...)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(ROOT, "fonts")
CSS_OUT = os.path.join(ROOT, "css", "fonts.css")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read()


def main():
    os.makedirs(FONTS_DIR, exist_ok=True)
    css = fetch(CSS_URL).decode("utf-8")

    # Kazdy blok @font-face poprzedza komentarz z nazwa podzbioru: /* latin-ext */
    block_re = re.compile(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{([^}]*)\}")

    out = []
    seen = set()
    for subset, body in block_re.findall(css):
        if subset not in KEEP_SUBSETS:
            continue
        family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
        style = re.search(r"font-style:\s*(\w+)", body).group(1)
        weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
        url = re.search(r"url\(([^)]+)\)", body).group(1).strip("'\"")
        urange_m = re.search(r"unicode-range:\s*([^;]+);", body)
        urange = urange_m.group(1).strip() if urange_m else None

        fname = "%s-%s-%s-%s.woff2" % (slug(family), weight, style, subset)
        if fname not in seen:
            data = fetch(url)
            with open(os.path.join(FONTS_DIR, fname), "wb") as f:
                f.write(data)
            seen.add(fname)
            print("  %-44s %5d KB" % (fname, len(data) // 1024))

        rule = ("/* %s %s %s - %s */\n"
                "@font-face {\n"
                "  font-family: '%s';\n"
                "  font-style: %s;\n"
                "  font-weight: %s;\n"
                "  font-display: swap;\n"
                "  src: url('../fonts/%s') format('woff2');\n"
                % (family, weight, style, subset, family, style, weight, fname))
        if urange:
            rule += "  unicode-range: %s;\n" % urange
        rule += "}\n"
        out.append(rule)

    header = ("/* Czcionki hostowane lokalnie - wygenerowane przez scripts/fetch_fonts.py\n"
              "   Zrodlo: Google Fonts (Cormorant Garamond, Lato). Podzbiory: latin, latin-ext.\n"
              "   NIE edytuj recznie - uruchom skrypt ponownie po zmianie wariantow. */\n\n")
    os.makedirs(os.path.dirname(CSS_OUT), exist_ok=True)
    with open(CSS_OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + "\n".join(out))

    print("\nPobrano %d plikow woff2 -> %s" % (len(seen), FONTS_DIR))
    print("Zapisano %s" % CSS_OUT)


if __name__ == "__main__":
    main()
