// Renderiza fotogramas (y opcionalmente exporta el MP4) de la plantilla de Neko en Studio con Playwright.
// Uso: node neko_render.js <carpeta_salida> <video.mp4> <audio.wav> "<tiempos json>" [export]
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [out, video, audio, tj, doExport] = process.argv.slice(2); const times = JSON.parse(tj || '[]');
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1500, height: 900 }, acceptDownloads: true }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('dialog', d => d.accept());
  await p.goto('http://localhost:8765/studio/'); await p.waitForTimeout(2000);
  await p.click('#btnTemplates'); await p.locator('.menu button', { hasText: 'Neko Ramen' }).click(); await p.waitForTimeout(1500);
  await p.setInputFiles('#fileMedia', video); await p.waitForTimeout(4000);
  await p.setInputFiles('#fileAudio', audio); await p.waitForTimeout(1500);
  console.log('medios:', JSON.stringify(await p.evaluate(() => [...window.__studio.assets.keys()])));
  await p.evaluate(() => document.fonts.ready);
  for (const t of times) {
    await p.evaluate(t => window.__studio.seek(t), t); await p.waitForTimeout(700);
    fs.writeFileSync(path.join(out, `f_${String(t).replace('.', '_')}.png`), Buffer.from((await p.evaluate(() => document.getElementById('cv').toDataURL('image/png'))).split(',')[1], 'base64'));
  }
  if (doExport) {
    await p.click('#btnExport'); await p.waitForFunction(() => window.__lastExport, null, { timeout: 480000 });
    console.log('export:', JSON.stringify(await p.evaluate(() => window.__lastExport)));
    const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#expActs a')]); await dl.saveAs(path.join(out, 'studio_export.mp4'));
  }
  console.log('errores:', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error('FALLO', e.message); process.exit(1); });
