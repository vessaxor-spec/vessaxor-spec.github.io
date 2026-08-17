#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const ROOT = new URL('../', import.meta.url).pathname;
const VISUAL_DIR = join(ROOT, 'assets', 'visuals');
const SOURCE_FILES = ['vessaxor-hero.png', 'teo-banner.png', 'grox-banner.png'];
const WIDTHS = [720, 1200, 1800];
const CHROME_CANDIDATES = ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'];

async function exists(path) {
  try { await readFile(path); return true; } catch { return false; }
}

async function findChrome() {
  for (const candidate of CHROME_CANDIDATES) if (await exists(candidate)) return candidate;
  throw new Error(`Chrome/Chromium not found in: ${CHROME_CANDIDATES.join(', ')}`);
}

async function launchChrome(chrome) {
  const profileDir = await mkdtemp(join(tmpdir(), 'vessaxor-media-chrome-'));
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
  if (!response.ok) throw new Error(`Unable to list Chrome targets: HTTP ${response.status}`);
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

async function waitForImage(cdp) {
  for (let attempt = 0; attempt < 100; attempt++) {
    const result = await cdp('Runtime.evaluate', {
      expression: `document.readyState === 'complete' && document.images.length === 1 && document.images[0].complete && document.images[0].naturalWidth > 0`,
      returnByValue: true
    });
    if (result.result?.value === true) {
      await cdp('Runtime.evaluate', {
        expression: `new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))`,
        awaitPromise: true
      });
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error('Capture image did not finish loading');
}

async function setCaptureDocument(cdp, imageBase64, social) {
  const frameTree = await cdp('Page.getFrameTree');
  const frameId = frameTree.frameTree?.frame?.id;
  if (!frameId) throw new Error('Unable to resolve main frame');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{margin:0;width:100%;height:100%;overflow:hidden;background:${social ? '#07090c' : '#05070a'};}
    body{display:flex;align-items:center;justify-content:center;}
    img{display:block;width:100%;height:${social ? '400px' : '100%'};object-fit:contain;}
  </style></head><body><img src="data:image/png;base64,${imageBase64}" alt=""></body></html>`;
  await cdp('Page.setDocumentContent', { frameId, html });
  await waitForImage(cdp);
}

async function capture(cdp, imageBase64, width, height, format, quality, output, social = false) {
  await cdp('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
  await setCaptureDocument(cdp, imageBase64, social);
  const params = { format, fromSurface: true, captureBeyondViewport: false };
  if (quality != null) params.quality = quality;
  const result = await cdp('Page.captureScreenshot', params);
  if (!result.data) throw new Error(`No screenshot data returned for ${output}`);
  await writeFile(output, Buffer.from(result.data, 'base64'));
  console.log(`built ${output.replace(ROOT, '')}`);
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
  const sourcePayloads = new Map();
  for (const file of SOURCE_FILES) {
    const path = join(VISUAL_DIR, file);
    if (!(await exists(path))) throw new Error(`Missing synchronized source visual: ${file}`);
    sourcePayloads.set(file, (await readFile(path)).toString('base64'));
  }

  const chrome = await findChrome();
  const { child, profileDir, port } = await launchChrome(chrome);
  try {
    const { socket, cdp } = await connectPage(port);
    await cdp('Page.enable');
    await cdp('Runtime.enable');
    try {
      for (const file of SOURCE_FILES) {
        const stem = file.replace(/\.png$/, '');
        const image = sourcePayloads.get(file);
        const quality = file === 'vessaxor-hero.png' ? 96 : 90;
        for (const width of WIDTHS) {
          await capture(cdp, image, width, Math.round(width / 3), 'webp', quality, join(VISUAL_DIR, `${stem}-${width}.webp`));
        }
      }
      await capture(
        cdp,
        sourcePayloads.get('vessaxor-hero.png'),
        1200,
        630,
        'png',
        null,
        join(VISUAL_DIR, 'vessaxor-social-preview.png'),
        true
      );
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
