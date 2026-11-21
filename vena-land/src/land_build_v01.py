"""land_build_v01.py : vena-land pattern studies (rows VLN-). Four venation patterns by four landform typologies, each a
100 x 100 mm heightfield with relief up to 20 mm. Veins are structure, cells are fill:
  berm : veins are ridges, crest height from Murray width, side slope 1 to 1.5
  wave : waveform mounds. Cells are mounds (height with cell size), veins are the swales between them
  pond : pond cells. Cells are basins (depth with cell size), veins are the dikes at the plateau level
  terr : terraces. Distance from the primary veins cut into steps (tread 3 mm, riser 2 mm)
Pattern study: no scale, no vertical exaggeration set.
usage: python land_build_v01.py <patterns_dir> <out_dir> [--stl id,id,...]
Per study: 16 bit heightfield PNG (0 = 0 mm, 65535 = 20 mm), contour SVG at 1 mm, graph.json (the pattern, tile frame), shaded preview
PNG with 1 mm contours, check JSON. With --stl: a solid on a 3 mm base with a mirrored underside label, STL and plate 3MF. No em dashes."""
import sys, os, json, math, time
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
TILE = 100.0; P = 0.25; N = int(TILE / P); RELIEF = 20.0; BASE = 3.0; PLA = 1.24e-3
PATS = [('wing', 'VS03-04'), ('ovate', 'VS02-04'), ('blob', 'VS02-10'), ('cells', 'VS02-16')]
TYPS = ['berm', 'wave', 'pond', 'terr']
TYPNAME = {'berm': 'berm', 'wave': 'waveform mounds', 'pond': 'pond cells', 'terr': 'terraces'}


def load(pdir, name, src):
    p = json.load(open(os.path.join(pdir, '%s-%s.pattern.json' % (name, src)), encoding='utf-8')); g = p['graph']; o = np.array(p['outline'], float)
    c = (o.min(0) + o.max(0)) / 2; ext = o.max(0) - o.min(0); rot = math.radians(45) if ext[0] / ext[1] > 2.5 else 0.0          # a slender outline (the wing) lies on the diagonal
    R = np.array([[math.cos(rot), -math.sin(rot)], [math.sin(rot), math.cos(rot)]]); o2 = (o - c) @ R.T; s = 94.0 / max(np.ptp(o2[:, 0]), np.ptp(o2[:, 1])); c2 = (o2.min(0) + o2.max(0)) / 2
    T = lambda q: ((np.asarray(q, float).reshape(-1, 2) - c) @ R.T - c2) * s + TILE / 2
    nodes = T([[n['x'], n['y']] for n in g['nodes']]) if g['nodes'] else np.zeros((0, 2)); w = np.array([n['w'] for n in g['nodes']], float) if g['nodes'] else np.zeros(0)
    E = np.array([[e['parent'], e['child']] for e in g['edges']], int) if g['edges'] else np.zeros((0, 2), int)
    cells = [T(cc) for cc in g['cells'] if len(cc) >= 3]
    return dict(outline=T(o), nodes=nodes, w=w, E=E, cells=cells, scale=s, rot_deg=math.degrees(rot), stat=p.get('stat'), spec=p.get('spec'))


def samples(pt):
    """vein centre lines as points with a normalised width 0..1; cell walls of a cells pattern count as the thinnest veins"""
    A = []; W = []
    if len(pt['E']):
        wn = np.clip(pt['w'] / max(1e-9, np.percentile(pt['w'], 99.5)), 0, 1)
        for a, b in pt['E']:
            L = np.linalg.norm(pt['nodes'][b] - pt['nodes'][a]); n = max(2, int(L / 0.2) + 1); t = np.linspace(0, 1, n)[:, None]
            A.append(pt['nodes'][a] + (pt['nodes'][b] - pt['nodes'][a]) * t); W.append(wn[a] + (wn[b] - wn[a]) * t[:, 0])
    if not len(pt['E']) or len(pt['cells']) > 200:                       # cells patterns: the walls
        areas = np.array([0.5 * abs(np.dot(c[:, 0], np.roll(c[:, 1], 1)) - np.dot(c[:, 1], np.roll(c[:, 0], 1))) for c in pt['cells']]); big = np.percentile(areas, 80)
        for c, ar in zip(pt['cells'], areas):
            q = np.r_[c, c[:1]]; wv = 0.55 if (not len(pt['E']) and ar >= big) else 0.12                 # with no veins at all, the walls of the largest fifth of the cells stand in as primaries
            for a, b in zip(q[:-1], q[1:]):
                L = np.linalg.norm(b - a); n = max(2, int(L / 0.2) + 1); t = np.linspace(0, 1, n)[:, None]; A.append(a + (b - a) * t); W.append(np.full(n, wv))
    return np.concatenate(A), np.concatenate(W)


def heights(pt, typ):
    xs = (np.arange(N) + 0.5) * P; X, Y = np.meshgrid(xs, xs, indexing='ij'); G = np.c_[X.ravel(), Y.ravel()]
    im = Image.new('L', (N, N), 0); ImageDraw.Draw(im).polygon([(x / P, y / P) for x, y in pt['outline']], fill=1); inside = np.asarray(im, bool).T
    S, W = samples(pt); tree = cKDTree(S); d, ix = tree.query(G, k=8); wk = W[ix]
    dany = d[:, 0].reshape(N, N)
    prim = W >= 0.5
    dprim = cKDTree(S[prim]).query(G)[0].reshape(N, N) if prim.sum() > 10 else dany
    # cells = fields between vein centre lines
    vmask = dany < 0.45; lab, nl = ndi.label(~vmask & inside); e = ndi.distance_transform_edt(~vmask & inside) * P
    emax = ndi.maximum(e, lab, np.arange(nl + 1)); em = np.maximum(emax[lab], 1e-6); u = np.clip(e / em, 0, 1)
    if typ == 'berm':
        hi = 3.0 + 15.0 * wk ** 0.7; z = (hi - 1.5 * np.maximum(d - (0.6 + 1.2 * wk), 0) / 1.5 * 1.0)      # crest half width 0.6 to 1.8 mm, side slope 1 down per 1.5 out
        z = 2.0 + np.clip(z.max(1), 0, None).reshape(N, N); z = np.where(inside, z, 2.0)
    elif typ == 'wave':
        A = np.clip(3.2 * em, 1.0, 17.0); z = 2.0 + A * (1 - np.cos(np.pi * u)) / 2; z = np.where(inside, z, 2.0)
    elif typ == 'pond':
        D = np.clip(3.2 * em, 1.0, 16.0); z = 19.0 - D * (1 - np.cos(np.pi * u)) / 2; z = np.where(inside, z, 19.0)
    else:
        z = 20.0 - 2.0 * np.floor(dprim / 3.0); z = np.where(inside, np.clip(z, 2.0, 20.0), 2.0)
    z = ndi.gaussian_filter(z, 0.6) if typ != 'terr' else z
    return np.clip(z, 0, RELIEF), dict(cells=int(nl), vein_samples=int(len(S)), primary_share=round(float(prim.mean()), 3))


def contour_svg(z, path, aid):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    xs = (np.arange(N) + 0.5) * P; fig, ax = plt.subplots(); cs = ax.contour(xs, xs, z.T, levels=np.arange(1, 20.01, 1.0)); out = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        for sg in segs:
            if len(sg) > 1: out.append('<polyline data-z="%.0f" points="%s"/>' % (lev, ' '.join('%.2f,%.2f' % (x, TILE - y) for x, y in sg)))
    plt.close(fig)
    open(path, 'w', encoding='utf-8').write('<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="100mm" viewBox="0 0 100 100"><title>%s contours 1 mm</title><g id="contours" fill="none" stroke="#111" stroke-width="0.1">%s</g></svg>' % (aid, ''.join(out)))
    return len(out)


def preview(z, path):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.colors import LightSource
    ls = LightSource(azdeg=315, altdeg=42); sh = ls.hillshade(z.T, vert_exag=1.0, dx=P, dy=P); xs = (np.arange(N) + 0.5) * P
    fig = plt.figure(figsize=(8, 8), dpi=112.5); ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(0.6 * sh + 0.4 * (0.25 + 0.75 * z.T / RELIEF), cmap='gray', origin='lower', extent=[0, TILE, 0, TILE], vmin=0.1, vmax=1.0)      # hillshade with a height tint, so flat terraces and basins read
    ax.contour(xs, xs, z.T, levels=np.arange(1, 20.01, 1.0), colors='#1d1c1a', linewidths=0.28, alpha=0.75); ax.set_xlim(0, TILE); ax.set_ylim(0, TILE); ax.axis('off'); fig.savefig(path); plt.close(fig)


def solid(z, aid, outdir, stem):
    import trimesh
    zz = z + BASE; n = N; xs = (np.arange(n) + 0.5) * P
    # top grid, flat bottom, four walls: vertices on cell centres, the rim pulled to the tile edge
    xe = xs.copy(); xe[0] = 0.0; xe[-1] = TILE; X, Y = np.meshgrid(xe, xe, indexing='ij')
    top = np.stack([X, Y, zz], -1).reshape(-1, 3); bot = np.stack([X, Y, np.zeros_like(zz)], -1).reshape(-1, 3); idx = np.arange(n * n).reshape(n, n)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel(), idx[:-1, 1:].ravel()
    ft = np.r_[np.c_[a, b, c], np.c_[a, c, d]]; fb = np.r_[np.c_[a, c, b], np.c_[a, d, c]] + n * n; F = [ft, fb]
    for edge, flip in ((idx[:, 0], False), (idx[-1, :], False), (idx[::-1, -1], False), (idx[0, ::-1], False)):
        e0, e1 = edge[:-1], edge[1:]; F.append(np.r_[np.c_[e0, e0 + n * n, e1 + n * n], np.c_[e0, e1 + n * n, e1]])
    m = trimesh.Trimesh(np.r_[top, bot], np.concatenate(F), process=False)
    if m.volume < 0: m.invert()
    import manifold3d as m3
    M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32))); st = str(M.status())
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dfly')); import dfly_build_v01 as d1
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'vena-dfly')); from dfly_build_v02 import text_geom
    from shapely import affinity
    lab = aid + ' v01'; tg = affinity.scale(text_geom(lab, 3.4), -1, 1, origin=(0, 0)); tg = affinity.translate(tg, TILE / 2, TILE / 2)
    M = (M - d1.prism(tg, -0.2, 0.6)).simplify(0.01); o = M.to_mesh(); m = trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False)
    m.vertices[:, 2] = np.where(np.abs(m.vertices[:, 2]) < 1e-4, 0.0, m.vertices[:, 2])
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lamps')); import lamp_build_v01 as v1
    c = v1.checks(m, stem); c['manifold_status'] = st; c['label'] = lab
    m.export(os.path.join(outdir, stem + '.stl'))
    m4 = m.copy(); m4.apply_translation([128 - TILE / 2, 128 - TILE / 2, 0]); sc = trimesh.Scene(); sc.add_geometry(m4, node_name=stem, geom_name=stem); sc.export(os.path.join(outdir, stem + '_plate.3mf'))
    return m, c, v1


def main():
    pdir, outdir = sys.argv[1], sys.argv[2]; os.makedirs(outdir, exist_ok=True)
    want = sys.argv[sys.argv.index('--stl') + 1].split(',') if '--stl' in sys.argv else []
    stl_dir = sys.argv[sys.argv.index('--stl') + 2] if '--stl' in sys.argv else None
    for name, src in PATS:
        pt = load(pdir, name, src)
        for typ in TYPS:
            aid = 'vena-land-%s--%s-%s__01' % (typ, name, src); stem = aid + '_s07_t100mm_r20mm_v01'; t0 = time.time()
            if want and aid not in want: continue
            z, info = heights(pt, typ)
            if not want:
                Image.fromarray(np.round(z.T[::-1] / RELIEF * 65535).astype(np.uint16)).save(os.path.join(outdir, stem + '_height16.png'))
                nc = contour_svg(z, os.path.join(outdir, stem + '_contours.svg'), aid); preview(z, os.path.join(outdir, stem + '_shaded.png'))
                json.dump(dict(format='venation-lab graph, tile frame', units='mm', frame=[0, 0, TILE, TILE], source_study=src, pattern=name, fit_scale=round(pt['scale'], 4), rotated_deg=pt['rot_deg'], params=pt['spec'],
                               nodes=[dict(x=round(float(x), 3), y=round(float(y), 3), w=round(float(w), 3)) for (x, y), w in zip(pt['nodes'], pt['w'])], edges=[dict(parent=int(a), child=int(b)) for a, b in pt['E']],
                               cells=[[[round(float(x), 3), round(float(y), 3)] for x, y in c] for c in pt['cells']], outline=[[round(float(x), 3), round(float(y), 3)] for x, y in pt['outline']]),
                          open(os.path.join(outdir, stem + '_graph.json'), 'w', encoding='utf-8'))
                gx, gy = np.gradient(z, P); sl = np.hypot(gx, gy)
                rep = dict(stem=stem, id=aid, typology=TYPNAME[typ], pattern=name, source_study=src, tile_mm=TILE, grid_mm=P, relief_mm=[round(float(z.min()), 2), round(float(z.max()), 2)], contours=nc, stats=info,
                           slope_p50=round(float(np.percentile(sl, 50)), 2), slope_p99=round(float(np.percentile(sl, 99)), 2), note='pattern study: no scale, no vertical exaggeration set', built=time.strftime('%Y-%m-%d %H:%M'))
                json.dump(rep, open(os.path.join(outdir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1)
                print(aid, 'relief', rep['relief_mm'], 'cells', info['cells'], 'contours', nc, '%.0fs' % (time.time() - t0))
            else:
                m, c, v1 = solid(z, aid, stl_dir, stem)
                gx, gy = np.gradient(z, P); thin = ndi.binary_opening(z > z.min() + 0.3, iterations=4)          # features that an opening of 1.0 mm radius removes are under 2 mm wide
                c['features_under_2mm_pct'] = round(100 * float(((z > z.min() + 0.3) & ~thin).mean()), 2)
                c['grams_est'] = round(float(m.volume) * 0.35 * PLA + float(m.area) * 0.85 * PLA, 0); c['hours_est'] = round(c['grams_est'] / 22.0 + float(m.extents[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
                c['pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_widest_strip_mm'] <= 1.0)
                c['pass_rule'] = 'watertight, one shell, 0 non-manifold edges, footprint in 203 x 203, height in 256, widest down-facing strip 1.0 mm or less (the label letters are the only down faces). Features under 2 mm are reported, not failed.'
                v1.overlay_png(m, os.path.join(stl_dir, stem + '_bed.png'), stem, c)
                json.dump(dict(stem=stem, id=aid, typology=TYPNAME[typ], base_mm=BASE, checks=c, tris=len(m.faces), built=time.strftime('%Y-%m-%d %H:%M')), open(os.path.join(stl_dir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str)
                print(stem, 'PASS' if c['pass'] else 'FAIL', c['watertight'], c['shells'], c['nonmanifold_edges'], c['dims_mm'], 'strip', c['overhang_widest_strip_mm'], 'thin pct', c['features_under_2mm_pct'], 'g', c['grams_est'], 'h', c['hours_est'], 'tris', len(m.faces))


if __name__ == '__main__': main()
