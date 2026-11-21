"""dfly_build_v01.py : the E1 Clubtail print body with venation wings (Phase P3, rows VLD-).
The source STL is never edited: it is loaded, scaled, its solid wing slabs are cut away, and wings built from page patterns
(graph.json contract) are fused on. Wings lie flat on the bed: membrane 2.0 mm, named ribs 3.0 wide x 2.5 tall on top,
grown veins 2.0 wide x 1.5 tall, cells open where a 3 mm circle fits, pterostigma solid.
usage: python dfly_build_v01.py <source.stl> <patterns_dir> <variant D1|D2> <fore pattern> <hind pattern> <out_dir> <tile_id> <mode_field>
Frame as E1: +X head to tail, +Y left wing, +Z up, mm. No em dashes."""
import sys, os, json, math, time
import numpy as np, trimesh, manifold3d as m3
from shapely.geometry import Polygon, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity

SRC_SCALE = 2.9                 # the E1 print file is the insect at 2.9
SCALE = 3.0                     # this build
FORE_ROOT_X, HIND_ROOT_X = 9.0, 12.8          # E1: HEAD_LEN + 4.0, HEAD_LEN + 7.8 (insect mm)
FORE_SWEEP, HIND_SWEEP = -7.0, 10.0           # E1 v02 sweeps, degrees
MEMBRANE, RIB_W, RIB_H, VEIN_W, VEIN_H = 2.0, 3.0, 2.5, 2.0, 1.5
WALL = 2.0; HOLE_MIN = 3.0
CUT_Z = 4.1                     # the old slabs and their veins end below this at 3.0 scale
PLA = 1.24e-3


def polys(g):
    if g.is_empty: return []
    if isinstance(g, Polygon): return [g]
    return [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon) and p.area > 1e-6]


def cs(g):
    rings = []
    for p in polys(g):
        rings.append(np.array(p.exterior.coords)[:-1])
        for i in p.interiors: rings.append(np.array(i.coords)[:-1])
    return m3.CrossSection(rings, m3.FillRule.EvenOdd)


def prism(g, z0, z1): return m3.Manifold.extrude(cs(g), z1 - z0).translate([0, 0, z0])


def wing_2d(pat_path):
    """a wing in its own frame at build scale: U along the span from the hinge, V toward the leading edge, mm"""
    pat = json.load(open(pat_path, encoding='utf-8')); g = pat['graph']; w = g['wing']; mpu = g['mm_per_unit']
    assert abs(mpu * 880 - 30 * SCALE) < 1e-6, 'pattern must be exported at forewing %g mm' % (30 * SCALE)
    def T(x, y): return (x - w['x0'] * mpu, w['vm'] * SCALE - (y - w['y0'] * mpu))
    out = Polygon([T(*q) for q in pat['outline']]).buffer(0)
    N = g['nodes']; P = [T(n['x'], n['y']) for n in N]
    named, grown = [], []; ptero = []
    for e in g['edges']:
        a, b = e['parent'], e['child']; seg = LineString([P[a], P[b]])
        if seg.length < 1e-6: continue
        (named if e['kind'] == 'fixed' else grown).append(seg)
    ptero = [P[i] for i, n in enumerate(N) if n.get('name') == 'pterostigma']
    cells = [Polygon([T(*q) for q in c]).buffer(0) for c in g['cells'] if len(c) >= 3]
    return dict(outline=out, named=named, grown=grown, ptero=Polygon(ptero).buffer(0) if len(ptero) >= 3 else None, cells=cells, kind=w['kind'], stat=pat.get('stat'))


def wing_parts(W):
    O = W['outline']
    ribs = unary_union([s.buffer(RIB_W / 2, cap_style=1) for s in W['named']]).intersection(O) if W['named'] else Polygon()
    veins = unary_union([s.buffer(VEIN_W / 2, cap_style=1) for s in W['grown']]).intersection(O) if W['grown'] else Polygon()
    solid = unary_union([ribs, veins] + ([W['ptero'].buffer(0.5)] if W['ptero'] is not None else []))
    inner = O.buffer(-WALL)                                 # a 2 mm rim all round
    holes = []; closed = 0
    for c in W['cells']:
        h = c.buffer(-WALL / 2).difference(solid).intersection(inner)
        for q in polys(h):
            if q.buffer(-HOLE_MIN / 2).is_empty: closed += 1; continue
            q = q.buffer(-0.6).buffer(0.6)                  # round the corners
            for r in polys(q):
                if not r.buffer(-HOLE_MIN / 2).is_empty: holes.append(r)
                else: closed += 1
    H = unary_union(holes) if holes else Polygon()
    return dict(membrane=O.difference(H), ribs=ribs, veins=veins, ptero=W['ptero'], n_holes=len(holes), n_closed=closed, hole_area=H.area, area=O.area)


def place(g, kind, side):
    """wing frame to the E1 world frame at build scale"""
    sw = math.radians(FORE_SWEEP if kind == 'fore' else HIND_SWEEP); rx = (FORE_ROOT_X if kind == 'fore' else HIND_ROOT_X) * SCALE
    # x = rx + U sin(sweep) - V ; y = side * U cos(sweep)
    return affinity.affine_transform(g, [math.sin(sw), -1.0, side * math.cos(sw), 0.0, rx, 0.0])


def label_cut(text, cx, cy, size=4.0, depth=0.6):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), text, size=size, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    ps = [Polygon(p).buffer(0) for p in tp.to_polygons() if len(p) >= 4]; ps = [p for p in ps if p.area > 1e-4]; ps.sort(key=lambda p: -p.area); g = None
    for p in ps: g = p if g is None else (g.difference(p) if g.contains(p.representative_point()) else g.union(p))
    b = g.bounds; g = affinity.translate(g, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2); g = affinity.scale(g, -1, 1, origin=(0, 0))      # mirrored: reads right from below
    g = affinity.translate(g, cx, cy); return prism(g, -0.2, depth), g.bounds


def to_trimesh(M):
    o = M.to_mesh(); return trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False)


def overhang(mesh, zmin=0.75):
    n = mesh.face_normals; c = mesh.triangles_center; a = mesh.area_faces
    return (n[:, 2] < -math.sin(math.radians(45.5))) & (c[:, 2] > zmin), a, c


def main():
    src, pdir, variant, pf, ph, outdir, tile, mode_field = sys.argv[1:9]; t0 = time.time(); os.makedirs(outdir, exist_ok=True)
    k = SCALE / SRC_SCALE
    m = trimesh.load(src); body = m3.Manifold(m3.Mesh(vert_properties=np.asarray(m.vertices * k, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
    assert str(body.status()).endswith('NoError'), body.status()
    body = max(body.decompose(), key=lambda q: q.volume())                  # the source carries two zero-volume specks
    src_mesh = to_trimesh(body); d0, a0, c0 = overhang(src_mesh)
    W = {'fore': wing_2d(os.path.join(pdir, pf)), 'hind': wing_2d(os.path.join(pdir, ph))}
    parts = {kd: wing_parts(W[kd]) for kd in W}
    cut_region = []; solids = []; wing_foot = []
    for kd in ('fore', 'hind'):
        for side in (1, -1):
            O = place(W[kd]['outline'], kd, side); cut_region.append(O.buffer(1.0)); wing_foot.append(O)
            p = parts[kd]
            solids.append(prism(place(p['membrane'], kd, side), 0, MEMBRANE))
            if not p['ribs'].is_empty: solids.append(prism(place(p['ribs'], kd, side), 0, MEMBRANE + RIB_H))
            if not p['veins'].is_empty: solids.append(prism(place(p['veins'], kd, side), 0, MEMBRANE + VEIN_H))
            if p['ptero'] is not None: solids.append(prism(place(p['ptero'].intersection(W[kd]['outline']), kd, side), 0, MEMBRANE + RIB_H))
    cut_region = unary_union(cut_region)
    # the old slabs: everything of the source under CUT_Z inside the wing footprints goes; what stood on the slabs is put back as straight pads
    sec = body.slice(CUT_Z)                                                 # CrossSection of the body just above the old slabs
    pads = m3.Manifold.extrude(sec ^ cs(cut_region), CUT_Z + 0.1)
    body_cut = body - prism(cut_region, -1.0, CUT_Z)
    M = m3.Manifold.batch_boolean([body_cut, pads] + solids, m3.OpType.Add)
    # mirrored label under the thorax
    lab_text = '%s v01 3x' % variant; lc, lb = label_cut(lab_text, (5.0 + 4.75) * SCALE + 6.0, 0.0)
    M = M - lc
    M = M.simplify(0.01)
    comps = sorted(M.decompose(), key=lambda q: -q.volume()); dropped = [round(q.volume(), 3) for q in comps[1:]]; M = comps[0]
    mesh = to_trimesh(M); mesh.vertices[:, 2] = np.where(np.abs(mesh.vertices[:, 2]) < 1e-4, 0.0, mesh.vertices[:, 2])
    stem = '%s_%s_clubtail-3x_s07_%dmm_v01' % (tile, mode_field, round(mesh.extents[1]))
    c = {}
    c['watertight'] = bool(mesh.is_watertight); c['shells'] = int(mesh.body_count)
    e = mesh.edges_sorted; _, cnt = np.unique(e, axis=0, return_counts=True); c['nonmanifold_edges'] = int((cnt != 2).sum())
    ext = mesh.extents; c['dims_mm'] = [round(float(x), 1) for x in ext]; c['dims_in'] = [round(float(x) / 25.4, 2) for x in ext]
    c['footprint_ok'] = bool(ext[0] <= 203 and ext[1] <= 203); c['margin_mm'] = [round((256 - float(ext[0])) / 2, 1), round((256 - float(ext[1])) / 2, 1)]; c['height_ok'] = bool(ext[2] <= 256)
    d1, a1, c1 = overhang(mesh)
    from shapely import contains_xy
    foot = unary_union(wing_foot).buffer(0.2)
    inw = contains_xy(foot, c1[:, 0], c1[:, 1]) & (c1[:, 2] < CUT_Z - 0.05)       # faces of the new wings and of the pads under the old slab line
    c['overhang_mm2_total'] = round(float(a1[d1].sum()), 1); c['overhang_mm2_new_wings'] = round(float(a1[d1 & inw].sum()), 1)
    c['overhang_mm2_source_body_at_3x'] = round(float(a0[d0].sum()), 1)
    c['volume_cm3'] = round(float(mesh.volume) / 1000, 1); solid = min(float(mesh.volume), float(mesh.area) * 0.85 + 0.15 * float(mesh.volume))
    c['grams_est'] = round(solid * PLA, 0); c['hours_est'] = round(c['grams_est'] / 22.0 + float(ext[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
    c['min_wall_design_mm'] = dict(membrane=MEMBRANE, rib=RIB_W, grown_vein=VEIN_W, between_holes=WALL, rim=WALL)
    c['label'] = lab_text; c['label_bounds_xy'] = [round(float(x), 1) for x in lb]
    c['wings_pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_mm2_new_wings'] <= 1.0)
    c['pass'] = bool(c['wings_pass'] and c['overhang_mm2_total'] <= 1.0)
    stats = dict(scale=SCALE, source_scale=SRC_SCALE, factor_on_source=round(k, 5), rotated_on_plate_deg=0,
                 wings={kd: dict(holes=parts[kd]['n_holes'], cells_kept_closed=parts[kd]['n_closed'], open_share=round(parts[kd]['hole_area'] / parts[kd]['area'], 3),
                                 named_segments=len(W[kd]['named']), grown_segments=len(W[kd]['grown'])) for kd in W},
                 dropped_fragments_mm3=dropped, tris=len(mesh.faces))
    mesh.export(os.path.join(outdir, stem + '.stl'))
    m4 = mesh.copy(); m4.apply_translation([128 - (m4.bounds[0][0] + m4.bounds[1][0]) / 2, 128 - (m4.bounds[0][1] + m4.bounds[1][1]) / 2, 0])
    sc = trimesh.Scene(); sc.add_geometry(m4, node_name=stem, geom_name=stem); sc.export(os.path.join(outdir, stem + '_plate.3mf'))
    # bed overlay
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 5.4), dpi=130); cx, cy = (mesh.bounds[0][:2] + mesh.bounds[1][:2]) / 2
    for s, ls, lbt in ((256, '-', 'bed 256 mm'), (228.6, '--', '9 in'), (203, '--', '8 in (203 mm)')):
        ax.add_patch(plt.Rectangle((-s / 2, -s / 2), s, s, fill=False, ls=ls, lw=0.9, ec='#333')); ax.text(-s / 2 + 2, s / 2 - 7, lbt, fontsize=6, family='monospace')
    hull = trimesh.convex.hull_points(mesh.vertices[:, :2]) if False else None
    from scipy.spatial import ConvexHull
    xy = mesh.vertices[::7, :2] - [cx, cy]; ax.plot(xy[:, 0], xy[:, 1], ',', color='#9a4a2c')
    ax.set_xlim(-135, 135); ax.set_ylim(-135, 135); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('%s\n%s x %s x %s mm (%s x %s x %s in) · margin to bed edge %s / %s mm' % (stem, *c['dims_mm'], *c['dims_in'], *c['margin_mm']), fontsize=6.5, family='monospace')
    fig.savefig(os.path.join(outdir, stem + '_bed.png'), bbox_inches='tight'); plt.close(fig)
    rep = dict(stem=stem, id=variant, tile=tile, stats=stats, checks=c, build_s=round(time.time() - t0, 1), built=time.strftime('%Y-%m-%d %H:%M'), patterns=[pf, ph])
    json.dump(rep, open(os.path.join(outdir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1)
    print(stem, 'PASS' if c['pass'] else ('WINGS PASS, BODY FAIL' if c['wings_pass'] else 'FAIL'), json.dumps(c), json.dumps(stats))


if __name__ == '__main__': main()
