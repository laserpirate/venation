"""check_lamp_v01.py : headless proof of lamp.html. Every built lamp loads and exports its stored spec unchanged; six captures (three built
lamps with preview and render side by side, light off, a changed spec with warnings, 400 px); a spec made on the page is written for the builder.
usage: python check_lamp_v01.py <site_dir> <work_dir> <sheet.png> [--trial]. No em dashes."""
import sys, json, time, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
site = Path(sys.argv[1]).resolve(); work = Path(sys.argv[2]).resolve(); sheet = Path(sys.argv[3]).resolve(); (work / 'cap').mkdir(parents=True, exist_ok=True)
rep = {'captures': []}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']); pg = b.new_page(viewport={'width': 1400, 'height': 1060}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto((site / 'lamp.html').as_uri()); pg.wait_for_function('window.LAMP && LAMP.has3D()', timeout=30000); pg.wait_for_timeout(1500)
    def shot(name, cap):
        pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(700); pg.screenshot(path=str(work / 'cap' / (name + '.png'))); rep['captures'].append(dict(file=name + '.png', caption=cap))
    keys = pg.evaluate('LAMP.LAMPS.map(l => l.key)'); rep['lamps'] = len(keys); bad = []; times = []
    for k in keys:
        r = pg.evaluate('''(k) => { const t0 = performance.now(); LAMP.load(k); const l = LAMP.LAMPS.find(l => l.key === k); return {same: JSON.stringify(LAMP.spec()) === JSON.stringify(l.spec), changed: LAMP.changed().length, id: LAMP.newId() === l.spec.id, ms: Math.round(performance.now() - t0), est: LAMP.est(), render: !!l.tile} }''', k)
        times.append(r['ms'])
        if not (r['same'] and r['changed'] == 0 and r['id']): bad.append((k, r))
    rep['load_exact'] = len(keys) - len(bad); rep['load_bad'] = bad; rep['load_ms_max'] = max(times); rep['with_render'] = pg.evaluate('LAMP.LAMPS.filter(l => l.tile).length')
    for i, k in enumerate(('a02', 'b02', 'c08')):
        pg.evaluate('(k) => LAMP.load(k)', k); e = pg.evaluate('LAMP.est()'); idn = pg.evaluate('LAMP.newId()')
        shot('%02d_%s' % (i + 1, k), '%d · %s · preview (stand-in) beside the lit render of the built lamp · cells, estimate %s' % (i + 1, idn, e['cells']))
    pg.evaluate('LAMP.load("c01"); LAMP.set("light", 0)'); shot('04_c01_off', '4 · %s · oblique rim, light off: ribs raised, windows thinner' % pg.evaluate('LAMP.newId()'))
    pg.evaluate('LAMP.load("a02"); LAMP.set("H", 229); LAMP.set("dens", 3); LAMP.set("tech", "T1T2"); LAMP.set("split", 90); LAMP.set("tear", 20); document.getElementById("note").value = "taller, denser, open above 90 mm"')
    rep['changed_spec'] = pg.evaluate('LAMP.spec()'); rep['changed_list'] = pg.evaluate('LAMP.changed()'); rep['chat_text'] = pg.evaluate('LAMP.chatText()'); rep['est_changed'] = pg.evaluate('LAMP.est()')
    (work / 'page_spec_v01.json').write_text(pg.evaluate('LAMP.specFile()'), encoding='utf-8')
    shot('05_changed', '5 · %s · from a02: height 229 mm, density 3x, window below and open above 90 mm, tear 20 mm · changed values marked, warnings in the readouts' % rep['changed_spec']['id'])
    png = pg.evaluate('LAMP.png()'); raw = base64.b64decode(png.split(',')[1]); (work / 'preview.png').write_bytes(raw); rep['preview_png_bytes'] = len(raw)
    pg.evaluate('LAMP.load("b06"); LAMP.set("count", "8"); LAMP.set("form", "cylw"); LAMP.set("W", 110)'); rep['wrap_spec_id'] = pg.evaluate('LAMP.newId()'); (work / 'page_spec_wrap_v01.json').write_text(pg.evaluate('LAMP.specFile()'), encoding='utf-8')
    shot('06_wrap', '6 · %s · from b06: leaf wrap, 8 panels, wide cylinder 110 mm' % rep['wrap_spec_id'])
    rep['warn_oblique_surface'] = pg.evaluate('(() => { LAMP.load("a02"); LAMP.set("rim", "oblique"); return LAMP.est().warnings })()')
    rep['warn_over'] = pg.evaluate('(() => { LAMP.load("a09"); LAMP.set("W", 200); const e = LAMP.est(); return e.warnings })()')
    rep['controls'] = pg.evaluate('[...document.querySelectorAll(".row")].map(r => r.id)'); rep['page_errors'] = list(errs)
    rep['storage_calls'] = [k for k in ('localStorage', 'sessionStorage', 'document.cookie') if k in (site / 'lamp.html').read_text(encoding='utf-8')]
    for wd in (400, 1400):
        p3 = b.new_page(viewport={'width': wd, 'height': 900}); p3.goto((site / 'lamp.html').as_uri()); p3.wait_for_function('window.LAMP && LAMP.est()', timeout=30000); p3.wait_for_timeout(900)
        rep['width_%d' % wd] = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]'); p3.screenshot(path=str(work / 'cap' / ('width_%d.png' % wd)), full_page=(wd == 400)); p3.close()
    caps = rep['captures']; tiles = ''.join('<figure><img src="%s"><figcaption>%s</figcaption></figure>' % ((work / 'cap' / c['file']).as_uri(), c['caption']) for c in caps)
    title = 'VS10 · %s · site: Lamp page v01 · %d captures of the page in headless Chromium · previews are stand-ins, not print meshes' % (sheet.stem.replace('VS10_', ''), len(caps))
    html = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"><style>body{margin:0;padding:28px;background:#f3f1ec;color:#1d1c1a;font:400 19px/1.35 "IBM Plex Mono",monospace}h1{font:500 22px "IBM Plex Mono",monospace;margin:0 0 18px}.g{display:grid;grid-template-columns:repeat(3,1000px);gap:22px}figure{margin:0;border:1px solid #c9c5bb;background:#e9e6df}img{display:block;width:1000px;height:757px;object-fit:cover;object-position:top}figcaption{padding:8px 10px 10px;min-height:86px;border-top:1px solid #c9c5bb;background:#f3f1ec}</style><h1>%s</h1><div class="g">%s</div>' % (title, tiles)
    (work / 'sheet.html').write_text(html, encoding='utf-8'); p5 = b.new_page(viewport={'width': 3100, 'height': 1000}); p5.goto((work / 'sheet.html').as_uri()); p5.wait_for_load_state('networkidle'); p5.wait_for_timeout(800); p5.screenshot(path=str(sheet), full_page=True); p5.close(); b.close()
rep['sheet'] = sheet.name; rep['built'] = time.strftime('%Y-%m-%d %H:%M')
Path(str(sheet)[:-4] + '_check.json').write_text(json.dumps(rep, indent=1), encoding='utf-8')
for k in ('warn_oblique_surface', 'lamps', 'with_render', 'load_exact', 'load_ms_max', 'changed_list', 'chat_text', 'est_changed', 'wrap_spec_id', 'warn_over', 'preview_png_bytes', 'width_400', 'width_1400', 'storage_calls', 'page_errors'): print(k, json.dumps(rep.get(k), ensure_ascii=True)[:600])
print('bad', rep['load_bad'][:2]); print('changed spec', json.dumps(rep['changed_spec'])[:700])
