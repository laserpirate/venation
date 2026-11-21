"""cut_tiles_v01.py : write each tile of a page-drawn study sheet as its own PNG (the same canvas the sheet shows) plus a captions JSON.
usage: python cut_tiles_v01.py <page.html> <sheetId> <specs.json> <out_dir>. No em dashes."""
import sys, json, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
page, sid, specs, out = Path(sys.argv[1]).resolve(), sys.argv[2], json.loads(Path(sys.argv[3]).read_text(encoding='utf-8')), Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 2200, 'height': 1400})
    pg.goto(page.as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    pg.evaluate('([s,t,i]) => { VL.sheet(s,t,i); return 0 }', [specs, sid, sid])
    urls = pg.evaluate("[...document.querySelectorAll('#sheet canvas')].map(c => { const k = document.createElement('canvas'); k.width = c.width; k.height = c.height; const g = k.getContext('2d'); g.fillStyle = '#e9e6df'; g.fillRect(0,0,k.width,k.height); g.drawImage(c,0,0); return k.toDataURL('image/png') })")
    caps = pg.evaluate("[...document.querySelectorAll('#sheet .cap')].map(c => [...c.children].map(d => d.textContent))"); b.close()
tiles = []
for i, (u, c) in enumerate(zip(urls, caps)):
    name = '%s-%02d.png' % (sid, i + 1); (out / name).write_bytes(base64.b64decode(u.split(',', 1)[1])); tiles.append(dict(id=name[:-4], img=name, lines=c))
(out / (sid + '.json')).write_text(json.dumps(tiles, indent=1), encoding='utf-8'); print(sid, len(tiles), 'tiles')
