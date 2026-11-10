import {
  W, H, BRAND, assets, renderFrame, layerBounds, hitTest, syncVideos, seekVideosExact, layerActive,
} from './engine.js';

const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else if (v !== false && v != null) n.setAttribute(k, v === true ? '' : v);
  }
  kids.flat().forEach((c) => c != null && n.append(c.nodeType ? c : document.createTextNode(c)));
  return n;
};
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const round = (v, d = 1) => Math.round(v * 10 ** d) / 10 ** d;
const uid = () => 'l' + Math.random().toString(36).slice(2, 8);
const fmt = (t) => `${Math.floor(t / 60)}:${(t % 60).toFixed(1).padStart(4, '0')}`;

const FPS = 30;
// Biblioteca de sonidos: nombre -> { name, label, buffer }. Incluye los de assets/sfx y los que importes.
const sounds = new Map();
let AC = null;
const getAC = () => { AC = AC || new (window.AudioContext || window.webkitAudioContext)(); return AC; };
let liveSrc = [];
const decodeSound = async (ab) => getAC().decodeAudioData(ab.slice(0));
async function loadSfxLibrary() {
  try {
    const r = await fetch('assets/sfx/sfx.json', { cache: 'no-cache' });
    if (!r.ok) return;
    const { sonidos } = await r.json();
    await Promise.all(sonidos.map(async (x) => {
      try {
        const rr = await fetch(`assets/sfx/${x.archivo}`); const buffer = await decodeSound(await rr.arrayBuffer());
        const name = x.archivo.replace(/\.mp3$/, '');
        sounds.set(name, { name, label: `${name} · ${x.uso}`, buffer });
      } catch { /* sonido no disponible */ }
    }));
  } catch { /* sin biblioteca */ }
}
const LS_KEY = 'ursulahr-studio-project-v1';
const cv = $('#cv'); const ctx = cv.getContext('2d');
const audioEl = new Audio(); audioEl.preload = 'auto';

const S = {
  P: null, sel: null, t: 0, playing: false, sc: 0.3, zoom: 38,
  clock: { base: 0, start: 0 }, audio: { buffer: null, name: '' },
  hist: [], hi: -1, exporting: false,
};

// ---------- utilidades de UI ----------
let toastTimer;
function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('on');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('on'), 2600);
}
const fontsReady = () => Promise.all([
  document.fonts.load('48px "Archivo Black"'), document.fonts.load('700 40px Lato'), document.fonts.load('400 40px Lato'),
]);

// ---------- proyecto, historial y guardado ----------
const sel = () => (S.P ? S.P.layers.find((l) => l.id === S.sel) || null : null);
let saveTimer;
function commit() {
  const s = JSON.stringify(S.P);
  if (s === S.hist[S.hi]) return;
  S.hist = S.hist.slice(0, S.hi + 1); S.hist.push(s); if (S.hist.length > 120) S.hist.shift();
  S.hi = S.hist.length - 1;
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => { try { localStorage.setItem(LS_KEY, s); } catch { /* sin almacenamiento */ } }, 400);
}
function restore(i) {
  if (i < 0 || i >= S.hist.length) return;
  S.hi = i; S.P = JSON.parse(S.hist[i]);
  if (!sel()) S.sel = null;
  refreshAll();
}
function setProject(p, keepAudio = false) {
  S.P = p; S.sel = null; S.t = 0; pause();
  p.layers.forEach((l) => { l.id = l.id || uid(); });
  S.hist = []; S.hi = -1; commit();
  if (!keepAudio) { audioEl.removeAttribute('src'); S.audio = { buffer: null, name: '' }; }
  $('#projName').value = p.name || 'Reel';
  $('#durInput').value = p.duration;
  refreshAll();
  const missing = [...new Set(p.layers.filter((l) => l.asset && !assets.has(l.asset)).map((l) => l.asset))];
  if (missing.length) toast('Faltan medios: ' + missing.join(', '));
}

function blankProject() {
  const mk = (o) => ({ id: uid(), start: 0, end: 15, x: 540, y: 960, w: 100, h: 100, rot: 0, opacity: 1, animIn: 'none', animOut: 'none', animDur: 0.45, ...o });
  return {
    name: 'Reel nuevo', width: W, height: H, fps: FPS, duration: 15, background: BRAND.ivory, voiceover: '',
    layers: [
      mk({ type: 'logo', name: 'Logo HR', variant: 'dark', x: 190, y: 190, w: 150, h: 100 }),
      mk({ type: 'shape', kind: 'arrow', name: 'Flecha', color: BRAND.black, x: 900, y: 190, w: 64, h: 64 }),
      mk({ type: 'text', name: 'Título', text: 'Tu *título* aquí', font: 'title', size: 120, color: BRAND.black, accent: BRAND.green, align: 'left', lh: 1.05, x: 540, y: 760, w: 880, h: 300, animIn: 'rise' }),
      mk({ type: 'caption', name: 'Subtítulos', text: 'Escribe aquí lo que dice la voz en off', size: 54, x: 540, y: 1440, w: 960, h: 110, capStyle: 'pill', maxWords: 4, accent: BRAND.coral, animIn: 'fade' }),
    ],
  };
}

async function loadTemplate(name) {
  try {
    if (name === 'blank') { setProject(blankProject()); return; }
    const r = await fetch(`projects/${name}.json`, { cache: 'no-cache' });
    if (!r.ok) throw new Error(r.status);
    setProject(await r.json());
  } catch (e) { toast('No pude cargar la plantilla'); console.error(e); }
}

// ---------- capas ----------
const TYPE_ICON = { text: 'T', shape: '◆', image: 'I', mockup: 'M', caption: 'S', logo: 'HR', sound: '♪' };
const NEW_LAYER = {
  text: ['Texto', { type: 'text', text: 'Tu *título* aquí', font: 'title', size: 96, color: BRAND.black, accent: BRAND.coral, align: 'left', lh: 1.05, w: 880, h: 200, animIn: 'rise', animOut: 'fade' }],
  caption: ['Subtítulos', { type: 'caption', text: 'Escribe aquí lo que dice la voz', size: 54, y: 1440, w: 960, h: 110, capStyle: 'pill', maxWords: 4, accent: BRAND.coral, animIn: 'fade' }],
  browser: ['Mockup navegador', { type: 'mockup', kind: 'browser', asset: '', url: 'ursulahr.cl', fit: 'cover', w: 880, h: 600, animIn: 'rise', animOut: 'fade' }],
  phone: ['Mockup celular', { type: 'mockup', kind: 'phone', asset: '', fit: 'cover', w: 420, h: 860, animIn: 'rise', animOut: 'fade' }],
  image: ['Imagen o video', { type: 'image', asset: '', fit: 'cover', radius: 36, shadow: true, w: 700, h: 700, animIn: 'pop', animOut: 'fade' }],
  pill: ['Botón (pill)', { type: 'shape', kind: 'pill', w: 520, h: 120, color: BRAND.black, label: 'Escríbeme', labelColor: BRAND.ivory, arrowIcon: true, arrowColor: BRAND.coral, animIn: 'pop', animOut: 'fade' }],
  halo: ['Halo', { type: 'shape', kind: 'halo', w: 1000, h: 1000, color: BRAND.sky, color2: BRAND.green, animIn: 'fade', animOut: 'fade', animDur: 0.8 }],
  card: ['Tarjeta', { type: 'shape', kind: 'rect', w: 700, h: 160, color: '#FFFFFF', radius: 40, shadow: true, animIn: 'pop', animOut: 'fade' }],
  arrow: ['Flecha', { type: 'shape', kind: 'arrow', w: 90, h: 90, color: BRAND.coral, animIn: 'draw' }],
  sparkle: ['Destello', { type: 'shape', kind: 'sparkle', w: 90, h: 90, color: BRAND.black, animIn: 'pop' }],
  squiggle: ['Línea orgánica', { type: 'shape', kind: 'squiggle', w: 600, h: 60, stroke: 14, animIn: 'draw' }],
  logo: ['Logo HR', { type: 'logo', variant: 'dark', w: 150, h: 100 }],
};

function addLayer(kind) {
  const [name, props] = NEW_LAYER[kind];
  const l = {
    id: uid(), name, start: round(S.t), end: round(Math.min(S.P.duration, S.t + 4)), x: 540, y: 960, w: 400, h: 200, rot: 0, opacity: 1,
    animIn: 'fade', animOut: 'none', animDur: 0.45, ...props,
  };
  if (l.end - l.start < 0.5) l.start = Math.max(0, l.end - 4);
  S.P.layers.push(l); S.sel = l.id; commit(); refreshAll();
}
function addSound(name) {
  const snd = sounds.get(name); if (!snd) return;
  const start = round(S.t);
  const l = { id: uid(), type: 'sound', name: `Sonido · ${name}`, asset: name, volume: 0.35, start, end: round(Math.min(S.P.duration, start + snd.buffer.duration), 2),
    x: 0, y: 0, w: 0, h: 0, rot: 0, opacity: 1, animIn: 'none', animOut: 'none', animDur: 0.45 };
  S.P.layers.push(l); S.sel = l.id; commit(); refreshAll(); previewSound(l);
}
function previewSound(l) {
  const snd = sounds.get(l.asset); if (!snd) return;
  const c = getAC(); if (c.state === 'suspended') c.resume();
  const src = c.createBufferSource(); src.buffer = snd.buffer;
  const g = c.createGain(); g.gain.value = l.volume ?? 0.35; src.connect(g).connect(c.destination); src.start();
}
function stopSounds() { for (const x of liveSrc) { try { x.stop(); } catch { /* ya terminó */ } } liveSrc = []; }
function scheduleSounds(t0) {
  stopSounds();
  const c = getAC(); if (c.state === 'suspended') c.resume();
  const now = c.currentTime;
  for (const l of S.P.layers) {
    if (l.type !== 'sound' || l.hidden) continue;
    const snd = sounds.get(l.asset); if (!snd) continue;
    const end = Math.min(l.end, l.start + snd.buffer.duration);
    if (end <= t0) continue;
    const src = c.createBufferSource(); src.buffer = snd.buffer;
    const g = c.createGain(); g.gain.value = l.volume ?? 0.35; src.connect(g).connect(c.destination);
    const from = Math.max(l.start, t0);
    src.start(now + Math.max(0, l.start - t0), Math.max(0, t0 - l.start), Math.max(0.01, end - from));
    liveSrc.push(src);
  }
}
function dupLayer() {
  const l = sel(); if (!l) return;
  const c = { ...JSON.parse(JSON.stringify(l)), id: uid(), name: l.name + ' copia', x: l.x + 30, y: l.y + 30 };
  S.P.layers.splice(S.P.layers.indexOf(l) + 1, 0, c); S.sel = c.id; commit(); refreshAll();
}
function delLayer() {
  const l = sel(); if (!l) return;
  S.P.layers.splice(S.P.layers.indexOf(l), 1); S.sel = null; commit(); refreshAll();
}
function moveLayer(dir) {
  const l = sel(); if (!l) return;
  const a = S.P.layers, i = a.indexOf(l), j = i + dir;
  if (j < 0 || j >= a.length) return;
  [a[i], a[j]] = [a[j], a[i]]; commit(); refreshAll();
}
function select(id) { S.sel = id; refreshAll(); }

// ---------- render del lienzo ----------
function paint() {
  syncVideos(S.P, S.t, S.playing);
  renderFrame(ctx, S.P, S.t);
  $('#timeLabel').textContent = `${fmt(S.t)} / ${fmt(S.P.duration)}`;
  const ph = $('#playhead'); if (ph) ph.style.left = `${S.t * S.zoom}px`;
}

function fitStage() {
  const a = $('#stageArea');
  const h = Math.min(a.clientHeight - 28, (a.clientWidth - 28) * 16 / 9);
  const w = h * 9 / 16;
  const wrap = $('#stageWrap'); wrap.style.width = `${w}px`; wrap.style.height = `${h}px`;
  S.sc = w / W; updateOverlay();
}
new ResizeObserver(fitStage).observe($('#stageArea'));

// ---------- overlay: selección, mover, redimensionar, rotar ----------
const overlay = $('#overlay');
const safe = el('div', { class: 'safe' }); overlay.append(safe);
let guideEls = [];

function updateOverlay() {
  [...overlay.children].forEach((c) => { if (c !== safe) c.remove(); });
  guideEls = [];
  const sc = S.sc;
  Object.assign(safe.style, { left: `${60 * sc}px`, top: `${250 * sc}px`, width: `${900 * sc}px`, height: `${1250 * sc}px` });
  safe.classList.toggle('on', $('#chkSafe').checked);
  const l = sel(); if (!l || l.type === 'sound') return;
  const b = layerBounds(l);
  const box = el('div', { class: 'sel' });
  Object.assign(box.style, { left: `${(l.x - b.w / 2) * sc}px`, top: `${(l.y - b.h / 2) * sc}px`, width: `${b.w * sc}px`, height: `${b.h * sc}px`, transform: `rotate(${l.rot || 0}deg)` });
  const hs = ['nw', 'ne', 'sw', 'se'];
  if (l.type === 'text') hs.push('e', 'w');
  hs.forEach((h) => box.append(el('div', { class: `h ${h}`, 'data-h': h })));
  box.append(el('div', { class: 'stem' }), el('div', { class: 'h rot', 'data-h': 'rot' }));
  overlay.append(box);
}

function toCanvas(e) {
  const r = cv.getBoundingClientRect();
  return { x: (e.clientX - r.left) / S.sc, y: (e.clientY - r.top) / S.sc };
}
function showGuides(gx, gy) {
  guideEls.forEach((g) => g.remove()); guideEls = [];
  if (gx != null) { const g = el('div', { class: 'guide v' }); g.style.left = `${gx * S.sc}px`; overlay.append(g); guideEls.push(g); }
  if (gy != null) { const g = el('div', { class: 'guide h' }); g.style.top = `${gy * S.sc}px`; overlay.append(g); guideEls.push(g); }
}
function drag(e, onMove) {
  const move = (ev) => onMove(ev);
  const up = () => { window.removeEventListener('pointermove', move); showGuides(); commit(); refreshInspectorValues(); updateOverlay(); };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up, { once: true });
}
function snapAxis(center, half, lines, thr = 10) {
  let best = null;
  for (const [target, edge] of lines) {
    for (const [pos, off] of [[center, 0], [center - half, -half], [center + half, half]]) {
      if (edge === 'c' && off !== 0) continue;
      if (edge === 'l' && off !== -half) continue;
      if (edge === 'r' && off !== half) continue;
      const d = target - pos;
      if (Math.abs(d) < thr && (!best || Math.abs(d) < Math.abs(best.d))) best = { d, line: target };
    }
  }
  return best;
}

overlay.addEventListener('pointerdown', (e) => {
  if (S.exporting) return;
  const p = toCanvas(e);
  const handle = e.target.closest?.('.h');
  const l = sel();
  if (handle && l) {
    const kind = handle.dataset.h; const b0 = layerBounds(l);
    const o = { ...l }; const d0 = Math.hypot(p.x - l.x, p.y - l.y) || 1;
    drag(e, (ev) => {
      const q = toCanvas(ev);
      if (kind === 'rot') {
        let a = Math.atan2(q.y - l.y, q.x - l.x) * 180 / Math.PI + 90;
        if (ev.shiftKey) a = Math.round(a / 15) * 15;
        a = ((a + 180) % 360 + 360) % 360 - 180;
        if (Math.abs(a) < 4) a = 0;
        l.rot = round(a);
      } else if (kind === 'e' || kind === 'w') {
        const ar = (o.rot || 0) * Math.PI / 180;
        const dxl = (q.x - p.x) * Math.cos(ar) + (q.y - p.y) * Math.sin(ar);
        l.w = Math.max(120, Math.round(o.w + (kind === 'e' ? 2 : -2) * dxl));
      } else {
        const f = clamp(Math.hypot(q.x - l.x, q.y - l.y) / d0, 0.1, 12);
        if (l.type === 'text') { l.size = Math.max(8, Math.round(o.size * f)); l.w = Math.round(o.w * f); }
        else if (l.type === 'caption') l.size = Math.max(16, Math.round(o.size * f));
        else { l.w = Math.max(10, Math.round(o.w * f)); l.h = Math.max(10, Math.round(o.h * f)); }
      }
      paint(); updateOverlay(); refreshInspectorValues();
    });
    void b0; return;
  }
  const hit = hitTest(S.P, S.t, p.x, p.y);
  S.sel = hit ? hit.id : null; refreshAll();
  if (!hit) return;
  const o = { x: hit.x, y: hit.y };
  drag(e, (ev) => {
    const q = toCanvas(ev);
    let nx = o.x + (q.x - p.x), ny = o.y + (q.y - p.y);
    let gx = null, gy = null;
    if ($('#chkSnap').checked && !ev.altKey) {
      const b = layerBounds(hit);
      const sx = snapAxis(nx, b.w / 2, [[W / 2, 'c'], [100, 'l'], [W - 100, 'r'], [60, 'l'], [W - 60, 'r']]);
      const sy = snapAxis(ny, b.h / 2, [[H / 2, 'c'], [250, 't'], [1500, 'b']].map(([t, k]) => [t, k === 'c' ? 'c' : k === 't' ? 'l' : 'r']));
      if (sx) { nx += sx.d; gx = sx.line; }
      if (sy) { ny += sy.d; gy = sy.line; }
    }
    hit.x = Math.round(nx); hit.y = Math.round(ny);
    showGuides(gx, gy); paint(); updateOverlay(); refreshInspectorValues();
  });
});

// ---------- capas (lista) ----------
function renderLayerList() {
  const ul = $('#layerList'); ul.innerHTML = '';
  [...S.P.layers].reverse().forEach((l) => {
    const li = el('li', { class: `${l.id === S.sel ? 'sel' : ''} ${l.hidden ? 'off' : ''}`, onclick: () => select(l.id) },
      el('span', { class: 'ty', text: TYPE_ICON[l.type] || '?' }),
      el('span', { class: 'nm', text: l.name || l.type }),
      el('button', { class: `ic ${l.hidden ? '' : 'on'}`, title: 'Mostrar / ocultar', text: l.hidden ? '○' : '●', onclick: (e) => { e.stopPropagation(); l.hidden = !l.hidden; commit(); refreshAll(); } }),
      el('button', { class: `ic ${l.locked ? 'on' : ''}`, title: 'Bloquear (no se selecciona en el lienzo)', text: l.locked ? '▣' : '▢', onclick: (e) => { e.stopPropagation(); l.locked = !l.locked; commit(); refreshAll(); } }));
    ul.append(li);
  });
}

function openMenu(anchor, items) {
  document.querySelectorAll('.menu').forEach((m) => m.remove());
  const r = anchor.getBoundingClientRect();
  const m = el('div', { class: 'menu' });
  items.forEach(([label, fn]) => m.append(el('button', { text: label, onclick: () => { m.remove(); fn(); } })));
  document.body.append(m);
  m.style.left = `${Math.min(r.left, innerWidth - 220)}px`; m.style.top = `${r.bottom + 6}px`;
  setTimeout(() => document.addEventListener('pointerdown', function h(ev) { if (!m.contains(ev.target)) { m.remove(); document.removeEventListener('pointerdown', h); } }), 0);
}
$('#btnSound').onclick = (e) => {
  const items = [...sounds.values()].map((x) => [x.label, () => addSound(x.name)]);
  if (!items.length) { toast('Aún no hay sonidos. Importa uno con "Medios".'); return; }
  openMenu(e.currentTarget, items);
};
$('#btnAdd').onclick = (e) => openMenu(e.currentTarget, [
  ['Texto', () => addLayer('text')], ['Subtítulos', () => addLayer('caption')],
  ['Mockup navegador', () => addLayer('browser')], ['Mockup celular', () => addLayer('phone')],
  ['Imagen o video', () => addLayer('image')], ['Botón (pill)', () => addLayer('pill')],
  ['Tarjeta', () => addLayer('card')], ['Halo', () => addLayer('halo')], ['Flecha', () => addLayer('arrow')],
  ['Destello', () => addLayer('sparkle')], ['Línea orgánica', () => addLayer('squiggle')], ['Logo HR', () => addLayer('logo')],
]);

// ---------- inspector ----------
const OPT_ANIM = [['none', 'Ninguna'], ['fade', 'Aparecer'], ['rise', 'Subir'], ['pop', 'Rebote'], ['blur', 'Desenfoque'], ['slide', 'Deslizar'], ['draw', 'Dibujar']];
const F = (key, label, type, extra = {}) => ({ key, label, type, ...extra });
const MEDIA_FIELDS = [
  F('zoom', 'Zoom', 'number', { step: 0.1, def: () => 1 }),
  F('fx', 'Enfoque X (0 a 1)', 'number', { step: 0.05, def: () => 0.5 }),
  F('fy', 'Enfoque Y (0 a 1)', 'number', { step: 0.05, def: () => 0.5 }),
  F('trim', 'Inicio del clip (s)', 'number', { step: 0.1 }), F('speed', 'Velocidad', 'number', { step: 0.1 }),
];
const SCHEMA = {
  text: [F('text', 'Texto', 'textarea'), F('font', 'Fuente', 'select', { options: [['title', 'Archivo Black'], ['body', 'Lato']] }),
    F('size', 'Tamaño', 'number', { step: 2 }), F('color', 'Color', 'color'), F('accent', 'Acento *palabra*', 'color'),
    F('align', 'Alineación', 'select', { options: [['left', 'Izquierda'], ['center', 'Centro'], ['right', 'Derecha']] }),
    F('lh', 'Interlineado', 'number', { step: 0.05 }), F('tracking', 'Espaciado', 'number', { step: 0.01 }),
    F('caps', 'Mayúsculas', 'checkbox', { def: (l) => l.font !== 'body' }), F('bold', 'Negrita (Lato)', 'checkbox')],
  caption: [F('text', 'Texto de la voz', 'textarea'), F('size', 'Tamaño', 'number', { step: 2 }),
    F('capStyle', 'Estilo', 'select', { options: [['pill', 'Pill negra'], ['plain-light', 'Texto claro'], ['plain-dark', 'Texto oscuro']] }),
    F('maxWords', 'Palabras por frase', 'number', { step: 1 }), F('color', 'Color texto', 'color'), F('accent', 'Palabra activa', 'color')],
  shape: [F('kind', 'Forma', 'select', { options: [['halo', 'Halo'], ['pill', 'Pill'], ['rect', 'Tarjeta / rectángulo'], ['circle', 'Círculo'], ['arrow', 'Flecha'], ['sparkle', 'Destello'], ['squiggle', 'Línea orgánica']] }),
    F('color', 'Color', 'color'), F('color2', 'Color 2', 'color'), F('radius', 'Radio', 'number', { step: 4 }), F('stroke', 'Grosor', 'number', { step: 1 }),
    F('label', 'Texto del botón', 'text'), F('labelColor', 'Color texto', 'color'), F('arrowIcon', 'Flecha en botón', 'checkbox'), F('shadow', 'Sombra', 'checkbox')],
  image: [F('asset', 'Medio', 'asset'), F('fit', 'Ajuste', 'select', { options: [['cover', 'Llenar'], ['contain', 'Contener']] }),
    F('radius', 'Radio', 'number', { step: 4 }), F('shadow', 'Sombra', 'checkbox'), ...MEDIA_FIELDS],
  mockup: [F('kind', 'Dispositivo', 'select', { options: [['browser', 'Navegador'], ['phone', 'Celular']] }), F('asset', 'Medio', 'asset'),
    F('url', 'URL (navegador)', 'text'), F('fit', 'Ajuste', 'select', { options: [['cover', 'Llenar'], ['contain', 'Contener']] }), ...MEDIA_FIELDS],
  logo: [F('variant', 'Versión', 'select', { options: [['dark', 'Negro'], ['light', 'Marfil']] })],
  sound: [F('asset', 'Sonido', 'asset', { sound: true }), F('volume', 'Volumen (0 a 1,5)', 'number', { step: 0.05, def: () => 0.35 })],
};
const SWATCHES = [BRAND.black, BRAND.ivory, BRAND.coral, BRAND.sun, BRAND.green, BRAND.sky, '#FFFFFF'];
let inspInputs = {};

function fieldRow(l, f) {
  const get = () => (l[f.key] !== undefined ? l[f.key] : f.def ? f.def(l) : f.type === 'number' && f.key === 'speed' ? 1 : f.type === 'number' ? 0 : '');
  const set = (v, final) => { l[f.key] = v; paint(); updateOverlay(); if (final) { commit(); refreshLists(); } };
  let input;
  if (f.type === 'textarea') input = el('textarea', { oninput: (e) => { set(e.target.value); }, onchange: () => commit() });
  else if (f.type === 'text') input = el('input', { type: 'text', oninput: (e) => set(e.target.value), onchange: () => commit() });
  else if (f.type === 'number') input = el('input', { type: 'number', step: f.step || 1, oninput: (e) => { if (e.target.value !== '') set(parseFloat(e.target.value)); }, onchange: () => commit() });
  else if (f.type === 'checkbox') { input = el('input', { type: 'checkbox', onchange: (e) => set(e.target.checked, true) }); }
  else if (f.type === 'select') {
    input = el('select', { onchange: (e) => { set(e.target.value, true); if (f.key === 'kind' || f.key === 'font') renderInspector(); } },
      f.options.map(([v, t]) => el('option', { value: v, text: t })));
  } else if (f.type === 'asset') {
    input = el('select', { onchange: (e) => set(e.target.value, true) });
  } else if (f.type === 'color') {
    const wrap = el('div', { class: 'swatches' });
    const cinp = el('input', { type: 'color', oninput: (e) => set(e.target.value), onchange: () => commit() });
    SWATCHES.forEach((c) => wrap.append(el('button', { class: 'sw', style: `background:${c}`, title: c, onclick: () => { set(c, true); sync(); } })));
    wrap.append(cinp);
    const sync = () => { const v = (get() || '').toLowerCase(); [...wrap.querySelectorAll('.sw')].forEach((b, i) => b.classList.toggle('on', SWATCHES[i].toLowerCase() === v)); cinp.value = /^#[0-9a-f]{6}$/i.test(v) ? v : '#000000'; };
    inspInputs[f.key] = { sync: () => sync() }; sync();
    return el('div', { class: 'row' }, el('label', { text: f.label }), wrap);
  }
  inspInputs[f.key] = { input, f, get };
  const row = el('div', { class: 'row' }, el('label', { text: f.label }), input);
  return row;
}

function fillValues() {
  const l = sel(); if (!l) return;
  for (const [key, o] of Object.entries(inspInputs)) {
    if (o.sync) { o.sync(); continue; }
    const { input, f, get } = o;
    if (document.activeElement === input) continue;
    const v = get();
    if (f.type === 'checkbox') input.checked = !!v;
    else if (f.type === 'asset') {
      const reg = f.sound ? sounds : assets;
      const names = [...reg.keys()];
      const cur = l.asset || '';
      if (input.dataset.names !== names.join('|') + '|' + cur) {
        input.innerHTML = '';
        input.append(el('option', { value: '', text: '— ninguno —' }));
        [...new Set([...names, ...(cur ? [cur] : [])])].forEach((n) => input.append(el('option', { value: n, text: reg.has(n) ? (f.sound ? reg.get(n).label : n) : `${n} (falta)` })));
        input.dataset.names = names.join('|') + '|' + cur;
      }
      input.value = cur;
    } else input.value = typeof v === 'number' ? round(v, 3) : v;
  }
}
function refreshInspectorValues() { fillValues(); }

function numField(l, key, label, step = 1, min, max) {
  const input = el('input', { type: 'number', step, ...(min != null ? { min } : {}), ...(max != null ? { max } : {}),
    oninput: (e) => { if (e.target.value === '') return; l[key] = parseFloat(e.target.value); paint(); updateOverlay(); if (key === 'start' || key === 'end') refreshTimeline(); },
    onchange: () => { commit(); } });
  inspInputs[key] = { input, f: { type: 'number' }, get: () => l[key] ?? 0 };
  return el('div', { class: 'row' }, el('label', { text: label }), input);
}

function renderInspector() {
  const box = $('#inspector'); box.innerHTML = ''; inspInputs = {};
  const l = sel();
  if (!l) {
    box.append(el('div', { class: 'empty' }, el('b', { text: 'Nada seleccionado' }), el('br'), 'Haz clic en un elemento del lienzo o en una capa. Arrastra para moverlo, usa las esquinas para el tamaño y el punto de arriba para rotar.'));
    return;
  }
  box.append(el('h4', { text: 'Capa' }));
  const nameIn = el('input', { type: 'text', value: l.name || '', oninput: (e) => { l.name = e.target.value; refreshLists(); }, onchange: () => commit() });
  box.append(el('div', { class: 'row' }, el('label', { text: 'Nombre' }), nameIn));
  const sch = SCHEMA[l.type] || [];
  const visible = sch.filter((f) => {
    if (l.type === 'shape') {
      const k = l.kind;
      if (f.key === 'radius') return k === 'rect';
      if (f.key === 'stroke') return k === 'arrow' || k === 'squiggle';
      if (['label', 'labelColor', 'arrowIcon'].includes(f.key)) return k === 'pill';
      if (f.key === 'color2') return ['halo', 'rect', 'squiggle'].includes(k);
      if (f.key === 'shadow') return ['pill', 'rect'].includes(k);
    }
    if (l.type === 'text' && f.key === 'bold') return l.font === 'body';
    if (l.type === 'mockup' && f.key === 'url') return l.kind === 'browser';
    return true;
  });
  if (visible.length) { box.append(el('h4', { text: 'Contenido' })); visible.forEach((f) => box.append(fieldRow(l, f))); }
  if (l.type === 'text') box.append(el('div', { class: 'hint', text: 'Rodea una palabra con *asteriscos* para pintarla con el color de acento.' }));
  if (l.type === 'caption') box.append(el('div', { class: 'hint', text: 'Las palabras se reparten entre Inicio y Fin según su largo. Ajusta esos tiempos para calzar con la voz.' }));

  if (l.type === 'sound') {
    box.append(el('div', { style: 'margin-top:8px' }, el('button', { class: 'btn small', text: '▶ Probar sonido', onclick: () => previewSound(l) })));
    box.append(el('div', { class: 'hint', text: 'El sonido suena desde "In" y se corta en "Out". Mantén el volumen bajo: la voz tiene que ser lo principal.' }));
    box.append(el('h4', { text: 'Tiempo' }));
    const gs = el('div', { class: 'grid2' }); gs.append(numField(l, 'start', 'In', 0.05), numField(l, 'end', 'Out', 0.05)); box.append(gs);
    box.append(el('h4', { text: 'Acciones' }),
      el('div', { style: 'display:flex;gap:6px;flex-wrap:wrap' }, el('button', { class: 'btn small', text: 'Duplicar', onclick: dupLayer }), el('button', { class: 'btn small', text: 'Eliminar', onclick: delLayer })));
    fillValues();
    return;
  }
  box.append(el('h4', { text: 'Posición y tamaño' }));
  const g = el('div', { class: 'grid2' });
  const compact = (key, label, step) => { const r = numField(l, key, label, step); return r; };
  g.append(compact('x', 'X', 1), compact('y', 'Y', 1));
  if (l.type !== 'text' && l.type !== 'caption') g.append(compact('w', 'W', 1), compact('h', 'H', 1)); else g.append(compact('w', 'W', 1));
  g.append(compact('rot', '°', 1));
  box.append(g);
  box.append(numField(l, 'opacity', 'Opacidad (0 a 1)', 0.05, 0, 1));

  box.append(el('h4', { text: 'Tiempo' }));
  const gt = el('div', { class: 'grid2' });
  gt.append(numField(l, 'start', 'In', 0.1), numField(l, 'end', 'Out', 0.1));
  box.append(gt);

  box.append(el('h4', { text: 'Animación' }));
  const animSel = (key, label) => {
    const s = el('select', { onchange: (e) => { l[key] = e.target.value; commit(); paint(); } }, OPT_ANIM.map(([v, t]) => el('option', { value: v, text: t })));
    s.value = l[key] || 'none';
    return el('div', { class: 'row' }, el('label', { text: label }), s);
  };
  box.append(animSel('animIn', 'Entrada'), animSel('animOut', 'Salida'), numField(l, 'animDur', 'Duración (s)', 0.05, 0.05, 3), numField(l, 'float', 'Flotar (px)', 1, 0, 80));

  box.append(el('h4', { text: 'Acciones' }),
    el('div', { style: 'display:flex;gap:6px;flex-wrap:wrap' },
      el('button', { class: 'btn small', text: 'Duplicar', onclick: dupLayer }), el('button', { class: 'btn small', text: 'Traer adelante', onclick: () => moveLayer(1) }),
      el('button', { class: 'btn small', text: 'Enviar atrás', onclick: () => moveLayer(-1) }), el('button', { class: 'btn small', text: 'Eliminar', onclick: delLayer })));
  fillValues();
}

// ---------- línea de tiempo ----------
let waveCanvas = null;
function refreshTimeline() {
  const sc = $('#tlScroll'); const inner = $('#tlInner');
  const dur = S.P.duration; const pps = S.zoom;
  inner.innerHTML = '';
  inner.style.width = `${Math.max(sc.clientWidth - 2, dur * pps + 60)}px`;
  const ruler = el('div', { class: 'ruler' });
  const step = pps > 80 ? 0.5 : pps < 24 ? 5 : 1;
  for (let s = 0; s <= dur + 0.001; s += step) ruler.append(el('div', { class: 'tick', style: `left:${s * pps}px`, text: Number.isInteger(s) ? `${s}s` : '' }));
  const seekFrom = (e) => { const r = inner.getBoundingClientRect(); seek(clamp((e.clientX - r.left) / pps, 0, dur)); };
  ruler.addEventListener('pointerdown', (e) => { pause(); seekFrom(e); const mv = (ev) => seekFrom(ev); window.addEventListener('pointermove', mv); window.addEventListener('pointerup', () => window.removeEventListener('pointermove', mv), { once: true }); });
  inner.append(ruler);
  const wave = el('div', { class: `wave ${S.audio.buffer ? 'on' : ''}` });
  waveCanvas = el('canvas'); wave.append(waveCanvas); inner.append(wave);
  [...S.P.layers].reverse().forEach((l) => {
    const row = el('div', { class: `trow ${l.id === S.sel ? 'sel' : ''}` });
    const bar = el('div', { class: `bar t-${l.type} ${l.id === S.sel ? 'sel' : ''}`, style: `left:${l.start * pps}px;width:${Math.max(6, (l.end - l.start) * pps)}px`, title: l.name, text: l.name },
      el('span', { class: 'eh l' }), el('span', { class: 'eh r' }));
    bar.addEventListener('pointerdown', (e) => startBar(e, l, bar));
    row.append(bar); inner.append(row);
  });
  inner.append(el('div', { class: 'playhead', id: 'playhead', style: `left:${S.t * pps}px` }));
  requestAnimationFrame(drawWave);
}

function drawWave() {
  const buf = S.audio.buffer; if (!buf || !waveCanvas) return;
  const w = waveCanvas.parentElement.clientWidth || 600; const h = 34;
  const dpr = devicePixelRatio || 1;
  waveCanvas.width = w * dpr; waveCanvas.height = h * dpr;
  const c = waveCanvas.getContext('2d'); c.scale(dpr, dpr); c.clearRect(0, 0, w, h);
  const data = buf.getChannelData(0); const total = buf.duration * S.zoom;
  c.fillStyle = '#34D399';
  for (let x = 0; x < Math.min(w, total); x++) {
    const a = Math.floor((x / total) * data.length), b = Math.floor(((x + 1) / total) * data.length);
    let mx = 0; for (let i = a; i < b; i += Math.max(1, Math.floor((b - a) / 40))) mx = Math.max(mx, Math.abs(data[i]));
    const bh = Math.max(1, mx * (h - 6)); c.fillRect(x, (h - bh) / 2, 1, bh);
  }
}

function startBar(e, l, bar) {
  e.preventDefault();
  S.sel = l.id; refreshAll(false);
  const mode = e.target.classList.contains('l') ? 'l' : e.target.classList.contains('r') ? 'r' : 'm';
  const x0 = e.clientX; const s0 = l.start, e0 = l.end, dur = S.P.duration, pps = S.zoom;
  const edges = [S.t, ...S.P.layers.filter((o) => o !== l).flatMap((o) => [o.start, o.end])];
  const snap = (v, alt) => {
    if (alt) return v;
    let best = round(v, 1); let bd = 0.05;
    for (const ed of edges) if (Math.abs(ed - v) * pps < 8 && Math.abs(ed - v) < bd + 1) { best = ed; bd = -1; break; }
    return best;
  };
  const move = (ev) => {
    const dt = (ev.clientX - x0) / pps;
    if (mode === 'm') { const len = e0 - s0; const ns = clamp(snap(s0 + dt, ev.altKey), 0, dur - len); l.start = round(ns, 2); l.end = round(ns + len, 2); }
    else if (mode === 'l') l.start = round(clamp(snap(s0 + dt, ev.altKey), 0, e0 - 0.1), 2);
    else l.end = round(clamp(snap(e0 + dt, ev.altKey), s0 + 0.1, dur), 2);
    bar.style.left = `${l.start * pps}px`; bar.style.width = `${Math.max(6, (l.end - l.start) * pps)}px`;
    paint(); fillValues();
  };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', () => { window.removeEventListener('pointermove', move); commit(); }, { once: true });
}

// ---------- reproducción ----------
function seek(t) {
  S.t = clamp(t, 0, S.P.duration);
  if (S.audio.buffer) { try { audioEl.currentTime = S.t; } catch { /* aún sin cargar */ } }
  if (S.playing) { S.clock = { base: S.t, start: performance.now() }; scheduleSounds(S.t); }
  paint();
}
function play() {
  if (S.playing) return;
  if (S.t >= S.P.duration - 0.05) S.t = 0;
  S.playing = true; S.clock = { base: S.t, start: performance.now() };
  $('#btnPlay').textContent = '❚❚';
  if (S.audio.buffer) { audioEl.currentTime = S.t; audioEl.play().catch(() => {}); }
  scheduleSounds(S.t);
  requestAnimationFrame(tick);
}
function pause() {
  if (!S.playing) { audioEl.pause(); return; }
  S.playing = false; audioEl.pause(); stopSounds(); $('#btnPlay').textContent = '▶';
  syncVideos(S.P, S.t, false);
}
function tick(now) {
  if (!S.playing) return;
  const t = S.clock.base + (now - S.clock.start) / 1000;
  if (t >= S.P.duration) {
    if ($('#chkLoop').checked) { S.playing = false; S.t = 0; play(); return; }
    pause(); S.t = S.P.duration - 0.001; paint(); return;
  }
  S.t = t;
  if (S.audio.buffer && !audioEl.paused && Math.abs(audioEl.currentTime - t) > 0.2) audioEl.currentTime = t;
  paint(); requestAnimationFrame(tick);
}
$('#btnPlay').onclick = () => (S.playing ? pause() : play());
$('#btnStart').onclick = () => { pause(); seek(0); };
$('#zoom').oninput = (e) => { S.zoom = +e.target.value; refreshTimeline(); };

// ---------- medios y audio ----------
async function importMedia(files, target) {
  let lastName = ''; let audioAdded = '';
  for (const f of files) {
    const url = URL.createObjectURL(f);
    if (f.type.startsWith('image/')) {
      const img = new Image(); img.src = url; await img.decode().catch(() => {});
      assets.set(f.name, { kind: 'image', el: img, name: f.name });
    } else if (f.type.startsWith('video/')) {
      const v = document.createElement('video'); v.muted = true; v.playsInline = true; v.preload = 'auto'; v.src = url;
      await new Promise((res) => { v.addEventListener('loadeddata', res, { once: true }); v.addEventListener('error', res, { once: true }); });
      v.addEventListener('seeked', () => { if (!S.exporting) paint(); });
      assets.set(f.name, { kind: 'video', el: v, name: f.name, duration: v.duration });
    } else if (f.type.startsWith('audio/')) {
      try { const buffer = await decodeSound(await f.arrayBuffer()); sounds.set(f.name, { name: f.name, label: f.name, buffer }); audioAdded = f.name; } catch { toast(`No pude leer ${f.name}`); }
      continue;
    } else continue;
    lastName = f.name;
  }
  if (!lastName && audioAdded) { toast(`Sonido "${audioAdded}" cargado. Agrégalo con el botón ♪ Sonido.`); refreshAll(); return; }
  if (!lastName) { toast('Formato no compatible'); return; }
  const l = target || sel();
  if (l && (l.type === 'image' || l.type === 'mockup')) { l.asset = lastName; commit(); toast(`"${lastName}" asignado a ${l.name}`); }
  else toast(`"${lastName}" cargado. Selecciona un mockup o imagen y elígelo en "Medio", o arrástralo encima.`);
  refreshAll();
}
$('#btnMedia').onclick = () => $('#fileMedia').click();
$('#fileMedia').onchange = (e) => { importMedia([...e.target.files]); e.target.value = ''; };
overlay.addEventListener('dragover', (e) => { e.preventDefault(); overlay.classList.add('drop'); });
overlay.addEventListener('dragleave', () => overlay.classList.remove('drop'));
overlay.addEventListener('drop', (e) => {
  e.preventDefault(); overlay.classList.remove('drop');
  const p = toCanvas(e);
  const hit = S.P.layers.slice().reverse().find((l) => (l.type === 'image' || l.type === 'mockup') && !l.hidden && Math.abs(p.x - l.x) <= l.w / 2 && Math.abs(p.y - l.y) <= l.h / 2);
  importMedia([...e.dataTransfer.files], hit);
});

$('#btnAudio').onclick = () => $('#fileAudio').click();
$('#fileAudio').onchange = async (e) => {
  const f = e.target.files[0]; e.target.value = ''; if (!f) return;
  try {
    pause();
    const ab = await f.arrayBuffer();
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    const buf = await ac.decodeAudioData(ab.slice(0)); ac.close();
    S.audio = { buffer: buf, name: f.name };
    audioEl.src = URL.createObjectURL(f);
    const d = round(buf.duration, 1);
    if (Math.abs(d - S.P.duration) > 0.5 && confirm(`El audio dura ${d} s y el reel ${S.P.duration} s.\n¿Escalar todos los tiempos para que calcen con el audio?\n(Después puedes afinar cada escena en la línea de tiempo.)`)) {
      const k = d / S.P.duration;
      S.P.layers.forEach((l) => { l.start = round(l.start * k, 2); l.end = round(l.end * k, 2); });
      S.P.duration = d; $('#durInput').value = d;
    }
    commit(); refreshAll(); toast(`Audio cargado: ${f.name}`);
  } catch (err) { console.error(err); toast('No pude leer ese audio'); }
};

$('#durInput').onchange = (e) => {
  const d = clamp(parseFloat(e.target.value) || 1, 1, 180);
  S.P.duration = d; e.target.value = d; S.P.layers.forEach((l) => { l.end = Math.min(l.end, d); l.start = Math.min(l.start, d - 0.1); });
  S.t = Math.min(S.t, d); commit(); refreshAll();
};
$('#projName').oninput = (e) => { S.P.name = e.target.value; };
$('#projName').onchange = () => commit();

// guion de voz
$('#btnScript').onclick = () => {
  const ta = el('textarea', { style: 'width:100%;min-height:200px;border:1px solid var(--line);border-radius:10px;padding:10px;font:inherit' });
  ta.value = S.P.voiceover || '';
  const m = $('#exportModal'); const box = m.querySelector('.box');
  const prev = box.innerHTML;
  box.innerHTML = ''; box.append(el('h3', { class: 'title', text: 'Guion de voz' }),
    el('div', { class: 'hint', text: 'Pega esto en tu herramienta de voz (por ejemplo ElevenLabs), descarga el audio y súbelo con "Voz / audio".' }), ta,
    el('div', { class: 'acts' },
      el('button', { class: 'btn', text: 'Copiar', onclick: () => { navigator.clipboard?.writeText(ta.value); toast('Guion copiado'); } }),
      el('button', { class: 'btn primary', text: 'Guardar y cerrar', onclick: () => { S.P.voiceover = ta.value; commit(); m.classList.remove('on'); box.innerHTML = prev; rebindExportModal(); } })));
  m.classList.add('on');
};

// plantillas, abrir y guardar
$('#btnTemplates').onclick = (e) => openMenu(e.currentTarget, [
  ['Reel: Cómo trabajo (proceso)', () => confirm('Esto reemplaza el proyecto actual. ¿Continuar?') && loadTemplate('proceso')],
  ['Reel en blanco', () => confirm('Esto reemplaza el proyecto actual. ¿Continuar?') && loadTemplate('blank')],
]);
$('#btnOpen').onclick = () => $('#fileProject').click();
$('#fileProject').onchange = async (e) => {
  const f = e.target.files[0]; e.target.value = ''; if (!f) return;
  try { const p = JSON.parse(await f.text()); if (!Array.isArray(p.layers)) throw new Error('inválido'); setProject(p); }
  catch { toast('Ese archivo no es un proyecto válido'); }
};
$('#btnSave').onclick = () => {
  const blob = new Blob([JSON.stringify(S.P, null, 2)], { type: 'application/json' });
  const a = el('a', { href: URL.createObjectURL(blob), download: `${(S.P.name || 'reel').replace(/[^\w\-]+/g, '_')}.json` });
  document.body.append(a); a.click(); a.remove(); toast('Proyecto guardado en Descargas');
};

// ---------- exportación ----------
let cancelExport = false;
function rebindExportModal() { const c = $('#expCancel'); if (c) c.onclick = () => { cancelExport = true; }; }
rebindExportModal();

async function mixAudio() {
  const live = S.P.layers.filter((l) => l.type === 'sound' && !l.hidden && sounds.has(l.asset));
  if (!S.audio.buffer && !live.length) return null;
  const sr = S.audio.buffer ? S.audio.buffer.sampleRate : 44100;
  const oc = new OfflineAudioContext(2, Math.ceil(S.P.duration * sr), sr);
  if (S.audio.buffer) { const v = oc.createBufferSource(); v.buffer = S.audio.buffer; v.connect(oc.destination); v.start(0); }
  for (const l of live) {
    const buf = sounds.get(l.asset).buffer;
    const src = oc.createBufferSource(); src.buffer = buf;
    const g = oc.createGain(); g.gain.value = l.volume ?? 0.35; src.connect(g).connect(oc.destination);
    src.start(l.start, 0, Math.max(0.01, Math.min(l.end - l.start, buf.duration)));
  }
  return oc.startRendering();
}

function trimAudio(buf, dur) {
  const frames = Math.min(buf.length, Math.round(dur * buf.sampleRate));
  if (frames === buf.length) return buf;
  const out = new AudioBuffer({ length: frames, numberOfChannels: buf.numberOfChannels, sampleRate: buf.sampleRate });
  for (let c = 0; c < buf.numberOfChannels; c++) out.copyToChannel(buf.getChannelData(c).subarray(0, frames), c);
  return out;
}

async function doExport() {
  if (S.exporting) return;
  pause();
  const missing = S.P.layers.filter((l) => !l.hidden && (l.type === 'image' || l.type === 'mockup') && !assets.has(l.asset)).length;
  if (missing && !confirm(`Hay ${missing} capa(s) sin grabación o imagen: saldrán con rayas.\n¿Exportar igual?`)) return;
  if (!window.VideoEncoder) { alert('Este navegador no puede exportar video. Usa Google Chrome actualizado.'); return; }
  const modal = $('#exportModal'); const box = modal.querySelector('.box');
  box.innerHTML = `<h3 class="title" id="expTitle">Exportando…</h3><div id="expMsg">Preparando</div><div class="progress"><i id="expBar"></i></div><div class="acts" id="expActs"><button class="btn" id="expCancel">Cancelar</button></div>`;
  rebindExportModal(); modal.classList.add('on');
  const msg = (t) => { $('#expMsg').textContent = t; };
  cancelExport = false; S.exporting = true;
  let output = null;
  try {
    await fontsReady();
    const MB = await import('./vendor/mediabunny.min.mjs');
    const cvx = document.createElement('canvas'); cvx.width = W; cvx.height = H;
    const cx = cvx.getContext('2d');
    const codec = await MB.getFirstEncodableVideoCodec(['avc', 'vp9', 'av1'], { width: W, height: H });
    if (!codec) throw new Error('Tu navegador no puede codificar video 1080x1920.');
    const mp4 = codec === 'avc';
    output = new MB.Output({ format: mp4 ? new MB.Mp4OutputFormat() : new MB.WebMOutputFormat(), target: new MB.BufferTarget() });
    const vsrc = new MB.CanvasSource(cvx, { codec, bitrate: MB.QUALITY_HIGH });
    output.addVideoTrack(vsrc, { frameRate: FPS });
    let asrc = null; let audioCodec = '';
    const mix = await mixAudio();
    if (mix) {
      const ac = await MB.getFirstEncodableAudioCodec(mp4 ? ['aac', 'opus'] : ['opus', 'vorbis'], { numberOfChannels: mix.numberOfChannels, sampleRate: mix.sampleRate });
      if (ac) { audioCodec = ac; asrc = new MB.AudioBufferSource({ codec: ac, bitrate: MB.QUALITY_HIGH }); output.addAudioTrack(asrc); }
      else toast('No pude codificar el audio: el video saldrá sin sonido');
    }
    await output.start();
    const audioJob = asrc ? asrc.add(mix) : null;
    const N = Math.ceil(S.P.duration * FPS);
    for (let i = 0; i < N; i++) {
      if (cancelExport) { await output.cancel(); S.exporting = false; modal.classList.remove('on'); toast('Exportación cancelada'); paint(); return; }
      const t = i / FPS;
      await seekVideosExact(S.P, t);
      renderFrame(cx, S.P, t);
      await vsrc.add(t, 1 / FPS);
      if (i % 3 === 0) { $('#expBar').style.width = `${(i / N) * 100}%`; msg(`Cuadro ${i + 1} de ${N}`); await new Promise((r) => setTimeout(r, 0)); }
    }
    vsrc.close();
    if (audioJob) { await audioJob; asrc.close(); }
    msg('Finalizando archivo…');
    await output.finalize();
    const blob = new Blob([output.target.buffer], { type: mp4 ? 'video/mp4' : 'video/webm' });
    const fname = `${(S.P.name || 'reel').replace(/[^\w\-]+/g, '_')}.${mp4 ? 'mp4' : 'webm'}`;
    $('#expBar').style.width = '100%'; $('#expTitle').textContent = 'Listo';
    const warn = mp4 && audioCodec === 'opus' ? ' Ojo: el audio quedó en Opus y Instagram podría rechazarlo. Exporta desde Google Chrome en Mac para obtener AAC.' : '';
    msg(`${(blob.size / 1e6).toFixed(1)} MB · ${mp4 ? 'MP4 (H.264)' : 'WebM (VP9)'}${asrc ? ` con audio (${audioCodec})` : ' sin audio'}.${warn}`);
    const acts = $('#expActs'); acts.innerHTML = '';
    const link = el('a', { class: 'btn primary', href: URL.createObjectURL(blob), download: fname, text: 'Descargar' });
    acts.append(el('button', { class: 'btn', text: 'Cerrar', onclick: () => modal.classList.remove('on') }), link);
    window.__lastExport = { size: blob.size, name: fname, mp4, hasAudio: !!asrc };
    S.exporting = false; paint();
  } catch (err) {
    console.error(err); S.exporting = false;
    $('#expTitle').textContent = 'No se pudo exportar'; msg(String(err.message || err));
    const acts = $('#expActs'); if (acts) { acts.innerHTML = ''; acts.append(el('button', { class: 'btn', text: 'Cerrar', onclick: () => modal.classList.remove('on') })); }
    window.__lastExport = { error: String(err.message || err) };
    try { await output?.cancel(); } catch { /* ya cerrado */ }
  }
}
$('#btnExport').onclick = doExport;

// ---------- teclado ----------
let nudgeTimer;
window.addEventListener('keydown', (e) => {
  const tag = (e.target.tagName || '').toLowerCase();
  if (['input', 'textarea', 'select'].includes(tag)) return;
  const mod = e.metaKey || e.ctrlKey;
  if (e.code === 'Space') { e.preventDefault(); S.playing ? pause() : play(); return; }
  if (e.code === 'Home') { seek(0); return; }
  if (mod && e.key.toLowerCase() === 'z') { e.preventDefault(); restore(e.shiftKey ? S.hi + 1 : S.hi - 1); return; }
  if (mod && e.key.toLowerCase() === 'd') { e.preventDefault(); dupLayer(); return; }
  if (e.key === 'Delete' || e.key === 'Backspace') { e.preventDefault(); delLayer(); return; }
  const l = sel();
  if (l && e.key.startsWith('Arrow')) {
    e.preventDefault(); const n = e.shiftKey ? 10 : 1;
    if (e.key === 'ArrowLeft') l.x -= n; if (e.key === 'ArrowRight') l.x += n; if (e.key === 'ArrowUp') l.y -= n; if (e.key === 'ArrowDown') l.y += n;
    paint(); updateOverlay(); fillValues(); clearTimeout(nudgeTimer); nudgeTimer = setTimeout(commit, 400);
  }
});
$('#chkSafe').onchange = updateOverlay;

// ---------- refrescos ----------
function refreshLists() { renderLayerList(); refreshTimeline(); }
function refreshAll(tl = true) {
  renderLayerList(); renderInspector(); updateOverlay();
  if (tl) refreshTimeline(); else {
    document.querySelectorAll('.trow').forEach((r, i) => { const l = [...S.P.layers].reverse()[i]; r.classList.toggle('sel', l.id === S.sel); r.firstChild.classList.toggle('sel', l.id === S.sel); });
  }
  paint();
}

// ---------- inicio ----------
(async () => {
  await fontsReady();
  fitStage();
  await loadSfxLibrary();
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); } catch { /* ignorar */ }
  if (saved && Array.isArray(saved.layers)) {
    // Si la plantilla del navegador es más antigua que la publicada, ofrecer la nueva.
    const tid = saved.template || (saved.name === 'Reel · Cómo trabajo' ? 'proceso' : null);
    let tpl = null;
    if (tid) { try { const r = await fetch(`projects/${tid}.json`, { cache: 'no-cache' }); if (r.ok) tpl = await r.json(); } catch { /* sin red */ } }
    if (tpl && (tpl.rev || 0) > (saved.rev || 0)
      && confirm(`Hay una versión nueva de la plantilla "${tpl.name}".\n\nAceptar: cargarla. Se conservan las grabaciones que asignaste a los mockups, pero se reemplaza lo demás (vuelve a subir tu audio).\nCancelar: seguir con tu proyecto actual.`)) {
      const byName = new Map(saved.layers.map((x) => [x.name, x]));
      tpl.layers.forEach((x) => {
        const o = (x.type === 'mockup' || x.type === 'image') && byName.get(x.name);
        if (o) ['asset', 'url', 'speed', 'trim', 'zoom', 'fx', 'fy', 'fit'].forEach((k) => { if (o[k] !== undefined) x[k] = o[k]; });
      });
      setProject(tpl);
    } else setProject(saved);
  } else await loadTemplate('proceso');
  fitStage(); refreshAll();
  window.__studio = { S, play, pause, seek, doExport, addLayer, select, assets, importMedia, sounds, addSound };
})();
