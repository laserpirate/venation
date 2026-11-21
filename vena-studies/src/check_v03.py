"""check_v03.py : load a venation-lab page headless, open each tab, count images that loaded, list page errors, screenshot each tab.
usage: python check_v03.py <page.html or http url> <out_prefix>. No em dashes."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
url = sys.argv[1] if sys.argv[1].startswith('http') else Path(sys.argv[1]).resolve().as_uri(); pre = sys.argv[2]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1400, 'height': 1000}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text)); pg.on('requestfailed', lambda r: errs.append('failed ' + r.url[-60:]))
    pg.goto(url); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    rep = dict(version=pg.evaluate('VL.VERSION'), title=pg.title(), stat=pg.evaluate("document.getElementById('stat').innerText")[:200])
    pg.screenshot(path=pre + '_lab.png')
    for k in ('studies', 'lamps'):
        pg.click('.tabs button[data-tab="%s"]' % k)
        pg.evaluate("k => document.querySelectorAll('#tab-' + k + ' img').forEach(i => i.loading = 'eager')", k); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(600)
        r = pg.evaluate("k => { const im = [...document.querySelectorAll('#tab-' + k + ' img')]; return {images: im.length, loaded: im.filter(i => i.complete && i.naturalWidth > 0).length, captions_with_id: [...document.querySelectorAll('#tab-' + k + ' figcaption')].filter(c => /^VS\\d\\d-\\d\\d/.test(c.innerText)).length, lab_hidden: getComputedStyle(document.querySelector('.wrap')).display === 'none', overflow_x: document.documentElement.scrollWidth > innerWidth} }", k)
        rep[k] = r; pg.screenshot(path=pre + '_' + k + '.png')
    rep['errors'] = errs; b.close()
print(json.dumps(rep, indent=1))
