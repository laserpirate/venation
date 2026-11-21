"""print_readme_v01.py : README.md for 00_print/vena-lamp, vena-dfly and vena-land, and SLICE_NOTES_v01.md, from the check files.
Run from the project root. No em dashes."""
import io, json, glob, os
def w(path, s): io.open(path, 'w', encoding='utf-8', newline='\n').write(s)
COMMON = '''Machine: Bambu P2S, 0.4 mm nozzle, 0.20 mm layers, no supports, one part per plate. Later pieces may move to an Objet 260 or an X1 Carbon; nothing here is prepared for those.
Nothing in this folder has been sliced. PASS means the mesh checks passed; grams and hours are estimates from mesh volume.
'''
# ------------------------------------------------------------------ lamps
D = '00_print/vena-lamp'; rows = []
for f in sorted(glob.glob(D + '/*_check.json')):
    r = json.load(io.open(f, encoding='utf-8')); c = r['checks']; rows.append(r)
def tile(r): return 'test piece' if r['tile'] == 0 else '%s-%02d' % (r['sheet'], r['tile'])
test = [r for r in rows if r['tile'] == 0]; first = [r for r in rows if r['sheet'] == 'VS06a' and r['tile'] == 2]; rest = sorted([r for r in rows if r not in test + first], key=lambda r: (r['checks']['hours_est'], r['stem']))
order = test + first + rest; G = sum(r['checks']['grams_est'] for r in order); H = sum(r['checks']['hours_est'] for r in order)
def techs(r):
    if r['tile'] == 0: return 'T1, windows 0.45, 0.65, 0.85 mm'
    return {'T1': 'T1 window 0.85 mm', 'T2': 'T2 open, graded', 'T1T2': 'T1 below, open above'}[r['tech']]
def least(r):
    c = r['checks']; out = []
    if 'least_window_mm' in c: out.append('window %.1f' % c['least_window_mm'])
    if 'least_hole_mm' in c: out.append('hole %.1f' % c['least_hole_mm'])
    return ', '.join(out)
s = '# vena-lamp, print files\n\n' + COMMON
s += '''Filament: white PLA is what the lab machines carry. These pieces are drawn to be lit from inside, so a transparent or translucent PLA is the intended material; the filament choice is open. A polycarbonate filament was named for the clear pieces; the lab P2S takes unmodified PLA only, so nothing here assumes it.
Base: each foot sleeves over a plain cylinder of the named diameter (internal diameter = base + 0.5 mm), light inside, cable through the 3 x 4 mm notch. That base is an assumption; no product has been named.
Every part prints foot down, open top up. The artifact ID is engraved inside the collar bore (0.45 mm deep), because the foot ring is 2 to 3 mm wide and an underside label would not be readable; the test piece has 45, 65, 85 cut into its underside.

## Print order
The test piece first, then VS06a-02, then the rest by estimated hours, shortest first.

| # | sheet tile | file stem | technique | L x W x H mm (in) | margin to bed edge mm | least mm | g est | h est | check |
|---|---|---|---|---|---|---|---|---|---|
'''
for i, r in enumerate(order):
    c = r['checks']; d = c['dims_mm']; di = c['dims_in']
    s += '| %d | %s | `%s` | %s | %.0f x %.0f x %.0f (%.2f x %.2f x %.2f) | %s / %s | %s | %d | %.1f | %s |\n' % (i + 1, tile(r), r['stem'], techs(r), d[0], d[1], d[2], di[0], di[1], di[2], c['margin_mm'][0], c['margin_mm'][1], least(r), c['grams_est'], c['hours_est'], 'PASS' if c['pass'] else 'FAIL')
s += '\nSet total: %d parts, %d g estimated (about $%.2f at $0.033 per gram), %.1f h of printing, about %.1f h wall clock on 2 printers.\n' % (len(order), G, G * 0.033, H, H / 2)
s += '''
## The test piece
`vena-lamp-test--windows-VS06a-01__01`: a 60 x 40 mm curved patch of the VS06a-01 pattern, standing on a 7 mm foot. Three bands of windows side by side: 0.45 mm, 0.65 mm, 0.85 mm, marked 45, 65, 85 under the foot. Print it in the filament meant for the lamps, hold it against the light, and pick the thinnest band that is closed everywhere and does not string. Every lamp here is built at 0.85 mm; a thinner window means a rebuild.

## Which pieces are fine work
All of them. The lab recommends 2 mm walls; these go under it on purpose:
- T1 window: skin 0.85 mm, ribs from 1.2 mm wide (2.0 mm deep plus relief).
- T2 open, graded (VS06a-07, VS06a-08): veins taper to 1.6 mm and holes to 2.0 mm above mid height.
- T1 below, open above (VS06c-06, 07, 09): ribs from 1.6 mm, holes from 2.0 mm, windows 0.85 mm in the lowest third.

## What was checked, and what was not
Checked on every mesh in this folder, after the label cut and after an STL reload: watertight, one shell, no non-manifold edges, footprint inside 203 x 203 mm, height under 256 mm, no down-facing strip wider than 1.0 mm (faces over 45.5 degrees, above the first 0.75 mm). Window thickness, least window and least hole come from the pattern field of the build; two meshes were also measured by rays (least wall 0.81 and 0.84 mm).
Not checked: a slice. Whether a 0.85 mm skin prints as two clean lines, where the seam lands, stringing across windows and open cells, and how the rim tips come out are unknown until the test piece and VS06a-02 are printed. Under every rib the skin is thicker than 0.85 mm for 1 to 2 mm (a 42 degree chamfer, the price of no supports), so a window glows less evenly near its top edge than the renders show.

## Included, and left out
- All twelve pieces of VS06a.
- From VS06b the 1 and 3 panel wraps. The owner named the wing wraps (VS06b-01, 02, 09). The leaf wraps (VS06b-05, 06, 10) are included on a reading of his note, not on his word.
- From VS06c every piece that passes: the four oblique rims, the wide cylinder, and three with windows below and open cells above (VS06c-06, 07, 09).
- Gallery only, no print files: VS06b-03, 04, 07, 08, 11 (superseded by the oblique rim versions) and VS06c-05 (its saved STL was not watertight on reload; VS06c-09 is the same design rebuilt).

## Files per part
stem.stl, stem_plate.3mf (centred on the 256 mm bed), stem_bed.png (bed overlay with the 9 in and 8 in squares), stem_lit.png (lit from inside, a stand-in material), stem_render.png (matte), stem_check.json. `SLICE_NOTES_v01.md` has the slicer settings for the first two prints; `sliced\\` is empty and waits for sliced files.
'''
w(D + '/README.md', s)
t = test[0]; a2 = first[0]
w(D + '/SLICE_NOTES_v01.md', '''# Slice notes v01: the test piece and VS06a-02

For `%s` and `%s`. Slice both in SimplyPrint and save the sliced files into `sliced\\`. Nothing else in this folder depends on them.

## Settings
- Profile: start from the Fab Lab profile `FabLab Default` in SimplyPrint (fine-detail if the default leaves gaps in the windows).
- Layer height 0.20 mm. Nozzle 0.4 mm.
- Wall generator: Arachne, if the profile allows the change. Classic walls drop features under two line widths; Arachne varies the line width and keeps a 0.45 or 0.65 mm skin as one line.
- Seam: aligned or back. Random scatters blobs over the windows.
- Supports: off. Brim: only if the collar lifts on a first try.
- Infill does not matter: no wall here is thick enough to carry any.

## What to look for in the slice preview
- Every window is there, as one or two wall lines, in every layer. Scrub through the height of one cell on each band of the test piece.
- No gap where a window meets a rib. A missing line there is a slit in the print.
- On the test piece the 0.45 mm band is the one most likely to vanish. If it is missing with Arachne on, that thickness is out for this printer and profile; note it.
- On VS06a-02 look at the rim tips last: single tips under 1.2 mm wide may be dropped by the slicer. That changes the rim, not the lamp.
- Estimated time and filament from the slicer replace the mesh estimates in the README (%d g, %.1f h for VS06a-02).
''' % (t['stem'], a2['stem'], a2['checks']['grams_est'], a2['checks']['hours_est']))
os.makedirs(D + '/sliced', exist_ok=True)
print('lamp', len(order), G, round(H, 1), [tile(r) for r in order][:4])
# ------------------------------------------------------------------ dragonfly
D = '00_print/vena-dfly'; s = '# vena-dfly, print files\n\n' + COMMON
s += 'Filament: white PLA as loaded; a transparent or translucent PLA shows the wing membrane against light. The filament choice is open.\nPrint flat, belly and wings on the bed. The artifact ID is cut mirrored into the bed face under the thorax and abdomen, 0.6 mm deep.\n\n| file stem | wings | L x W x H mm (in) | margin to bed edge mm | g est | h est | down-facing mm2, widest strip mm | check |\n|---|---|---|---|---|---|---|---|\n'
tg = th = 0
for f in sorted(glob.glob(D + '/*_check.json')):
    r = json.load(io.open(f, encoding='utf-8')); c = r['checks']; d = c['dims_mm']; di = c['dims_in']; tg += c['grams_est']; th += c['hours_est']; st = r['stats']
    s += '| `%s` | %s | %.0f x %.0f x %.0f (%.2f x %.2f x %.2f) | %s / %s | %d | %.1f | %.0f, %.2f | %s |\n' % (r['stem'], 'open: VS03-01 fore, VS03-05 hind' if '--open-' in r['stem'] else 'cells fab: VS03-04 fore, VS03-08 hind', d[0], d[1], d[2], di[0], di[1], di[2], c['margin_mm'][0], c['margin_mm'][1], c['grams_est'], c['hours_est'], c['overhang_mm2'], c['overhang_widest_strip_mm'], 'PASS' if c['pass'] else 'FAIL')
s += '\nBoth: %d g estimated (about $%.2f), %.1f h, about %.1f h wall clock on 2 printers. Print order: the open variant first; its ribs are fewer and wider apart.\n' % (tg, tg * 0.033, th, th / 2)
s += '''
## What changed against v01
- Body: v01 kept the E1 body as it was and failed the no-supports rule (1894 mm2 of down-facing faces). Here every layer rests on the one under it: 45 degree chamfers under the legs and the rounded undersides, and webs 0.75 mm wide down to the bed where a chamfer alone would end in mid air. %.1f cm3 added to %.1f. The plan outline is unchanged; from the side the legs now stand on thin webs.
- Wings: a closed membrane 0.4 mm thick (two layers) with ribs 2.0 to 3.6 mm wide and 1.2 to 3.0 mm tall, wider and taller where the vein carries more. No cell is opened.
- Eyes: hexagonal facets, 1.6 mm pitch, 0.3 mm relief, left off where the eye surface looks down or into the head.

## Fine work, below the lab minimum
The membrane (0.4 mm) and the webs under the legs (0.75 mm). Both are under the 2 mm recommendation on purpose.

## What was checked, and what was not
Checked: watertight, one shell, no non-manifold edges, footprint, height, no down-facing strip wider than 1.0 mm. The remaining down-facing area is the rounded smoothing of the grid and the roofs of the label letters, in patches of about 1 mm2.
Not checked: a slice. The vein sets were thinned to fit 2 mm ribs on a 21 mm chord, so the wings carry far fewer veins than the studies they are named for; the counts are in each check file. The body was rebuilt on a 0.25 mm grid, so it is slightly softer than the E1 mesh.

## Files per variant
stem.stl, stem_plate.3mf, stem_bed.png, stem_top.png and stem_tq.png (matte), stem_backlit.png (left wings over a light table, a stand-in material), stem_check.json.
''' % (st['body_volume_added_cm3'], st['body_volume_source_cm3'])
w(D + '/README.md', s); print('dfly', tg, th)
# ------------------------------------------------------------------ land
D = '00_print/vena-land'; s = '# vena-land, print files\n\n' + COMMON
s += 'Filament: white PLA as loaded; the filament choice is open.\nFour tiles, one per typology, each a 100 x 100 mm solid on a 3 mm base, flat side down. Pattern studies: no scale, no vertical exaggeration set. The artifact ID is cut mirrored into the underside, 0.6 mm deep.\n\n| file stem | typology | L x W x H mm (in) | g est | h est | features under 2 mm, percent of plan | check |\n|---|---|---|---|---|---|---|\n'
tg = th = 0; rr = [json.load(io.open(f, encoding='utf-8')) for f in sorted(glob.glob(D + '/*_check.json'))]
for r in sorted(rr, key=lambda r: r['checks']['hours_est']):
    c = r['checks']; d = c['dims_mm']; di = c['dims_in']; tg += c['grams_est']; th += c['hours_est']
    s += '| `%s` | %s | %.0f x %.0f x %.0f (%.2f x %.2f x %.2f) | %d | %.1f | %.2f | %s |\n' % (r['stem'], r['typology'], d[0], d[1], d[2], di[0], di[1], di[2], c['grams_est'], c['hours_est'], c['features_under_2mm_pct'], 'PASS' if c['pass'] else 'FAIL')
s += '\nSet: %d g estimated (about $%.2f), %.1f h, about %.1f h wall clock on 2 printers. Grams assume 15 percent infill under a 0.85 mm skin. Print order as listed, shortest first.\n' % (tg, tg * 0.033, th, th / 2)
s += '''
## The rule behind each typology
Veins are structure, cells are fill.
- berm: veins are ridges; crest height follows Murray width, sides fall 1 in 1.5.
- waveform mounds: cells are mounds, taller where the cell is larger; veins are the swales between them.
- pond cells: cells are basins, deeper where the cell is larger; veins are the dikes at plateau level.
- terraces: distance from the primary veins cut into steps, 3 mm tread, 2 mm riser.

## What was checked, and what was not
Checked: watertight, one shell, no non-manifold edges, footprint, height. A heightfield has no overhangs; the only down faces are the roofs of the label letters.
Not checked: a slice. Ridge crests and dike tops narrower than 2 mm are reported per tile, not removed. On the waveform cells tile they are 7.7 percent of the plan; expect soft crests there.

## The other twelve
All sixteen studies of sheet VS08 are in `00_export_svg\\vena-land\\` as a 16 bit heightfield PNG (0 = 0 mm, 65535 = 20 mm), a contour SVG at 1 mm and a graph.json. Only these four are solids.

## Files per tile
stem.stl, stem_plate.3mf, stem_bed.png, stem_render.png (matte), stem_check.json.
'''
w(D + '/README.md', s); print('land', tg, th)
