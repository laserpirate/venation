"""lamp_sheet_v01.py : read every *_check.json in a print folder, write the VS04 sheet spec and the README with print order.
usage: python lamp_sheet_v01.py <print_dir> <sheet.json> <title>. No em dashes."""
import sys, json, glob, os
d, out, title = sys.argv[1], sys.argv[2], sys.argv[3]; D = '·'; BT = chr(96)
R = [json.load(open(f, encoding='utf-8')) for f in sorted(glob.glob(os.path.join(d, 'VS04-*_check.json')))]
FORM = {'L1': 'egg 2:1, veins grown on the surface', 'L2': 'egg, six ovate leaf panels', 'L3': 'egg, eight Clubtail wing panels', 'L4': 'cylinder, disk study unrolled', 'L5': 'mound, blob outline lofted', 'L6': 'egg, cells only (control)'}
tiles = []
for r in R:
    c = r['checks']; mm = c['dims_mm']; inch = c['dims_in']
    tiles.append(dict(img=os.path.join(d, r['stem'] + '_render.png'), lines=[
        '%s %s %s %s seed %02d' % (r['tile'], D, r['id'], D, r['seed']), FORM[r['id']], 'source: ' + r['source_study'],
        '%.0f x %.0f x %.0f mm (%.2f x %.2f x %.2f in)' % (*mm, *inch), '%d g %s %.1f h estimated, not sliced' % (c['grams_est'], D, c['hours_est']),
        'holes %d %s cells kept closed %d' % (r['stats']['holes_open'], D, r['stats']['cells_kept_closed']), 'PASS' if c['pass'] else 'FAIL']))
json.dump(dict(title=title, id='VS04', cols=4, tiles=tiles), open(out, 'w', encoding='utf-8'), indent=1)
g = sum(r['checks']['grams_est'] for r in R); h = sum(r['checks']['hours_est'] for r in R)
L = ['# Lamps v01, print set (Phase P2)', '', 'Bambu P2S, PLA, 0.4 mm nozzle, 0.20 mm layers, no supports. One part per plate. Every part prints foot down, open top up.',
     'Grams and hours are estimates from the mesh (not sliced): grams = 1.24 g/cm3 x min(volume, area x 0.85 mm + 15 % of volume); hours = grams / 22 + layers x 8 s.', '',
     '| tile | file stem | L x W x H mm (in) | margin to bed edge mm | g est | h est | holes | check |', '|---|---|---|---|---|---|---|---|']
for r in R:
    c = r['checks']
    L.append('| %s | %s%s%s | %.0f x %.0f x %.0f (%.2f x %.2f x %.2f) | %.0f / %.0f | %d | %.1f | %d | %s |' % (r['tile'], BT, r['stem'], BT, *c['dims_mm'], *c['dims_in'], *c['margin_mm'], c['grams_est'], c['hours_est'], r['stats']['holes_open'], 'PASS' if c['pass'] else 'FAIL'))
L += ['', 'Set total: %d g estimated (about $%.2f at $0.033 per gram), %.1f h of printing, about %.1f h wall clock on 2 printers.' % (g, g * 0.033, h, h / 2), '',
      '## Files per part', 'stem.stl, stem_plate.3mf (part centred on the 256 mm bed), stem_bed.png (bed overlay with the 9 in and 8 in squares), stem_render.png, stem_check.json (every number above and the build statistics).', '',
      '## Print order', '1. VS04-11 (L6 control, lightest): it proves the hole roofs and the shell at 2.0 mm before anything else is printed.',
      '2. VS04-01 (L1, the reference form).', '3. One seed of each of L2, L3, L4, L5, in that order.', '4. The second seeds.', '',
      '## What the check means',
      '- watertight, one shell, 0 non-manifold edges; footprint inside 203 x 203 mm; height under 256 mm.',
      '- overhang: faces more than 45.5 degrees below horizontal, above the label (z over 0.75 mm). Each hole comes to a point at the top, and the mesh leaves a strip there; a part passes when the widest such strip is 1.0 mm or less. The total area and the largest patch are in the check file.',
      '- walls by construction: shell 2.0 mm, veins 2.0 to 4.5 mm wide and 1.5 mm proud, cell walls 2.4 mm, at least 4.7 mm of shell across a vein between two holes; an opening test at 2.0 mm on the shell mask reports the share of thinner area (pass at 1 % or less).',
      '- holes are cut only where a 3 mm circle fits; smaller cells stay closed. Hole roofs rise at 59 degrees or steeper. Hole edges carry a 0.8 mm chamfer inside and 0.4 mm outside.',
      '- foot: solid ring 18 mm tall, clear hole 50 mm (L4: 80 mm, L5 follows the outline; the ring is 10 or 16 mm wide), cable notch 3 x 4 mm with a pointed top, mirrored label 0.6 mm deep on the underside.', '',
      'Not checked here: a real slice. Run the lab profile in the print queue and read the first layers of VS04-11 before committing the set.']
open(os.path.join(d, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n'); print(len(R), 'parts', g, 'g', round(h, 1), 'h')
