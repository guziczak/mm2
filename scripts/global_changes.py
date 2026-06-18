# -*- coding: utf-8 -*-
"""Zmiany globalne na wszystkich podstronach (nazwa, social, rok, nawigacja, domena)."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1) blog.html -> aktualnosci.html
blog = os.path.join(ROOT, "blog.html")
akt = os.path.join(ROOT, "aktualnosci.html")
if os.path.exists(blog) and not os.path.exists(akt):
    os.rename(blog, akt)
    print("Zmieniono nazwę blog.html -> aktualnosci.html")

TIKTOK = ('<a href="https://www.tiktok.com/@zofiasiek" target="_blank" rel="noopener noreferrer" '
          'aria-label="TikTok"><svg viewBox="0 0 24 24"><path d="M16.5 3h-2.9v12.6a2.6 2.6 0 1 1-2-2.5V10a5.6 5.6 0 1 0 4.9 5.5V8.9a6.7 6.7 0 0 0 3.9 1.3V7.3a3.8 3.8 0 0 1-3.8-3.8z"/></svg></a>')

files = [f for f in glob.glob(os.path.join(ROOT, "*.html"))
         if os.path.basename(f) != "warsztaty.html"]

for path in files:
    name = os.path.basename(path)
    s = open(path, encoding="utf-8").read()
    orig = s

    # link blog -> aktualnosci
    s = s.replace('href="blog.html"', 'href="aktualnosci.html"')

    # usuń pozycję Warsztaty z nawigacji i stopki
    s = re.sub(r'\s*<li><a href="warsztaty\.html"[^>]*>Warsztaty</a></li>', '', s)

    # tekst Blog -> Aktualności (po zmianie href)
    s = s.replace('>Blog</a>', '>Aktualności</a>')

    # nazwa: Zofia Siek -> Zofia Siek-Mlicka (idempotentnie, nie ruszamy URL/maili)
    s = re.sub(r'Zofia Siek(?!-Mlicka)', 'Zofia Siek-Mlicka', s)

    # social media
    s = s.replace('https://pl-pl.facebook.com/Zofia.siekart',
                  'https://www.facebook.com/share/15gsfSCKKnL/')
    s = s.replace('https://www.instagram.com/zofia.siekart/',
                  'https://www.instagram.com/zofia.siekmlicka')

    # dodaj TikTok po Instagramie (raz)
    if 'tiktok.com/@zofiasiek' not in s:
        s = re.sub(r'(<a href="https://www\.instagram\.com/zofia\.siekmlicka"[^>]*>.*?</a>)',
                   r'\1' + TIKTOK, s, flags=re.DOTALL)

    # rok w stopce
    s = s.replace('&copy; 2024', '&copy; 2026')

    # domena hostingu
    s = s.replace('https://zofiasiek.pl', 'https://guziczak.github.io/mm2')

    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        print(f"  zmieniono: {name}")
    else:
        print(f"  bez zmian: {name}")
