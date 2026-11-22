"""check_layout_v01.py : stage 1 proof. For the Lab, Land and Lamp pages at 1400 x 900, 1920 x 1080, 1100 x 700 and 400 x 800, run VSHELL.audit()
(every control scrolled into view inside its rail, or inside the page clear of the sticky drawing on narrow screens; the drawing box share in
the viewport with each rail at its last control), capture the viewport in that state, and write a check JSON and a contact sheet.
usage: python check_layout_v01.py <site_dir> <work_dir> <sheet.png>. No em dashes."""
import sys, json, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
import os
FONTS = os.path.join(os.environ.get('WINDIR', ''), 'Fonts', '')   # the system font folder
site = Path(sys.argv[1]).resolve(); work = Path(sys.argv[2]).resolve(); sheet = Path(sys.argv[3]).resolve(); (work / 'cap').mkdir(parents=True, exist_ok=True)
ARGS = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
PAGES = [('lab', 'index.html', 'window.VL && typeof d3!=="undefined" && document.querySelector("#stat span")'), ('land', 'land.html', 'window.LAND && LAND.has3D()'), ('lamp', 'lamp.html', 'window.LAMP && LAMP.has3D()')]
SIZES = [(1400, 900), (1920, 1080), (1100, 700), (400, 800)]
rep = {'runs': []}; caps = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=ARGS)
    for name, f, ready in PAGES:
        for (w, h) in SIZES:
            pg = b.new_page(viewport={'width': w, 'height': h}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
            pg.goto((site / f).as_uri()); pg.wait_for_function(ready, timeout=40000); pg.wait_for_timeout(900)
            pg.evaluate('window.scrollTo(0,0)'); a = pg.evaluate('VSHELL.audit()'); pg.wait_for_timeout(300)
            a['rail2_groups'] = pg.evaluate('Array.from(document.querySelectorAll("#rail2 details.grp")).map(d=>d.id)')
            a['page'] = name; a['errors'] = errs; a['ok'] = (not a['fails']) and all(x['drawingInView'] >= 0.6 for x in a['afterLast']) and a['hscroll'] <= 0 and not errs
            fn = work / 'cap' / ('%s_%dx%d.png' % (name, w, h)); pg.screenshot(path=str(fn)); a['file'] = fn.name
            rep['runs'].append(a); caps.append(a); print(name, w, h, 'controls', a['controls'], 'fails', len(a['fails']), 'inview', [x['drawingInView'] for x in a['afterLast']], 'hscroll', a['hscroll'], 'rail2', len(a['rail2_groups']), 'errors', len(errs), 'OK' if a['ok'] else 'NOT OK')
            pg.close()
    b.close()
rep['all_ok'] = all(r['ok'] for r in rep['runs'])
Path(str(sheet).replace('.png', '_check.json')).write_text(json.dumps(rep, indent=1), encoding='utf-8')
# contact sheet: 3 rows (pages) x 4 columns (sizes), each capture scaled into a 640 x 560 cell with its caption under it
CW, CH, TH = 640, 470, 128; M = 24
try: F = ImageFont.truetype(FONTS + 'consola.ttf', 17); FB = ImageFont.truetype(FONTS + 'consolab.ttf', 22)
except Exception: F = FB = ImageFont.load_default()
W = M + 4 * (CW + M); H = 70 + 3 * (CH + TH + M) + M
im = Image.new('RGB', (W, H), (243, 241, 236)); d = ImageDraw.Draw(im)
d.text((M, 22), 'VS12 · site layout v01 · each page at four sizes, captured with every rail scrolled to its last control · audit by measurement', fill=(29, 28, 26), font=FB)
for i, a in enumerate(caps):
    r, c = divmod(i, 4); x = M + c * (CW + M); y = 70 + r * (CH + TH + M)
    s = Image.open(work / 'cap' / a['file']).convert('RGB'); k = min(CW / s.width, CH / s.height); s = s.resize((max(1, int(s.width * k)), max(1, int(s.height * k))), Image.LANCZOS)
    d.rectangle([x - 1, y - 1, x + CW, y + CH], outline=(201, 197, 187)); im.paste(s, (x + (CW - s.width) // 2, y + (CH - s.height) // 2))
    L = ['%s.html · %d x %d' % ({'lab': 'index', 'land': 'land', 'lamp': 'lamp'}[a['page']], a['w'], a['h']),
         'controls %d · not reachable %d' % (a['controls'], len(a['fails'])),
         'drawing in view at last control: ' + ', '.join('%s %.0f %%' % (x_['rail'], 100 * x_['drawingInView']) for x_ in a['afterLast']),
         'second rail: %s' % (', '.join(g[2:] for g in a['rail2_groups']) or 'none at this width'),
         'sideways scroll %d px · page errors %d · %s' % (max(0, a['hscroll']), len(a['errors']), 'PASS' if a['ok'] else 'FAIL')]
    for j, t in enumerate(L): d.text((x, y + CH + 8 + j * 23), t, fill=(29, 28, 26) if j == 0 else (80, 78, 72), font=F)
im.save(sheet); print('sheet', sheet, im.size, 'all ok', rep['all_ok'])
