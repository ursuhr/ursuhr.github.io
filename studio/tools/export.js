const { chromium } = require('playwright');
const SP = '/tmp/claude-0/-home-user-ursuhr-github-io/04152018-28c8-58e3-870c-9128478f1773/scratchpad/';
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1500, height: 900 }, acceptDownloads: true }); const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type()==='error') errs.push(m.text()); });
  p.on('dialog', d => { console.log('DIALOG:', d.message().split('\n')[0].slice(0,70)); d.accept(); });
  await p.goto('http://localhost:8765/studio/'); await p.waitForTimeout(2000);
  await p.click('#btnTemplates'); await p.locator('.menu button', { hasText: "NOMBRE DE LA PLANTILLA" }).click(); await p.waitForTimeout(1800);
  await p.setInputFiles('#fileAudio', SP+'VOZ.mp3'); await p.waitForTimeout(1500);
  await p.click('#btnExport'); await p.waitForFunction(() => window.__lastExport, null, { timeout: 280000 });
  console.log('export:', JSON.stringify(await p.evaluate(() => window.__lastExport)));
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#expActs a')]); await dl.saveAs(SP+'SALIDA.mp4');
  console.log('errores:', JSON.stringify(errs)); await b.close();
})().catch(e => { console.error('FALLO', e.message); process.exit(1); });
