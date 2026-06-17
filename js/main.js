/* ============================================================
   Zofia Siek — Main JavaScript
   ============================================================ */

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

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  elements.forEach(el => observer.observe(el));
}

/* ----- Contact Form ----- */
function initContactForm() {
  const form = document.querySelector('.contact-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const consent = form.querySelector('[name="consent"]');
    if (consent && !consent.checked) {
      alert('Proszę zaakceptować zgodę na przetwarzanie danych osobowych.');
      return;
    }

    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Wysyłanie...';
    btn.disabled = true;

    // Simulate send — replace with real endpoint
    setTimeout(() => {
      btn.textContent = 'Wysłano!';
      form.reset();
      setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
      }, 2000);
    }, 1000);
  });
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
