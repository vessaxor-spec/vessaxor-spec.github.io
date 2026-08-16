const DATA_URL = './data/projects.json';

async function loadPortfolioData() {
  try {
    const response = await fetch(DATA_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();

    document.querySelector('#teo-release').textContent = data.projects.teo.release;
    document.querySelector('#grox-release').textContent = data.projects.grox.release;
    document.querySelector('#teo-status').textContent = data.projects.teo.status;
    document.querySelector('#grox-status').textContent = data.projects.grox.status;
    document.querySelector('#teo-focus').textContent = data.projects.teo.focus;
    document.querySelector('#grox-focus').textContent = data.projects.grox.focus;
    document.querySelector('#research-focus').textContent = data.research.focus;
    document.querySelector('#reviewed-at').textContent = `Curated public state · reviewed ${data.profile.reviewed_at}`;
  } catch (error) {
    console.warn('Portfolio data unavailable; static site content remains usable.', error);
  }
}

function startSignalField() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const canvas = document.querySelector('#signal-field');
  const context = canvas.getContext('2d');
  const particles = [];
  const pointer = { x: -9999, y: -9999 };
  let width = 0;
  let height = 0;
  let frame = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = rect.width;
    height = rect.height;
    canvas.width = Math.floor(width * ratio);
    canvas.height = Math.floor(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    particles.length = 0;
    const count = Math.max(28, Math.min(72, Math.floor(width / 19)));
    for (let i = 0; i < count; i += 1) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.16,
        vy: (Math.random() - 0.5) * 0.16,
        r: Math.random() * 1.25 + 0.55,
        family: Math.random() > 0.62 ? 'cyan' : 'orange'
      });
    }
  }

  function draw() {
    frame = requestAnimationFrame(draw);
    context.clearRect(0, 0, width, height);
    for (const p of particles) {
      const dx = p.x - pointer.x;
      const dy = p.y - pointer.y;
      const distance = Math.hypot(dx, dy);
      if (distance < 120 && distance > 0) {
        p.x += (dx / distance) * 0.12;
        p.y += (dy / distance) * 0.12;
      }
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < -10) p.x = width + 10;
      if (p.x > width + 10) p.x = -10;
      if (p.y < -10) p.y = height + 10;
      if (p.y > height + 10) p.y = -10;

      context.beginPath();
      context.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      context.fillStyle = p.family === 'cyan' ? 'rgba(50,199,255,.6)' : 'rgba(255,122,23,.58)';
      context.fill();
    }
  }

  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  canvas.addEventListener('pointermove', (event) => {
    const rect = canvas.getBoundingClientRect();
    pointer.x = event.clientX - rect.left;
    pointer.y = event.clientY - rect.top;
  });
  canvas.addEventListener('pointerleave', () => { pointer.x = -9999; pointer.y = -9999; });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancelAnimationFrame(frame);
    else draw();
  });
  resize();
  draw();
}

loadPortfolioData();
startSignalField();
