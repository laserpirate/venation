"""lamp_print_v01.py : print files for lamp mockups (Part B). A mockup mesh is loaded, never rebuilt: the artifact ID is engraved
inside the collar bore (0.45 mm deep, read from inside the foot), the checks run again on the cut mesh, and STL, plate 3MF, bed overlay
and check JSON go to 00_print/vena-lamp. The foot ring is only 2 to 3 mm wide, so an underside label at a readable size does not fit;
the bore wall is hidden once the lamp sits on its base. The window test piece has no bore: its three thicknesses are cut into its underside.
usage: python lamp_print_v01.py <specs.json> <key> [<key> ...]    No em dashes."""
import sys, os, json, glob, math, shutil
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'lamps')); import lamp_build_v01 as v1
import lamp_build_v03 as v3
MOCK = os.path.join(ROOT, '00_mockups', 'vena-lamp'); OUT = os.path.join(ROOT, '00_print', 'vena-lamp')


def glyphs(text, size):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from shapely.geometry import Polygon
    fp = FontProperties(family='DejaVu Sans', weight='bold'); x = 0.0; out = []
    for ch in text:
        tp = TextPath((0, 0), ch if ch != ' ' else 'n', size=size, prop=fp); bb = tp.get_extents()
        if ch != ' ':
            ps = [Polygon(p).buffer(0) for p in tp.to_polygons() if len(p) >= 4]; ps = [p for p in ps if p.area > 1e-4]; ps.sort(key=lambda p: -p.area); g = None
            for p in ps: g = p if g is None else (g.difference(p) if g.contains(p.representative_point()) else g.union(p))
            out.append((g, x - bb.x0, bb.width))
        x += bb.width + size * 0.14
    return out, x


def bore_label(text, r, collar):
    """cutters for text on the inside of a cylinder of radius r, readable from the axis: each glyph is a flat prism set 0.45 mm into the wall"""
    size = min(4.0, collar * 0.5); gl, total = glyphs(text, size); z0 = max(1.2, (collar - 0.73 * size) / 2); th = math.radians(-25.0); parts = []
    assert total < 2 * math.pi * r - 12, 'label longer than the bore'
    from shapely import affinity
    for g, dx, wdt in gl:
        tc = th - (dx + wdt / 2 + 0.0) / r                      # text runs toward decreasing bearing
        g2 = affinity.translate(g, -(g.bounds[0] + g.bounds[2]) / 2, 0)
        for q in (g2.geoms if hasattr(g2, 'geoms') else [g2]):
            m = trimesh.creation.extrude_polygon(q, 0.75)
            t = np.array([math.sin(tc), -math.cos(tc), 0.0]); rh = np.array([math.cos(tc), math.sin(tc), 0.0]); M = np.eye(4)
            M[:3, 0] = t; M[:3, 1] = [0, 0, 1]; M[:3, 2] = -rh; M[:3, 3] = rh * (r + 0.45) + [0, 0, z0]; m.apply_transform(M); parts.append(m)
    return parts, size


def main():
    specs = json.load(open(sys.argv[1], encoding='utf-8')); os.makedirs(OUT, exist_ok=True)
    for key in sys.argv[2:]:
        sp = specs[key]; cj = glob.glob(os.path.join(MOCK, sp['id'] + '_s*_check.json'))[0]; r0 = json.load(open(cj, encoding='utf-8')); stem = r0['stem']
        mesh = trimesh.load(os.path.join(MOCK, stem + '.stl')); F = v3.Form(sp['form']); label = sp['id'] + ' v01'; info = {}
        try:
            if sp.get('window_bands'):
                cut = []
                for txt, s in zip(('45', '65', '85'), (-20.0, 0.0, 20.0)):
                    c1 = v1.label_solid(txt, F.R - 3.5, depth=0.6, size=4.2); c1 = trimesh.util.concatenate(c1); c1.apply_transform(trimesh.transformations.rotation_matrix(math.pi + s / F.R - math.pi / 2, [0, 0, 1])); cut.append(c1)
                info = dict(label='45 65 85 under the foot (window thickness in hundredths of a mm)', where='underside, mirrored')
                cutters = cut
            else:
                cutters, size = bore_label(label, F.rbase, F.collar); info = dict(label=label, where='inside the collar bore, %.1f mm letters, 0.45 mm deep' % size)
            cu = trimesh.boolean.union(cutters, engine='manifold'); m3 = trimesh.boolean.difference([mesh, cu], engine='manifold')
            if m3.is_watertight and len(m3.faces) > 1000 and m3.body_count == 1: info['label_cut'] = True; info['label_volume_mm3'] = round(float(mesh.volume - m3.volume), 2); mesh = m3
            else: info['label_cut'] = 'rejected'
        except Exception as ex: info['label_cut'] = 'error ' + str(ex)[:160]
        mesh.vertices[:, 2] = np.where(np.abs(mesh.vertices[:, 2]) < 0.02, 0.0, mesh.vertices[:, 2])
        c = v1.checks(mesh, stem); c0 = r0['checks']
        c['grams_est'] = round(float(mesh.volume) * v1.PLA, 0); c['hours_est'] = round(c['grams_est'] / 22.0 + float(mesh.extents[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
        for q in ('least_window_mm', 'least_hole_mm', 'pass_rule'):
            if q in c0: c[q] = c0[q]
        field_ok = bool(c0['pass'])                       # skin, window and hole figures come from the pattern field of the mockup build; the mesh checks are re-run here
        c['pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_widest_strip_mm'] <= 1.0 and field_ok and info.get('label_cut') is True)
        mesh.export(os.path.join(OUT, stem + '.stl'))
        sc = trimesh.Scene(); m4 = mesh.copy(); m4.apply_translation([128 - (m4.bounds[0][0] + m4.bounds[1][0]) / 2, 128 - (m4.bounds[0][1] + m4.bounds[1][1]) / 2, 0])
        sc.add_geometry(m4, node_name=stem, geom_name=stem); sc.export(os.path.join(OUT, stem + '_plate.3mf')); v1.overlay_png(mesh, os.path.join(OUT, stem + '_bed.png'), stem, c)
        lit = os.path.join(MOCK, stem + '_lit.png')
        if os.path.exists(lit): shutil.copyfile(lit, os.path.join(OUT, stem + '_lit.png'))
        rep = dict(stem=stem, id=sp['id'], key=key, sheet=sp['sheet'], tile=sp['tile'], tech=sp['tech'], window_mm=r0['window_mm'], form=sp['form'], foot=r0['foot'], stats=r0['stats'], label=info, checks=c, tris=len(mesh.faces),
                   mockup_checks_pass=field_ok, sliced=False)
        json.dump(rep, open(os.path.join(OUT, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str)
        print(stem, 'PASS' if c['pass'] else 'FAIL', 'label', info.get('label_cut'), 'wt', c['watertight'], c['shells'], c['nonmanifold_edges'], 'strip', c['overhang_widest_strip_mm'], 'g', c['grams_est'], 'h', c['hours_est'], 'tris', len(mesh.faces))


if __name__ == '__main__': main()
