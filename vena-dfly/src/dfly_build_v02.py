"""dfly_build_v02.py : vena-dfly-phys, the E1 Clubtail print body at 3x with window wings (rows VLD-06 and up).
v01 fused prisms on the source mesh and left the body's overhangs. v02 builds everything as one occupancy field on a grid
(0.25 mm in plan, 0.28 mm in height), so the body can be made printable without supports and the wings can carry a 0.4 mm membrane:
  body  : the source STL (never edited) sliced into the grid; the old wing slabs come out as in v01; then every layer is made to
          rest on the layer under it within one grid step (41.8 degrees off vertical): a 45 degree chamfer under every
          overhang, and a web 0.75 mm wide down to the bed where a chamfer alone would end in mid air (under legs).
  wings : flat on the bed. Membrane 0.4 mm (two layers), closed. Ribs 2.0 mm wide and up, wider and taller with Murray width.
  eyes  : hexagonal facets, 1.6 mm pitch, 0.3 mm relief, only where the eye surface does not look down.
  label : mirrored, 0.6 mm deep, cut into the bed face under the thorax.
It imports dfly_build_v01 (00_src/dfly) for the wing frame and placement. usage:
python dfly_build_v02.py <source.stl> <patterns_dir> <fore pattern> <hind pattern> <artifact id> <out_dir>
Frame as E1: +X head to tail, +Y left wing, +Z up, mm. No em dashes."""
import sys, os, json, math, time
import numpy as np, trimesh
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
from PIL import Image, ImageDraw
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'dfly'))
import dfly_build_v01 as d1

P = 0.25; DZ = 0.28; PAD = 3.0
MEMBRANE = 0.4; RIB_W0, RIB_W1 = 2.0, 3.6; RIB_H0, RIB_H1 = 1.2, 3.0; RIM_W, RIM_H = 2.0, 1.6
RIB_W1C = 2.6               # cells fab: nine named veins share a 21 mm chord, so their width range is narrower
CELL_WIN = 3.0
RIB_SHARE = 0.55            # open pattern: grown veins are thinned until ribs and rim together cover no more than this share of the wing (the 2 mm rim alone is about 0.3)
WIN_MIN = 1.5               # a membrane field narrower than this is filled to rib height (the lamp T1 window rule)
FACET_PITCH, FACET_RELIEF = 1.6, 0.3
PLA = 1.24e-3
SS = 4                      # supersampling for plan coverage


def raster(geom, x0, y0, nx, ny):
    """coverage 0..1 of a shapely geometry on the plan grid (x index first)"""
    im = Image.new('L', (nx * SS, ny * SS), 0); dr = ImageDraw.Draw(im)
    for pg in d1.polys(geom):
        dr.polygon([((x - x0) / P * SS, (y - y0) / P * SS) for x, y in pg.exterior.coords], fill=255)
        for r in pg.interiors: dr.polygon([((x - x0) / P * SS, (y - y0) / P * SS) for x, y in r.coords], fill=0)
    a = np.asarray(im.resize((nx, ny), Image.BOX), np.float32) / 255.0
    return a.T


def wing_layers(pat_path):
    """a wing in its own frame at build scale: list of (geometry, height) layers and counts"""
    pat = json.load(open(pat_path, encoding='utf-8')); g = pat['graph']; W = d1.wing_2d(pat_path); O = W['outline']
    w = g['wing']; mpu = g['mm_per_unit']
    def T(x, y): return (x - w['x0'] * mpu, w['vm'] * d1.SCALE - (y - w['y0'] * mpu))
    N = g['nodes']; Pt = [T(n['x'], n['y']) for n in N]; wn = np.array([n['w'] for n in N], float); wn = np.clip(wn / max(1e-9, np.percentile(wn, 99.5)), 0, 1)
    segs = []
    for e in g['edges']:
        a, b = e['parent'], e['child']
        if Pt[a] == Pt[b]: continue
        segs.append((LineString([Pt[a], Pt[b]]), 0.5 * (wn[a] + wn[b]), e['kind'], N[b].get('name') or N[a].get('name') or 'unnamed'))
    fixed = [s for s in segs if s[2] == 'fixed']; grown = [s for s in segs if s[2] != 'fixed']
    def ribs_of(ss, lo):                      # four height classes; width and height rise with Murray width
        out = []
        for c in range(4):
            sel = [s for s in ss if s[1] >= lo and min(3, int(s[1] * 4)) == c]
            if not sel: continue
            u = (c + 0.5) / 4; wd = RIB_W0 + u * ((RIB_W1C if W['cells'] else RIB_W1) - RIB_W0); out.append((unary_union([s[0].buffer(wd / 2, cap_style=1) for s in sel]).intersection(O), RIB_H0 + u * (RIB_H1 - RIB_H0)))
        return out
    names_kept = []; names_dropped = []
    if fixed:                                 # fit the named set: a named vein stays if, beyond the first fifth of the span, 60 percent of it keeps a 2.5 mm window to the ribs already kept
        rimg = O.difference(O.buffer(-RIM_W)); xs = O.bounds[0] + 0.2 * (O.bounds[2] - O.bounds[0]); base = rimg; grp = {}
        for sg in fixed: grp.setdefault(sg[3], []).append(sg)
        keepf = []
        for nm, ss in sorted(grp.items(), key=lambda kv: -np.mean([q[1] for q in kv[1]])):
            Lg = unary_union([q[0] for q in ss]); from shapely.geometry import box
            test = Lg.intersection(box(xs, -1e3, 1e3, 1e3)); free = test.difference(base.buffer(RIB_W0 / 2 + WIN_MIN))
            if nm in ('pterostigma', 'nodus', 'triangle') or (test.length > 1 and free.length / test.length >= 0.5):
                keepf += ss; names_kept.append(nm)
                if nm not in ('pterostigma', 'nodus', 'triangle'): base = base.union(Lg.buffer(RIB_W0 / 2))
            else: names_dropped.append(nm)
        fixed = keepf
    layers = ribs_of(fixed, 0.0); thr = 0.0; dropped = 0
    if grown:                                 # thin the grown set from the thin end until the ribs leave windows
        ws = np.array([s[1] for s in grown])
        for thr in np.linspace(0.0, 0.95, 39):
            gl = ribs_of(grown, thr); area = unary_union([q[0] for q in layers + gl] + [O.difference(O.buffer(-RIM_W))]).area
            if area <= RIB_SHARE * O.area: break
        layers += gl; dropped = int((ws < thr).sum())
    rim = O.difference(O.buffer(-RIM_W)); layers.append((rim, RIM_H))
    if W['ptero'] is not None: layers.append((W['ptero'].intersection(O), RIB_H0 + 0.6 * (RIB_H1 - RIB_H0)))
    walls = []; cellinfo = (0, 0)
    if W['cells']:                            # cells fab: the cell walls are ribs at the least width and height
        base = unary_union([q[0] for q in layers]); kept = 0; tried = 0
        for c in sorted([q for c in W['cells'] for q in d1.polys(c)], key=lambda q: -q.area):
            tried += 1; wl = c.exterior.buffer(RIB_W0 / 2).intersection(O)
            ok = not c.buffer(-RIB_W0 / 2).difference(base).buffer(-CELL_WIN / 2).is_empty       # a cell keeps its walls only if its own window stays 3 mm across; slivers left outside are filled and counted
            if ok: walls.append(wl); base = base.union(wl); kept += 1
        if walls: layers.append((unary_union(walls), RIB_H0))
        cellinfo = (kept, tried)
    ribs = unary_union([q[0] for q in layers]); mem = O.difference(ribs); wins = []; filled = []
    for q in d1.polys(mem):
        (wins if not q.buffer(-WIN_MIN / 2).is_empty else filled).append(q)
    if filled: layers.append((unary_union(filled), RIB_H0))
    big = sum(1 for q in wins if not q.buffer(-4.0).is_empty)
    info = dict(kind=W['kind'], named_segments=len(fixed), grown_segments=len(grown), grown_dropped=dropped, grown_threshold=round(float(thr), 3), windows=len(wins), fields_filled=len(filled),
                windows_over_8mm=big, named_kept=names_kept, named_dropped=names_dropped, cell_walls_kept=cellinfo[0], cell_walls_tried=cellinfo[1], rib_share=round(float(unary_union([q[0] for q in layers]).area / O.area), 3), area_mm2=round(O.area, 1),
                least_window_mm=round(min((2 * max_inscribed(q) for q in wins), default=0.0), 2), stat=pat.get('stat'))
    return O, layers, info


def max_inscribed(q):
    lo, hi = 0.0, 20.0
    for _ in range(14):
        m = (lo + hi) / 2
        if q.buffer(-m).is_empty: hi = m
        else: lo = m
    return lo


def text_geom(text, size):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), text, size=size, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    ps = [Polygon(p).buffer(0) for p in tp.to_polygons() if len(p) >= 4]; ps = [p for p in ps if p.area > 1e-4]; ps.sort(key=lambda p: -p.area); g = None
    for p in ps: g = p if g is None else (g.difference(p) if g.contains(p.representative_point()) else g.union(p))
    b = g.bounds; return affinity.translate(g, -(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2)


def main():
    src, pdir, pf, ph, aid, outdir = sys.argv[1:7]; t0 = time.time(); os.makedirs(outdir, exist_ok=True)
    k = d1.SCALE / d1.SRC_SCALE
    m = trimesh.load(src); m.apply_scale(k); comps = m.split(only_watertight=False); m = max(comps, key=lambda q: abs(q.volume))
    b0, b1 = m.bounds; x0, y0 = b0[0] - PAD, b0[1] - PAD; nx = int(math.ceil((b1[0] - b0[0] + 2 * PAD) / P)); ny = int(math.ceil((b1[1] - b0[1] + 2 * PAD) / P)); nz = int(math.ceil((b1[2] + 1.0) / DZ))
    zc = (np.arange(nz) + 0.5) * DZ
    # ---- body into the grid, slice by slice
    B = np.zeros((nx, ny, nz), bool)
    for j, z in enumerate(zc):
        sec = m.section(plane_origin=[0, 0, float(z)], plane_normal=[0, 0, 1])
        if sec is None: continue
        im = Image.new('1', (nx, ny), 0); acc = np.zeros((ny, nx), bool)
        for path in sec.discrete:
            im = Image.new('1', (nx, ny), 0); ImageDraw.Draw(im).polygon([((x - x0) / P - 0.5, (y - y0) / P - 0.5) for x, y, _ in path], fill=1); acc ^= np.asarray(im, bool)
        B[:, :, j] = acc.T
    vol_src = float(B.sum()) * P * P * DZ
    # ---- wings: outlines, the old slab region, pads
    WL = {'fore': wing_layers(os.path.join(pdir, pf)), 'hind': wing_layers(os.path.join(pdir, ph))}
    cut = unary_union([d1.place(WL[kd][0], kd, sd).buffer(1.0) for kd in WL for sd in (1, -1)]); cutm = raster(cut, x0, y0, nx, ny) > 0.5
    jc = int(d1.CUT_Z / DZ); above = B[:, :, jc + 1].copy()
    for j in range(jc + 1): B[:, :, j] = np.where(cutm, above, B[:, :, j])          # slabs out, what stood on them back as straight pads
    # ---- no supports: every layer rests on the one under it within one grid step; a web to the bed where a chamfer would end in mid air
    st = ndi.generate_binary_structure(2, 1); st9 = np.ones((3, 3), bool); before = int(B.sum()); webs = 0
    for j in range(nz - 1, 0, -1):
        up = B[:, :, j]; er = ndi.binary_erosion(up, st); lo = B[:, :, j - 1] | er
        need = up & ~ndi.binary_dilation(lo, st9)
        if need.any(): lo |= ndi.binary_dilation(need, st9); webs += int(need.sum())
        B[:, :, j - 1] = lo
    added = (int(B.sum()) - before) * P * P * DZ
    Fb = ndi.gaussian_filter(B.astype(np.float32), (0.8, 0.8, 0.6), mode='nearest')
    # ---- eyes: facets on the two eye spheres (E1 script: EYE_R 2.4, centres from eye_centers(), sunk in the head)
    S3 = d1.SCALE; R = 2.4 * S3; zb = (2.6 + 0.4) * k; ez = zb + 5.0 * S3 / 2 - 1.2 * k + 0.9 * S3; facets = 0; eye_hit = []
    X = x0 + (np.arange(nx) + 0.5) * P; Y = y0 + (np.arange(ny) + 0.5) * P
    for sd in (1, -1):
        ex, ey = 5.0 * 0.45 * S3, sd * (2.2 / 2 + 2.4 * 0.9) * 0.92 * S3
        i0, i1 = np.searchsorted(X, [ex - R - 1, ex + R + 1]); j0, j1 = np.searchsorted(Y, [ey - R - 1, ey + R + 1]); k1 = min(nz, int((ez + R + 1) / DZ) + 1)
        gx, gy, gz = np.meshgrid(X[i0:i1] - ex, Y[j0:j1] - ey, zc[:k1] - ez, indexing='ij'); r = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2) + 1e-9
        n_ = int(4 * math.pi * R * R / (FACET_PITCH ** 2 * 0.866)); ii = np.arange(n_) + 0.5; zz = 1 - 2 * ii / n_; rr = np.sqrt(1 - zz * zz); aa = ii * math.pi * (3 - math.sqrt(5))
        L = np.stack([rr * np.cos(aa), rr * np.sin(aa), zz], 1)
        from scipy.spatial import cKDTree
        shell = np.abs(r - R) < 1.2; U = np.stack([gx[shell] / r[shell], gy[shell] / r[shell], gz[shell] / r[shell]], 1); dch, ix = cKDTree(L).query(U)
        arcd = 2 * np.arcsin(np.clip(dch / 2, 0, 1)) * R; ok = (L[ix, 2] > -0.1) & (U[:, 2] > -0.1) & (U[:, 1] * sd > -0.3)      # no facet where the eye looks down or into the head
        bump = np.where(ok, FACET_RELIEF * np.clip(1 - (arcd / (0.5 * FACET_PITCH)) ** 2, 0, 1), 0.0)
        fe = np.zeros(r.shape, np.float32); fe[shell] = np.clip(0.5 + (R + bump - r[shell]) / P, 0, 1) * (bump > 0)
        sub = Fb[i0:i1, j0:j1, :k1]; eye_hit.append(round(float((sub[np.abs(r - (R - 0.4)) < 0.2] > 0.5).mean()), 3)); np.maximum(sub, fe, out=sub)
        facets += int(((L[:, 2] > -0.1) & (L[:, 1] * sd > -0.3)).sum())
    # ---- wings into the field
    Fw = np.zeros((nx, ny, nz), np.float32); winfo = {}
    for kd in WL:
        O, layers, info = WL[kd]; winfo[kd] = info
        for sd in (1, -1):
            for geom, h in [(O, MEMBRANE)] + layers:
                if geom.is_empty: continue
                cov = raster(d1.place(geom, kd, sd), x0, y0, nx, ny); kk = min(nz, int(h / DZ) + 2)
                np.maximum(Fw[:, :, :kk], cov[:, :, None] * np.clip(0.5 + (h - zc[:kk]) / DZ, 0, 1)[None, None, :], out=Fw[:, :, :kk])
    Ff = np.maximum(Fb, Fw); del Fw
    # ---- label, mirrored, cut 0.6 mm into the bed face under the thorax and abdomen
    lab_text = aid + ' v01'; tg = affinity.scale(text_geom(lab_text, 3.0), 1, -1, origin=(0, 0))                 # mirrored across the body axis: reads right from below
    lx = (5.0 + 4.75) * S3 + 24.0; tgp = affinity.translate(tg, lx, 0.0); lm = raster(tgp, x0, y0, nx, ny) > 0.5
    contact = Ff[:, :, 0] > 0.5; lab_cover = float((lm & contact).sum()) / max(1, int(lm.sum())); kk = int(round(0.6 / DZ))
    Ff[:, :, :kk] = np.where(lm[:, :, None], 0.0, Ff[:, :, :kk])
    # ---- mesh
    G = np.zeros((nx + 2, ny + 2, nz + 2), np.float32); G[1:-1, 1:-1, 1:-1] = Ff
    v, f, _, _ = marching_cubes(G, 0.5, spacing=(P, P, DZ)); v = v + [x0 - 0.5 * P, y0 - 0.5 * P, -0.5 * DZ]
    mesh = trimesh.Trimesh(v, f, process=False); mesh.merge_vertices(digits_vertex=5)
    if mesh.volume < 0: mesh.invert()
    stats = dict(grid=[nx, ny, nz], pitch_mm=[P, DZ], tris_raw=len(mesh.faces))
    try:
        import manifold3d as m3
        M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32), tri_verts=np.asarray(mesh.faces, np.uint32)))
        if str(M.status()).endswith('NoError'):
            parts = sorted(M.decompose(), key=lambda q: -q.volume()); stats['dropped_fragments_mm3'] = [round(q.volume(), 3) for q in parts[1:]][:10]; stats['dropped_fragments'] = len(parts) - 1
            o = parts[0].simplify(0.02).to_mesh(); mesh = trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False); stats['decimated'] = 'manifold simplify 0.02 mm'
        else: stats['decimated'] = 'input not manifold: ' + str(M.status())
    except Exception as ex: stats['decimated'] = 'error ' + str(ex)[:80]
    mesh.vertices[:, 2] = np.where(mesh.vertices[:, 2] < 0.02, 0.0, mesh.vertices[:, 2])
    stem = '%s_s07_3x_span%dmm_v01' % (aid, round(mesh.extents[1]))
    sys.path.insert(0, os.path.join(HERE, '..', 'lamps')); import lamp_build_v01 as v1
    c = v1.checks(mesh, stem)
    c['grams_est'] = round(min(float(mesh.volume), float(mesh.area) * 0.85 + 0.15 * float(mesh.volume)) * PLA, 0); c['hours_est'] = round(c['grams_est'] / 22.0 + float(mesh.extents[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
    c['min_wall_design_mm'] = dict(membrane=MEMBRANE, rib=RIB_W0, rim=RIM_W, web_under_legs=3 * P); c['fine_below_lab_minimum'] = 'membrane 0.4 mm, webs 0.75 mm'
    c['pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_widest_strip_mm'] <= 1.0)
    c['pass_rule'] = 'watertight, one shell, 0 non-manifold edges, footprint in 203 x 203, height in 256, widest down-facing strip 1.0 mm or less (faces over 45.5 deg, above z 0.75). The 2 mm wall is not part of it: membrane and webs are fine by design.'
    stats.update(scale=d1.SCALE, factor_on_source=round(k, 5), wings=winfo, body_volume_source_cm3=round(vol_src / 1000, 2), body_volume_added_cm3=round(added / 1000, 2), web_columns_started=webs,
                 eye_facets=facets, eye_sphere_inside_body_share=eye_hit, label=lab_text, label_on_bed_contact_share=round(lab_cover, 2), tris=len(mesh.faces))
    mesh.export(os.path.join(outdir, stem + '.stl'))
    m4 = mesh.copy(); m4.apply_translation([128 - (m4.bounds[0][0] + m4.bounds[1][0]) / 2, 128 - (m4.bounds[0][1] + m4.bounds[1][1]) / 2, 0])
    sc = trimesh.Scene(); sc.add_geometry(m4, node_name=stem, geom_name=stem); sc.export(os.path.join(outdir, stem + '_plate.3mf'))
    v1.overlay_png(mesh, os.path.join(outdir, stem + '_bed.png'), stem, c)
    rep = dict(stem=stem, id=aid, stats=stats, checks=c, patterns=[pf, ph], build_s=round(time.time() - t0, 1), built=time.strftime('%Y-%m-%d %H:%M'))
    json.dump(rep, open(os.path.join(outdir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str)
    print(stem, 'PASS' if c['pass'] else 'FAIL', json.dumps({q: c[q] for q in ('watertight', 'shells', 'nonmanifold_edges', 'dims_mm', 'overhang_mm2', 'overhang_widest_strip_mm', 'overhang_largest_patch_mm2', 'grams_est', 'hours_est')}),
          json.dumps({q: stats[q] for q in ('body_volume_source_cm3', 'body_volume_added_cm3', 'web_columns_started', 'eye_facets', 'eye_sphere_inside_body_share', 'label_on_bed_contact_share', 'tris', 'decimated', 'dropped_fragments')}),
          json.dumps({kd: {q: winfo[kd][q] for q in ('windows', 'fields_filled', 'windows_over_8mm', 'rib_share', 'cell_walls_kept', 'cell_walls_tried', 'named_kept', 'named_dropped', 'grown_dropped', 'grown_segments', 'least_window_mm')} for kd in winfo}), '%.0fs' % (time.time() - t0))


if __name__ == '__main__': main()
