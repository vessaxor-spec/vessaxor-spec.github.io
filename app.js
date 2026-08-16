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
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })}`;
}

async function loadPortfolioData() {
  try {
    const response = await fetch(DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    const teo = data.projects?.teo ?? {};
    const grox = data.projects?.grox ?? {};

    setText('#teo-release', teo.release);
    setText('#grox-release', grox.release);
    setText('#teo-status', teo.status);
    setText('#grox-status', grox.status);
    setText('#state-teo-release', teo.release);
    setText('#state-grox-release', grox.release);
    setText('#state-teo-status', teo.status);
    setText('#state-grox-status', grox.status);
    setText('#teo-focus', teo.focus);
    setText('#grox-focus', grox.focus);
    setText('#research-focus', data.research?.focus);
    setText('#reviewed-at', `reviewed ${data.profile?.reviewed_at ?? '—'}`);
    setText('#generated-at', formatGeneratedAt(data.generated_at));
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
  };

  toggle.addEventListener('click', () => {
    const open = !nav.classList.contains('is-open');
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', close));
  window.addEventListener('resize', () => {
    if (window.innerWidth > 980) close();
  });
}

function configureReveals() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const targets = document.querySelectorAll(
    '.system-panel, .relation-grid, .state-board, .work-list li, .principles-grid article, .source-links'
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
configureReveals();
