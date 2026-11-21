"""Contact sheet render for venation-lab v02b and later. Loads the page, calls VL.sheet (the page's own build and draw),
asserts captions (inside own tile, no overlap, no overflow, 16 px IBM Plex Mono, starts with its study ID), screenshots.
usage: python contact_sheet_v03.py <page.html> <out.png> <title> <sheetId> <specs.json> [--compare <older page.html>]
--compare: the same specs run on the older page (without sheetId); tile canvases are compared by sha1 of their PNG data."""
import sys, json, time, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
page_path, out_png, title, sheet_id = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), sys.argv[3], sys.argv[4]
SPECS = json.loads(Path(sys.argv[5]).read_text(encoding='utf-8'))
cmp_page = Path(sys.argv[sys.argv.index('--compare') + 1]).resolve() if '--compare' in sys.argv else None
def hashes(pg): return [hashlib.sha1(u.encode()).hexdigest()[:12] for u in pg.evaluate("[...document.querySelectorAll('#sheet canvas')].map(c=>c.toDataURL())")]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 2200, 'height': 1400}, device_scale_factor=2)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto(page_path.as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    pg.evaluate('document.fonts.ready')
    t0 = time.time(); stats = pg.evaluate('([s,t,i]) => VL.sheet(s,t,i)', [SPECS, title, sheet_id]); dt = time.time() - t0
    pg.evaluate('document.fonts.ready')
    mono = pg.evaluate('document.fonts.check(\'16px "IBM Plex Mono"\')')
    boxes = pg.evaluate('''() => [...document.querySelectorAll('#sheet .tile')].map((t,i) => { const c = document.getElementById('cap'+i);
        const r = t.getBoundingClientRect(), q = c.getBoundingClientRect(); const fs = parseFloat(getComputedStyle(c).fontSize);
        return {tile:[r.left,r.top,r.right,r.bottom], cap:[q.left,q.top,q.right,q.bottom], fs, text:c.innerText, scrollW:c.scrollWidth, clientW:c.clientWidth} })''')
    fails = []
    for i, bx in enumerate(boxes):
        c = bx['cap']; t = bx['tile']; want = '%s-%02d' % (sheet_id, i + 1)
        if not bx['text'].startswith(want): fails.append(f'cap{i} does not start with {want}')
        if not (c[0] >= t[0]-0.5 and c[2] <= t[2]+0.5 and c[3] <= t[3]+0.5): fails.append(f'cap{i} outside its tile')
        if bx['scrollW'] > bx['clientW'] + 1: fails.append(f'cap{i} text overflows ({bx["scrollW"]}>{bx["clientW"]})')
        if bx['fs'] < 16: fails.append(f'cap{i} font {bx["fs"]}px < 16px (12 pt)')
        for j, ob in enumerate(boxes):
            if j == i: continue
            o = ob['tile']
            if c[0] < o[2] and c[2] > o[0] and c[1] < o[3] and c[3] > o[1]: fails.append(f'cap{i} overlaps tile{j}')
    pg.locator('#sheet').screenshot(path=str(out_png)); h_new = hashes(pg)
    same = None
    if cmp_page:
        pg2 = b.new_page(viewport={'width': 2200, 'height': 1400}, device_scale_factor=2)
        pg2.goto(cmp_page.as_uri()); pg2.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
        pg2.evaluate('([s,t]) => VL.sheet(s,t)', [SPECS, 'cmp']); h_old = hashes(pg2)
        same = [a == c for a, c in zip(h_new, h_old)]
    b.close()
rep = {'png': str(out_png), 'render_s': round(dt, 2), 'plex_mono_loaded': mono, 'page_errors': errs, 'assert_fails': fails,
       'caption_px': sorted({bx['fs'] for bx in boxes}), 'tiles_equal_to_compare_page': same, 'captions': [bx['text'] for bx in boxes], 'stats': stats}
Path(str(out_png)[:-4] + '_check.json').write_text(json.dumps(rep, indent=1), encoding='utf-8')
print(json.dumps({k: rep[k] for k in ('png', 'render_s', 'plex_mono_loaded', 'page_errors', 'assert_fails', 'caption_px', 'tiles_equal_to_compare_page')}))
for c in rep['captions']: print(' |', c.replace('\n', ' / '))
