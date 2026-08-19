#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const TARGET = process.argv[2] ?? 'http://127.0.0.1:8000/';
const CHROME_CANDIDATES = ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
const PATHS = ['/', '/teo/', '/grox/', '/evidence/', '/notes/'];

async function findChrome() {
  const { access } = await import('node:fs/promises');
  for (const candidate of CHROME_CANDIDATES) {
    try { await access(candidate); return candidate; } catch {}
  }
  throw new Error(`Chrome/Chromium not found in: ${CHROME_CANDIDATES.join(', ')}`);
}

async function launchChrome(chrome) {
  const profileDir = await mkdtemp(join(tmpdir(), 'vessaxor-render-chrome-'));
  const child = spawn(chrome, [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
    '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0',
    `--user-data-dir=${profileDir}`, '--no-first-run', '--no-default-browser-check', 'about:blank'
  ], { stdio: ['ignore', 'ignore', 'pipe'] });
  const debuggerUrl = await new Promise((resolve, reject) => {
    let stderr = '';
    const timer = setTimeout(() => reject(new Error(`Chrome DevTools endpoint timeout: ${stderr}`)), 15000);
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', chunk => {
      stderr += chunk;
      const match = stderr.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
    child.once('exit', code => { clearTimeout(timer); reject(new Error(`Chrome exited before DevTools endpoint (code ${code}): ${stderr}`)); });
    child.once('error', error => { clearTimeout(timer); reject(error); });
  });
  return { child, profileDir, port: Number(new URL(debuggerUrl).port) };
}

async function connectPage(port) {
  const response = await fetch(`http://127.0.0.1:${port}/json/list`);
  const targets = await response.json();
  const page = targets.find(target => target.type === 'page');
  if (!page?.webSocketDebuggerUrl) throw new Error('No Chrome page target available');
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, { once: true });
    socket.addEventListener('error', reject, { once: true });
  });
  let nextId = 1;
  const pending = new Map();
  socket.addEventListener('message', event => {
    const message = JSON.parse(event.data);
    if (!message.id) return;
    const waiter = pending.get(message.id);
    if (!waiter) return;
    pending.delete(message.id);
    if (message.error) waiter.reject(new Error(`${waiter.method}: ${JSON.stringify(message.error)}`));
    else waiter.resolve(message.result ?? {});
  });
  function cdp(method, params = {}) {
    const id = nextId++;
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject, method });
      socket.send(JSON.stringify({ id, method, params }));
    });
  }
  return { socket, cdp };
}

async function waitReady(cdp) {
  for (let attempt = 0; attempt < 100; attempt++) {
    const result = await cdp('Runtime.evaluate', {
      expression: `document.readyState === 'complete' && document.querySelector('#main') !== null`,
      returnByValue: true
    });
    if (result.result?.value === true) {
      await new Promise(resolve => setTimeout(resolve, 350));
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error('Portfolio page did not become ready for render capture');
}

async function primeLazyMedia(cdp) {
  const result = await cdp('Runtime.evaluate', {
    expression: `(async () => {
      const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
      const step = Math.max(320, Math.floor(window.innerHeight * 0.72));
      const limit = document.documentElement.scrollHeight;
      for (let y = 0; y < limit; y += step) {
        window.scrollTo(0, y);
        await sleep(70);
      }
      window.scrollTo(0, document.documentElement.scrollHeight);
      await sleep(100);
      const images = Array.from(document.images);
      await Promise.all(images.map(image => {
        if (image.complete) return Promise.resolve();
        return new Promise(resolve => {
          image.addEventListener('load', resolve, { once: true });
          image.addEventListener('error', resolve, { once: true });
          setTimeout(resolve, 3000);
        });
      }));
      window.scrollTo(0, 0);
      await sleep(100);
      document.querySelectorAll('.reveal').forEach(node => node.classList.add('is-visible'));
      return images.map(image => ({ src: image.currentSrc || image.src, complete: image.complete, width: image.naturalWidth }));
    })()`,
    awaitPromise: true,
    returnByValue: true
  });
  const images = result.result?.value ?? [];
  const failed = images.filter(image => !image.complete || !image.width);
  if (failed.length) throw new Error(`Render review found unloaded images: ${JSON.stringify(failed)}`);
}

async function preparePage(cdp, width, viewportHeight, path) {
  const url = new URL(path, TARGET).href;
  await cdp('Emulation.setDeviceMetricsOverride', { width, height: viewportHeight, deviceScaleFactor: 1, mobile: width <= 640 });
  await cdp('Page.navigate', { url });
  await waitReady(cdp);
  await cdp('Runtime.evaluate', { expression: `document.documentElement.style.scrollBehavior='auto'; true;`, returnByValue: true });
  await primeLazyMedia(cdp);
  const metrics = await cdp('Page.getLayoutMetrics');
  const content = metrics.cssContentSize ?? metrics.contentSize;
  const captureWidth = Math.ceil(content.width);
  const captureHeight = Math.ceil(content.height);
  if (captureWidth > width + 1) throw new Error(`Horizontal overflow at ${width}px on ${path}: content width ${captureWidth}px`);
  return { captureWidth, captureHeight, path };
}

async function capture(cdp, width, viewportHeight, output, path = '/') {
  const { captureWidth, captureHeight } = await preparePage(cdp, width, viewportHeight, path);
  const result = await cdp('Page.captureScreenshot', {
    format: 'png', fromSurface: true, captureBeyondViewport: true,
    clip: { x: 0, y: 0, width: captureWidth, height: captureHeight, scale: 1 }
  });
  await writeFile(output, Buffer.from(result.data, 'base64'));
  console.log(`captured ${output}: ${captureWidth}x${captureHeight}`);
}

async function assertReliableMediaFallback(cdp) {
  await preparePage(cdp, 1440, 1000, '/');
  const result = await cdp('Runtime.evaluate', {
    expression: `(async () => {
      const frame = document.querySelector('.hero-art[data-reliable-media]');
      const image = frame?.querySelector('img');
      const fallback = frame?.querySelector('.media-fallback');
      if (!frame || !image || !fallback) return { ok: false, reason: 'missing reliability markup' };
      image.dispatchEvent(new Event('error'));
      await new Promise(resolve => setTimeout(resolve, 80));
      image.dispatchEvent(new Event('error'));
      await new Promise(resolve => setTimeout(resolve, 80));
      const style = getComputedStyle(fallback);
      const rect = fallback.getBoundingClientRect();
      const ok = frame.dataset.mediaState === 'failed' && Number(style.opacity) > 0.9 && rect.width > 200 && rect.height > 100;
      return { ok, state: frame.dataset.mediaState, opacity: style.opacity, width: rect.width, height: rect.height };
    })()`,
    awaitPromise: true,
    returnByValue: true
  });
  const verdict = result.result?.value ?? {};
  if (!verdict.ok) throw new Error(`Hero fail-visible fallback check failed: ${JSON.stringify(verdict)}`);
  console.log(`hero fail-visible fallback passed: ${JSON.stringify(verdict)}`);
}

async function cleanupChrome(child, profileDir) {
  if (child.exitCode == null) child.kill('SIGTERM');
  if (child.exitCode == null) {
    await Promise.race([
      new Promise(resolve => child.once('exit', resolve)),
      new Promise(resolve => setTimeout(resolve, 3000))
    ]);
  }
  try {
    await rm(profileDir, { recursive: true, force: true, maxRetries: 10, retryDelay: 100 });
  } catch (error) {
    console.warn(`Temporary Chrome profile cleanup deferred: ${error.message}`);
  }
}

async function main() {
  const chrome = await findChrome();
  const { child, profileDir, port } = await launchChrome(chrome);
  try {
    const { socket, cdp } = await connectPage(port);
    await cdp('Page.enable');
    await cdp('Runtime.enable');
    try {
      await capture(cdp, 1440, 1000, 'render-desktop.png', '/');
      await capture(cdp, 390, 844, 'render-mobile.png', '/');
      for (const path of PATHS.slice(1)) {
        await preparePage(cdp, 1440, 1000, path);
        await preparePage(cdp, 390, 844, path);
        console.log(`layout passed on desktop/mobile: ${path}`);
      }
      await assertReliableMediaFallback(cdp);
    } finally {
      try { await cdp('Browser.close'); } catch {}
      socket.close();
    }
  } finally {
    await cleanupChrome(child, profileDir);
  }
}

main().catch(error => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
