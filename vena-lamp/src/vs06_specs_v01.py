"""vs06_specs_v01.py : writes VS06_specs_v01.json, one entry per lamp piece of sheets VS06a and VS06b.
usage: python vs06_specs_v01.py    No em dashes."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
EGG2 = {'type': 'egg', 'base_in': 2.0, 'H': 190, 'W': 95}                       # the VS04-11 profile at 190 mm, foot fitted to the 2.0 in base
EGG6 = {'type': 'egg', 'base_in': 6.0, 'H': 220, 'W': 176, 'zc': 80, 'rtop': 50, 'foot_wall': 3.0}
S = {}
def add(key, sheet, tile, id_, tech, form, pattern, seed, note=None, window=0.85, free=None):
    S[key] = dict(id=id_, sheet=sheet, tile=tile, tech=tech, form=form, pattern=pattern, seed=seed, note=note, window_mm=window, free=free)

# ---- VS06a
add('a01', 'VS06a', 1, 'vena-lamp-egg--cells-VS04-12__01', 'T1', EGG2, {'kind': 'surface', 'cell_spacing': [10.3, 5.8], 'cell_w': [2.2, 1.3]}, 23, 'density 1x')
add('a02', 'VS06a', 2, 'vena-lamp-egg--cells-VS04-12__02', 'T1', EGG2, {'kind': 'surface', 'cell_spacing': [7.8, 4.4], 'cell_w': [1.9, 1.2]}, 23, 'density 2x')
add('a03', 'VS06a', 3, 'vena-lamp-egg--cells-VS04-12__03', 'T1', EGG2, {'kind': 'surface', 'cell_spacing': [6.6, 3.75], 'cell_w': [1.7, 1.2]}, 23, 'density 3x')
add('a04', 'VS06a', 4, 'vena-lamp-egg--closed-VS04-01__01', 'T1', EGG2, {'kind': 'surface', 'vein_spacing': [5.4, 4.2], 'rim_px': 4, 'roots': 4, 'vein_w': {'foot': [1.3, 4.2], 'rim': [1.2, 2.2]}}, 7, 'veins grown on the surface from four roots at the foot')
add('a05', 'VS06a', 5, 'vena-lamp-cyl--hybrid-VS04-07__01', 'T1', {'type': 'cyl', 'base_in': 2.25, 'H': 200}, {'kind': 'surface', 'vein_spacing': [13.0, 10.0], 'roots': 3, 'cell_spacing': [6.5, 4.2], 'cell_w': [1.5, 1.2], 'vein_w': {'foot': [1.8, 4.2], 'rim': [1.5, 2.6]}}, 7, 'regrown on the cylinder from three roots at the foot, cells fill')
add('a06', 'VS06a', 6, 'vena-lamp-cyl--cells-VS04-12__01', 'T1', {'type': 'cyl', 'base_in': 1.75, 'H': 165}, {'kind': 'surface', 'cell_spacing': [7.5, 4.2], 'cell_w': [1.7, 1.2]}, 23)
add('a07', 'VS06a', 7, 'vena-lamp-egg--cells-VS04-12__04', 'T2', EGG2, {'kind': 'surface', 'cell_spacing': [13.0, 5.3], 'cell_w': [4.0, 1.6], 'tear': 10}, 23, 'foot coarse, rim fine')
add('a08', 'VS06a', 8, 'vena-lamp-cyl--closed-VS04-01__01', 'T2', {'type': 'cyl', 'base_in': 2.0, 'H': 180}, {'kind': 'surface', 'vein_spacing': [19.0, 8.0], 'roots': 3, 'vein_w': {'foot': [3.5, 4.5], 'rim': [1.6, 1.6]}, 'tear': 10}, 7, 'foot coarse, rim fine')
add('a09', 'VS06a', 9, 'vena-lamp-egg--closed-VS04-01__02', 'T1', EGG6, {'kind': 'surface', 'vein_spacing': [6.5, 5.0], 'rim_px': 5, 'roots': 6, 'vein_w': {'foot': [1.4, 5.0], 'rim': [1.2, 2.4]}, 'tear': 22}, 7, '6 in base, 1.25 to 1')
add('a10', 'VS06a', 10, 'vena-lamp-cyl--cells-VS04-12__02', 'T1', {'type': 'cyl', 'base_in': 6.0, 'H': 200}, {'kind': 'surface', 'cell_spacing': [11.0, 5.5], 'cell_w': [2.2, 1.3], 'tear': 20}, 23, '6 in base, 1.27 to 1')
add('a11', 'VS06a', 11, 'vena-lamp-free--closed-tilt-VS04-01__01', 'T1', {'type': 'egg', 'base_in': 2.25, 'H': 215, 'W': 118, 'zc': 80, 'rtop': 34}, {'kind': 'surface', 'vein_spacing': [5.6, 4.4], 'rim_px': 4, 'roots': 3, 'tilt': 46, 'tear': 12, 'vein_w': {'foot': [1.3, 4.6], 'rim': [1.2, 2.0]}}, 11,
    'free', free='free: a wider egg cut on a slant, so the rim shows the inside of the far wall as the Hyphae photos do.')
add('a12', 'VS06a', 12, 'vena-lamp-free--hybrid-fine-VS04-12__01', 'T1', {'type': 'egg', 'base_in': 2.0, 'H': 228, 'W': 100, 'zc': 95, 'rtop': 22}, {'kind': 'surface', 'vein_spacing': [16.0, 11.0], 'roots': 5, 'cell_spacing': [5.2, 3.6], 'cell_w': [1.3, 1.2], 'vein_w': {'foot': [2.0, 4.6], 'rim': [1.6, 2.8]}, 'tear': 18}, 5,
    'free', free='free: the tallest egg (9 in), five trunks over the finest cells the window rule allows, to test hierarchy against density.', window=0.85)

# ---- VS06b : wraps. Wing = named veins of VS03-04 (fore) and VS03-08 (hind) stretched with the panel, secondaries and cells regrown at true size.
WING = lambda n, **k: dict({'kind': 'panels', 'count': n, 'patterns': ['L3_fore_s07', 'L3_hind_s07'] if n > 1 else ['L3_fore_s07'], 'fixed': 'named', 'vein_spacing': [13.0, 11.0], 'kill_k': 0.6,
                            'cell_spacing': [5.6, 4.4], 'cell_w': [1.4, 1.2], 'vein_w': {'foot': [1.6, 3.6], 'rim': [1.4, 2.4]}}, **k)
LEAF = lambda n, **k: dict({'kind': 'panels', 'count': n, 'patterns': ['L2_ovate_s07'], 'fixed': 'midrib', 'secondary_gap': 18.0, 'vein_spacing': [6.0, 5.2], 'vein_w': {'foot': [1.3, 4.4], 'rim': [1.2, 2.2]}}, **k)
EGGW = {'type': 'egg', 'base_in': 2.0, 'H': 200, 'W': 100}
CYLL = {'type': 'cyl', 'base_in': 2.25, 'H': 200}
for i, n in enumerate((1, 3, 6, 8)):
    add('b%02d' % (i + 1), 'VS06b', i + 1, 'vena-lamp-egg--wing-wrap%d-VS03-04__01' % n, 'T1', EGGW, WING(n), 7, 'wing wrap, %d panel%s, regrown' % (n, '' if n == 1 else 's'))
for i, n in enumerate((1, 3, 6, 8)):
    add('b%02d' % (i + 5), 'VS06b', i + 5, 'vena-lamp-cyl--leaf-wrap%d-VS02-04__01' % n, 'T1', CYLL, LEAF(n), 7, 'leaf wrap, %d panel%s, regrown' % (n, '' if n == 1 else 's'))
add('b09', 'VS06b', 9, 'vena-lamp-egg--wing-wrap1-VS03-04__02', 'T1', EGGW, WING(1, stored=True), 7, 'warped, not regrown')
add('b10', 'VS06b', 10, 'vena-lamp-egg--leaf-wrap3-VS02-04__01', 'T1', EGGW, LEAF(3), 7, 'leaf on egg, 3 panels, regrown')
add('b11', 'VS06b', 11, 'vena-lamp-cyl--wing-wrap6-VS03-04__01', 'T1', CYLL, WING(6), 7, 'wing on cylinder, 6 panels, regrown')
json.dump(S, open(os.path.join(HERE, 'VS06_specs_v01.json'), 'w', encoding='utf-8'), indent=1)
print(len(S), 'pieces')
