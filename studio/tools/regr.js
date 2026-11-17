const { chromium } = require('playwright'); const crypto=require('crypto');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('dialog', d => d.accept());
  await p.goto('http://localhost:8765/studio/'); await p.waitForTimeout(2000);
  for (const [n, t] of [['Cómo trabajo', 12], ['a tu nombre', 10], ['200.000', 14], ['millón', 20.5]]) {
    await p.click('#btnTemplates'); await p.locator('.menu button', { hasText: n }).click(); await p.waitForTimeout(1500);
    await p.evaluate(t => window.__studio.seek(t), t); await p.waitForTimeout(500);
    const h = await p.evaluate(() => { const c = document.getElementById('cv'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let nz = 0; for (let i = 0; i < d.length; i += 4000) if (d[i] !== 245) nz++; return [nz, window.__studio.S.P.layers.length, window.__studio.S.P.duration]; });
    console.log(n, JSON.stringify(h));
  }
  console.log('errores:', JSON.stringify(errs)); await b.close();
})();
