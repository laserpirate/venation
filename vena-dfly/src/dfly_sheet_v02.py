"""dfly_sheet_v02.py : sheet VS07 (2 variants x top, three-quarter, back-lit wing close-up) from the check files.
usage: python dfly_sheet_v02.py <out.png>    No em dashes."""
import sys, os, json, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); MOCK = os.path.join(ROOT, '00_mockups', 'vena-dfly')
out = sys.argv[1]; tiles = []; npass = 0; n = 0
SRC = {'vena-dfly-phys--open-VS03-01__01': 'forewings VS03-01, hindwings VS03-05 (open)', 'vena-dfly-phys--cells-VS03-04__01': 'forewings VS03-04, hindwings VS03-08 (cells fab)'}
for aid in SRC:
    r = json.load(open(glob.glob(os.path.join(MOCK, aid + '_*_check.json'))[0], encoding='utf-8')); c = r['checks']; st = r['stats']; d = c['dims_mm']; w = st['wings']; n += 1; npass += bool(c['pass'])
    for view, vt in (('top', 'top'), ('tq', 'three-quarter'), ('backlit', 'left wings back-lit')):
        t = len(tiles) + 1
        L = [aid, 'VS07-%02d · %s · %s' % (t, vt, SRC[aid]), 'E1 Clubtail body at 3x · %.0f x %.0f x %.0f mm (%.2f x %.2f x %.2f in)' % (d[0], d[1], d[2], d[0] / 25.4, d[1] / 25.4, d[2] / 25.4)]
        if view == 'top':
            L.append('wings: membrane 0.4 mm closed, ribs 2.0 to 3.6 mm wide, 1.2 to 3.0 mm tall · fine, below lab minimum')
            L.append('ribs cover %.0f and %.0f percent of fore and hind wing · windows %d and %d · none opened' % (100 * w['fore']['rib_share'], 100 * w['hind']['rib_share'], w['fore']['windows'], w['hind']['windows']))
        elif view == 'tq':
            L.append('body: 45 degree chamfers and 0.75 mm webs under the legs, %.1f cm3 added to %.1f · down-facing %.0f mm2, widest strip %.2f mm' % (st['body_volume_added_cm3'], st['body_volume_source_cm3'], c['overhang_mm2'], c['overhang_widest_strip_mm']))
            L.append('eyes: %d hexagonal facets, 1.6 mm pitch, 0.3 mm relief' % st['eye_facets'])
        else:
            if w['fore']['grown_segments']: L.append('veins thinned to fit: %d of %d and %d of %d grown segments kept' % (w['fore']['grown_segments'] - w['fore']['grown_dropped'], w['fore']['grown_segments'], w['hind']['grown_segments'] - w['hind']['grown_dropped'], w['hind']['grown_segments']))
            else: L.append('named veins kept: fore %s; hind %s · cells kept %d of %d and %d of %d' % (', '.join(q for q in w['fore']['named_kept'] if q not in ('triangle', 'nodus', 'pterostigma')), ', '.join(q for q in w['hind']['named_kept'] if q not in ('triangle', 'nodus', 'pterostigma')), w['fore']['cell_walls_kept'], w['fore']['cell_walls_tried'], w['hind']['cell_walls_kept'], w['hind']['cell_walls_tried']))
            L.append('render material is a stand-in, not a measured filament')
        L.append('%d g · %.1f h estimated, not sliced' % (c['grams_est'], c['hours_est'])); L.append('PASS' if c['pass'] else 'FAIL')
        tiles.append(dict(id=aid, img=os.path.join(MOCK, r['stem'] + '_' + view + '.png'), lines=L))
name = os.path.splitext(os.path.basename(out))[0]
sj = os.path.join(ROOT, '_work', 'v03c', 'VS07_sheet.json'); json.dump(dict(title='VS07 · %s · vena-dfly-phys · %d variants, %d PASS' % (name.split('_', 1)[1], n, npass), id='VS07', cols=3, tile_px=560, tiles=tiles), open(sj, 'w', encoding='utf-8'), indent=1)
print('VS07', n, 'built', npass, 'PASS', n - npass, 'FAIL')
subprocess.check_call([sys.executable, os.path.join(HERE, '..', 'image_sheet_v02.py'), sj, out])
