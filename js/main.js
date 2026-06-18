/* ============================================================
   Zofia Siek-Mlicka — Main JavaScript
   ============================================================ */

/* ----- Pozycja przewijania: ręczne przywracanie (bez "skoku od dołu") -----
   Auto-restore przeglądarki odpala się, zanim doczytają się zdjęcia, i na długiej
   stronie ląduje przy dole. Wyłączamy go i odtwarzamy pozycję sami, od razu po
   sparsowaniu strony (układ jest stabilny dzięki zarezerwowanym wymiarom obrazów). */
(function () {
  if (!('scrollRestoration' in history)) return;
  history.scrollRestoration = 'manual';

  const KEY = 'scrollY:' + location.pathname;
  let saveTimer = null;
  const save = () => {
    try { sessionStorage.setItem(KEY, String(Math.round(window.scrollY))); } catch (e) {}
  };
  window.addEventListener('scroll', () => {
    if (saveTimer) return;
    saveTimer = setTimeout(() => { save(); saveTimer = null; }, 150);
  }, { passive: true });
  window.addEventListener('pagehide', save);

  let y = 0;
  try { y = parseInt(sessionStorage.getItem(KEY) || '0', 10); } catch (e) {}
  if (y > 0) {
    window.scrollTo(0, y);
    requestAnimationFrame(() => window.scrollTo(0, y));
  }
})();

document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initMobileNav();
  initFAQ();
  initCookieConsent();
  initScrollTop();
  initRevealAnimations();
  initContactForm();
  initHeroSlider();
  initLightbox();
  initExpandable();
});

/* ----- Sticky Header ----- */
function initHeader() {
  const header = document.querySelector('.header');
  if (!header) return;

  const isHomePage = header.classList.contains('header--transparent');

  function updateHeader() {
    if (window.scrollY > 50) {
      header.classList.remove('header--transparent');
      header.classList.add('header--solid');
    } else if (isHomePage) {
      header.classList.remove('header--solid');
      header.classList.add('header--transparent');
    }
  }

  if (isHomePage) {
    window.addEventListener('scroll', updateHeader, { passive: true });
    updateHeader();
  } else {
    header.classList.add('header--solid');
  }
}

/* ----- Mobile Navigation ----- */
function initMobileNav() {
  const toggle = document.querySelector('.nav__toggle');
  const navList = document.querySelector('.nav__list');
  const overlay = document.querySelector('.mobile-nav-overlay');
  if (!toggle || !navList) return;

  function closeNav() {
    toggle.classList.remove('active');
    navList.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  function openNav() {
    toggle.classList.add('active');
    navList.classList.add('open');
    if (overlay) overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  toggle.addEventListener('click', () => {
    if (navList.classList.contains('open')) {
      closeNav();
    } else {
      openNav();
    }
  });

  if (overlay) {
    overlay.addEventListener('click', closeNav);
  }

  navList.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', closeNav);
  });
}

/* ----- FAQ Accordion ----- */
function initFAQ() {
  document.querySelectorAll('.faq-item__question').forEach(button => {
    button.addEventListener('click', () => {
      const item = button.closest('.faq-item');
      const isActive = item.classList.contains('active');

      item.closest('.faq-list')
        ?.querySelectorAll('.faq-item.active')
        .forEach(el => el.classList.remove('active'));

      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
}

/* ----- Cookie Consent ----- */
function initCookieConsent() {
  const banner = document.querySelector('.cookie-banner');
  if (!banner) return;

  if (localStorage.getItem('cookies-accepted')) {
    banner.remove();
    return;
  }

  setTimeout(() => banner.classList.add('visible'), 1000);

  banner.querySelector('[data-accept]')?.addEventListener('click', () => {
    localStorage.setItem('cookies-accepted', 'true');
    banner.classList.remove('visible');
    setTimeout(() => banner.remove(), 300);
  });

  banner.querySelector('[data-reject]')?.addEventListener('click', () => {
    localStorage.setItem('cookies-accepted', 'essential');
    banner.classList.remove('visible');
    setTimeout(() => banner.remove(), 300);
  });
}

/* ----- Scroll to Top ----- */
function initScrollTop() {
  const btn = document.querySelector('.scroll-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 600);
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ----- Reveal Animations ----- */
function initRevealAnimations() {
  const elements = document.querySelectorAll('.reveal');
  if (!elements.length) return;

  // Brak wsparcia IntersectionObserver → pokaż wszystko od razu (bezpieczny fallback)
  if (!('IntersectionObserver' in window)) {
    elements.forEach(el => el.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0, rootMargin: '0px 0px -40px 0px' });
  // threshold 0: kluczowe dla wysokich galerii na telefonie — przy 0.15 element
  // wyższy niż ekran nigdy nie osiąga 15% widoczności i zostaje ukryty.

  elements.forEach(el => {
    // Elementy już w polu widzenia lub przewinięte powyżej — pokaż natychmiast,
    // żeby nic nie zostało ukryte (np. po odświeżeniu z zachowaną pozycją).
    if (el.getBoundingClientRect().top < window.innerHeight) {
      el.classList.add('visible');
    } else {
      observer.observe(el);
    }
  });
}

/* ----- Contact Form ----- */
function initContactForm() {
  const form = document.querySelector('.contact-form');
  if (!form) return;

  const RECIPIENT = 'zo.siek@interia.pl';

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(form).entries());

    // Pola wymagane (formularz ma novalidate, więc sprawdzamy ręcznie)
    const required = ['name', 'email', 'subject', 'message'];
    const missing = required.find((k) => !String(data[k] || '').trim());
    if (missing) {
      showToast('Proszę uzupełnić wymagane pola.', 'error');
      form.elements[missing]?.focus();
      return;
    }
    if (!form.querySelector('[name="consent"]')?.checked) {
      showToast('Proszę zaakceptować zgodę na przetwarzanie danych osobowych.', 'error');
      return;
    }

    // Brak backendu — składamy wiadomość i otwieramy program pocztowy gościa.
    const subject = `Zapytanie ze strony — ${data.subject}`;
    const body =
      `Imię i nazwisko: ${data.name}\n` +
      `E-mail: ${data.email}\n` +
      `Telefon: ${data.phone ? data.phone : '—'}\n\n` +
      `${data.message}\n`;
    const href =
      `mailto:${RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    showToast('Otwieram Twój program pocztowy…', 'success');
    window.location.href = href;
    setTimeout(() => form.reset(), 1500);
  });
}

/* ----- Toast (styl Sonner: zwijane w talię, rozwijane po najechaniu) ----- */
let toastsExpanded = false;
let toastCollapseTimer = null;

function showToast(message, type = 'info', duration = 4000) {
  let stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    stack.setAttribute('role', 'status');
    stack.setAttribute('aria-live', 'polite');
    document.body.appendChild(stack);
  }

  // Podnieś toasty nad baner cookie, gdy jest otwarty
  const cookie = document.querySelector('.cookie-banner.visible');
  stack.style.bottom = cookie
    ? `calc(var(--space-lg) + ${cookie.offsetHeight + 12}px)`
    : '';

  const toast = document.createElement('div');
  toast.className = 'toast toast--' + type;
  toast.textContent = message;
  toast._duration = duration;
  stack.appendChild(toast);

  toast.addEventListener('mouseenter', expandToasts);
  toast.addEventListener('mouseleave', scheduleCollapseToasts);
  toast.addEventListener('click', () => removeToast(toast));

  requestAnimationFrame(layoutToasts); // wjazd + przebudowa talii
  toast._timer = setTimeout(() => removeToast(toast), duration);
}

// Układa stos: zwinięty (talia) lub rozwinięty (lista). 0 = najnowszy = na wierzchu (na dole).
function layoutToasts() {
  const stack = document.querySelector('.toast-stack');
  if (!stack) return;
  const toasts = [...stack.children].filter((t) => !t._removing);
  const n = toasts.length;
  const GAP = 12, PEEK = 16, SCALE_STEP = 0.06, VISIBLE = 3;

  let offset = 0;
  for (let front = 0; front < n; front++) {
    const t = toasts[n - 1 - front];
    if (toastsExpanded) {
      t.style.transform = `translateY(${-offset}px) scale(1)`;
      t.style.opacity = '1';
      offset += t.offsetHeight + GAP;
    } else {
      const scale = Math.max(0, 1 - front * SCALE_STEP);
      t.style.transform = `translateY(${-front * PEEK}px) scale(${scale})`;
      t.style.opacity = front < VISIBLE ? '1' : '0';
    }
    t.style.zIndex = String(1000 - front);
  }
}

function removeToast(toast) {
  if (!toast || toast._removing) return;
  toast._removing = true;
  clearTimeout(toast._timer);
  toast.style.opacity = '0';
  toast.style.transform = 'translateY(16px) scale(0.9)';
  layoutToasts();
  setTimeout(() => toast.remove(), 300);
}

function expandToasts() {
  clearTimeout(toastCollapseTimer);
  if (toastsExpanded) return;
  toastsExpanded = true;
  document.querySelectorAll('.toast').forEach((t) => clearTimeout(t._timer)); // pauza autoznikania
  layoutToasts();
}

function scheduleCollapseToasts() {
  clearTimeout(toastCollapseTimer);
  toastCollapseTimer = setTimeout(() => {
    toastsExpanded = false;
    document.querySelectorAll('.toast').forEach((t) => {
      if (!t._removing) t._timer = setTimeout(() => removeToast(t), t._duration || 4000);
    });
    layoutToasts();
  }, 140);
}

/* ----- Hero Slider ----- */
function initHeroSlider() {
  const slider = document.querySelector('.hero-slider');
  if (!slider) return;
  const slides = [...slider.querySelectorAll('.hero-slider__slide')];
  if (slides.length < 2) return;

  const delay = parseInt(slider.dataset.autoplay, 10) || 6000;
  let index = slides.findIndex(s => s.classList.contains('is-active'));
  if (index < 0) index = 0;
  let timer = null;

  // Dots
  const dots = document.createElement('div');
  dots.className = 'hero-slider__dots';
  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'hero-slider__dot' + (i === index ? ' is-active' : '');
    dot.setAttribute('aria-label', `Slajd ${i + 1}`);
    dot.addEventListener('click', () => { go(i); restart(); });
    dots.appendChild(dot);
  });
  slider.appendChild(dots);

  function go(i) {
    slides[index].classList.remove('is-active');
    dots.children[index].classList.remove('is-active');
    index = (i + slides.length) % slides.length;
    slides[index].classList.add('is-active');
    dots.children[index].classList.add('is-active');
  }
  function next() { go(index + 1); }
  function start() { timer = setInterval(next, delay); }
  function stop() { clearInterval(timer); }
  function restart() { stop(); start(); }

  slider.addEventListener('mouseenter', stop);
  slider.addEventListener('mouseleave', start);
  document.addEventListener('visibilitychange', () => {
    document.hidden ? stop() : start();
  });
  start();
}

/* ----- Lightbox (galerie + podgalerie) ----- */
function initLightbox() {
  const triggers = [...document.querySelectorAll('.gallery-item[data-images]')];
  if (!triggers.length) return;

  // Build overlay once
  const box = document.createElement('div');
  box.className = 'lightbox';
  box.setAttribute('role', 'dialog');
  box.setAttribute('aria-modal', 'true');
  box.innerHTML = `
    <button class="lightbox__close" aria-label="Zamknij">&times;</button>
    <button class="lightbox__nav lightbox__nav--prev" aria-label="Poprzednie">&#8249;</button>
    <figure class="lightbox__stage">
      <img class="lightbox__img" src="" alt="">
      <figcaption class="lightbox__caption"></figcaption>
    </figure>
    <button class="lightbox__nav lightbox__nav--next" aria-label="Następne">&#8250;</button>
    <span class="lightbox__counter"></span>`;
  document.body.appendChild(box);

  const imgEl = box.querySelector('.lightbox__img');
  const capEl = box.querySelector('.lightbox__caption');
  const countEl = box.querySelector('.lightbox__counter');
  let slides = [];
  let pos = 0;

  function render() {
    const s = slides[pos];
    imgEl.src = s.src;
    imgEl.alt = s.title || '';
    capEl.textContent = s.meta ? `${s.title} — ${s.meta}` : (s.title || '');
    countEl.textContent = slides.length > 1 ? `${pos + 1} / ${slides.length}` : '';
    box.querySelectorAll('.lightbox__nav').forEach(n => {
      n.style.display = slides.length > 1 ? '' : 'none';
    });
    // preload neighbour
    if (slides.length > 1) {
      const nx = new Image();
      nx.src = slides[(pos + 1) % slides.length].src;
    }
  }
  function open(list, start) {
    slides = list; pos = start;
    document.body.style.overflow = 'hidden';
    box.classList.add('is-open');
    render();
  }
  function close() {
    box.classList.remove('is-open');
    document.body.style.overflow = '';
  }
  function move(d) { pos = (pos + d + slides.length) % slides.length; render(); }

  triggers.forEach(item => {
    item.addEventListener('click', () => {
      const imgs = item.dataset.images.split('|').filter(Boolean);
      if (imgs.length > 1) {
        // podgaleria danego obiektu
        open(imgs.map(src => ({ src, title: item.dataset.title, meta: item.dataset.meta })), 0);
      } else {
        // pojedyncze kafelki — przegląd całej siatki
        const grid = item.closest('.gallery-grid') || document;
        const sib = [...grid.querySelectorAll('.gallery-item[data-images]')];
        const list = sib.map(el => ({
          src: el.dataset.images.split('|')[0],
          title: el.dataset.title, meta: el.dataset.meta
        }));
        open(list, sib.indexOf(item));
      }
    });
  });

  box.querySelector('.lightbox__close').addEventListener('click', close);
  box.querySelector('.lightbox__nav--prev').addEventListener('click', () => move(-1));
  box.querySelector('.lightbox__nav--next').addEventListener('click', () => move(1));
  box.addEventListener('click', e => { if (e.target === box) close(); });
  document.addEventListener('keydown', e => {
    if (!box.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') move(-1);
    else if (e.key === 'ArrowRight') move(1);
  });
}

/* ----- Rozwijany tekst ----- */
function initExpandable() {
  document.querySelectorAll('.expandable').forEach(box => {
    const toggle = box.querySelector('.expandable__toggle');
    if (!toggle) return;
    toggle.addEventListener('click', () => {
      const open = box.classList.toggle('is-open');
      toggle.textContent = open ? 'Zwiń' : 'Czytaj więcej';
    });
  });
}
