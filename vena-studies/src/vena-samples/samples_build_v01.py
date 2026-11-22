"""samples_build_v01.py : sample plates of the flat studies (rows VLS-). VS02 and VS03 pattern tiles, VS08 landform tiles.
A pattern tile: a frame 2.0 mm wide and 2.0 mm tall (5.0 mm wide on the lower edge, where the study ID stands 0.4 mm proud), a membrane
0.6 mm thick inside it, ribs on the membrane 0.8 to 2.4 mm wide and 1.2 to 2.0 mm tall in all, by Murray width. Flat underside.
Thinning, the same rule for every tile: links, veins and cells are dropped by rank from the thinnest (cells: from the smallest) until
gaps under 0.8 mm make up no more than GAP_SHARE of the rib area and at least OPEN_MIN of the area inside the outline is open
membrane (ribs that run together into a plate are not a pattern); rib width goes with the square of the normalised Murray width, so
only the main veins are wide; named wing veins and the outline always stay; what gaps remain under
0.8 mm (the wedges where ribs meet) are closed as rib. Nothing is redrawn.
A landform tile: the VS08 heightfield as a solid, base 2.0 mm, relief scaled to 6.0 mm at its highest, the same frame at base level.
Tiles 45 x 45 mm, wings 95 x 45 mm. Plates: 4 x 4 slots at 51 mm pitch inside 203 x 203 mm, a wing takes two slots, ID order.
usage: python samples_build_v01.py <patterns_dir> <vs08_export_dir> <out_dir> [only_id ...]. No em dashes."""
import sys, os, io, json, math, time, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import trimesh, manifold3d as m3
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lamps')); import lamp_build_v01 as v1
sys.path.insert(0, os.path.join(HERE, '..', 'dfly')); import dfly_build_v01 as d1
sys.path.insert(0, os.path.join(HERE, '..', 'vena-dfly')); from dfly_build_v02 import text_geom
G = 0.125; TH = 45.0; FRAME = 2.0; FRAME_Z = 2.0; IDEDGE = 5.0; MEMB = 0.6; W0, W1 = 0.8, 2.4; H0, H1 = 1.2, 2.0; GAPMIN = 0.8; GAP_SHARE = 0.12; OPEN_MIN = 0.45
ID_UP = 0.4; ID_CAP = 3.0; UNDER = 0.6; BASE = 2.0; RELIEF = 6.0; PLA = 1.24e-3; PITCH = 51.0; LEVELS = 12; NCLS = 9


def geom_mask(g, nx, ny, x0, y0):
    """a shapely geometry in tile mm (y up) to a boolean image, row 0 at the top"""
    im = Image.new('L', (nx, ny), 0); d = ImageDraw.Draw(im); P = lambda c: [((x - x0) / G, ny - (y - y0) / G) for x, y in c]
    for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
        d.polygon(P(poly.exterior.coords), fill=1)
        for h in poly.interiors: d.polygon(P(h.coords), fill=0)
    return np.asarray(im, bool)


def id_text(text, cap):
    g = text_geom(text, cap / 0.73); b = g.bounds; return affinity.scale(g, cap / (b[3] - b[1]), cap / (b[3] - b[1]), origin=(0, 0))


def lines_mask(nx, ny, items):
    """items: (x0, y0, x1, y1, width_mm) in tile mm, y up. Round ends."""
    im = Image.new('L', (nx, ny), 0); d = ImageDraw.Draw(im)
    for x0, y0, x1, y1, w in items:
        a = (x0 / G, ny - y0 / G); b = (x1 / G, ny - y1 / G); r = w / G / 2; d.line([a, b], fill=1, width=max(1, int(round(w / G))))
        d.ellipse([a[0] - r, a[1] - r, a[0] + r, a[1] + r], fill=1); d.ellipse([b[0] - r, b[1] - r, b[0] + r, b[1] + r], fill=1)
    return np.asarray(im, bool)


def closing(R, r_mm):
    r = r_mm / G; dil = ndi.distance_transform_edt(~R) <= r; return ndi.distance_transform_edt(dil) > r


def pattern_tile(pat):
    wing = pat['wing']; TW = 95.0 if wing else 45.0; nx, ny = int(round(TW / G)), int(round(TH / G))
    o = np.array(pat['outline'], float); b0, b1 = o.min(0), o.max(0); iw, ih = TW - 2 * FRAME, TH - FRAME - IDEDGE
    s = min(iw * 0.96 / (b1[0] - b0[0]), ih * 0.96 / (b1[1] - b0[1])); cx, cy = FRAME + iw / 2, IDEDGE + ih / 2; c0 = (b0 + b1) / 2
    T = lambda x, y: (cx + (x - c0[0]) * s, cy - (y - c0[1]) * s)
    # ---- items with a rank: veins by Murray width, links thinnest, cells by area
    ws = [q[5] for q in pat['segs']] + [w for f in pat['fixed'] for w in f['w']]; top = float(np.max(ws)) if ws else 1.0; wn = lambda w: min(1.0, w / max(top, 1e-9))
    named = []; veins = []; cells = []
    for f in pat['fixed']:
        for i in range(len(f['pts']) - 1): named.append((*T(*f['pts'][i]), *T(*f['pts'][i + 1]), wn((f['w'][i] + f['w'][i + 1]) / 2)))
    for q in pat['segs']:
        it = (*T(q[0], q[1]), *T(q[2], q[3]), wn((q[4] + q[5]) / 2)); (named if q[6] else veins).append(it)
    for q in pat['links']: veins.append((*T(q[0], q[1]), *T(q[2], q[3]), -1.0))                  # links rank under every vein
    for c in pat['cells']:
        p = np.array([T(x, y) for x, y in c]); ar = 0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], 1)) - np.dot(p[:, 1], np.roll(p[:, 0], 1))); cells.append((ar, p))
    outl = [T(x, y) for x, y in pat['outline']]; outline_items = [(*outl[i], *outl[(i + 1) % len(outl)], 0.0) for i in range(len(outl))]
    vr = np.array([v[4] for v in veins]) if veins else np.zeros(0); cr = np.array([c[0] for c in cells]) if cells else np.zeros(0)
    om = Image.new('L', (nx, ny), 0); ImageDraw.Draw(om).polygon([(x / G, ny - y / G) for x, y in outl], fill=1); inside = np.asarray(om, bool)
    width = lambda k: W0 + (W1 - W0) * (k / (NCLS - 1)) ** 2; height = lambda k: H0 + (H1 - H0) * k / (NCLS - 1); cls = lambda w: int(round(max(0.0, w) * (NCLS - 1)))

    def draw(level):
        vt = np.quantile(vr, level / LEVELS) if len(vr) and level else -2.0; ct = np.quantile(cr, level / LEVELS) if len(cr) and level else -1.0
        kv = [v for v in veins if v[4] >= vt] if level < LEVELS else []; kc = [c for c in cells if c[0] >= ct] if level < LEVELS else []
        per = {k: [] for k in range(NCLS)}
        for it in named + kv + outline_items: per[cls(it[4])].append((it[0], it[1], it[2], it[3], width(cls(it[4]))))
        for ar, p in kc:
            for i in range(len(p)): per[0].append((p[i][0], p[i][1], p[(i + 1) % len(p)][0], p[(i + 1) % len(p)][1], W0))
        hm = np.zeros((ny, nx), np.float32)
        for k in range(NCLS):
            if per[k]: hm = np.maximum(hm, lines_mask(nx, ny, per[k]) * height(k))
        R = hm > 0; C = closing(R, GAPMIN / 2); filled = C & ~R; share = float(filled.sum()) / max(1, int(R.sum())); merged = float((~C & inside).sum()) / max(1, int(inside.sum()))      # share of the outline left as open membrane
        return hm, R, C, filled, share, len(kv), len(kc), merged
    for level in range(LEVELS + 1):
        hm, R, C, filled, share, nv, nc, merged = draw(level)
        if share <= GAP_SHARE and merged >= OPEN_MIN: break
    hm = np.where(filled, H0, hm)
    z = np.full((ny, nx), MEMB, np.float32); z = np.maximum(z, hm)
    yy, xx = np.mgrid[0:ny, 0:nx]; X = (xx + 0.5) * G; Y = TH - (yy + 0.5) * G
    fr = (X < FRAME) | (X > TW - FRAME) | (Y > TH - FRAME) | (Y < IDEDGE); z = np.where(fr, FRAME_Z, z)
    tg = affinity.translate(id_text(pat['id'], ID_CAP), TW / 2, IDEDGE / 2); z = np.where(geom_mask(tg, nx, ny, 0, 0), FRAME_Z + ID_UP, z)
    info = dict(kind='pattern', size_mm=[TW, TH], scale_mm_per_lab_unit=round(s, 5), drop_level=level, of_levels=LEVELS, gap_share=round(share, 4), open_in_outline=round(merged, 4), veins_kept=nv, veins_total=len(veins), named_kept=len(named), cells_kept=nc, cells_total=len(cells),
                gaps_closed_as_rib_mm2=round(float(filled.sum()) * G * G, 2), rib_area_mm2=round(float(R.sum()) * G * G, 1), membrane_open_share=round(float((~C & ~fr).sum()) / max(1, int((~fr).sum())), 3))
    kept = (nv + nc + len(named)); tot = len(veins) + len(cells) + len(named); info['kept'] = kept; info['total'] = tot; info['kept_share'] = round(kept / max(1, tot), 3)
    under = [(pat['id'], TW / 2, IDEDGE / 2, 2.6)]
    return z, TW, info, under


def land_tile(aid, sid, png):
    TW = 45.0; nx = ny = int(round(TW / G)); h = np.asarray(Image.open(png)).astype(np.float32) / 65535 * 20.0; side = TH - FRAME - IDEDGE; n = int(round(side / G))
    hs = np.asarray(Image.fromarray(h).resize((n, n), Image.BILINEAR)); zmax = float(hs.max()); z = np.full((ny, nx), BASE, np.float32)
    x0 = int(round((TW - side) / 2 / G)); y0 = int(round(FRAME / G)); z[y0:y0 + n, x0:x0 + n] = BASE + hs * (RELIEF / zmax)
    tg = affinity.translate(id_text(sid, ID_CAP), TW / 2, IDEDGE / 2); z = np.where(geom_mask(tg, nx, ny, 0, 0), BASE + ID_UP, z)
    info = dict(kind='landform', size_mm=[TW, TH], source_relief_mm=[round(float(h.min()), 2), round(float(h.max()), 2)], relief_scale=round(RELIEF / zmax, 4), tile_relief_mm=[round(float(hs.min()) * RELIEF / zmax, 2), RELIEF], landform_side_mm=side, kept=1, total=1, kept_share=1.0)
    a, b = aid.split('--'); under = [(a + '--', TW / 2, TH / 2 + 2.2, 2.2), (b, TW / 2, TH / 2 - 2.2, 2.2)]
    return z, TW, info, under


def solid(z, TW, under):
    ny, nx = z.shape; xs = (np.arange(nx) + 0.5) * G; ys = TH - (np.arange(ny) + 0.5) * G; xs[0] = 0; xs[-1] = TW; ys[0] = TH; ys[-1] = 0
    X, Y = np.meshgrid(xs, ys); top = np.stack([X, Y, z], -1).reshape(-1, 3); bot = np.stack([X, Y, np.zeros_like(z)], -1).reshape(-1, 3); idx = np.arange(nx * ny).reshape(ny, nx); N = nx * ny
    a, b, c, d = idx[:-1, :-1].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel(), idx[:-1, 1:].ravel()
    F = [np.r_[np.c_[a, b, c], np.c_[a, c, d]], np.r_[np.c_[a, c, b], np.c_[a, d, c]] + N]
    for edge in (idx[:, 0], idx[-1, :], idx[:, -1][::-1], idx[0, :][::-1]):
        e0, e1 = edge[:-1], edge[1:]; F.append(np.r_[np.c_[e0, e0 + N, e1 + N], np.c_[e0, e1 + N, e1]])
    m = trimesh.Trimesh(np.r_[top, bot], np.concatenate(F), process=False)
    if m.volume < 0: m.invert()
    M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32))); st = str(M.status())
    for text, x, y, cap in under:
        tg = affinity.scale(id_text(text, cap), -1, 1, origin=(0, 0)); tg = affinity.translate(tg, x, y); M = M - d1.prism(tg, -0.2, UNDER)
    best = None
    for tol in (0.02, 0.01, 0.005, 0.0):                  # keep the first result that survives a float32 round trip as one closed body
        o = (M.simplify(tol) if tol else M).to_mesh(); m2 = trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False)
        m2.vertices[:, 2] = np.where(np.abs(m2.vertices[:, 2]) < 1e-4, 0.0, m2.vertices[:, 2]); buf = io.BytesIO(m2.export(file_type='stl')); r = trimesh.load(buf, file_type='stl', force='mesh')
        if r.is_watertight and r.body_count == 1: best = (m2, tol); break
    if best is None: best = (m2, -1)
    return best[0], st, best[1]


def main():
    pdir, ldir, out = sys.argv[1:4]; only = set(sys.argv[4:]); os.makedirs(out, exist_ok=True); os.makedirs(os.path.join(out, 'height'), exist_ok=True); tiles = []
    jobs = [('VS02', 'VS02-%02d' % i, None) for i in range(1, 17)] + [('VS03', 'VS03-%02d' % i, None) for i in range(1, 17)]
    order = [(n, s) for n, s in (('wing', 'VS03-04'), ('ovate', 'VS02-04'), ('blob', 'VS02-10'), ('cells', 'VS02-16'))]; k = 0
    for name, src in order:
        for typ in ('berm', 'wave', 'pond', 'terr'):
            k += 1; jobs.append(('VS08', 'VS08-%02d' % k, 'vena-land-%s--%s-%s__01' % (typ, name, src)))
    for st_, sid, aid in jobs:
        if only and sid not in only: continue
        t0 = time.time()
        if aid is None: z, TW, info, under = pattern_tile(json.load(open(os.path.join(pdir, sid + '.pattern.json'), encoding='utf-8'))); full = sid
        else: z, TW, info, under = land_tile(aid, sid, glob.glob(os.path.join(ldir, aid + '_*_height16.png'))[0]); full = aid
        stem = 'vena-samples--%s_t%dx%dmm_v01' % (sid, round(TW), round(TH)); m, mst, tol = solid(z, TW, under)
        p = os.path.join(out, stem + '.stl'); m.export(p); r = trimesh.load(p, force='mesh'); c = v1.checks(r, stem); c['manifold_status'] = mst; c['simplify_tol'] = tol; c['reload_watertight'] = bool(r.is_watertight); c['reload_bodies'] = int(r.body_count)
        c['grams_est'] = round(float(r.volume) * PLA, 1); c['hours_est'] = round(c['grams_est'] / 22.0 + float(r.extents[2]) / 0.2 * 8 / 3600, 2); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
        c['pass'] = bool(c['watertight'] and c['reload_watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_widest_strip_mm'] <= 1.0)
        c['pass_rule'] = 'as saved and reloaded: watertight, one shell, 0 non-manifold edges, footprint in 203 x 203, height in 256, widest down-facing strip 1.0 mm or less (the engraved underside ID is the only down face). The 2.0 mm lab minimum wall is not met by design: fine, below lab minimum.'
        np.save(os.path.join(out, 'height', sid + '.npy'), z)
        rec = dict(stem=stem, id=sid, full_id=full, set=st_, wing=bool(TW > 50), info=info, checks=c, tris=int(len(r.faces)), built=time.strftime('%Y-%m-%d %H:%M'))
        json.dump(rec, open(os.path.join(out, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str); tiles.append(rec)
        print(sid, 'PASS' if c['pass'] else 'FAIL', c['dims_mm'], 'tris', len(r.faces), 'tol', tol, 'kept', info['kept'], 'of', info['total'], 'level', info.get('drop_level'), 'gap share', info.get('gap_share'), 'open in outline', info.get('open_in_outline'), 'g', c['grams_est'], '%.0fs' % (time.time() - t0), flush=True)
    if only: return
    # ---- plates: 4 x 4 slots, a wing takes two, ID order, a new row when a wing does not fit
    plates = []
    for st_ in ('VS02', 'VS03', 'VS08'):
        cur = None; row = col = 0; n = 0
        for t in [t for t in tiles if t['set'] == st_]:
            need = 2 if t['wing'] else 1
            if cur is not None and col + need > 4: row += 1; col = 0
            if cur is None or row > 3: n += 1; cur = dict(name='vena-samples--%s__%02d' % (st_, n), set=st_, tiles=[]); plates.append(cur); row = col = 0
            cur['tiles'].append(dict(id=t['id'], stem=t['stem'], x=col * PITCH, y=(3 - row) * PITCH, w=t['info']['size_mm'][0], h=TH, row=row, col=col)); col += need
    for pl in plates:
        sc = trimesh.Scene(); ms = []; W = max(t['x'] + t['w'] for t in pl['tiles']); y0 = min(t['y'] for t in pl['tiles']); H = max(t['y'] + t['h'] for t in pl['tiles']) - y0
        for t in pl['tiles']:
            m = trimesh.load(os.path.join(out, t['stem'] + '.stl'), force='mesh'); t['y'] -= y0; m.apply_translation([128 - W / 2 + t['x'], 128 - H / 2 + t['y'], 0]); sc.add_geometry(m, node_name=t['id'], geom_name=t['id']); ms.append(m)
        sc.export(os.path.join(out, pl['name'] + '_plate.3mf')); allm = trimesh.util.concatenate(ms); c = v1.checks(allm, pl['name']); recs = [x for x in tiles if x['id'] in [t['id'] for t in pl['tiles']]]
        c['pass'] = bool(c['footprint_ok'] and c['height_ok'] and all(x['checks']['pass'] for x in recs)); c['grams_est'] = round(sum(x['checks']['grams_est'] for x in recs), 1)
        c['hours_est'] = round(c['grams_est'] / 22.0 + float(allm.extents[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
        v1.overlay_png(allm, os.path.join(out, pl['name'] + '_bed.png'), pl['name'], c); pl['size_mm'] = [round(W, 1), round(H, 1)]; pl['checks'] = {k: c[k] for k in ('dims_mm', 'dims_in', 'margin_mm', 'footprint_ok', 'height_ok', 'pass', 'grams_est', 'hours_est', 'cost_usd_est')}
        pl['tiles_pass'] = sum(1 for x in recs if x['checks']['pass']); pl['tiles_fail'] = len(recs) - pl['tiles_pass']
        print(pl['name'], len(pl['tiles']), 'tiles', pl['size_mm'], 'mm', 'PASS' if c['pass'] else 'FAIL', 'g', c['grams_est'], 'h', c['hours_est'], flush=True)
    json.dump(dict(plates=plates, tiles=tiles, built=time.strftime('%Y-%m-%d %H:%M'), rules=dict(grid_mm=G, frame=[FRAME, FRAME_Z], id_edge_mm=IDEDGE, membrane_mm=MEMB, rib_width_mm=[W0, W1], rib_height_mm=[H0, H1], gap_min_mm=GAPMIN, gap_share=GAP_SHARE, base_mm=BASE, relief_mm=RELIEF, pitch_mm=PITCH)),
              open(os.path.join(out, 'vena-samples_set_v01.json'), 'w', encoding='utf-8'), indent=1, default=str)


if __name__ == '__main__': main()
