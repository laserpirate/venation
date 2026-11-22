"""check_land_v02.py : headless proof of land.html v02. Fifteen captures of the page itself (the eight of the prompt, the two of ADD-1 as three,
the four of ADD-2: six fills in one form, four profiles, the slope map with its band readout, cut and fill before and after Balance), the exports
saved and reloaded (16 bit PNG with PIL, STL with trimesh, SVG parsed), the file ground round trip, changed marks, width checks at 400 and 1400 px.
Writes captures and exports under <work>, the check JSON, and the contact sheet PNG. usage: python check_land_v01.py <site_dir> <work_dir> <sheet.png>
No em dashes."""
import sys, json, base64, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright
site = Path(sys.argv[1]).resolve(); work = Path(sys.argv[2]).resolve(); sheet = Path(sys.argv[3]).resolve(); (work / 'cap').mkdir(parents=True, exist_ok=True); (work / 'exports').mkdir(exist_ok=True)
rep = {'captures': []}; ARGS = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
B64 = '''async (b) => { const u = new Uint8Array(await b.arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return btoa(s) }'''


def shot(pg, name, cap, full=False, clip=None):
    pg.wait_for_timeout(450); f = work / 'cap' / (name + '.png')
    if clip: pg.screenshot(path=str(f), full_page=True, clip=clip)
    else: pg.screenshot(path=str(f), full_page=full)
    rep['captures'].append(dict(file=f.name, caption=cap, page_caption=pg.evaluate('LAND.capLines()')))


with sync_playwright() as pw:
    b = pw.chromium.launch(args=ARGS); pg = b.new_page(viewport={'width': 1400, 'height': 1060}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto((site / 'land.html').as_uri()); pg.wait_for_function('window.LAND && LAND.has3D()', timeout=30000); pg.wait_for_timeout(1200)
    rep['fonts'] = pg.evaluate('document.fonts.check("12px \\"IBM Plex Mono\\"") && document.fonts.check("12px \\"IBM Plex Sans\\"")')
    # 1 to 4: four typologies on one study
    for i, (t, nm) in enumerate((('berm', 'berm'), ('wave', 'waveform mounds'), ('pond', 'pond cells'), ('terr', 'terraces'))):
        pg.evaluate('(t) => LAND.loadTile("vena-land-" + t + "--ovate-VS02-04__01")', t); pg.evaluate('window.scrollTo(0,0)')
        f = pg.evaluate('(() => { const f = LAND.field(); return [f.zmin, f.zmax, f.nl] })()')
        shot(pg, '%02d_%s' % (i + 1, t), '%d · %s on ovate-VS02-04 · relief %.1f to %.1f mm' % (i + 1, nm, f[0], f[1]))
    # 5: river bank ground, water up
    pg.evaluate('''() => { LAND.loadTile("vena-land-berm--ovate-VS02-04__01"); LAND.set("ground", "bank"); LAND.set("blend", 0.55); LAND.set("grel", 24); LAND.set("wl", 9); document.getElementById("g_Ground").open = true; document.getElementById("g_Water").open = true; document.getElementById("g_Fillrelief").open = false; window.scrollTo(0,0) }''')
    w = pg.evaluate('(() => { const w = LAND.water(); return [w.area, w.vol] })()'); rep['water_bank'] = w
    shot(pg, '05_bank_water', '5 · berm on the river bank ground, blend 0.55, water level 9 mm · wet %.0f mm2 · stored %.0f mm3' % (w[0], w[1]))
    # 6: rain
    pg.evaluate('''() => { LAND.loadTile("vena-land-pond--ovate-VS02-04__01"); LAND.set("pnotch", 1); LAND.set("rain", 1); LAND.view("plan"); document.getElementById("g_Water").open = true; window.scrollTo(0,0) }''')
    fl = pg.evaluate('(() => { const f = LAND.flow(); return {basins: f.basins.length, all: f.all, segs: f.wd.length, notches: LAND.field().notches.length, top: f.basins.slice(0, 3).map(b => [b.level, b.area, b.vol, b.spill >= 0])} })()'); rep['rain_pond_notch'] = fl
    pg.evaluate('LAND.set("pnotch", 0)'); fl0 = pg.evaluate('(() => { const f = LAND.flow(); return {basins: f.basins.length, all: f.all} })()'); rep['rain_pond_no_notch'] = fl0; pg.evaluate('LAND.set("pnotch", 1)')
    shot(pg, '06_rain', '6 · rain on pond cells with spill notches · %d closed basins (%d without notches) · %d flow segments' % (fl['basins'], fl0['basins'], fl['segs']))
    # 7: section
    pg.evaluate('''() => { LAND.loadTile("vena-land-terr--ovate-VS02-04__01"); LAND.set("wl", 8); LAND.setSection([0.05, 0.2], [0.95, 0.8]); LAND.view("axa"); document.getElementById("sec").scrollIntoView({block: "center"}) }''')
    shot(pg, '07_section', '7 · section A to B dragged across terraces, water level 8 mm drawn on the profile, exaggeration stated')
    # exports from this state (terraces, water, section) plus rain
    pg.evaluate('LAND.set("rain", 1)')
    E = work / 'exports'; stem = pg.evaluate('LAND.stem()'); rep['stem'] = stem
    top = pg.evaluate('LAND.topOf()'); png = base64.b64decode(pg.evaluate('async () => { const f = %s; return await f(await LAND.png16(LAND.field(), LAND.topOf())) }' % B64)); (E / (stem + '_height16.png')).write_bytes(png)
    (E / (stem + '_height16.json')).write_text(json.dumps(pg.evaluate('LAND.sidecar(LAND.topOf())'), indent=1), encoding='utf-8')
    svg = pg.evaluate('LAND.sheetSVG()'); (E / (stem + '_contours.svg')).write_text(svg, encoding='utf-8'); sec = pg.evaluate('LAND.sectionSVG()'); (E / (stem + '_section.svg')).write_text(sec, encoding='utf-8')
    stl = base64.b64decode(pg.evaluate('async () => { const f = %s; return await f(LAND.stlBlob().blob) }' % B64)); (E / (stem + '_b3mm.stl')).write_bytes(stl)
    (E / (stem + '_graph.json')).write_text(pg.evaluate('LAND.graphJSON()'), encoding='utf-8'); (E / (stem + '_params.json')).write_text(json.dumps(pg.evaluate('LAND.paramJSON()'), indent=1), encoding='utf-8')
    zstat = pg.evaluate('(() => { const f = LAND.field(); return [f.zmin, f.zmax, f.z[0], f.z[128 * 256 + 128]] })()')
    from PIL import Image
    import numpy as np
    im = Image.open(E / (stem + '_height16.png')); a = np.asarray(im).astype(float) / 65535 * top
    rep['png16'] = dict(mode=im.mode, size=im.size, reload_min=round(float(a.min()), 3), reload_max=round(float(a.max()), 3), page_min=round(zstat[0], 3), page_max=round(zstat[1], 3), centre_reload=round(float(a[128, 128]), 3), centre_page=round(zstat[3], 3), bytes=len(png))
    import trimesh
    m = trimesh.load(E / (stem + '_b3mm.stl')); rep['stl'] = dict(bytes=len(stl), tris=int(len(m.faces)), watertight=bool(m.is_watertight), winding=bool(m.is_winding_consistent), volume_mm3=round(float(m.volume), 1), extents=[round(float(x), 2) for x in m.extents], bodies=int(len(m.split(only_watertight=False))))
    import xml.etree.ElementTree as ET
    def svginfo(s):
        r = ET.fromstring(s); ns = '{http://www.w3.org/2000/svg}'; ids = [g.get('id') for g in r.iter(ns + 'g') if g.get('id')]; fs = [float(t.get('font-size') or 0) for t in r.iter(ns + 'text')] + [float(g.get('font-size')) for g in r.iter(ns + 'g') if g.get('font-size')]
        return dict(width=r.get('width'), height=r.get('height'), layers=ids, counts={i: len(list(g)) for g in r.iter(ns + 'g') for i in [g.get('id')] if i}, texts=len(list(r.iter(ns + 'text'))), least_font_pt=round(min([x for x in fs if x > 0]) / 25.4 * 72, 2))
    rep['svg_contours'] = svginfo(svg); rep['svg_section'] = svginfo(sec)
    # 8: one export opened
    p2 = b.new_page(viewport={'width': 1100, 'height': 1250}); p2.goto((E / (stem + '_contours.svg')).as_uri()); p2.wait_for_timeout(500); p2.screenshot(path=str(work / 'cap' / '08_export.png')); p2.close()
    rep['captures'].append(dict(file='08_export.png', caption='8 · export opened: contour SVG in layers, with caption and key (terraces, water line, flow lines, section line)', page_caption=None))
    # file ground: the exported PNG read back by the page's own reader, and an Esri grid
    rt = pg.evaluate('''async () => { const top = LAND.topOf(); const z = LAND.field().z.slice(); const blob = await LAND.png16(LAND.field(), top); const G = await LAND.readPNG(await blob.arrayBuffer()); let md = 0; for (let i = 0; i < z.length; i++) md = Math.max(md, Math.abs(G.data[i] / 65535 * top - z[i]));
        let asc = 'ncols 5\\nnrows 4\\nxllcorner 0\\nyllcorner 0\\ncellsize 25\\nNODATA_value -9999\\n'; for (let j = 0; j < 4; j++) { for (let i = 0; i < 5; i++) asc += (10 + i * 2 + j) + ' '; asc += '\\n' } const A = LAND.readASC(asc);
        LAND.useGrid(A, 'file'); return {png_kind: G.kind, png_size: [G.w, G.h], png_max_abs_diff_mm: md, asc: [A.w, A.h, A.cell, A.data[0], A.data[19]], state: document.getElementById('fstate').textContent, ground: LAND.V.ground, fw: document.getElementById('fw').value, zr: [document.getElementById('fz0').value, document.getElementById('fz1').value]} }''')
    rep['file_ground'] = rt
    # 9: cell count least and greatest (a cells pattern: the count drives it)
    for k, v in (('a', 40), ('b', 2000)):
        pg.evaluate('''(v) => { LAND.loadTile("vena-land-wave--cells-VS02-16__01"); LAND.set("ncell", v); LAND.view("orbit"); document.getElementById("g_Fillrelief").open = false; window.scrollTo(0,0) }''', v)
        f = pg.evaluate('(() => { const f = LAND.field(); return [f.zmin, f.zmax, f.nl] })()')
        shot(pg, '09%s_cells_%d' % (k, v), '9%s · cell count %d (%s) on waveform mounds, cells-VS02-16 · %d mounds · relief %.1f to %.1f mm' % (k, v, 'least' if v == 40 else 'greatest', f[2], f[0], f[1]))
    # 10: relief gain and vertical exaggeration changed, caption visible
    pg.evaluate('''() => { LAND.loadTile("vena-land-berm--blob-VS02-10__01"); LAND.set("gain", 0.5); LAND.set("ve", 3); LAND.set("scaleN", 500); document.getElementById("g_Scale").open = true; document.getElementById("cap").scrollIntoView({block: "end"}); window.scrollBy(0, 230) }''')
    rep['changed_gain_ve'] = pg.evaluate('LAND.changed()'); rep['chat_text'] = pg.evaluate('LAND.chatText()'); rep['readout_rows'] = pg.evaluate('[...document.querySelectorAll("#read tr")].map(r => [...r.children].map(c => c.textContent))')
    rep['marked_rows'] = pg.evaluate('[...document.querySelectorAll(".row.chg")].map(r => r.id + ": " + r.querySelector(".was").textContent)')
    shot(pg, '10_gain_ve', '10 · relief gain 1 to 0.5, vertical exaggeration 3x, scale 1:500 on berm, blob-VS02-10 · caption and ground readouts visible')

    # ---- ADD-2 captures. Composed tiles are made of the page's own canvases and element screenshots.
    def compose(name, cap, cells, cols, cw, ch):
        h = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"><style>body{margin:0;background:#f3f1ec;font:500 17px "IBM Plex Mono",monospace;color:#1d1c1a}.g{display:grid;grid-template-columns:repeat(%d,%dpx);gap:6px;padding:6px}figure{margin:0;background:#07090e}img{display:block;width:%dpx;height:%dpx;object-fit:contain;object-position:top left;background:#07090e}figcaption{background:#f3f1ec;padding:3px 4px}</style><div class="g">%s</div>' % (cols, cw, cw, ch, ''.join('<figure><img src="%s"><figcaption>%s</figcaption></figure>' % c for c in cells))
        (work / (name + '.html')).write_text(h, encoding='utf-8'); q = b.new_page(viewport={'width': cols * (cw + 6) + 6, 'height': 400}); q.goto((work / (name + '.html')).as_uri()); q.wait_for_load_state('networkidle'); q.wait_for_timeout(500); q.screenshot(path=str(work / 'cap' / (name + '.png')), full_page=True); q.close()
        rep['captures'].append(dict(file=name + '.png', caption=cap, page_caption=None, fit='contain'))
    # 11: one form, six fills
    pg.evaluate("""() => { LAND.loadTile("vena-land-berm--ovate-VS02-04__01"); LAND.set("form", "square"); LAND.set("fw", 84); LAND.set("fl", 84); LAND.set("frad", 12); LAND.set("fit", 150); LAND.set("shape", "disk"); LAND.set("bhmax", 8); LAND.set("bhmin", 2) }""")
    cells6 = []; rep['fills'] = {}
    for m, nm in (('open', 'venation, open'), ('closed', 'venation, closed'), ('xylem', 'xylem'), ('cells', 'Voronoi cells'), ('radiolaria', 'radiolaria'), ('delaunay', 'Delaunay')):
        pg.evaluate('(m) => LAND.set("mode", m)', m); pg.wait_for_timeout(150); st = pg.evaluate('(() => { const f = LAND.field(); return [f.segT.length, f.zmin, f.zmax, LAND.artId()] })()'); rep['fills'][m] = st
        cells6.append((pg.evaluate('LAND.planPNG()'), '%s · %d edges' % (nm, st[0])))
    compose('11_six_fills', '11 · one form (square, rounded corners), six fills, edges as ridges: venation open and closed, xylem, Voronoi cells, radiolaria, Delaunay', cells6, 3, 440, 440)
    # 12: four profiles, one fill each
    cells4 = []; rep['profiles'] = {}
    for prof, form, mode, typ, nm in (('berm', 'rectangle', 'xylem', 'berm', 'berm profile · xylem as ridges'), ('mound', 'oval', 'cells', 'wave', 'mound profile · Voronoi cells as mounds'), ('terrace', 'rectangle', 'delaunay', 'berm', 'terrace profile · Delaunay as ridges'), ('pond', 'circle', 'radiolaria', 'pond', 'pond profile · radiolaria as basins')):
        pg.evaluate("""([prof, form, mode, typ]) => { LAND.loadTile("vena-land-berm--ovate-VS02-04__01"); LAND.set("form", form); LAND.set("fw", prof === "berm" ? 46 : 80); LAND.set("fl", 86); LAND.set("frot", prof === "berm" ? 35 : 0); LAND.set("fit", 150); LAND.set("shape", "disk"); LAND.set("prof", prof); LAND.set("typ", typ); LAND.set("gain", 0.3); LAND.set("fall", 0.3); LAND.set("lo", 6); LAND.set("mode", mode); LAND.view("orbit") }""", [prof, form, mode, typ]); pg.wait_for_timeout(300)
        rep['profiles'][prof] = pg.evaluate('(() => { const f = LAND.field(); return {relief: [f.zmin, f.zmax], pinfo: f.pinfo, cut: f.cut, fill: f.fill, id: LAND.artId()} })()'); cells4.append((pg.evaluate('LAND.view3PNG()'), nm))
    compose('12_four_profiles', '12 · four landform profiles, each with one fill: berm, mound, terrace, pond (relief gain 0.3, fall-off 0.3)', cells4, 2, 660, 500)
    # 13: slope map with the band readout
    pg.evaluate("""() => { LAND.loadTile("vena-land-berm--ovate-VS02-04__01"); LAND.set("form", "oval"); LAND.set("fw", 70); LAND.set("fl", 88); LAND.set("fit", 150); LAND.set("shape", "disk"); LAND.set("prof", "mound"); LAND.set("mh", 6); LAND.set("mode", "xylem"); LAND.set("gain", 0.12); LAND.set("smo", 3); LAND.set("scaleN", 200); LAND.set("ve", 1); LAND.set("map", "slope"); LAND.spot(0.5, 0.5); LAND.spot(0.3, 0.62); LAND.setSection([0.1, 0.5], [0.9, 0.5]); document.getElementById("g_Grading").open = true }""")
    pg.wait_for_timeout(300); rep['slope_map'] = pg.evaluate('(() => { const f = LAND.field(); return {bands_pct: f.bands, sum: f.bands[0] + f.bands[1] + f.bands[2], steepest: f.smx, smoothing_largest_change: f.smax, grade: LAND.secGrade(), key: document.getElementById("mapkey").textContent} })()')
    pg.locator('#read').screenshot(path=str(work / 'cap' / '_13_read.png')); pg.locator('#g_Grading').screenshot(path=str(work / 'cap' / '_13_ctl.png'))
    compose('13_slope_map', '13 · slope map in three bands (5 and 33 percent) on a mound with xylem ridges, scale 1:200: bands %.1f, %.1f, %.1f percent of the tile · two spot elevations' % tuple(rep['slope_map']['bands_pct']), [(pg.evaluate('LAND.planPNG()'), 'plan with the slope map'), ((work / 'cap' / '_13_read.png').as_uri(), 'readouts'), ((work / 'cap' / '_13_ctl.png').as_uri(), 'Grading controls and key')], 3, 760, 760)
    # 14: cut and fill before and after Balance
    pg.evaluate('LAND.set("map", "none")'); before = pg.evaluate('(() => { const f = LAND.field(); return {cut: f.cut, fill: f.fill, net: f.fill - f.cut, shift: LAND.V.shift} })()'); pg.locator('#read').screenshot(path=str(work / 'cap' / '_14_before.png'))
    res = pg.evaluate('LAND.balance()'); after = pg.evaluate('(() => { const f = LAND.field(); return {cut: f.cut, fill: f.fill, net: f.fill - f.cut, shift: LAND.V.shift, state: document.getElementById("gstate").textContent} })()'); pg.locator('#read').screenshot(path=str(work / 'cap' / '_14_after.png'))
    rep['balance'] = dict(before=before, after=after, result=res)
    compose('14_balance', '14 · cut and fill against the ground before and after Balance: net %.0f to %.0f mm3, form level shifted %.2f mm' % (before['net'], after['net'], after['shift'] - before['shift']), [((work / 'cap' / '_14_before.png').as_uri(), 'before · shift %.2f mm' % before['shift']), ((work / 'cap' / '_14_after.png').as_uri(), 'after Balance · shift %.2f mm' % after['shift'])], 2, 1070, 640)
    rep['spot_svg_layer'] = 'spot-elevations' in pg.evaluate('LAND.sheetSVG()')
    pg.evaluate('LAND.reset()'); rep['changed_after_reset'] = pg.evaluate('LAND.changed().length')
    # live drag: an input event on a heightfield slider updates without a release; a regrow slider waits for the release
    rep['live'] = pg.evaluate('''() => { const z0 = LAND.field().zmax; const e = document.getElementById('c_gain'); e.value = 0.7; e.dispatchEvent(new Event('input', {bubbles: true})); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => { const z1 = LAND.field().zmax; const s = document.getElementById('c_seed'); const n0 = LAND.field().segT.length; s.value = 23; s.dispatchEvent(new Event('input', {bubbles: true})); const n1 = LAND.field().segT.length; s.dispatchEvent(new Event('change', {bubbles: true})); const st = document.getElementById('state').textContent; setTimeout(() => r({zmax_before: z0, zmax_after_input: z1, segs_before: n0, segs_after_input: n1, state_on_release: st, segs_after_release: LAND.field().segT.length, state_after: document.getElementById('state').textContent}), 900) }))) }''')
    # every control: listed with its group; every PR entry has a row
    rep['controls'] = pg.evaluate('LAND.PR.map(p => [p.g, p.id, p.label, !!document.getElementById("row_" + p.id), !p.type ? !!document.getElementById("n_" + p.id) : null])')
    rep['groups'] = pg.evaluate('[...document.querySelectorAll("details.grp > summary")].map(s => s.textContent)')
    rep['storage_calls'] = [k for k in ('localStorage', 'sessionStorage', 'document.cookie') if k in (site / 'land.html').read_text(encoding='utf-8')]
    rep['page_errors'] = list(errs)
    # widths
    for wd in (400, 1400):
        p3 = b.new_page(viewport={'width': wd, 'height': 900}); p3.goto((site / 'land.html').as_uri()); p3.wait_for_function('window.LAND && LAND.field()', timeout=30000); p3.wait_for_timeout(800)
        rep['width_%d' % wd] = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]'); p3.screenshot(path=str(work / 'cap' / ('width_%d.png' % wd)), full_page=(wd == 400)); p3.close()
    # the Lab link
    p4 = b.new_page(viewport={'width': 1400, 'height': 900}); p4.goto((site / 'index.html').as_uri()); p4.wait_for_function('window.VL', timeout=30000); p4.evaluate('VL.loadStudy("VS03-09")'); p4.click('#toland'); p4.wait_for_function('window.LAND && LAND.field()', timeout=30000)
    rep['lab_link'] = p4.evaluate('[location.pathname.split("/").pop(), LAND.V.src, LAND.V.mode, LAND.V.shape, LAND.artId(), LAND.changed().length]'); p4.close()
    # contact sheet, drawn by the browser so the type is Plex
    caps = rep['captures']; tiles = ''.join('<figure><img style="object-fit:%s" src="%s"><figcaption>%s</figcaption></figure>' % (c.get('fit', 'cover'), (work / 'cap' / c['file']).as_uri(), c['caption']) for c in caps)
    title = 'VS09 · %s · site: Land page v02 · %d captures of the page in headless Chromium' % (sheet.stem.replace('VS09_', ''), len(caps))
    html = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"><style>body{margin:0;padding:28px;background:#f3f1ec;color:#1d1c1a;font:400 19px/1.35 "IBM Plex Mono",monospace}h1{font:500 22px "IBM Plex Mono",monospace;margin:0 0 18px}.g{display:grid;grid-template-columns:repeat(4,900px);gap:22px}figure{margin:0;border:1px solid #c9c5bb;background:#e9e6df}img{display:block;width:900px;height:680px;object-fit:cover;object-position:top}figcaption{padding:8px 10px 10px;min-height:86px;border-top:1px solid #c9c5bb;background:#f3f1ec}</style><h1>%s</h1><div class="g">%s</div>' % (title, tiles)
    (work / 'sheet.html').write_text(html, encoding='utf-8'); p5 = b.new_page(viewport={'width': 3760, 'height': 1000}); p5.goto((work / 'sheet.html').as_uri()); p5.wait_for_load_state('networkidle'); p5.wait_for_timeout(800)
    big = ''.join('<figure><img src="%s"><figcaption>%s</figcaption></figure>' % ((work / 'cap' / c['file']).as_uri(), c['caption']) for c in caps if c.get('fit') == 'contain')
    html2 = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap"><style>body{margin:0;padding:28px;background:#f3f1ec;color:#1d1c1a;font:400 19px/1.35 "IBM Plex Mono",monospace}h1{font:500 22px "IBM Plex Mono",monospace;margin:0 0 18px}.g{display:grid;grid-template-columns:repeat(2,1640px);gap:22px;align-items:start}figure{margin:0;border:1px solid #c9c5bb;background:#e9e6df}img{display:block;width:1640px;height:auto}figcaption{padding:8px 10px 10px;border-top:1px solid #c9c5bb;background:#f3f1ec}</style><h1>%s</h1><div class="g">%s</div>' % (title.replace('captures of the page', 'captures, the four of ADD-2 at reading size, of the page'), big)
    (work / 'sheet2.html').write_text(html2, encoding='utf-8'); p6 = b.new_page(viewport={'width': 3380, 'height': 1000}); p6.goto((work / 'sheet2.html').as_uri()); p6.wait_for_load_state('networkidle'); p6.wait_for_timeout(800); p6.screenshot(path=str(sheet)[:-4] + '_add2.png', full_page=True); p6.close()
    rep['sheet_plex'] = p5.evaluate('document.fonts.check("19px \\"IBM Plex Mono\\"")'); p5.screenshot(path=str(sheet), full_page=True); p5.close(); b.close()
rep['sheet'] = sheet.name; rep['built'] = time.strftime('%Y-%m-%d %H:%M')
Path(str(sheet)[:-4] + '_check.json').write_text(json.dumps(rep, indent=1), encoding='utf-8')
for k in ('fills', 'profiles', 'slope_map', 'balance', 'spot_svg_layer', 'fonts', 'png16', 'stl', 'svg_contours', 'svg_section', 'file_ground', 'water_bank', 'rain_pond_notch', 'rain_pond_no_notch', 'changed_gain_ve', 'marked_rows', 'changed_after_reset', 'live', 'groups', 'width_400', 'width_1400', 'lab_link', 'storage_calls', 'page_errors', 'chat_text'): print(k, json.dumps(rep.get(k), ensure_ascii=True)[:700])
print('controls', len(rep['controls']), 'rows missing', [c for c in rep['controls'] if not c[3]])
