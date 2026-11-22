"""smoke_land_v01.py : first look at land.html in headless Chromium. Loads the page, prints page errors, the relief of the four typologies on
each VS08 pattern beside the VS08 caption value, timings, and saves one screenshot. usage: python smoke_land_v01.py <site_dir> <out.png>. No em dashes."""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
site = Path(sys.argv[1]).resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']); pg = b.new_page(viewport={'width': 1400, 'height': 1000}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto((site / 'land.html').as_uri()); pg.wait_for_timeout(2500)
    print('errors', errs); print('LAND', pg.evaluate('typeof window.LAND'), '3D', pg.evaluate('window.LAND && LAND.has3D()'))
    rows = pg.evaluate('''() => { const out = []; for (const t of VS08) { const t0 = performance.now(); LAND.loadTile(t.id); const f = LAND.field(); out.push([t.id, t.lines[2], f.zmin.toFixed(1) + ' to ' + f.zmax.toFixed(1), f.nl, Math.round(performance.now() - t0)]) } return out }''')
    for r in rows: print(r)
    print('update ms', pg.evaluate('''() => { const t0 = performance.now(); for (let i = 0; i < 5; i++) LAND.set('gain', 1 + i * 0.1); return Math.round((performance.now() - t0) / 5) }'''))
    print('errors', errs)
    pg.evaluate('LAND.loadTile("vena-land-berm--ovate-VS02-04__01")'); pg.wait_for_timeout(600); pg.screenshot(path=sys.argv[2], full_page=True)
    b.close()
