/* isw-fronte.js: the Ukrainian front as assessed by ISW / AEI Critical Threats Project, loaded by the
 * visitor's browser straight from ISW's public ArcGIS items. Nothing is copied into this repository.
 *
 *   const fr = await window.caricaFronteISW();   // null on error or timeout
 *   fr = { aree: [{ t: 'ru'|'contesa'|'avanzata'|'controffensiva', d: 'AAAA-MM-GG', p: [[[[lon,lat],...]]] }],
 *          data_valutazione, data, fonte: 'ISW/CTP', autore, link, attribuzione, licenza, origine }
 *
 * Source 1 (fresh, daily): the web map "Assessed Control of Terrain in Ukraine" behind ISW's interactive map
 *   (StoryMap 36a7f6a6...). Its layers are feature collections stored inside the web map, in EPSG:4326,
 *   each feature with pub_date 'AAAA-MM-GG'. ~1.7 MB gzip.
 * Source 2 (fallback): the public FeatureServer "views" of the same org; the most recently edited one per kind,
 *   queried as simplified GeoJSON (a few KB each). In Nov 2026 these lag the web map by weeks.
 *
 * Licence: the ArcGIS items say "This geodata is the exclusive intellectual property of the Institute for the
 * Study of War (ISW). You may not use this geodata without the written consent of ISW." Show it only with
 * ISW's permission; see report/agenti/isw.md.
 */
(function () {
  'use strict';
  const AGOL = 'https://www.arcgis.com/sharing/rest/content/items/';
  const STORYMAP = '36a7f6a6f5a9448496de641cf64bd375';   // "Interactive Map: Russia's Invasion of Ukraine"
  const WEBMAP = '9f04944a2fe84edab9da31750c2b15eb';     // "Assessed Control of Terrain in Ukraine" (Nov 2026)
  const ORG = 'https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/';
  const LINK = 'https://storymaps.arcgis.com/stories/' + STORYMAP;
  const ATTR = 'Mappa: Institute for the Study of War e AEI Critical Threats Project (ISW/CTP), valutazione del controllo del territorio. Dati caricati dal server ArcGIS di ISW, non ripubblicati.';
  const LICENZA = 'This geodata is the exclusive intellectual property of the Institute for the Study of War (ISW). You may not use this geodata without the written consent of ISW.';
  const TOL = 0.002, DEC = 1e4;                          // simplification ~150-200 m, 4 decimals (~10 m)

  // web map layer title -> our type (titles as of Nov 2026; matched loosely)
  const TIPO_WM = [
    [/assessed russian.?controlled terrain|assessed russian.?controlled ukrainian territory/i, 'ru'],
    [/infiltration/i, 'contesa'],
    [/gains in the past 24|past 24 hours/i, 'avanzata24'],
    [/assessed russian advance/i, 'avanzata'],
    [/claimed ukrainian counteroffensive|ukrainian territorial gains/i, 'controffensiva'],
  ];
  // FeatureServer fallback: service-name pattern -> type (the newest by editingInfo.lastEditDate wins)
  const TIPO_FS = [
    [/^VIEW_RussiaCoTinUkraine_V\d+$/i, 'ru'],
    [/^View_AssessedRussianInfiltrationAreasinUkraine_V\d+$/i, 'contesa'],
    [/^AssessedRussianAdvanceInUkraine_V\d+_view$/i, 'avanzata'],
    [/^Assessed_Russian_Gains_in_the_Past_24_Hours_view$/i, 'avanzata24'],
    [/^MDS_Claimed_Ukrainian_Counteroffensives_V\d+_view$/i, 'controffensiva'],
  ];

  async function j(url, ms, signal) {
    const ac = new AbortController(), t = setTimeout(() => ac.abort(), ms);
    const stop = () => ac.abort(); if (signal) signal.addEventListener('abort', stop);
    try {
      const r = await fetch(url, { signal: ac.signal, credentials: 'omit', referrerPolicy: 'no-referrer' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const d = await r.json(); if (d && d.error) throw new Error(d.error.message || 'ArcGIS error'); return d;
    } finally { clearTimeout(t); if (signal) signal.removeEventListener('abort', stop); }
  }
  const iso = ms => (ms ? new Date(ms).toISOString().slice(0, 10) : null);
  const tipo = (tab, s) => { for (const [re, t] of tab) if (re.test(s)) return t; return null; };

  // Douglas-Peucker on one ring, then rounding; keeps the ring's winding (holes stay holes under nonzero fill)
  function semplifica(r) {
    const n = r.length; if (n < 4) return null;
    const keep = new Uint8Array(n); keep[0] = keep[n - 1] = 1; const st = [[0, n - 1]];
    while (st.length) {
      const [a, b] = st.pop(); const [ax, ay] = r[a], [bx, by] = r[b], dx = bx - ax, dy = by - ay, L = dx * dx + dy * dy;
      let md = 0, mi = -1;
      for (let i = a + 1; i < b; i++) {
        const px = r[i][0] - ax, py = r[i][1] - ay;
        const d = L ? Math.abs(px * dy - py * dx) / Math.sqrt(L) : Math.hypot(px, py);
        if (d > md) { md = d; mi = i; }
      }
      if (md > TOL) { keep[mi] = 1; st.push([a, mi], [mi, b]); }
    }
    const out = []; let px, py;
    for (let i = 0; i < n; i++) if (keep[i]) {
      const x = Math.round(r[i][0] * DEC) / DEC, y = Math.round(r[i][1] * DEC) / DEC;
      if (x !== px || y !== py) out.push([x, y]); px = x; py = y;
    }
    if (out.length < 4) return null;
    const f = out[0], l = out[out.length - 1]; if (f[0] !== l[0] || f[1] !== l[1]) out.push([f[0], f[1]]);
    return out;
  }
  const area = r => { let s = 0; for (let i = 0, n = r.length - 1; i < n; i++) s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]; return s / 2; };
  const dentro = (pt, r) => { let c = false; for (let i = 0, k = r.length - 1; i < r.length; k = i++) { const [xi, yi] = r[i], [xk, yk] = r[k]; if ((yi > pt[1]) !== (yk > pt[1]) && pt[0] < (xk - xi) * (pt[1] - yi) / (yk - yi) + xi) c = !c; } return c; };

  // Esri rings (outer clockwise, holes anticlockwise) -> MultiPolygon coordinates
  function daAnelli(rings) {
    const outer = [], holes = [];
    for (const r0 of rings || []) { const r = semplifica(r0); if (r) (area(r) < 0 ? outer : holes).push(r); }
    const polys = outer.map(o => [o]);
    for (const h of holes) { const p = polys.find(p => dentro(h[0], p[0])); if (p) p.push(h); else polys.push([h]); }
    return polys;
  }
  // GeoJSON geometry -> MultiPolygon coordinates (simplified again, server tolerance may be coarser/finer)
  function daGeoJSON(g) {
    if (!g) return [];
    const polys = g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : [];
    return polys.map(p => p.map(semplifica).filter(Boolean)).filter(p => p.length);
  }

  function aggiungi(aree, t, d, p) {
    if (!p.length) return;
    if (t === 'avanzata24') t = 'avanzata';
    const a = aree.find(x => x.t === t && x.d === d);
    if (a) a.p.push(...p); else aree.push(d ? { t, d, p } : { t, p });
  }

  async function daWebMap(signal) {
    let id = WEBMAP;
    try {                                               // the StoryMap points at the current web map
      const sm = await j(AGOL + STORYMAP + '/data?f=json', 3000, signal);
      const wm = Object.values(sm.resources || {}).find(r => r && r.type === 'webmap' && r.data && r.data.itemId);
      if (wm) id = wm.data.itemId;
    } catch (e) { /* keep the known id */ }
    const wm = await j(AGOL + id + '/data?f=json', 9000, signal);
    const aree = []; let data = null;
    for (const l of wm.operationalLayers || []) {
      for (const x of (l.featureCollection && l.featureCollection.layers) || []) {
        const t = tipo(TIPO_WM, l.title || (x.layerDefinition && x.layerDefinition.name) || ''); if (!t) continue;
        const sr = (x.featureSet && x.featureSet.spatialReference) || {};
        for (const f of (x.featureSet && x.featureSet.features) || []) {
          const g = f.geometry; if (!g || !g.rings) continue;
          const wk = (g.spatialReference && g.spatialReference.wkid) || sr.wkid || 4326;
          if (wk !== 4326 && wk !== 4269) continue;      // all ISW layers are lon/lat today; skip anything else
          const d = f.attributes && /^\d{4}-\d{2}-\d{2}$/.test(f.attributes.pub_date) ? f.attributes.pub_date : null;
          if (d && (!data || d > data)) data = d;
          aggiungi(aree, t, t === 'ru' ? undefined : d, daAnelli(g.rings));
        }
      }
    }
    if (!aree.some(a => a.t === 'ru')) throw new Error('web map senza controllo russo');
    for (const a of aree) if (!a.d && a.t !== 'ru' && data) a.d = data;
    return { aree, data, origine: 'webmap ' + id };
  }

  async function daFeatureServer(signal) {
    const list = await j(ORG + '?f=json', 4000, signal);
    const cand = (list.services || []).map(s => ({ s: s.name, t: tipo(TIPO_FS, s.name) })).filter(c => c.t);
    const meta = await Promise.all(cand.map(async c => {
      try {
        const fs = await j(ORG + c.s + '/FeatureServer?f=json', 4000, signal);
        const lid = fs.layers && fs.layers[0] && fs.layers[0].id; if (lid == null) return null;
        const li = await j(ORG + c.s + '/FeatureServer/' + lid + '?f=json', 4000, signal);
        return { ...c, lid, ed: (li.editingInfo && (li.editingInfo.dataLastEditDate || li.editingInfo.lastEditDate)) || 0 };
      } catch (e) { return null; }
    }));
    const best = {};
    for (const m of meta) if (m && (!best[m.t] || m.ed > best[m.t].ed)) best[m.t] = m;
    if (!best.ru) throw new Error('nessun servizio di controllo russo');
    const aree = []; let data = null;
    await Promise.all(Object.values(best).map(async m => {
      const q = 'where=1%3D1&outFields=OBJECTID&returnGeometry=true&f=geojson&maxAllowableOffset=0.002&geometryPrecision=4&outSR=4326';
      const gj = await j(ORG + m.s + '/FeatureServer/' + m.lid + '/query?' + q, 6000, signal).catch(() => null);
      if (!gj) return;
      const d = iso(m.ed); if (m.t === 'ru' && d) data = d;
      for (const f of gj.features || []) aggiungi(aree, m.t, m.t === 'ru' ? undefined : d, daGeoJSON(f.geometry));
    }));
    if (!aree.some(a => a.t === 'ru')) throw new Error('query vuota');
    return { aree, data, origine: 'FeatureServer ' + Object.values(best).map(m => m.s + '/' + m.lid).join(', ') };
  }

  async function caricaFronteISW(opz) {
    const tempo = (opz && opz.timeout) || 12000, ac = new AbortController(), t = setTimeout(() => ac.abort(), tempo);
    try {
      let r = null;
      try { r = await daWebMap(ac.signal); } catch (e) { if (ac.signal.aborted) return null; console.warn('ISW web map:', e.message); }
      if (!r) { try { r = await daFeatureServer(ac.signal); } catch (e) { console.warn('ISW FeatureServer:', e.message); return null; } }
      return { aree: r.aree, data_valutazione: r.data, data: r.data, fonte: 'ISW/CTP', autore: 'ISW / AEI Critical Threats Project',
        link: LINK, attribuzione: ATTR, licenza: LICENZA, origine: r.origine };
    } catch (e) { console.warn('ISW:', e && e.message); return null; }
    finally { clearTimeout(t); }
  }

  window.caricaFronteISW = caricaFronteISW;
  window.caricaFronteISW._fallback = () => daFeatureServer();   // for tests
})();
