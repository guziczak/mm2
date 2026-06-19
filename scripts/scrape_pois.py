#!/usr/bin/env python3
"""
Wyciaga wspolrzedne firm widocznych na mapie Google (z mapka.png) przez
automatyzacje przegladarki (Playwright). Nie uzywa API key - po prostu
renderuje strone jak normalna przegladarka i czyta wspolrzedne z URL-a.

Uruchom:  python scripts/scrape_pois.py  ->  scripts/pois.json
"""
import json
import os
import re

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Nazwy z mapka.png (krotka etykieta -> zapytanie do Google Maps)
BUSINESSES = {
    "Paczkomat InPost": "Paczkomat InPost Siedlec Krzeszowice",
    "Wishes School of English": "Wishes School of English Siedlec Krzeszowice",
    "Szlachta - slusarsko-tokarskie": "Szlachta uslugi slusarsko-tokarskie Siedlec",
    "Uslugi spawalnicze": "uslugi spawalnicze Siedlec Krzeszowice",
    "Dom rekolekcyjny siostr": "Dom rekolekcyjny Siedlec Krzeszowice",
    "BanBan Ogrody": "BanBan Ogrody Siedlec Krzeszowice",
    "Pracownie Artystyczne Siek ART": "Pracownie Artystyczne Siek ART Siedlec 11 Krzeszowice",
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

CENTER = (50.143839, 19.678532)  # Siedlec 3 — do biasowania wyszukiwania i odrzucania zlych trafien


def dist_km(a, b):
    import math
    dlat = (a[0] - b[0]) * 111.0
    dlon = (a[1] - b[1]) * 111.0 * math.cos(math.radians(a[0]))
    return (dlat ** 2 + dlon ** 2) ** 0.5


def extract(url):
    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r"/@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        return float(m.group(1)), float(m.group(2))
    return None


def click_consent(page):
    for sel in ['button:has-text("Odrzuć wszystko")',
                'button:has-text("Zaakceptuj wszystko")',
                'button:has-text("Reject all")',
                'button:has-text("Accept all")',
                'button[aria-label*="Odrzuć"]',
                'button[aria-label*="Reject"]']:
        try:
            page.locator(sel).first.click(timeout=2000)
            page.wait_for_timeout(1500)
            return True
        except Exception:
            pass
    return False


def main():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(locale="pl-PL", user_agent=UA)
        page = ctx.new_page()

        page.goto("https://www.google.com/maps?hl=pl", wait_until="domcontentloaded", timeout=60000)
        click_consent(page)
        page.wait_for_timeout(2000)

        for label, query in BUSINESSES.items():
            q = query.replace(" ", "+")
            coords = None
            try:
                page.goto("https://www.google.com/maps/search/" + q +
                          "/@%s,%s,15z?hl=pl" % (CENTER[0], CENTER[1]),
                          wait_until="domcontentloaded", timeout=60000)
                click_consent(page)
                for _ in range(25):
                    c = extract(page.url)
                    if c and dist_km(c, CENTER) <= 2.5:
                        coords = c
                        break
                    page.wait_for_timeout(800)
            except Exception as e:
                print("  %-32s ERR %s" % (label, repr(e)[:70]))
            results[label] = coords
            flag = "" if coords else "  (nie znaleziono w okolicy)"
            print("  %-32s -> %s%s" % (label, coords, flag))

        browser.close()

    out = os.path.join(ROOT, "scripts", "pois.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    got = sum(1 for v in results.values() if v)
    print("\nWyciagnieto %d/%d wspolrzednych -> %s" % (got, len(results), out))


if __name__ == "__main__":
    main()
