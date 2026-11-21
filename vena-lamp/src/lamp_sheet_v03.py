"""lamp_sheet_v03.py : sheet JSON for a lamp sheet from the check files, then image_sheet_v02.py draws it. v02 plus a specs file
argument and the window below, open above caption. usage: python lamp_sheet_v03.py <specs.json> <VS06c> <out.png>    No em dashes."""
import sys, os, json, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); MOCK = os.path.join(ROOT, '00_mockups', 'vena-lamp')
sfile, sheet, out = sys.argv[1], sys.argv[2], sys.argv[3]; S = json.load(open(sfile, encoding='utf-8'))
PHOTO = 'Hyphae photo ref01 about 533 a face'       # count_photo_cells_v01.py
tiles = []; tot_g = tot_h = 0; npass = 0
for k in sorted(k for k in S if S[k]['sheet'] == sheet and S[k]['tile'] > 0):
    sp = S[k]; cj = glob.glob(os.path.join(MOCK, sp['id'] + '_s*_check.json'))
    if not cj: continue
    r = json.load(open(cj[0], encoding='utf-8')); c = r['checks']; st = r['stats']; d = c['dims_mm']; f = sp['form']
    tech = {'T1': 'T1 window %.2f mm' % sp['window_mm'], 'T2': 'T2 open, graded', 'T1T2': 'T1 window %.2f mm below, open above' % sp['window_mm']}[sp['tech']]
    note = sp.get('note') or ''
    if sp['tech'] == 'T1T2': note = note.replace('window below, open above · ', '')
    L = [sp['id'], '%s-%02d · %s%s' % (sheet, sp['tile'], tech, (' · ' + note) if note else '')]
    L.append('base %.2f in, collar %.2f in · %.0f x %.0f x %.0f mm (%.2f in tall)' % (f['base_in'], r['foot']['collar_mm'] / 25.4, d[0], d[1], d[2], d[2] / 25.4))
    if sp['tech'] == 'T1':
        L.append('cells %d (about %d a face) · %s' % (st['cells'], st['cells'] // 2, PHOTO))
        L.append('least window %.1f mm · ribs %.1f to %.1f mm · %d small cells closed' % (c['least_window_mm'], st['rib_w_mm'][0], st['rib_w_mm'][1], st['cells_closed_small']))
    else:
        L.append('cells %d (about %d a face) · %s' % (st['cells'], st['cells'] // 2, PHOTO))
        L.append('opened %d · stayed windows %d (%d of them above the change) · change at %.0f mm over %.0f mm' % (st['holes_open'], st['windows_kept'], st['above_split_kept_closed'], st['split_z_mm'], 2 * st['split_band_mm']))
        L.append('least hole %.1f mm · least window %.1f mm · ribs %.1f to %.1f mm · fine, below lab minimum' % (c['least_hole_mm'], c['least_window_mm'], st['rib_w_mm'][0], st['rib_w_mm'][1]))
    L.append('%d g · %.1f h estimated, not sliced' % (c['grams_est'], c['hours_est'])); ok = bool(c['pass']) and not sp.get('reload_fail'); L.append('PASS' if ok else (sp.get('reload_fail') or 'FAIL'))
    tot_g += c['grams_est']; tot_h += c['hours_est']; npass += ok
    tiles.append(dict(id=sp['id'], img=os.path.join(MOCK, r['stem'] + '_lit.png'), lines=L))
name = os.path.splitext(os.path.basename(out))[0]
title = '%s · %s · vena-lamp iterations · mockups lit from inside · %d pieces, %d PASS · %d g, %.1f h estimated' % (sheet, name.split('_', 1)[1], len(tiles), npass, tot_g, tot_h)
os.makedirs(os.path.join(ROOT, '_work', 'v03c'), exist_ok=True)
sj = os.path.join(ROOT, '_work', 'v03c', sheet + '_sheet.json'); json.dump(dict(title=title, id=sheet, cols=4, tile_px=520, tiles=tiles), open(sj, 'w', encoding='utf-8'), indent=1)
print(sheet, len(tiles), 'built', npass, 'PASS', len(tiles) - npass, 'FAIL', tot_g, 'g', round(tot_h, 1), 'h')
subprocess.check_call([sys.executable, os.path.join(HERE, '..', 'image_sheet_v02.py'), sj, out])
