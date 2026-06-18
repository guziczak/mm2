# -*- coding: utf-8 -*-
"""Zamienia stare sekcje galerii na puste siatki z markerem data-fill (do wypełnienia)."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- KOPIE: cała sekcja <!-- Gallery --> ... </section> -> placeholder kopie
kopie = os.path.join(ROOT, "kopie-obrazow.html")
s = open(kopie, encoding="utf-8").read()
new_section = '''  <!-- Gallery -->
  <section class="section section--warm">
    <div class="container">
      <div class="gallery-grid reveal" data-fill="kopie"></div>
    </div>
  </section>'''
s2, n = re.subn(r'  <!-- Gallery -->.*?</section>', new_section, s, count=1, flags=re.DOTALL)
open(kopie, "w", encoding="utf-8").write(s2)
print("kopie-obrazow.html: galeria ->", n)

# --- KONSERWACJA: sekcja <!-- Gallery --> ... </section> -> placeholder konserwacje (+ nagłówek)
kons = os.path.join(ROOT, "konserwacja.html")
s = open(kons, encoding="utf-8").read()
new_section = '''  <!-- Gallery -->
  <section class="section section--warm">
    <div class="container">
      <div class="text-center">
        <p class="section-subtitle reveal">Realizacje</p>
        <h2 class="section-title reveal">Konserwacje — przed i&nbsp;po</h2>
        <p class="section-description reveal">Każdy obiekt dokumentuję fotograficznie. Kliknij, aby zobaczyć pełny zestaw zdjęć przed i po konserwacji.</p>
      </div>
      <div class="gallery-grid reveal" data-fill="konserwacje" style="margin-top: var(--space-xl);"></div>
    </div>
  </section>'''
s2, n = re.subn(r'  <!-- Gallery -->.*?</section>', new_section, s, count=1, flags=re.DOTALL)
open(kons, "w", encoding="utf-8").write(s2)
print("konserwacja.html: galeria ->", n)
