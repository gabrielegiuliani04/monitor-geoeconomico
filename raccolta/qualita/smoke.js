#!/usr/bin/env node
/* Browser smoke test of the published site (docs/), with Playwright and Chromium.

   What it does:
     1. serves docs/ with `python3 -m http.server` on a free local port;
     2. opens the map (index.html): no JS errors, no failed data/*.json requests,
        every map layer built from the data has > 0 points or lines;
     3. opens the Terminal and each of its tabs: each renders some content without errors;
     4. opens the simulator, news, credits and every report page (docs/report/, docs/report/en/);
     5. writes raccolta/qualita/smoke.json (read by controlla_tutto.py).

   Usage:   node raccolta/qualita/smoke.js
   Needs:   require('playwright') and a Chromium build. Locally both are preinstalled;
            on GitHub Actions:  npm i --no-save playwright && npx playwright install --with-deps chromium
   Exit code: 0 when every test passes, 1 otherwise (the result file is always written).
   External requests (CDN scripts) go through HTTPS_PROXY when that variable is set. */
'use strict';
const { spawn } = require('child_process');
const fs = require('fs');
const net = require('net');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const DOCS = path.join(ROOT, 'docs');
const OUT = path.join(__dirname, 'smoke.json');
const T0 = Date.now();
const results = [];
const pass = (page, test, detail = '') => results.push({ page, test, ok: true, detail });
const fail = (page, test, detail = '') => results.push({ page, test, ok: false, detail: String(detail).slice(0, 600) });

function freePort() {
  return new Promise((res, rej) => { const s = net.createServer(); s.listen(0, '127.0.0.1', () => { const p = s.address().port; s.close(() => res(p)); }); s.on('error', rej); });
}
async function waitServer(port, ms = 10000) {
  const end = Date.now() + ms;
  while (Date.now() < end) {
    const ok = await new Promise(r => { const c = net.connect(port, '127.0.0.1', () => { c.end(); r(true); }); c.on('error', () => r(false)); });
    if (ok) return true;
    await new Promise(r => setTimeout(r, 200));
  }
  return false;
}
function write(extra) {
  const failed = results.filter(r => !r.ok);
  const out = Object.assign({
    updated: new Date().toISOString().slice(0, 16) + 'Z',
    overall: failed.length ? (failed.some(f => f.page === 'index.html') ? 'red' : 'amber') : 'green',
    seconds: Math.round((Date.now() - T0) / 1000),
    passed: results.length - failed.length,
    failed,
    results,
  }, extra || {});
  fs.writeFileSync(OUT, JSON.stringify(out, null, 1) + '\n');
  return out;
}

// Errors that come from the test environment, not from the site (ad blockers, missing fonts...).
const IGNORE = [/favicon\.ico/i, /fonts\.(googleapis|gstatic)\.com/i];

function watch(page, bag) {
  page.on('pageerror', e => bag.errors.push('pageerror: ' + (e && e.message || e)));
  page.on('console', m => { if (m.type() === 'error') { const t = m.text(); if (!IGNORE.some(r => r.test(t))) bag.errors.push('console: ' + t); } });
  page.on('requestfailed', r => { const u = r.url(); if (!IGNORE.some(x => x.test(u))) bag.failedReq.push(u + ' (' + ((r.failure() || {}).errorText || '?') + ')'); });
  page.on('response', r => { if (r.status() >= 400 && !IGNORE.some(x => x.test(r.url()))) bag.failedReq.push(r.url() + ' (HTTP ' + r.status() + ')'); });
}

async function main() {
  let chromium;
  try { ({ chromium } = require('playwright')); } catch (e) {
    fail('-', 'playwright available', 'require("playwright") failed: ' + e.message); write(); process.exit(1);
  }
  const port = await freePort();
  const srv = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1', '--directory', DOCS], { stdio: 'ignore' });
  const stop = () => { try { srv.kill(); } catch (e) { /* already gone */ } };
  process.on('exit', stop);
  if (!(await waitServer(port))) { fail('-', 'local server', 'python3 -m http.server did not start'); write(); stop(); process.exit(1); }
  const base = `http://127.0.0.1:${port}/`;
  const launch = { headless: true };
  if (process.env.HTTPS_PROXY) launch.proxy = { server: process.env.HTTPS_PROXY, bypass: '127.0.0.1,localhost' };
  let browser;
  try { browser = await chromium.launch(launch); } catch (e) {
    fail('-', 'launch chromium', e.message + ' (on CI run: npx playwright install --with-deps chromium)'); write(); stop(); process.exit(1);
  }
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 860 } });
  const layerCounts = {};

  // ------------------------------------------------------------------ the map
  {
    const name = 'index.html', bag = { errors: [], failedReq: [] };
    const page = await ctx.newPage(); watch(page, bag);
    try {
      await page.goto(base + 'index.html', { waitUntil: 'load', timeout: 45000 });
      await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
      await page.waitForFunction(() => typeof X !== 'undefined' && X && X.data && Object.keys(X.data).length > 0, null, { timeout: 30000 })
        .catch(() => {});
      pass(name, 'page loads');
      const info = await page.evaluate(() => {
        const o = { points_main: (typeof PT !== 'undefined' && PT) ? PT.length : null, pts: {}, lines: {}, dataNull: [] };
        if (typeof X !== 'undefined' && X) {
          for (const [k, v] of Object.entries(X.pts || {})) o.pts[k] = Array.isArray(v) ? v.length : (v && v.length) || 0;
          for (const [k, v] of Object.entries(X.lines || {})) o.lines[k] = v && v.list ? v.list.length : 0;
          for (const [k, v] of Object.entries(X.data || {})) if (v == null) o.dataNull.push(k);
        }
        return o;
      });
      Object.assign(layerCounts, { main_points: info.points_main }, Object.fromEntries(Object.entries(info.pts).map(([k, v]) => ['pts.' + k, v])),
        Object.fromEntries(Object.entries(info.lines).map(([k, v]) => ['lines.' + k, v])));
      if (info.points_main > 0) pass(name, 'main points > 0', String(info.points_main)); else fail(name, 'main points > 0', 'PT has ' + info.points_main + ' points');
      const empty = [...Object.entries(info.pts), ...Object.entries(info.lines)].filter(([, v]) => !(v > 0)).map(([k]) => k);
      const nLayers = Object.keys(info.pts).length + Object.keys(info.lines).length;
      if (nLayers === 0) fail(name, 'extra layers built', 'X.pts and X.lines are empty: the data files were not loaded');
      else if (empty.length) fail(name, 'every layer has > 0 elements', 'empty: ' + empty.join(', '));
      else pass(name, 'every layer has > 0 elements', nLayers + ' layers');
      if (info.dataNull.length) fail(name, 'data files loaded', 'null in X.data: ' + info.dataNull.join(', '));
      else pass(name, 'data files loaded');
      // close the intro box if shown
      await page.click('#intro-ok', { timeout: 2000 }).catch(() => {});
      // ---------------------------------------------------------------- the Terminal and its tabs
      const btn = await page.$('#trm-btn');
      if (!btn || !(await btn.isVisible())) fail(name, 'Terminal button visible', '#trm-btn hidden or missing');
      else {
        await btn.click();
        await page.waitForSelector('#trm:not([hidden])', { timeout: 5000 }).then(() => pass(name, 'Terminal opens'))
          .catch(e => fail(name, 'Terminal opens', e.message));
        const tabs = await page.$$eval('#trm-tabs .chip', bs => bs.map(b => ({ tab: b.dataset.tab, label: b.textContent.trim() })));
        if (!tabs.length) fail(name, 'Terminal tabs', 'no tab buttons');
        for (const t of tabs) {
          const before = bag.errors.length;
          try {
            await page.click(`#trm-tabs .chip[data-tab="${t.tab}"]`, { timeout: 5000 });
            await page.waitForTimeout(400);
            const len = await page.$eval('#trm', el => el.innerText.replace(/\s+/g, ' ').trim().length);
            const pressed = await page.$eval(`#trm-tabs .chip[data-tab="${t.tab}"]`, b => b.getAttribute('aria-pressed'));
            const newErr = bag.errors.slice(before);
            if (newErr.length) fail(name, `Terminal tab ${t.label}`, newErr.join(' | '));
            else if (len < 200) fail(name, `Terminal tab ${t.label}`, `only ${len} characters of content`);
            else if (pressed !== 'true') fail(name, `Terminal tab ${t.label}`, 'tab not marked as selected');
            else pass(name, `Terminal tab ${t.label}`, `${len} characters`);
          } catch (e) { fail(name, `Terminal tab ${t.label}`, e.message); }
        }
      }
    } catch (e) { fail(name, 'page loads', e.message); }
    const dataFail = bag.failedReq.filter(u => /\/data\//.test(u));
    if (dataFail.length) fail(name, 'no failed data requests', dataFail.join(' | ')); else pass(name, 'no failed data requests');
    const otherFail = bag.failedReq.filter(u => !/\/data\//.test(u));
    if (otherFail.length) fail(name, 'no failed requests (scripts, pages)', otherFail.join(' | '));
    if (bag.errors.length) fail(name, 'no JS errors', [...new Set(bag.errors)].slice(0, 10).join(' | ')); else pass(name, 'no JS errors');
    await page.close();
  }

  // ------------------------------------------------------------------ the other pages
  const pages = ['simulatore.html', 'notizie.html', 'crediti.html'];
  for (const dir of ['report', path.join('report', 'en')]) {
    try { for (const f of fs.readdirSync(path.join(DOCS, dir)).sort()) if (f.endsWith('.html')) pages.push(path.join(dir, f).split(path.sep).join('/')); } catch (e) { /* folder missing */ }
  }
  for (const name of pages) {
    if (!fs.existsSync(path.join(DOCS, name))) { fail(name, 'page exists', 'missing'); continue; }
    const bag = { errors: [], failedReq: [] };
    const page = await ctx.newPage(); watch(page, bag);
    try {
      await page.goto(base + name, { waitUntil: 'load', timeout: 45000 });
      await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {});
      await page.waitForTimeout(500);
      const info = await page.evaluate(() => ({ len: document.body ? document.body.innerText.replace(/\s+/g, ' ').trim().length : 0, title: document.title }));
      if (info.len < 300) fail(name, 'content rendered', `only ${info.len} characters (title: ${info.title})`);
      else pass(name, 'content rendered', `${info.len} characters`);
      if (name === 'simulatore.html') {
        // move the first range or click the first button: the page must react without errors
        const before = bag.errors.length;
        const ctl = await page.$('input[type=range], select, button');
        if (ctl) {
          const tag = await ctl.evaluate(e => e.tagName + (e.type ? ':' + e.type : ''));
          if (tag === 'INPUT:range') await ctl.evaluate(e => { e.value = e.max || 1; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); });
          else if (tag.startsWith('SELECT')) await ctl.evaluate(e => { if (e.options.length > 1) e.selectedIndex = 1; e.dispatchEvent(new Event('change', { bubbles: true })); });
          else await ctl.click({ timeout: 3000 }).catch(() => {});
          await page.waitForTimeout(500);
          if (bag.errors.length > before) fail(name, 'simulator reacts to input', bag.errors.slice(before).join(' | '));
          else pass(name, 'simulator reacts to input', tag);
        }
      }
      if (name === 'notizie.html') {
        const n = await page.$$eval('a[href^="http"]', as => as.length);
        if (n > 20) pass(name, 'news links listed', `${n} external links`); else fail(name, 'news links listed', `${n} external links`);
      }
    } catch (e) { fail(name, 'page loads', e.message); }
    const dataFail = bag.failedReq.filter(u => u.startsWith(base));
    if (dataFail.length) fail(name, 'no failed local requests', dataFail.join(' | '));
    if (bag.errors.length) fail(name, 'no JS errors', [...new Set(bag.errors)].slice(0, 8).join(' | ')); else pass(name, 'no JS errors');
    await page.close();
  }
  await browser.close();
  stop();
  const out = write({ layer_counts: layerCounts, pages });
  console.log(`Smoke test: ${out.overall.toUpperCase()}, ${out.passed} passed, ${out.failed.length} failed in ${out.seconds} s -> ${path.relative(ROOT, OUT)}`);
  for (const f of out.failed) console.log(`  FAIL ${f.page}: ${f.test}: ${f.detail.slice(0, 200)}`);
  process.exit(out.failed.length ? 1 : 0);
}

main().catch(e => { fail('-', 'smoke test ran', e && e.stack || e); write(); process.exit(1); });
