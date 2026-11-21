"""dfly_sheet_v01.py : read the VS05 check files, write the sheet spec (top and three-quarter per variant) and the README.
usage: python dfly_sheet_v01.py <print_dir> <sheet.json> <title>. No em dashes."""
import sys, json, glob, os
d, out, title = sys.argv[1], sys.argv[2], sys.argv[3]; D = '·'
R = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(d, 'VS05-*_check.json')))]
NAME = {'D1': 'hybrid fab wings (named ribs, grown veins, cells)', 'D2': 'cells fab wings (the Stage 1 picks VS03-04, VS03-08)'}
tiles = []; n = 0
for r in R:
    c = r['checks']; w = r['stats']['wings']
    verdict = 'PASS' if c['pass'] else ('FAIL: wings pass, body keeps the E1 overhang (%.0f mm2)' % c['overhang_mm2_total'] if c['wings_pass'] else 'FAIL')
    for view, suf in (('top view', '_top.png'), ('three-quarter view', '_render.png')):
        n += 1
        tiles.append(dict(img=os.path.join(d, r['stem'] + suf), lines=[
            'VS05-%02d %s %s %s %s' % (n, D, r['id'], D, view), NAME[r['id']], 'E1 Clubtail print body at 3x (factor %.4f on the source)' % r['stats']['factor_on_source'],
            '%.0f x %.0f x %.0f mm (%.2f x %.2f x %.2f in)' % (*c['dims_mm'], *c['dims_in']), '%d g %s %.1f h estimated, not sliced' % (c['grams_est'], D, c['hours_est']),
            'open cells: fore %d, hind %d per wing %s kept closed %d, %d' % (w['fore']['holes'], w['hind']['holes'], D, w['fore']['cells_kept_closed'], w['hind']['cells_kept_closed']), verdict]))
json.dump(dict(title=title, id='VS05', cols=2, tile_px=700, tiles=tiles), open(out, 'w', encoding='utf-8'), indent=1)
g = sum(r['checks']['grams_est'] for r in R); h = sum(r['checks']['hours_est'] for r in R)
L = ['# Dragonfly with venation wings v01, print set (Phase P3)', '',
     'The E1 Skillet Clubtail print body with its solid wing slabs replaced by venation wings. Bambu P2S, PLA, 0.20 mm layers. One part per plate, flat on the bed as modelled: belly, feet and wings down. No rotation on the plate was needed.', '',
     '| part | file stem | L x W x H mm (in) | margin to bed edge mm | g est | h est | open cells per wing (fore, hind) | check |', '|---|---|---|---|---|---|---|---|']
for r in R:
    c = r['checks']; w = r['stats']['wings']
    L.append('| %s | %s | %.0f x %.0f x %.0f (%.2f x %.2f x %.2f) | %.0f / %.0f | %d | %.1f | %d, %d | %s |' % (r['id'], r['stem'], *c['dims_mm'], *c['dims_in'], *c['margin_mm'], c['grams_est'], c['hours_est'], w['fore']['holes'], w['hind']['holes'],
             'PASS' if c['pass'] else 'FAIL (body overhang %.0f mm2; new wings %.1f mm2)' % (c['overhang_mm2_total'], c['overhang_mm2_new_wings'])))
L += ['', 'Set total: %d g estimated (about $%.2f), %.1f h, about %.1f h wall clock on 2 printers. Estimates from the mesh, not sliced.' % (g, g * 0.033, h, h / 2), '',
      '## Read this before printing',
      '- Both parts FAIL the no-supports rule, and the cause is the body, not the wings. The E1 body has legs and rounded undersides that face down more than 45 degrees (about 2090 mm2 on the source at this scale). This build was told to leave the body unchanged apart from scale. The new wings add 0.0 mm2: they are flat prisms on the bed.',
      '- The E1 file printed before with these legs; whether it needs supports here is a slicer and owner call. Nothing in this folder claims the body is support-free.',
      '- The wings are mostly closed. Nine named ribs at 3 mm fill most of a 21 mm chord, so few cells clear the 3 mm rule (see the counts above).', '',
      '## What was built',
      '- Scale 3.0 on the insect; the source file is the insect at 2.9, so the factor on the source is 1.0345. Overall 168 mm long, span 179 mm (the prompt expected about 189; 63 mm x 3 ignores the sweep of the wings, and the source at 2.9 spans 172.2).',
      '- Wings: membrane 2.0 mm, named fab ribs 3.0 wide and 2.5 tall on top of it, grown veins (D1 only) 2.0 wide and 1.5 tall, pterostigma solid at rib height, a 2.0 mm rim all round, 2.0 mm of membrane between open cells.',
      '- The old slabs are cut away under z 4.1 inside the wing outlines; whatever stood on them (feet, gussets, the thorax floor) is put back as straight pads down to the bed, so the feet over the wings stay attached.',
      '- No fillet under the wing roots: the wings lie on the bed, so there is no underside to fillet. The roots run under the thorax and fuse with it.',
      '- Mirrored label 0.6 mm deep under the thorax.', '',
      '## Print order', '1. D2 (cells fab), then D1.']
open(os.path.join(d, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n'); print(len(R), 'parts', g, 'g', round(h, 1), 'h')
