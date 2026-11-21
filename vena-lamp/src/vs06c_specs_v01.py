"""vs06c_specs_v01.py : writes VS06c_specs_v01.json, the eight VS06c pieces (owner's reply at the stop, ADD-2) and the window test piece.
usage: python vs06c_specs_v01.py    Built by lamp_build_v03.py. No em dashes."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = {}
def add(key, tile, id_, tech, form, pattern, seed, note=None, window=0.85, **kw):
    S[key] = dict(dict(id=id_, sheet='VS06c', tile=tile, tech=tech, form=form, pattern=pattern, seed=seed, note=note, window_mm=window, free=None), **kw)
EGG2 = {'type': 'egg', 'base_in': 2.0, 'H': 190, 'W': 95}
EGGW = {'type': 'egg', 'base_in': 2.0, 'H': 200, 'W': 100}
CYLL = {'type': 'cyl', 'base_in': 2.25, 'H': 200}
WING = lambda n, **k: dict({'kind': 'panels', 'count': n, 'patterns': ['L3_fore_s07', 'L3_hind_s07'] if n > 1 else ['L3_fore_s07'], 'fixed': 'named', 'vein_spacing': [13.0, 11.0], 'kill_k': 0.6,
                            'cell_spacing': [5.6, 4.4], 'cell_w': [1.4, 1.2], 'vein_w': {'foot': [1.6, 3.6], 'rim': [1.4, 2.4]}}, **k)
LEAF = lambda n, **k: dict({'kind': 'panels', 'count': n, 'patterns': ['L2_ovate_s07'], 'fixed': 'midrib', 'secondary_gap': 18.0, 'vein_spacing': [6.0, 5.2], 'vein_w': {'foot': [1.3, 4.4], 'rim': [1.2, 2.2]}}, **k)
# 1. oblique rim on the many-panel wraps: one plane through the top, the cut edge is a rib
CE = {'deg': 32, 'zc': 158, 'phi_deg': 200}; CC = {'deg': 38, 'zc': 166, 'phi_deg': 200}
add('c01', 1, 'vena-lamp-egg--wing-wrap6-VS03-04__02', 'T1', EGGW, WING(6, cut=CE), 7, 'wing wrap, 6 panels, oblique rim 32 deg')
add('c02', 2, 'vena-lamp-egg--wing-wrap8-VS03-04__02', 'T1', EGGW, WING(8, cut=CE), 7, 'wing wrap, 8 panels, oblique rim 32 deg')
add('c03', 3, 'vena-lamp-cyl--leaf-wrap6-VS02-04__02', 'T1', CYLL, LEAF(6, cut=CC), 7, 'leaf wrap, 6 panels, oblique rim 38 deg')
add('c04', 4, 'vena-lamp-cyl--leaf-wrap8-VS02-04__02', 'T1', CYLL, LEAF(8, cut=CC), 7, 'leaf wrap, 8 panels, oblique rim 38 deg')
# 2. window below, open above (ribs 1.6 mm and up, as T2 above the split)
add('c05', 5, 'vena-lamp-egg--cells-winopen-VS04-12__01', 'T1T2', EGG2, {'kind': 'surface', 'cell_spacing': [8.2, 5.6], 'cell_w': [2.4, 1.6], 'tear': 10}, 23, 'window below, open above · VS06a-02 lineage', reload_fail='FAIL as a print file: the saved STL is not watertight on reload (pinched vertices); superseded by VS06c-09')
add('c09', 9, 'vena-lamp-egg--cells-winopen-VS04-12__02', 'T1T2', EGG2, {'kind': 'surface', 'cell_spacing': [8.4, 5.8], 'cell_w': [2.4, 1.6], 'tear': 10}, 23, 'window below, open above · VS06a-02 lineage, rebuilt')
add('c06', 6, 'vena-lamp-free--hybrid-fine-winopen-VS04-12__01', 'T1T2', {'type': 'egg', 'base_in': 2.0, 'H': 228, 'W': 100, 'zc': 95, 'rtop': 22},
    {'kind': 'surface', 'vein_spacing': [16.0, 11.0], 'roots': 5, 'cell_spacing': [6.4, 5.2], 'cell_w': [1.8, 1.6], 'vein_w': {'foot': [2.2, 4.6], 'rim': [1.8, 2.8]}, 'tear': 14}, 5, 'window below, open above · VS06a-12 lineage')
add('c07', 7, 'vena-lamp-egg--wing-wrap3-winopen-VS03-04__01', 'T1T2', EGGW, WING(3, cell_spacing=[6.6, 5.6], cell_w=[1.8, 1.6], vein_w={'foot': [1.8, 3.6], 'rim': [1.6, 2.4]}, rim_w=2.0), 7, 'window below, open above · VS06b-02 lineage')
# 3. wide cylinder
add('c08', 8, 'vena-lamp-cyl--cells-wide-VS04-12__01', 'T1', {'type': 'cylw', 'base_in': 2.25, 'H': 175, 'W': 100}, {'kind': 'surface', 'cell_spacing': [8.0, 4.6], 'cell_w': [1.9, 1.2], 'tear': 14}, 23, 'wide cylinder, 100 mm, shoulder to the 2.25 in collar')
# window test piece: a 60 x 40 mm patch of the VS06a-01 pattern at the egg's widest radius, three window thicknesses
add('t01', 0, 'vena-lamp-test--windows-VS06a-01__01', 'T1', {'type': 'cyl', 'base_in': 3.2, 'H': 46, 'R': 47.5, 'foot_w': 7.0, 'collar_in': 0.16},
    {'kind': 'surface', 'cell_spacing': [9.0, 9.0], 'cell_w': [1.6, 1.6], 'sector_mm': 30.0}, 23, 'test piece: windows 0.45, 0.65, 0.85 mm', window_bands=[0.45, 0.65, 0.85])
json.dump(S, open(os.path.join(HERE, 'VS06c_specs_v01.json'), 'w', encoding='utf-8'), indent=1)
print(len(S), 'pieces')
