// Motor de render del studio UrsulaHR. Dibuja un proyecto (lista de capas) en un canvas 1080x1920.
export const W = 1080, H = 1920;
export const BRAND = {
  ivory: '#F5F1E8', black: '#0B0B0B', coral: '#FF6BA7',
  sun: '#FFD357', green: '#34D399', sky: '#6EC6FF',
};
export const FONTS = {
  title: '"Archivo Black", "Arial Black", Arial, sans-serif',
  body: '"Lato", Arial, sans-serif',
};

// Medios importados por el usuario: nombre -> { kind: 'image' | 'video', el, name, duration }
export const assets = new Map();

// Logos incluidos
export const logos = {};
for (const [k, src] of [['dark', 'assets/logo-hr.png'], ['light', 'assets/logo-hr-light.png']]) {
  const img = new Image(); img.src = src; logos[k] = img;
}

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const eo = (t) => 1 - Math.pow(1 - t, 3);
const eb = (t) => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };

function rgba(hex, a) {
  const h = (hex || '#000000').replace('#', '');
  const n = parseInt(h.length === 3 ? h.split('').map((c) => c + c).join('') : h, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

export const layerActive = (l, t) => !l.hidden && t >= l.start && t < l.end;

// ---------- animaciones ----------
function anim(l, t) {
  const d = Math.max(0.01, l.animDur ?? 0.45);
  const s = { dx: 0, dy: 0, sc: 1, a: 1, blur: 0, draw: 1 };
  const apply = (kind, p, dir) => {
    if (!kind || kind === 'none' || p >= 1) return;
    const e = eo(p);
    switch (kind) {
      case 'fade': s.a *= p; break;
      case 'rise': s.a *= p; s.dy += dir > 0 ? (1 - e) * 80 : -(1 - e) * 50; break;
      case 'pop': s.sc *= 0.7 + 0.3 * (dir > 0 ? eb(p) : e); s.a *= clamp(p * 2, 0, 1); break;
      case 'blur': s.a *= p; s.blur = Math.max(s.blur, (1 - e) * 30); break;
      case 'slide': s.a *= clamp(p * 2, 0, 1); s.dx += dir > 0 ? (1 - e) * 260 : -(1 - e) * 260; break;
      case 'draw': s.draw = Math.min(s.draw, e); s.a *= clamp(p * 3, 0, 1); break;
      case 'drop': {
        const bo = (x) => { const n1 = 7.5625, d1 = 2.75; if (x < 1 / d1) return n1 * x * x; if (x < 2 / d1) { x -= 1.5 / d1; return n1 * x * x + 0.75; } if (x < 2.5 / d1) { x -= 2.25 / d1; return n1 * x * x + 0.9375; } x -= 2.625 / d1; return n1 * x * x + 0.984375; };
        s.dy += dir > 0 ? -520 * (1 - bo(p)) : -(1 - e) * 60; s.a *= clamp(p * 4, 0, 1); break;
      }
      default: break;
    }
  };
  apply(l.animIn, clamp((t - l.start) / d, 0, 1), 1);
  apply(l.animOut, clamp((l.end - t) / d, 0, 1), -1);
  return s;
}

// ---------- texto ----------
function parseTokens(text) {
  const out = [];
  let ends = true; // el texto anterior terminó en espacio: si no, la palabra siguiente va pegada (p. ej. "*web*?")
  text.split('*').forEach((seg, i) => {
    const accent = i % 2 === 1;
    seg.split('\n').forEach((line, li) => {
      if (li > 0) { out.push({ nl: true }); ends = true; }
      line.split(/\s+/).forEach((w, wi) => {
        if (!w) return;
        out.push({ text: w, accent, glue: wi === 0 && !ends && out.length > 0 && !out[out.length - 1].nl });
      });
      if (line.length) ends = /\s$/.test(line);
    });
  });
  return out;
}

function fontFor(l, size) {
  const body = l.font === 'body';
  return `${body ? (l.bold ? '700' : '400') : '400'} ${size}px ${body ? FONTS.body : FONTS.title}`;
}

function layoutText(ctx, l) {
  const size = l.size || 60;
  ctx.font = fontFor(l, size);
  ctx.letterSpacing = `${(l.tracking || 0) * size}px`;
  const caps = l.caps ?? (l.font !== 'body');
  const toks = parseTokens(caps ? (l.text || '').toUpperCase() : (l.text || ''));
  const space = ctx.measureText(' ').width;
  const lines = [];
  let line = { words: [], w: 0 };
  const push = () => { lines.push(line); line = { words: [], w: 0 }; };
  for (const tk of toks) {
    if (tk.nl) { push(); continue; }
    const w = ctx.measureText(tk.text).width;
    if (line.words.length && !tk.glue && line.w + space + w > l.w) push();
    const sp = line.words.length && !tk.glue ? space : 0;
    line.w += sp + w;
    line.words.push({ ...tk, w, sp });
  }
  push();
  const lh = size * (l.lh || 1.05);
  return { lines, lh, h: lines.length * lh, space, size };
}

const measureCtx = document.createElement('canvas').getContext('2d');

function drawText(ctx, l, t = 0) {
  const { lines, lh, h, space } = layoutText(ctx, l);
  const letters = l.animIn === 'letters'; let ci = 0;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'left';
  const align = l.align || 'left';
  lines.forEach((ln, i) => {
    const y = -h / 2 + (i + 0.5) * lh;
    let x = align === 'center' ? -ln.w / 2 : align === 'right' ? l.w / 2 - ln.w : -l.w / 2;
    for (const wd of ln.words) {
      x += wd.sp;
      ctx.fillStyle = wd.accent ? (l.accent || BRAND.coral) : (l.color || BRAND.black);
      if (letters) {
        // cada letra entra con un pequeño desfase, subiendo y asentándose
        for (let k = 0; k < wd.text.length; k++) {
          const ch = wd.text[k]; const cw = ctx.measureText(ch).width; const cx0 = x + ctx.measureText(wd.text.slice(0, k)).width;
          const q = clamp((t - l.start - ci * (l.stagger || 0.05)) / 0.3, 0, 1); ci++;
          if (q <= 0) continue;
          ctx.save(); ctx.globalAlpha *= q; ctx.translate(cx0 + cw / 2, y + (1 - eo(q)) * 70); const sc = 0.6 + 0.4 * eb(q); ctx.scale(sc, sc);
          ctx.fillText(ch, -cw / 2, 0); ctx.restore();
        }
      } else ctx.fillText(wd.text, x, y);
      x += wd.w;
    }
  });
}

// ---------- formas ----------
function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

function strokeArrow(ctx, s, color, lw) {
  ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath();
  ctx.moveTo(-s / 2, s / 2); ctx.lineTo(s / 2, -s / 2);
  ctx.moveTo(s / 2 - s * 0.55, -s / 2); ctx.lineTo(s / 2, -s / 2); ctx.lineTo(s / 2, -s / 2 + s * 0.55);
  ctx.stroke();
}

function squigglePoints(l, n = 80) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const u = i / n;
    pts.push([-l.w / 2 + u * l.w, Math.sin(u * Math.PI * 4) * (l.h / 2) * (0.6 + 0.4 * Math.sin(u * Math.PI))]);
  }
  return pts;
}

function drawShape(ctx, l, t, st) {
  const color = l.color || BRAND.coral;
  switch (l.kind) {
    case 'halo': {
      const r = l.w / 2;
      ctx.save();
      ctx.scale(1, l.h / l.w);
      const blobs = [[0, 0, color]];
      if (l.color2) blobs.push([r * 0.35, r * 0.2, l.color2]);
      for (const [bx, by, c] of blobs) {
        const g = ctx.createRadialGradient(bx, by, 0, bx, by, r);
        g.addColorStop(0, rgba(c, 0.7));
        g.addColorStop(0.5, rgba(c, 0.28));
        g.addColorStop(1, rgba(c, 0));
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(bx, by, r, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();
      break;
    }
    case 'pill': {
      if (l.shadow) { ctx.shadowColor = 'rgba(0,0,0,.22)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14; }
      ctx.fillStyle = color;
      roundRect(ctx, -l.w / 2, -l.h / 2, l.w, l.h, l.h / 2); ctx.fill();
      ctx.shadowColor = 'transparent';
      if (l.label) {
        const size = l.labelSize || l.h * 0.4;
        ctx.font = `700 ${size}px ${FONTS.body}`;
        ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
        ctx.fillStyle = l.labelColor || BRAND.ivory;
        const off = l.arrowIcon ? -size * 0.6 : 0;
        ctx.fillText(l.label, off, 2);
        if (l.arrowIcon) {
          ctx.save(); ctx.translate(l.w / 2 - l.h * 0.55, 0);
          strokeArrow(ctx, size * 0.7, l.arrowColor || BRAND.coral, size * 0.1);
          ctx.restore();
        }
      }
      break;
    }
    case 'arrow': strokeArrow(ctx, l.w, color, l.stroke || l.w * 0.09); break;
    case 'sparkle': {
      const r = (l.w / 2) * (1 + 0.06 * Math.sin(t * 3 + l.start));
      const k = r * 0.12;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(0, -r); ctx.quadraticCurveTo(k, -k, r, 0); ctx.quadraticCurveTo(k, k, 0, r);
      ctx.quadraticCurveTo(-k, k, -r, 0); ctx.quadraticCurveTo(-k, -k, 0, -r); ctx.fill();
      break;
    }
    case 'squiggle': {
      const pts = squigglePoints(l);
      const upto = Math.max(1, Math.round(pts.length * st.draw));
      const g = ctx.createLinearGradient(-l.w / 2, 0, l.w / 2, 0);
      g.addColorStop(0, BRAND.coral); g.addColorStop(0.35, BRAND.sun);
      g.addColorStop(0.7, BRAND.green); g.addColorStop(1, BRAND.sky);
      ctx.strokeStyle = l.color2 ? color : g;
      ctx.lineWidth = l.stroke || 14; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath();
      pts.slice(0, upto).forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
      break;
    }
    case 'padlock': {
      const k = l.w, bh = k * 0.78, r = k * 0.26;
      ctx.strokeStyle = l.color2 || BRAND.black; ctx.lineWidth = k * 0.1; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-r, -bh / 2 + 6); ctx.lineTo(-r, -bh / 2 - r * 0.5); ctx.arc(0, -bh / 2 - r * 0.5, r, Math.PI, 0); ctx.lineTo(r, -bh / 2 + 6); ctx.stroke();
      ctx.fillStyle = color; roundRect(ctx, -k / 2, -bh / 2, k, bh, k * 0.12); ctx.fill();
      ctx.fillStyle = l.color2 || BRAND.black; ctx.beginPath(); ctx.arc(0, -bh * 0.06, k * 0.075, 0, Math.PI * 2); ctx.fill();
      roundRect(ctx, -k * 0.03, -bh * 0.06, k * 0.06, k * 0.2, k * 0.02); ctx.fill();
      break;
    }
    case 'line': {
      ctx.strokeStyle = color; ctx.lineWidth = l.stroke || 6; ctx.lineCap = 'round';
      if (l.dash) ctx.setLineDash([l.dash, l.dash * 0.9]);
      ctx.beginPath(); ctx.moveTo(-l.w / 2, 0); ctx.lineTo(-l.w / 2 + l.w * st.draw, 0); ctx.stroke(); ctx.setLineDash([]);
      break;
    }
    case 'key': {
      const k = l.w, lw = l.stroke || k * 0.07;
      ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      ctx.beginPath(); ctx.arc(-k * 0.3, 0, k * 0.17, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-k * 0.13, 0); ctx.lineTo(k * 0.42, 0);
      ctx.moveTo(k * 0.26, 0); ctx.lineTo(k * 0.26, k * 0.16); ctx.moveTo(k * 0.42, 0); ctx.lineTo(k * 0.42, k * 0.11); ctx.stroke();
      break;
    }
    case 'circle':
      ctx.fillStyle = color; ctx.beginPath(); ctx.ellipse(0, 0, l.w / 2, l.h / 2, 0, 0, Math.PI * 2); ctx.fill(); break;
    case 'rect':
    default: {
      if (l.shadow) { ctx.shadowColor = 'rgba(0,0,0,.16)'; ctx.shadowBlur = 60; ctx.shadowOffsetY = 20; }
      if (l.color2) {
        const g = ctx.createLinearGradient(0, -l.h / 2, 0, l.h / 2);
        g.addColorStop(0, color); g.addColorStop(1, l.color2); ctx.fillStyle = g;
      } else ctx.fillStyle = color;
      roundRect(ctx, -l.w / 2, -l.h / 2, l.w, l.h, l.radius || 0); ctx.fill();
      ctx.shadowColor = 'transparent';
      break;
    }
  }
}

// ---------- medios ----------
function mediaSize(a) {
  return a.kind === 'video' ? [a.el.videoWidth, a.el.videoHeight] : [a.el.naturalWidth, a.el.naturalHeight];
}

function drawMedia(ctx, a, x, y, w, h, fit, l = {}) {
  if (!a) return false;
  const [iw, ih] = mediaSize(a);
  if (!iw || !ih) return false;
  // zoom acerca el medio; fx/fy (0 a 1) eligen qué parte queda visible (0 izquierda/arriba, 1 derecha/abajo)
  const s = (fit === 'contain' ? Math.min(w / iw, h / ih) : Math.max(w / iw, h / ih)) * (l.zoom || 1);
  const dw = iw * s, dh = ih * s;
  ctx.drawImage(a.el, x + (w - dw) * (l.fx ?? 0.5), y + (h - dh) * (l.fy ?? 0.5), dw, dh);
  return true;
}

function placeholder(ctx, x, y, w, h, label) {
  ctx.fillStyle = '#ECE6D6'; ctx.fillRect(x, y, w, h);
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  ctx.strokeStyle = 'rgba(11,11,11,.07)'; ctx.lineWidth = 18;
  for (let i = -h; i < w + h; i += 56) { ctx.beginPath(); ctx.moveTo(x + i, y + h); ctx.lineTo(x + i + h, y); ctx.stroke(); }
  ctx.restore();
  ctx.fillStyle = 'rgba(11,11,11,.55)';
  ctx.font = `700 ${Math.max(22, Math.min(w, h) * 0.06)}px ${FONTS.body}`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(label || 'Aquí va tu grabación', x + w / 2, y + h / 2);
}

function drawImageLayer(ctx, l) {
  const a = assets.get(l.asset);
  if (l.shadow) { ctx.shadowColor = 'rgba(0,0,0,.18)'; ctx.shadowBlur = 50; ctx.shadowOffsetY = 18; }
  ctx.save();
  roundRect(ctx, -l.w / 2, -l.h / 2, l.w, l.h, l.radius || 0);
  ctx.fillStyle = '#fff'; ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.clip();
  if (!drawMedia(ctx, a, -l.w / 2, -l.h / 2, l.w, l.h, l.fit, l)) placeholder(ctx, -l.w / 2, -l.h / 2, l.w, l.h, l.placeholder);
  ctx.restore();
}

// Página ilustrada para el navegador. Props: wire 'old' | 'new'; buildAt (la página se arma por capas desde ese segundo);
// cursor [[segundo, x, y], ...] con x,y en fracción de la página; clicks [segundos]; menuAt (abre el menú de Ajustes); lockAt (aviso de permisos).
function drawWire(ctx, x, y, w, h, l, t) {
  const nw = l.wire === 'new';
  const b0 = l.buildAt;
  const st = (a, d = 0.35) => (b0 == null ? 1 : clamp((t - b0 - a) / d, 0, 1));
  const clicks = l.clicks || [];
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(x, y, w, h);
  // cabecera: logo, dos enlaces y el botón Ajustes
  const p0 = st(0);
  ctx.save(); ctx.globalAlpha *= p0;
  ctx.fillStyle = nw ? BRAND.black : '#CBD2DC'; roundRect(ctx, x + 32, y + 28, 46, 46, 23); ctx.fill();
  ctx.restore();
  for (let i = 0; i < 2; i++) {
    ctx.save(); ctx.globalAlpha *= st(0.15 + i * 0.12);
    ctx.fillStyle = nw ? 'rgba(11,11,11,.5)' : '#DDE2EA'; roundRect(ctx, x + w - 440 + i * 100, y + 42, 80, 18, 9); ctx.fill(); ctx.restore();
  }
  const bx = x + w - 190, by = y + 28, bw = 150, bh = 46;
  const pressed = clicks.length && clicks.some((c) => t >= c && t < c + 0.14) && (l.menuAt == null || t < l.menuAt + 0.14);
  const active = l.menuAt != null && t >= l.menuAt;
  ctx.save(); ctx.globalAlpha *= st(0.4);
  ctx.translate(bx + bw / 2, by + bh / 2); if (pressed) ctx.scale(0.93, 0.93);
  ctx.fillStyle = active ? '#FFE0EE' : '#FFFFFF'; ctx.strokeStyle = active ? BRAND.coral : '#CBD2DC'; ctx.lineWidth = 3;
  roundRect(ctx, -bw / 2, -bh / 2, bw, bh, 23); ctx.fill(); ctx.stroke();
  ctx.fillStyle = BRAND.black; ctx.font = `700 22px ${FONTS.body}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('Ajustes', 0, 2);
  ctx.restore();
  // héroe: la imagen se revela con un barrido
  const hy = y + 110, hh = h * 0.36;
  const pw = eo(st(0.5, 0.6));
  if (pw > 0) {
    ctx.save(); ctx.beginPath(); ctx.rect(x + 32, hy - 4, (w - 64) * pw, hh + 8); ctx.clip();
    if (nw) { const g = ctx.createLinearGradient(x + 32, hy, x + w - 32, hy + hh); g.addColorStop(0, BRAND.coral); g.addColorStop(0.5, BRAND.sun); g.addColorStop(1, BRAND.green); ctx.fillStyle = g; }
    else ctx.fillStyle = '#E9ECF1';
    roundRect(ctx, x + 32, hy, w - 64, hh, 22); ctx.fill();
    ctx.restore();
  }
  ctx.fillStyle = nw ? BRAND.black : '#C5CCD6';
  ctx.save(); ctx.globalAlpha *= st(1.0); roundRect(ctx, x + 72, hy + hh * 0.26 + (1 - eo(st(1.0))) * 14, w * 0.42, 30, 15); ctx.fill(); ctx.restore();
  ctx.save(); ctx.globalAlpha *= st(1.15); roundRect(ctx, x + 72, hy + hh * 0.26 + 48 + (1 - eo(st(1.15))) * 14, w * 0.3, 30, 15); ctx.fill(); ctx.restore();
  if (nw) { ctx.save(); ctx.globalAlpha *= st(1.3); ctx.fillStyle = BRAND.black; roundRect(ctx, x + 72, hy + hh * 0.26 + 110, 170, 52, 26); ctx.fill(); ctx.restore(); }
  // tarjetas, una tras otra
  const cy = hy + hh + 30, cw = (w - 64 - 48) / 3, ch = Math.max(40, y + h - cy - 24);
  for (let i = 0; i < 3; i++) {
    const pc = st(1.45 + i * 0.15);
    ctx.save(); ctx.globalAlpha *= pc; ctx.translate(0, (1 - eo(pc)) * 26);
    ctx.fillStyle = nw ? ['#FFE0EE', '#FFF1C7', '#D2F5E7'][i] : '#EEF1F5'; roundRect(ctx, x + 32 + i * (cw + 24), cy, cw, ch, 18); ctx.fill();
    ctx.fillStyle = nw ? 'rgba(11,11,11,.45)' : '#CBD2DC'; roundRect(ctx, x + 52 + i * (cw + 24), cy + 22, cw * 0.6, 16, 8); ctx.fill();
    ctx.restore();
  }
  // menú de Ajustes: la última opción está restringida
  if (l.menuAt != null && t >= l.menuAt) {
    const q = eo(clamp((t - l.menuAt) / 0.2, 0, 1));
    const mx = x + w - 340, my = y + 90, mw = 300, rh = 56;
    ctx.save(); ctx.globalAlpha *= q; ctx.translate(mx + mw / 2, my); ctx.scale(1, 0.85 + 0.15 * q); ctx.translate(-(mx + mw / 2), -my);
    ctx.shadowColor = 'rgba(0,0,0,.2)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
    ctx.fillStyle = '#FFFFFF'; roundRect(ctx, mx, my, mw, rh * 3 + 16, 20); ctx.fill(); ctx.shadowColor = 'transparent';
    const flash = l.lockAt != null && t >= l.lockAt - 0.1 && t < l.lockAt + 0.35;
    ['Contenido', 'Diseño', 'Administrador'].forEach((lab, i) => {
      const ry = my + 8 + i * rh;
      if (i === 2 && flash) { ctx.fillStyle = '#FFE0EE'; roundRect(ctx, mx + 8, ry, mw - 16, rh, 14); ctx.fill(); }
      ctx.fillStyle = i === 2 ? 'rgba(11,11,11,.42)' : BRAND.black; ctx.font = `700 24px ${FONTS.body}`; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillText(lab, mx + 28, ry + rh / 2 + 1);
      if (i === 2) { ctx.strokeStyle = 'rgba(11,11,11,.42)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(mx + mw - 44, ry + rh / 2 - 6, 7, Math.PI, 0); ctx.stroke(); ctx.fillStyle = 'rgba(11,11,11,.42)'; roundRect(ctx, mx + mw - 53, ry + rh / 2 - 6, 18, 14, 4); ctx.fill(); }
    });
    ctx.restore();
  }
  // aviso de permisos: el fondo baja de intensidad y la ventana "rebota" al entrar
  if (l.lockAt != null && t >= l.lockAt) {
    const p = clamp((t - l.lockAt) / 0.35, 0, 1);
    ctx.fillStyle = `rgba(11,11,11,${0.42 * p})`; ctx.fillRect(x, y, w, h);
    const mw = Math.min(w - 120, 560), mh = 300;
    ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.scale(0.7 + 0.3 * eb(p), 0.7 + 0.3 * eb(p)); ctx.globalAlpha *= clamp(p * 2, 0, 1);
    ctx.shadowColor = 'rgba(0,0,0,.3)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
    ctx.fillStyle = '#FFFFFF'; roundRect(ctx, -mw / 2, -mh / 2, mw, mh, 28); ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = BRAND.coral; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(0, -72, 26, Math.PI, 0); ctx.lineTo(26, -50); ctx.moveTo(-26, -72); ctx.lineTo(-26, -50); ctx.stroke();
    ctx.fillStyle = BRAND.coral; roundRect(ctx, -42, -52, 84, 66, 14); ctx.fill();
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillStyle = BRAND.black; ctx.font = `700 40px ${FONTS.body}`; ctx.fillText(l.lockTitle || 'Permisos limitados', 0, 56);
    ctx.fillStyle = 'rgba(11,11,11,.55)'; ctx.font = `400 27px ${FONTS.body}`; ctx.fillText(l.lockText || 'Se necesita rol de administrador', 0, 102);
    ctx.restore();
  }
  // cursor: sigue una trayectoria con puntos [segundo, x, y]; cada clic dibuja una onda
  if (l.cursor) {
    let cx, cyy;
    const kf = Array.isArray(l.cursor[0]) ? l.cursor : null;
    if (!kf) { cx = l.cursor[0]; cyy = l.cursor[1]; }
    else if (t >= kf[0][0]) {
      let i = 0; while (i < kf.length - 1 && t >= kf[i + 1][0]) i++;
      if (i === kf.length - 1) { cx = kf[i][1]; cyy = kf[i][2]; }
      else { const a = kf[i], b = kf[i + 1]; const q = clamp((t - a[0]) / (b[0] - a[0]), 0, 1); const e = q * q * (3 - 2 * q); cx = a[1] + (b[1] - a[1]) * e; cyy = a[2] + (b[2] - a[2]) * e; }
    }
    if (cx != null) {
      const px = x + w * cx, py = y + h * cyy;
      for (const c of clicks) if (t >= c && t < c + 0.45) { const q = (t - c) / 0.45; ctx.strokeStyle = `rgba(255,107,167,${0.7 * (1 - q)})`; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(px, py, 10 + 56 * eo(q), 0, Math.PI * 2); ctx.stroke(); }
      const down = clicks.some((c) => t >= c && t < c + 0.12);
      ctx.save(); ctx.translate(px, py); if (down) ctx.scale(0.86, 0.86);
      ctx.fillStyle = BRAND.black; ctx.strokeStyle = '#fff'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 44); ctx.lineTo(12, 34); ctx.lineTo(22, 56); ctx.lineTo(32, 51); ctx.lineTo(22, 31); ctx.lineTo(38, 31); ctx.closePath(); ctx.stroke(); ctx.fill();
      ctx.restore();
    }
  }
}

function drawMockup(ctx, l, t = 0) {
  const a = assets.get(l.asset);
  const { w, h } = l;
  if (l.kind === 'phone') {
    const bez = 16, r = Math.min(w * 0.17, 80);
    ctx.shadowColor = 'rgba(0,0,0,.28)'; ctx.shadowBlur = 70; ctx.shadowOffsetY = 28;
    ctx.fillStyle = '#0B0B0B'; roundRect(ctx, -w / 2, -h / 2, w, h, r); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.save();
    roundRect(ctx, -w / 2 + bez, -h / 2 + bez, w - bez * 2, h - bez * 2, r - bez); ctx.clip();
    if (!drawMedia(ctx, a, -w / 2 + bez, -h / 2 + bez, w - bez * 2, h - bez * 2, l.fit, l)) placeholder(ctx, -w / 2 + bez, -h / 2 + bez, w - bez * 2, h - bez * 2, l.placeholder);
    ctx.restore();
    ctx.fillStyle = '#0B0B0B'; roundRect(ctx, -w * 0.17, -h / 2 + bez + 10, w * 0.34, 30, 15); ctx.fill();
  } else {
    const bar = 64, r = 28;
    ctx.shadowColor = 'rgba(0,0,0,.2)'; ctx.shadowBlur = 70; ctx.shadowOffsetY = 26;
    ctx.fillStyle = '#FFFFFF'; roundRect(ctx, -w / 2, -h / 2, w, h, r); ctx.fill();
    ctx.shadowColor = 'transparent';
    ctx.save();
    roundRect(ctx, -w / 2, -h / 2, w, h, r); ctx.clip();
    ctx.fillStyle = '#EFE9DA'; ctx.fillRect(-w / 2, -h / 2, w, bar);
    [BRAND.coral, BRAND.sun, BRAND.green].forEach((c, i) => {
      ctx.fillStyle = c; ctx.beginPath(); ctx.arc(-w / 2 + 38 + i * 30, -h / 2 + bar / 2, 9, 0, Math.PI * 2); ctx.fill();
    });
    const uw = Math.min(w * 0.55, 520);
    ctx.fillStyle = '#FFFFFF'; roundRect(ctx, -uw / 2 + 30, -h / 2 + 14, uw, bar - 28, (bar - 28) / 2); ctx.fill();
    ctx.fillStyle = 'rgba(11,11,11,.5)'; ctx.font = `400 24px ${FONTS.body}`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(l.url || 'ursulahr.cl', 30, -h / 2 + bar / 2 + 1);
    ctx.save();
    ctx.beginPath(); ctx.rect(-w / 2, -h / 2 + bar, w, h - bar); ctx.clip();
    if (l.wire && !a) drawWire(ctx, -w / 2, -h / 2 + bar, w, h - bar, l, t); // si hay grabación asignada, manda la grabación
    else if (!drawMedia(ctx, a, -w / 2, -h / 2 + bar, w, h - bar, l.fit, l)) placeholder(ctx, -w / 2, -h / 2 + bar, w, h - bar, l.placeholder);
    ctx.restore();
    ctx.restore();
  }
}

// ---------- subtítulos ----------
const chunkCache = new Map();
export function captionChunks(l) {
  const maxW = l.maxWords || 4;
  const key = `${l.text}|${l.start}|${l.end}|${maxW}`;
  if (chunkCache.has(key)) return chunkCache.get(key);
  const words = (l.text || '').trim().split(/\s+/).filter(Boolean);
  const weights = words.map((w) => w.length + 2 + (/[,.;:!?]$/.test(w) ? 4 : 0));
  const total = weights.reduce((a, b) => a + b, 0) || 1;
  const dur = l.end - l.start;
  let acc = 0;
  const timed = words.map((w, i) => {
    const t0 = l.start + (dur * acc) / total; acc += weights[i];
    return { w, t0, t1: l.start + (dur * acc) / total };
  });
  const chunks = [];
  let cur = [];
  timed.forEach((wd, i) => {
    cur.push(wd);
    if (cur.length >= maxW || /[.!?]$/.test(wd.w) || (/,$/.test(wd.w) && cur.length >= 2) || i === timed.length - 1) { chunks.push(cur); cur = []; }
  });
  chunkCache.set(key, chunks);
  return chunks;
}

function drawCaption(ctx, l, t) {
  const chunks = captionChunks(l);
  if (!chunks.length) return;
  let idx = 0;
  chunks.forEach((c, i) => { if (t >= c[0].t0) idx = i; });
  const chunk = chunks[idx];
  let size = l.size || 54;
  ctx.font = `700 ${size}px ${FONTS.body}`;
  const text = chunk.map((c) => c.w).join(' ');
  const full = ctx.measureText(text).width;
  const maxW = l.w - 80;
  if (full > maxW) { size = size * (maxW / full); ctx.font = `700 ${size}px ${FONTS.body}`; }
  const space = ctx.measureText(' ').width;
  const widths = chunk.map((c) => ctx.measureText(c.w).width);
  const totalW = widths.reduce((a, b) => a + b, 0) + space * (chunk.length - 1);
  const style = l.capStyle || 'pill';
  const fg = style === 'plain-dark' ? BRAND.black : BRAND.ivory;
  if (style === 'pill') {
    ctx.fillStyle = rgba(BRAND.black, 0.92);
    const ph = size * 1.9, pw = totalW + size * 1.6;
    roundRect(ctx, -pw / 2, -ph / 2, pw, ph, ph / 2); ctx.fill();
  }
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  let lastShown = -1;
  chunk.forEach((c, i) => { if (t >= c.t0) lastShown = i; });
  let x = -totalW / 2;
  chunk.forEach((c, i) => {
    if (i <= lastShown) {
      const fade = clamp((t - c.t0) / 0.12, 0, 1);
      ctx.globalAlpha *= fade;
      ctx.fillStyle = i === lastShown ? (l.accent || BRAND.coral) : (l.color || fg);
      ctx.fillText(c.w, x, 3);
      ctx.globalAlpha /= (fade || 1);
    }
    x += widths[i] + space;
  });
}

// ---------- capas ----------
const DRAW = {
  text: (ctx, l, t) => drawText(ctx, l, t),
  shape: drawShape,
  image: (ctx, l) => drawImageLayer(ctx, l),
  mockup: (ctx, l, t) => drawMockup(ctx, l, t),
  caption: (ctx, l, t) => drawCaption(ctx, l, t),
  logo: (ctx, l) => {
    const img = logos[l.variant === 'light' ? 'light' : 'dark'];
    if (img && img.complete && img.naturalWidth) ctx.drawImage(img, -l.w / 2, -l.h / 2, l.w, l.h);
  },
};

// Valor de una trayectoria [[segundo, v1, v2...], ...]: antes del primer punto usa `base`, luego interpola suave y se queda en el último.
function kfValue(kf, t, base) {
  if (!kf || !kf.length || t < kf[0][0]) return base;
  let i = 0; while (i < kf.length - 1 && t >= kf[i + 1][0]) i++;
  if (i === kf.length - 1) return kf[i].slice(1);
  const a = kf[i], b = kf[i + 1]; const q = clamp((t - a[0]) / (b[0] - a[0]), 0, 1); const e = q * q * (3 - 2 * q);
  return a.slice(1).map((v, k) => v + (b[k + 1] - v) * e);
}

export function drawLayer(ctx, l, t) {
  const st = anim(l, t);
  const fl = l.float ? Math.sin((t - l.start) * 2) * l.float : 0;
  const [px, py] = l.move ? kfValue(l.move, t, [l.x, l.y]) : [l.x, l.y];
  const ksc = l.scaleKf ? kfValue(l.scaleKf, t, [1])[0] : 1;
  const rec = l.recedeAt != null && t >= l.recedeAt ? eo(clamp((t - l.recedeAt) / 0.55, 0, 1)) : 0; // se aleja al fondo
  const shake = l.shakeAt != null && t >= l.shakeAt ? 16 * Math.sin(70 * (t - l.shakeAt)) * Math.exp(-9 * (t - l.shakeAt)) : 0;
  ctx.save();
  ctx.translate(px + st.dx + shake, py + st.dy + fl - 130 * rec);
  if (l.rot) ctx.rotate((l.rot * Math.PI) / 180);
  if (l.swing && t >= l.swing.t0) { // péndulo que se asienta, girando desde el borde de arriba
    const u = t - l.swing.t0; const pv = (l.h || 0) / 2;
    ctx.translate(0, -pv); ctx.rotate(((l.swing.amp * Math.exp(-u * (l.swing.decay || 2.2)) * Math.sin((2 * Math.PI * u) / (l.swing.period || 0.9))) * Math.PI) / 180); ctx.translate(0, pv);
  }
  const hit = l.hitAt != null && t >= l.hitAt ? 1 + 0.12 * Math.max(0, 1 - (t - l.hitAt) / 0.2) : 1;
  const drift0 = l.drift ? 1 + l.drift * clamp((t - l.start) / Math.max(0.01, l.end - l.start), 0, 1) : 1;
  const sc = st.sc * drift0 * hit * ksc * (1 - 0.18 * rec);
  if (sc !== 1) ctx.scale(sc, sc);
  ctx.globalAlpha = clamp((l.opacity ?? 1) * st.a * (1 - 0.6 * rec), 0, 1);
  if (st.blur > 0.5) ctx.filter = `blur(${st.blur}px)`;
  try { (DRAW[l.type] || (() => {}))(ctx, l, t, st); } finally { ctx.restore(); }
}

export function renderFrame(ctx, project, t) {
  ctx.save();
  ctx.fillStyle = project.background || BRAND.ivory;
  ctx.fillRect(0, 0, W, H);
  for (const l of project.layers) if (layerActive(l, t)) drawLayer(ctx, l, t);
  ctx.restore();
}

// ---------- geometría para el editor ----------
export function layerBounds(l) {
  if (l.type === 'sound') return { w: 0, h: 0 };
  if (l.type === 'text') return { w: l.w, h: layoutText(measureCtx, l).h };
  if (l.type === 'caption') return { w: Math.min(l.w, 900), h: (l.size || 54) * 1.9 };
  return { w: l.w, h: l.h };
}

export function hitTest(project, t, px, py) {
  for (let i = project.layers.length - 1; i >= 0; i--) {
    const l = project.layers[i];
    if (l.locked || l.type === 'sound' || !layerActive(l, t)) continue;
    const b = layerBounds(l);
    const a = -((l.rot || 0) * Math.PI) / 180;
    const dx = px - l.x, dy = py - l.y;
    const lx = dx * Math.cos(a) - dy * Math.sin(a);
    const ly = dx * Math.sin(a) + dy * Math.cos(a);
    if (Math.abs(lx) <= b.w / 2 && Math.abs(ly) <= b.h / 2) return l;
  }
  return null;
}

// ---------- video ----------
export function syncVideos(project, t, playing) {
  for (const l of project.layers) {
    if (!(l.type === 'image' || l.type === 'mockup')) continue;
    const a = assets.get(l.asset);
    if (!a || a.kind !== 'video') continue;
    const el = a.el;
    el.muted = true;
    if (!layerActive(l, t)) { if (!el.paused) el.pause(); continue; }
    const target = (l.trim || 0) + (t - l.start) * (l.speed || 1);
    if (playing) {
      if (Math.abs(el.currentTime - target) > 0.3) el.currentTime = target;
      if (el.paused) el.play().catch(() => {});
    } else {
      if (!el.paused) el.pause();
      if (Math.abs(el.currentTime - target) > 0.03) el.currentTime = target;
    }
  }
}

export async function seekVideosExact(project, t) {
  const jobs = [];
  for (const l of project.layers) {
    if (!(l.type === 'image' || l.type === 'mockup') || !layerActive(l, t)) continue;
    const a = assets.get(l.asset);
    if (!a || a.kind !== 'video') continue;
    const target = Math.min((l.trim || 0) + (t - l.start) * (l.speed || 1), Math.max(0, (a.el.duration || 1e9) - 0.001));
    if (Math.abs(a.el.currentTime - target) < 0.001) continue;
    jobs.push(new Promise((res) => {
      // Si el navegador no avisa que terminó de posicionar el video, seguimos igual en vez de quedar pegados.
      const done = () => { clearTimeout(timer); a.el.removeEventListener('seeked', done); res(); };
      const timer = setTimeout(done, 1500);
      a.el.addEventListener('seeked', done);
      a.el.currentTime = target;
    }));
  }
  await Promise.all(jobs);
}
