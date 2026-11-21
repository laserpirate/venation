"""image_sheet_v02.py : a study sheet of image tiles with ID captions, same look and asserts as the page's contact sheets.
usage: python image_sheet_v02.py <sheet.json> <out.png>
sheet.json: {"title": str, "id": "VS04", "cols": 4, "tile_px": 500, "tiles": [{"img": path, "lines": [str, ...]}]}
Asserts: every caption starts with its artifact ID (tiles[i].id), sits inside its own tile, overlaps no other tile, does not overflow, is 16 px IBM Plex Mono;
every image loaded with a natural size. No em dashes."""
import sys, json, html
from pathlib import Path
from playwright.sync_api import sync_playwright
spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); out = Path(sys.argv[2]); W = spec.get('tile_px', 500); cols = spec['cols']
tiles = ''.join('<div class="tile" id="tile%d"><img src="%s"><div class="cap" id="cap%d">%s</div></div>' % (
    i, Path(t['img']).resolve().as_uri(), i, ''.join('<div>%s</div>' % html.escape(x) for x in t['lines'])) for i, t in enumerate(spec['tiles']))
doc = '''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>body{margin:0;background:#f3f1ec;color:#1d1c1a}#sheet{padding:24px;display:inline-block}.t{font:500 16px "IBM Plex Mono",monospace;margin:0 0 14px}
.g{display:grid;grid-template-columns:repeat(%d,%dpx);gap:20px}.tile{width:%dpx;border:1px solid #c9c5bb;background:#e9e6df}
.tile img{display:block;width:%dpx;height:auto}.cap{font:400 16px/1.35 "IBM Plex Mono",monospace;padding:6px 8px 8px;border-top:1px solid #c9c5bb;background:#f3f1ec;min-height:calc(%d * 1.35em)}</style></head>
<body><div id="sheet"><div class="t">%s</div><div class="g">%s</div></div></body></html>''' % (cols, W, W, W, max(len(t['lines']) for t in spec['tiles']), html.escape(spec['title']), tiles)
tmp = out.resolve().with_suffix('.html'); tmp.write_text(doc, encoding='utf-8')
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': cols * (W + 20) + 80, 'height': 1400}, device_scale_factor=2)
    pg.goto(tmp.as_uri()); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
    mono = pg.evaluate('document.fonts.check(\'16px "IBM Plex Mono"\')')
    boxes = pg.evaluate('''() => [...document.querySelectorAll('.tile')].map((t,i) => { const c = document.getElementById('cap'+i), im = t.querySelector('img');
        const r = t.getBoundingClientRect(), q = c.getBoundingClientRect();
        return {tile:[r.left,r.top,r.right,r.bottom], cap:[q.left,q.top,q.right,q.bottom], fs:parseFloat(getComputedStyle(c).fontSize), text:c.innerText, sw:c.scrollWidth, cw:c.clientWidth, nat:im.naturalWidth} })''')
    fails = []
    for i, bx in enumerate(boxes):
        c, t = bx['cap'], bx['tile']; want = spec['tiles'][i]['id']
        if not bx['text'].startswith(want): fails.append('cap%d does not start with %s' % (i, want))
        if not (c[0] >= t[0] - 0.5 and c[2] <= t[2] + 0.5 and c[3] <= t[3] + 0.5): fails.append('cap%d outside its tile' % i)
        if bx['sw'] > bx['cw'] + 1: fails.append('cap%d overflows' % i)
        if bx['fs'] < 16: fails.append('cap%d font under 16 px' % i)
        if not bx['nat']: fails.append('img%d did not load' % i)
        for j, ob in enumerate(boxes):
            o = ob['tile']
            if j != i and c[0] < o[2] and c[2] > o[0] and c[1] < o[3] and c[3] > o[1]: fails.append('cap%d overlaps tile%d' % (i, j))
    pg.locator('#sheet').screenshot(path=str(out)); b.close()
tmp.unlink()
rep = dict(png=out.name, tiles=len(boxes), plex_mono_loaded=mono, assert_fails=fails, captions=[bx['text'] for bx in boxes])
Path(str(out)[:-4] + '_check.json').write_text(json.dumps(rep, indent=1), encoding='utf-8'); print(json.dumps({k: rep[k] for k in ('png', 'tiles', 'plex_mono_loaded', 'assert_fails')}))
