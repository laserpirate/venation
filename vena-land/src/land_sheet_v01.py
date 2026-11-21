"""land_sheet_v01.py : sheet VS08, 4 x 4: rows are the venation patterns, columns the typologies. usage: python land_sheet_v01.py <out.png>. No em dashes."""
import sys, os, json, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); D = os.path.join(ROOT, '00_export_svg', 'vena-land')
out = sys.argv[1]; tiles = []
for pat in ('wing-VS03-04', 'ovate-VS02-04', 'blob-VS02-10', 'cells-VS02-16'):
    for typ in ('berm', 'wave', 'pond', 'terr'):
        r = json.load(open(glob.glob(os.path.join(D, 'vena-land-%s--%s__01_*_check.json' % (typ, pat)))[0], encoding='utf-8')); t = len(tiles) + 1
        tiles.append(dict(id=r['id'], img=os.path.join(D, r['stem'] + '_shaded.png'), lines=[r['id'], 'VS08-%02d · %s · %s' % (t, r['typology'], pat), '100 x 100 mm tile · relief %.1f to %.1f mm · 1 mm contours' % tuple(r['relief_mm']), 'pattern study: no scale, no vertical exaggeration set']))
name = os.path.splitext(os.path.basename(out))[0]
sj = os.path.join(ROOT, '_work', 'v03c', 'VS08_sheet.json'); json.dump(dict(title='VS08 · %s · vena-land · 16 studies (4 venation patterns x 4 typologies)' % name.split('_', 1)[1], id='VS08', cols=4, tile_px=500, tiles=tiles), open(sj, 'w', encoding='utf-8'), indent=1)
subprocess.check_call([sys.executable, os.path.join(HERE, '..', 'image_sheet_v02.py'), sj, out])
