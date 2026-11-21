"""Contact sheet render for venation-lab v02: loads the page, calls VL.sheet (the page's own build/draw), measures, screenshots."""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
page_path, out_png = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
title = sys.argv[3]
F, H = 'clubtail-fore', 'clubtail-hind'
SPECS = [
 dict(mode='hybrid', shape=F, preset='p2s120'), dict(mode='hybrid', shape=F, preset='p2s150'), dict(mode='hybrid', shape=F, preset='objet45'), dict(mode='closed', shape='ovate'),
 dict(mode='hybrid', shape=H, preset='p2s120'), dict(mode='hybrid', shape=H, preset='p2s150'), dict(mode='hybrid', shape=H, preset='objet45'), dict(mode='closed', shape='ovate', seed=23),
 dict(mode='open', shape='blob'), dict(mode='closed', shape='blob'), dict(mode='hybrid', shape='blob'), dict(mode='closed', shape='blob', view='ridges'),
 dict(mode='open', shape='disk'), dict(mode='closed', shape='disk'), dict(mode='hybrid', shape='disk'), dict(mode='cells', shape='disk'),
]
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 2200, 'height': 1400}, device_scale_factor=2)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto(page_path.as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    pg.evaluate('document.fonts.ready')
    t0 = time.time(); stats = pg.evaluate('([s,t]) => VL.sheet(s,t)', [SPECS, title]); dt = time.time() - t0
    pg.evaluate('document.fonts.ready')
    mono = pg.evaluate('document.fonts.check(\'16px "IBM Plex Mono"\')')
    boxes = pg.evaluate('''() => [...document.querySelectorAll('#sheet .tile')].map((t,i) => { const c = document.getElementById('cap'+i);
        const r = t.getBoundingClientRect(), q = c.getBoundingClientRect(); const fs = parseFloat(getComputedStyle(c).fontSize);
        return {tile:[r.left,r.top,r.right,r.bottom], cap:[q.left,q.top,q.right,q.bottom], fs, fam:getComputedStyle(c).fontFamily, scrollW:c.scrollWidth, clientW:c.clientWidth} })''')
    fails = []
    for i, bx in enumerate(boxes):
        c = bx['cap']; t = bx['tile']
        if not (c[0] >= t[0]-0.5 and c[2] <= t[2]+0.5 and c[3] <= t[3]+0.5): fails.append(f'cap{i} outside its tile')
        if bx['scrollW'] > bx['clientW'] + 1: fails.append(f'cap{i} text overflows ({bx["scrollW"]}>{bx["clientW"]})')
        if bx['fs'] < 16: fails.append(f'cap{i} font {bx["fs"]}px < 16px (12 pt)')
        for j, ob in enumerate(boxes):
            if j == i: continue
            o = ob['tile']
            if c[0] < o[2] and c[2] > o[0] and c[1] < o[3] and c[3] > o[1]: fails.append(f'cap{i} overlaps tile{j}')
    pg.locator('#sheet').screenshot(path=str(out_png))
    b.close()
print(json.dumps({'png': str(out_png), 'render_s': round(dt, 2), 'plex_mono_loaded': mono, 'page_errors': errs, 'assert_fails': fails,
                  'caption_px': sorted({bx['fs'] for bx in boxes}), 'stats': [s['stat'] for s in stats]}, indent=1))
