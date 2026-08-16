const DATA_URL = './data/projects.json';

function setText(selector, value) {
  const node = document.querySelector(selector);
  if (node && value != null && value !== '') node.textContent = value;
}

function formatGeneratedAt(value) {
  if (!value || value === 'baseline') return 'build-time public data';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return `generated ${parsed.toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric'
  })}`;
}

async function loadPortfolioData() {
  try {
    const response = await fetch(DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const teo = data.projects?.teo ?? {};
    const grox = data.projects?.grox ?? {};

    [
      ['#teo-release', teo.release], ['#teo-status', teo.status],
      ['#state-teo-release', teo.release], ['#state-teo-status', teo.status],
      ['#hero-teo-release', teo.release], ['#hero-teo-status', teo.status],
      ['#grox-release', grox.release], ['#grox-status', grox.status],
      ['#state-grox-release', grox.release], ['#state-grox-status', grox.status],
      ['#hero-grox-release', grox.release], ['#hero-grox-status', grox.status],
      ['#teo-focus', teo.focus], ['#grox-focus', grox.focus],
      ['#research-focus', data.research?.focus],
      ['#reviewed-at', `reviewed ${data.profile?.reviewed_at ?? '—'}`],
      ['#generated-at', formatGeneratedAt(data.generated_at)]
    ].forEach(([selector, value]) => setText(selector, value));
  } catch (error) {
    console.warn('Portfolio data unavailable; current static fallback content remains visible.', error);
  }
}

function configureNavigation() {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#site-nav');
  if (!toggle || !nav) return;

  const close = () => {
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = 'Menu';
  };

  toggle.addEventListener('click', () => {
    const open = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? 'Close' : 'Menu';
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      close();
      toggle.focus();
    }
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', close));
  window.addEventListener('resize', () => {
    if (window.innerWidth > 980) close();
  });
}

function configureActiveNavigation() {
  const links = [...document.querySelectorAll('#site-nav a[href^="#"]')];
  const targets = links
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);
  if (!targets.length) return;

  const byId = new Map(links.map((link) => [link.getAttribute('href').slice(1), link]));
  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    links.forEach((link) => link.classList.remove('is-active'));
    const active = byId.get(visible.target.id);
    if (active) active.classList.add('is-active');
  }, { rootMargin: '-18% 0px -68% 0px', threshold: [0, 0.1, 0.25, 0.5] });

  targets.forEach((target) => observer.observe(target));
}

function configureReveals() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const targets = document.querySelectorAll(
    '.system-panel, .relation-spine, .state-work-layout, .principles-list li, .source-links'
  );
  targets.forEach((node) => node.classList.add('reveal'));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -7% 0px', threshold: 0.07 });
  targets.forEach((node) => observer.observe(node));
}

loadPortfolioData();
configureNavigation();
configureActiveNavigation();
configureReveals();
