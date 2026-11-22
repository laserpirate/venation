"""check_galleries_v01.py : stage 2 proof. Counts the gallery tiles on each page by sheet, which load parameters and which say image only,
clicks one loadable tile per sheet and reads back what loaded, and captures the gallery section of each page.
usage: python check_galleries_v01.py <site_dir> <work_dir>. No em dashes."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
site = Path(sys.argv[1]).resolve(); work = Path(sys.argv[2]).resolve(); work.mkdir(parents=True, exist_ok=True); rep = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader']); pg = b.new_page(viewport={'width': 1400, 'height': 900})
    pg.goto((site / 'index.html').as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=40000)
    rep['lab'] = pg.evaluate('''() => { const o = {}; document.querySelectorAll('#tab-studies h2').forEach(h => { const g = h.nextElementSibling; if (!g || !g.classList.contains('gal')) return;
      const f = Array.from(g.querySelectorAll('figure')); o[h.textContent.split(' ')[0]] = {tiles: f.length, load: f.filter(x => x.classList.contains('load')).length, image_only: f.filter(x => x.textContent.includes('image only')).length} }); return o }''')
    pg.click('#tab-studies figure.load >> nth=20'); pg.wait_for_timeout(500); rep['lab_click'] = pg.evaluate('[VL.params().sid, scrollY]')
    pg.evaluate('document.getElementById("below").scrollIntoView()'); pg.wait_for_timeout(500); pg.screenshot(path=str(work / 'lab_below.png'))
    pg.goto((site / 'lamp.html').as_uri()); pg.wait_for_function('window.LAMP && LAMP.has3D()', timeout=40000)
    rep['lamp'] = pg.evaluate('''() => { const o = {}; document.querySelectorAll('#gals h2').forEach(h => { const g = h.nextElementSibling; if (!g || !g.classList.contains('gal')) return;
      const f = Array.from(g.querySelectorAll('figure')); o[h.textContent.split(' ')[0]] = {tiles: f.length, load: f.filter(x => x.dataset.key).length, image_only: f.filter(x => x.textContent.includes('image only')).length} }); return o }''')
    rep['lamp_galn'] = pg.evaluate('LAMP.GALN'); rep['lamp_params_blocks'] = pg.evaluate('document.querySelectorAll("#gals details").length')
    k = pg.evaluate('document.querySelectorAll("#gals figure[data-key]")[13].dataset.key'); pg.click('#gals figure[data-key="%s"]' % k); pg.wait_for_timeout(800)
    rep['lamp_click'] = [k, pg.evaluate('LAMP.spec().id'), pg.evaluate('LAMP.changed().length')]
    pg.evaluate('document.getElementById("below").scrollIntoView()'); pg.wait_for_timeout(500); pg.screenshot(path=str(work / 'lamp_below.png'))
    pg.goto((site / 'land.html').as_uri()); pg.wait_for_function('window.LAND && LAND.has3D()', timeout=40000)
    rep['land'] = pg.evaluate('({VS08: document.querySelectorAll("#gal figure").length})')
    pg.evaluate('document.getElementById("below").scrollIntoView()'); pg.wait_for_timeout(500); pg.screenshot(path=str(work / 'land_below.png'))
    b.close()
Path(work / 'galleries_check_v01.json').write_text(json.dumps(rep, indent=1), encoding='utf-8'); print(json.dumps(rep))
