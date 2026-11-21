"""lamp_sheet_v02.py : sheet JSON for VS06a or VS06b from the check files, then image_sheet_v02.py draws it.
usage: python lamp_sheet_v02.py <VS06a|VS06b> <out.png>    No em dashes."""
import sys, os, json, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); MOCK = os.path.join(ROOT, '00_mockups', 'vena-lamp')
sheet, out = sys.argv[1], sys.argv[2]; S = json.load(open(os.path.join(HERE, 'VS06_specs_v01.json'), encoding='utf-8'))
PHOTO = 'Hyphae photo ref01 about 533 a face'       # count_photo_cells_v01.py: dark regions of 6 px or more inside the silhouette of ref01
tiles = []; tot_g = tot_h = 0; npass = 0
for k in sorted(k for k in S if S[k]['sheet'] == sheet):
    sp = S[k]; cj = glob.glob(os.path.join(MOCK, sp['id'] + '_s*_check.json'))
    if not cj: continue
    r = json.load(open(cj[0], encoding='utf-8')); c = r['checks']; st = r['stats']; d = c['dims_mm']; f = sp['form']
    tech = 'T1 window %.2f mm' % sp['window_mm'] if sp['tech'] == 'T1' else 'T2 open, graded'
    L = [sp['id'], '%s-%02d · %s%s' % (sheet, sp['tile'], tech, (' · ' + sp['note']) if sp.get('note') and sp['note'] != 'free' else '')]
    if sp.get('free'): L.append(sp['free'])
    L.append('base %.2f in, collar %.2f in · %.0f x %.0f x %.0f mm (%.2f in tall)' % (f['base_in'], r['foot']['collar_mm'] / 25.4, d[0], d[1], d[2], d[2] / 25.4))
    if sp['tech'] == 'T1':
        L.append('cells %d (about %d a face) · %s' % (st['cells'], st['cells'] // 2, PHOTO))
        L.append('least window %.1f mm · ribs %.1f to %.1f mm · %d small cells closed' % (c['least_window_mm'], st['rib_w_mm'][0], st['rib_w_mm'][1], st['cells_closed_small']))
    else:
        L.append('holes %d (about %d a face) · %s' % (st['holes_open'], st['holes_open'] // 2, PHOTO))
        L.append('least hole %.1f mm · veins %.1f to %.1f mm · fine, below lab minimum above mid height' % (c['least_hole_mm'], st['rib_w_mm'][0], st['rib_w_mm'][1]))
    L.append('%d g · %.1f h estimated, not sliced' % (c['grams_est'], c['hours_est'])); L.append('PASS' if c['pass'] else 'FAIL')
    tot_g += c['grams_est']; tot_h += c['hours_est']; npass += bool(c['pass'])
    tiles.append(dict(id=sp['id'], img=os.path.join(MOCK, r['stem'] + '_lit.png'), lines=L))
name = os.path.splitext(os.path.basename(out))[0]
title = '%s · %s · vena-lamp %s · mockups lit from inside · %d pieces, %d PASS · %d g, %.1f h estimated' % (sheet, name.split('_', 1)[1], 'patterns' if sheet == 'VS06a' else 'wraps', len(tiles), npass, tot_g, tot_h)
sj = os.path.join(ROOT, '_work', 'v03b', sheet + '_sheet.json'); json.dump(dict(title=title, id=sheet, cols=4, tile_px=520, tiles=tiles), open(sj, 'w', encoding='utf-8'), indent=1)
print(sheet, len(tiles), 'built', npass, 'PASS', len(tiles) - npass, 'FAIL', tot_g, 'g', round(tot_h, 1), 'h')
subprocess.check_call([sys.executable, os.path.join(HERE, '..', 'image_sheet_v02.py'), sj, out])
