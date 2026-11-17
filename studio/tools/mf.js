const { chromium } = require('playwright'); const fs = require('fs');
const SP = '/tmp/claude-0/-home-user-ursuhr-github-io/04152018-28c8-58e3-870c-9128478f1773/scratchpad/';
const times = JSON.parse(process.argv[2]); const tag = process.argv[3] || 'mf';
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1500, height: 900 } })).newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('dialog', d => d.accept());
  await p.goto('http://localhost:8765/studio/'); await p.waitForTimeout(2000);
  await p.click('#btnTemplates'); await p.locator('.menu button', { hasText: 'millón' }).click(); await p.waitForTimeout(1800);
  for (const t of times) { await p.evaluate(t => window.__studio.seek(t), t); await p.waitForTimeout(350);
    fs.writeFileSync(SP + `${tag}_${t}.png`, Buffer.from((await p.evaluate(() => document.getElementById('cv').toDataURL('image/png'))).split(',')[1], 'base64')); }
  console.log('errores:', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error('FALLO', e.message); process.exit(1); });
