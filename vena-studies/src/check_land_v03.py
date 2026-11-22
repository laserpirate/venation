"""check_land_v03.py : stage 3 proof of land.html v03. Captures of the page itself: one pattern under each fill rule, two rules combined, the six
falloff curves on one berm (section), the stream network at two thresholds, watersheds, curvature classes, wetness, sun and shade, the 3D view at
vertical exaggeration 1 and 3; the Grasshopper set saved, unzipped and reloaded in Python (DXF entities per layer and ASCII grid against the page).
Also a flat tile and a divided tile through the stream network first (flattest and most divided case). Writes captures, the set, a check JSON and
the contact sheet. usage: python check_land_v03.py <site_dir> <work_dir> <sheet.png>. No em dashes."""
import sys, json, base64, io, zipfile, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
site = Path(sys.argv[1]).resolve(); work = Path(sys.argv[2]).resolve(); sheet = Path(sys.argv[3]).resolve(); (work / 'cap').mkdir(parents=True, exist_ok=True)
rep = {'captures': [], 'checks': {}}; caps = []
OFF = dict(rv_on=0, bc_on=0, pb_on=0, hd_on=0, cv_on=0, ex_on=0, st_on=0, ws_on=0, tw_on=0, sun_on=0, rain=0, map='none', ve=1, typ='none', ground='flat', blend=0)


def png(data_url, name):
    f = work / 'cap' / name; f.write_bytes(base64.b64decode(data_url.split(',', 1)[1])); return f


def setall(pg, d):
    pg.evaluate('(d) => { for (const k of Object.keys(d)) LAND.V[k] = (typeof LAND.V[k] === "number") ? +d[k] : String(d[k]); }', d)
    pg.evaluate('(d) => { const k0 = Object.keys(d)[0]; LAND.set(k0, d[k0]) }', d)


def cap(pg, name, title, what='plan'):
    pg.wait_for_timeout(150)
    if what == 'plan': f = png(pg.evaluate('LAND.planPNG()'), name + '.png')
    elif what == '3d': f = png(pg.evaluate('LAND.view3PNG()'), name + '.png')
    else: f = png(pg.evaluate('document.getElementById("sec").toDataURL("image/png")'), name + '.png')
    lines = pg.evaluate('LAND.capLines()'); caps.append(dict(file=f.name, title=title, lines=lines)); rep['captures'].append(dict(file=f.name, title=title, page_caption=lines)); return f


with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    pg = b.new_page(viewport={'width': 1500, 'height': 1000}, accept_downloads=True); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto((site / 'land.html').as_uri()); pg.wait_for_function('window.LAND && LAND.has3D()', timeout=40000); pg.wait_for_timeout(800)
    rep['controls'] = pg.evaluate('LAND.PR.length')
    # VS08 tiles unchanged by default: relief of the first tile against v02's recorded 2.0 to 20.0 mm
    rep['checks']['vs08_first_relief'] = pg.evaluate('[LAND.field().zmin, LAND.field().zmax]')
    # flattest and most divided cases through the stream network
    setall(pg, dict(OFF, st_on=1, ws_on=1, gain=0, prof='none'))
    rep['checks']['flat_streams'] = pg.evaluate('(() => { const a = LAND.ana(); return {cells: a.st.cells, sources: a.st.src.length, outlets: a.st.out.length, watersheds: a.ws.count} })()')
    setall(pg, dict(OFF, typ='pond', st_on=1, ws_on=1, gain=1))
    rep['checks']['divided_streams'] = pg.evaluate('(() => { const a = LAND.ana(); return {cells: a.st.cells, sources: a.st.src.length, outlets: a.st.out.length, order: a.st.omax, watersheds: a.ws.count} })()')
    pg.evaluate('LAND.loadTile("vena-land-berm--ovate-VS02-04__01")')
    # 1 to 4: one pattern under each fill rule
    for i, (r, extra, t) in enumerate((('rv', {}, 'ridges on the veins, three orders'), ('bc', {}, 'berms on the veins, trapezoid, 100 % sides'), ('pb', {'pb_sign': '-1'}, 'basins in the cells, flat floors'), ('hd', {}, 'hills on the cell centroids'))):
        setall(pg, dict(OFF, **{r + '_on': 1}, **extra)); cap(pg, '%02d_%s' % (i + 1, r), '%d · %s' % (i + 1, t))
    rep['checks']['rules'] = pg.evaluate('(() => { const f = LAND.field(); return f.rules })()') and None
    # 5: two rules combined
    setall(pg, dict(OFF, bc_on=1, bc_h2=0, bc_h3=0, pb_on=1, pb_sign='-1', pb_h=4, bc_ov='1')); cap(pg, '05_combined', '5 · berms on the primary veins (highest) with basins in the cells')
    # 6: six falloff curves on one berm, section across it
    # the berm on the midrib only (secondary and finer at height 0), cut across it; heights sampled from the page's own field
    PROF = '''() => { const f = LAND.field(); const n = f.n, cs = f.cs; const out = []; for (let i = 0; i <= 240; i++) { const y = (0.3 + 0.4 * i / 240) * f.T, x = 0.5 * f.T;
      const u = x / cs - .5, v = y / cs - .5; const a = Math.floor(u), b = Math.floor(v), fa = u - a, fb = v - b; const Z = (p, q) => f.z[q * n + p];
      out.push([y, Z(a, b) * (1 - fa) * (1 - fb) + Z(a + 1, b) * fa * (1 - fb) + Z(a, b + 1) * (1 - fa) * fb + Z(a + 1, b + 1) * fa * fb]) } return out }'''
    profs = []
    for k in range(6):
        setall(pg, dict(OFF, bc_on=1, bc_w1=3, bc_h1=10, bc_h2=0, bc_h3=0, bc_s1=40, bc_fo=str(k), bc_ov='1')); profs.append(pg.evaluate(PROF))
    pg.evaluate('document.getElementById("g_Ruleberm" + "orchannel").open = true'); el = pg.query_selector('#fokey_bc_fo'); el.scroll_into_view_if_needed(); el.screenshot(path=str(work / 'cap' / '06_key.png'))
    caps.append(dict(file='06_key.png', title='6a · the falloff control on the page: six curves with their names', lines=['the selected one is marked; a click selects it', 'shapes are this page\'s own (see DECISIONS)']))
    rep['checks']['falloff_profiles_peak'] = [round(max(z for _, z in p), 3) for p in profs]
    ci = Image.new('RGB', (1000, 520), (7, 9, 14)); cd = ImageDraw.Draw(ci); cols = [(255, 255, 255), (230, 159, 0), (86, 180, 233), (0, 158, 115), (240, 228, 66), (204, 121, 167)]
    y0s = [p[0][0] for p in profs]; zmax = max(max(z for _, z in p) for p in profs); zmin = min(min(z for _, z in p) for p in profs)
    X = lambda y: 40 + (y - profs[0][0][0]) / (profs[0][-1][0] - profs[0][0][0]) * 920; Yp = lambda z: 470 - (z - zmin) / max(1e-6, zmax - zmin) * 400
    for k, p in enumerate(profs): cd.line([(X(y), Yp(z)) for y, z in p], fill=cols[k], width=2)
    try: FK = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
    except Exception: FK = ImageFont.load_default()
    for k in range(6): cd.text((48 + (k % 3) * 300, 12 + (k // 3) * 24), '%d %s' % (k, ['linear', 'ease-out', 'smooth', 'very smooth', 'cosine', 'concentrated'][k]), fill=cols[k], font=FK)
    cd.text((40, 490), 'across the midrib, 40 %% of the tile · height %.1f to %.1f mm, height axis stretched to fit' % (zmin, zmax), fill=(176, 176, 193), font=FK)
    ci.save(work / 'cap' / '06_fo.png'); caps.append(dict(file='06_fo.png', title='6b · six falloffs on one berm, side slope 40 %, profiles overlaid', lines=['berm top width 3 mm, height 10 mm, on the primary veins only', 'heights read from the page field; chart drawn by the check script']))
    # 7 to 11: open venation (a tree) as valleys on an even slope
    pg.evaluate('LAND.set("mode", "open")')
    setall(pg, dict(OFF, rv_on=1, rv_sign='-1', ground='slope', blend=0.35, grel=18, st_on=1, st_thr=0.05)); cap(pg, '07_st02', '7 · stream network, threshold 0.05 of the greatest accumulation, open veins as valleys on an even slope (blend 0.35)')
    rep['checks']['streams_0.05'] = pg.evaluate('(() => { const s = LAND.ana().st; return {cells: s.cells, order: s.omax, sources: s.src.length, outlets: s.out.length} })()')
    setall(pg, dict(OFF, rv_on=1, rv_sign='-1', ground='slope', blend=0.35, grel=18, st_on=1, st_thr=0.15)); cap(pg, '08_st10', '8 · stream network, threshold 0.15')
    rep['checks']['streams_0.15'] = pg.evaluate('(() => { const s = LAND.ana().st; return {cells: s.cells, order: s.omax, sources: s.src.length, outlets: s.out.length} })()')
    setall(pg, dict(OFF, rv_on=1, rv_sign='-1', ground='slope', blend=0.35, grel=18, st_on=1, ws_on=1, st_thr=0.05)); cap(pg, '09_ws', '9 · watersheds per outlet, the eight largest')
    rep['checks']['watersheds'] = pg.evaluate('LAND.ana().ws.list.map(w => +w.area.toFixed(1))')
    setall(pg, dict(OFF, typ='berm', cv_on=1)); cap(pg, '10_cv', '10 · curvature: landform classes')
    rep['checks']['curv_counts'] = pg.evaluate('Array.from(LAND.ana().cv.cnt)')
    setall(pg, dict(OFF, rv_on=1, rv_sign='-1', ground='slope', blend=0.35, grel=18, tw_on=1)); cap(pg, '11_tw', '11 · wetness index')
    pg.evaluate('LAND.set("mode", "closed")')
    setall(pg, dict(OFF, typ='berm', sun_on=1, sun_az=315, sun_alt=25)); cap(pg, '12_sun', '12 · sun and shade, sun from 315 deg at 25 deg')
    rep['checks']['sun_shadow_pct'] = pg.evaluate('LAND.ana().sun.share')
    setall(pg, dict(OFF, typ='berm', ex_on=1)); cap(pg, '13_ex', '13 · extrema: top and bottom 10 % of the range')
    # 14, 15: 3D at exaggeration 1 and 3
    setall(pg, dict(OFF, bc_on=1, pb_on=1, pb_sign='-1', ve=1)); pg.evaluate('LAND.view("axa")'); cap(pg, '14_ve1', '14 · 3D, vertical exaggeration 1', '3d')
    setall(pg, dict(OFF, bc_on=1, pb_on=1, pb_sign='-1', ve=3)); pg.evaluate('LAND.view("axa")'); cap(pg, '15_ve3', '15 · 3D, vertical exaggeration 3 (same heights)', '3d')
    rep['checks']['ve3_readout_relief'] = pg.evaluate('[LAND.field().zmin, LAND.field().zmax]')
    # the Grasshopper set: through the button, saved, unzipped
    setall(pg, dict(OFF, bc_on=1, pb_on=1, pb_sign='-1', hd_on=1, ve=3))
    with pg.expect_download() as dl: pg.evaluate('document.getElementById("x_gh").click()')
    d = dl.value; zp = work / d.suggested_filename; d.save_as(str(zp))
    page_counts = pg.evaluate('LAND.ghSet().counts'); fz = pg.evaluate('(() => { const f = LAND.field(); return {n: f.n, cs: f.cs, z: Array.from(f.z.filter((v, i) => i % 997 === 0)), zb: Array.from(f.zb.filter((v, i) => i % 997 === 0))} })()')
    rep['errors'] = errs; b.close()
# reload the set in Python
zf = zipfile.ZipFile(zp); names = zf.namelist(); rep['checks']['zip_files'] = names
dxf = zf.read([n for n in names if n.endswith('.dxf')][0]).decode('ascii'); L = dxf.split('\n'); pairs = [(L[i].strip(), L[i + 1].strip()) for i in range(0, len(L) - 1, 2)]
cnt = {}; cur = None; nv = 0
for i, (c, v) in enumerate(pairs):
    if c == '0' and v in ('POLYLINE', 'POINT'):
        lay = next(pv for pc, pv in pairs[i + 1:i + 4] if pc == '8'); cnt[lay] = cnt.get(lay, 0) + 1
    if c == '0' and v == 'VERTEX': nv += 1
rep['checks']['dxf_counts'] = cnt; rep['checks']['dxf_vertices'] = nv; rep['checks']['page_counts'] = page_counts
assert all(cnt.get(k, 0) == v for k, v in page_counts.items()), (cnt, page_counts)
def asc(name):
    t = zf.read(name).decode('ascii').split('\n'); hd = {}
    for l in t[:6]: k, v = l.split(); hd[k.lower()] = float(v)
    vals = [float(x) for l in t[6:] if l.strip() for x in l.split()]; return hd, vals
for tag, key in (('surface', 'z'), ('base', 'zb')):
    hd, vals = asc([n for n in names if n.endswith('_' + tag + '.asc')][0]); assert int(hd['ncols']) == fz['n'] and int(hd['nrows']) == fz['n'] and len(vals) == fz['n'] ** 2
    sub = vals[::997]; dmax = max(abs(a - b) for a, b in zip(sub, fz[key])); rep['checks']['asc_' + tag] = dict(ncols=int(hd['ncols']), cellsize=hd['cellsize'], values=len(vals), max_diff_mm=round(dmax, 5)); assert dmax < 1e-3
csv1 = zf.read([n for n in names if n.endswith('_veins_1.csv')][0]).decode('ascii').splitlines(); csvc = zf.read([n for n in names if n.endswith('_cells.csv')][0]).decode('ascii').splitlines()
assert len(csv1) - 1 == page_counts['veins_1'] and len(csvc) - 1 == page_counts['cells']
readme = zf.read('README_grasshopper.txt').decode('utf-8')
rep['all_ok'] = not rep['errors']; Path(str(sheet).replace('.png', '_check.json')).write_text(json.dumps(rep, indent=1), encoding='utf-8')
print('controls', rep['controls'], 'errors', len(rep['errors']), json.dumps(rep['checks'])[:1500])
# the set as a tile: layers, counts, first CSV rows, README head
gi = Image.new('RGB', (1000, 1000), (250, 249, 246)); gd = ImageDraw.Draw(gi)
try: F = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15); FB = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 17); FT = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 17)
except Exception: F = FB = FT = ImageFont.load_default()
y = 12; gd.text((12, y), zp.name, fill=(20, 20, 20), font=FB); y += 28
for n in names: gd.text((12, y), n, fill=(60, 60, 60), font=F); y += 19
y += 8; gd.text((12, y), 'DXF reloaded in Python: ' + ', '.join('%s %d' % (k, v) for k, v in sorted(cnt.items())) + ' · vertices %d' % nv, fill=(20, 20, 20), font=F); y += 19
gd.text((12, y), 'page counts equal: yes · ASCII grids %d x %d, values equal to the page within %.5f mm' % (fz['n'], fz['n'], max(rep['checks']['asc_surface']['max_diff_mm'], rep['checks']['asc_base']['max_diff_mm'])), fill=(20, 20, 20), font=F); y += 30
for title, rows in (('veins_1.csv, first rows', csv1[:4]), ('cells.csv, first rows', csvc[:4])):
    gd.text((12, y), title, fill=(20, 20, 20), font=FB); y += 22
    for r in rows:
        while r: gd.text((12, y), r[:118], fill=(60, 60, 60), font=F); r = r[118:]; y += 18
    y += 8
gd.text((12, y), 'README_grasshopper.txt, first lines', fill=(20, 20, 20), font=FB); y += 22
for r in readme.splitlines()[:16]:
    while r and y < 985: gd.text((12, y), r[:118], fill=(60, 60, 60), font=F); r = r[118:]; y += 18
gi.save(work / 'cap' / '16_gh.png'); caps.append(dict(file='16_gh.png', title='16 · the Grasshopper set opened: layers, counts, first CSV rows', lines=['reloaded in Python: counts and grids equal to the page']))
# contact sheet: 4 columns
CW = 560; M = 22; rows = []
for c in caps:
    s = Image.open(work / 'cap' / c['file']).convert('RGB'); k = CW / s.width; s = s.resize((CW, int(s.height * k)), Image.LANCZOS); c['img'] = s
NC = 4; cols_h = []
W = M + NC * (CW + M); y0 = 64
# lay out row by row
placed = []; y = y0
for r0 in range(0, len(caps), NC):
    row = caps[r0:r0 + NC]; th = []
    for c in row:
        L = [c['title']] + [l for l in c['lines'][:5]]; wrapped = []
        for l in L:
            while len(l) > 58: cut = l.rfind(' ', 0, 58); cut = cut if cut > 20 else 58; wrapped.append(l[:cut]); l = l[cut:].lstrip()
            wrapped.append(l)
        c['wr'] = wrapped; th.append(c['img'].height + 10 + 20 * len(wrapped))
    for i, c in enumerate(row): placed.append((c, M + i * (CW + M), y))
    y += max(th) + M
H = y + M; im = Image.new('RGB', (W, H), (243, 241, 236)); d = ImageDraw.Draw(im)
d.text((M, 20), 'VS13 · site land v03 · fill rules, shared controls, analyses, the Grasshopper set · captures of the page; vertical exaggeration acts on the 3D view and the section only', fill=(29, 28, 26), font=FB)
for c, x, yy in placed:
    im.paste(c['img'], (x, yy)); d.rectangle([x - 1, yy - 1, x + CW, yy + c['img'].height], outline=(201, 197, 187))
    for j, t in enumerate(c['wr']): d.text((x, yy + c['img'].height + 8 + 20 * j), t, fill=(29, 28, 26) if j == 0 else (80, 78, 72), font=FT if j == 0 else F)
im.save(sheet); print('sheet', sheet, im.size)
