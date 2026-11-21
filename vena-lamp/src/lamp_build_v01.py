"""lamp_build_v01.py : venation lamps for FDM (Bambu P2S, PLA, no supports). Phase P2, rows VLL-.
A lamp is a perforated shell over a base surface r = Rb(theta, z): shell 2.0 mm, veins proud 1.5 mm outside, holes = cells
between veins (or Voronoi cells), 3 mm minimum across, smaller cells stay closed. Solid foot ring, cable notch, open top.
Everything is built as fields on a (theta, z) grid of the base surface, meshed by marching cubes in parameter space
(4 layers through the wall), mapped to 3D, welded, decimated, labelled on the underside, checked, exported.
usage: python lamp_build_v01.py <params.json> <seed> <out_dir> <tile_id> [--force]
Units mm. No em dashes."""
import sys, os, json, math, time, io
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
import trimesh

DZ = 0.4            # grid pitch along z and (at the widest ring) along the arc
T_SHELL = 2.0       # shell wall, measured along the surface normal
RELIEF = 1.5        # veins proud of the shell
FLANK = 0.75        # run of the vein flank
VMIN, VMAX = 2.0, 4.5   # vein width range (Murray width mapped into it)
FLANGE = 0.6        # shell left each side of a vein before a hole starts
WALL_HALF = 1.2     # half width of a Voronoi cell wall (wall 2.4)
HOLE_MIN = 3.0      # a hole is cut only where a 3 mm circle fits
EDGE_KEEP = 2.5     # no hole closer than this to a free edge of the shell
CH_IN, CH_OUT = 0.8, 0.4    # chamfer on the inside and outside edge of every hole
FOOT_H, HOLE_R, FOOT_W = 18.0, 25.0, 10.0
NOTCH_W, NOTCH_H = 3.0, 4.0
WEDGE_K = 0.6       # hole roofs: arc half width per mm of drop (31 degrees from vertical)
SLOPE = 0.9         # largest radial gain per mm of drop on any outer face (42 degrees)
STEP = 1.2          # outer panels sit this far proud of inner panels
PLA = 1.24e-3       # g per mm3


def js_rng(seed):
    s = [seed * 9301 + 49297]
    def r():
        s[0] = (s[0] * 9301 + 49297) % 233280; return s[0] / 233280
    return r


# ------------------------------------------------------------------ base surfaces
class Egg:
    def __init__(s, H=170.0, W=85.0, r0=33.0, zc=62.0, rtop=17.0):
        s.H, s.Rmax, s.r0, s.zc = H, W / 2, r0, zc
        s.a = (H - zc) / math.sqrt(1 - (rtop / s.Rmax) ** 2)
    def Rb(s, th, z):
        z = np.asarray(z, float)
        lo = s.r0 + (s.Rmax - s.r0) * np.sin(0.5 * np.pi * np.clip(z / s.zc, 0, 1))
        hi = s.Rmax * np.sqrt(np.clip(1 - ((z - s.zc) / s.a) ** 2, 1e-6, 1))
        return np.where(z < s.zc, lo, hi) + 0 * np.asarray(th)
    rmax = property(lambda s: s.Rmax)


class Cyl:
    def __init__(s, H=150.0, W=100.0): s.H, s.R = H, W / 2
    def Rb(s, th, z): return s.R + 0 * np.asarray(th) + 0 * np.asarray(z, float)
    rmax = property(lambda s: s.R)


class Mound:
    """the page's blob outline (rng 3) as a polar radius, lofted: Rb = Rblob(theta) * (1 - k (z/H)^2)"""
    def __init__(s, H=90.0, W=160.0, k=0.45):
        r = js_rng(3); amp = [(r() * 60, r() * math.pi * 2, 2 + i) for i in range(5)]
        t = np.linspace(0, 2 * np.pi, 2000, endpoint=False); rad = 270 + sum(a * np.sin(f * t + p) for a, p, f in amp)
        x, y = rad * np.cos(t) * 1.25, rad * np.sin(t) * 0.95
        sc = W / (x.max() - x.min()); ph = np.unwrap(np.arctan2(y, x)); R = np.hypot(x, y) * sc
        o = np.argsort(ph % (2 * np.pi)); s.ph, s.R = (ph % (2 * np.pi))[o], R[o]
        s.H, s.k = H, k
    def Rb(s, th, z):
        th = np.asarray(th) % (2 * np.pi); z = np.asarray(z, float)
        return np.interp(th, s.ph, s.R, period=2 * np.pi) * (1 - s.k * (z / s.H) ** 2)
    rmax = property(lambda s: float(s.R.max()))


def P3(form, th, z):
    r = form.Rb(th, z); return np.stack([r * np.cos(th), r * np.sin(th), z + 0 * r], -1)


# ------------------------------------------------------------------ venation grown on the surface (Runions 2005, sections 3 and 4)
def surface_sources(form, rng, spacing, zlo, zhi, n_try=60000):
    """dart throwing on the surface, area weighted"""
    pts = []; tree_pts = np.zeros((0, 3))
    zz = np.linspace(zlo, zhi, 400); rr = form.Rb(0, zz); rr = rr / rr.max()
    cand_z = rng.uniform(zlo, zhi, n_try); cand_t = rng.uniform(0, 2 * np.pi, n_try); acc = rng.uniform(0, 1, n_try)
    keep = acc < np.interp(cand_z, zz, rr); C = P3(form, cand_t[keep], cand_z[keep])
    grid = {}
    cs = spacing
    out = []
    for p in C:
        k = tuple((p // cs).astype(int)); ok = True
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz_ in (-1, 0, 1):
                    for q in grid.get((k[0] + dx, k[1] + dy, k[2] + dz_), ()):
                        if np.dot(p - q, p - q) < spacing * spacing: ok = False; break
                    if not ok: break
                if not ok: break
            if not ok: break
        if ok: grid.setdefault(k, []).append(p); out.append(p)
    return np.array(out)


def grow_on_surface(form, rng, mode, spacing, step, kill, zlo, zhi, n_roots, iters=260):
    """space colonization with every new node projected back to the base surface.
    mode 'open': a source pulls its nearest node and dies when a node is within kill.
    mode 'closed': a source pulls every node of its relative neighbourhood and stays until each tagged vein arrives; arrivals are linked."""
    infl = spacing * 4
    def proj(p):
        th = np.arctan2(p[1], p[0]); z = min(max(p[2], zlo), zhi); return P3(form, th, z)
    src = surface_sources(form, rng, spacing, zlo + 2, zhi - 1)
    nodes = []; parent = []
    for k in range(n_roots):
        th = 2 * np.pi * (k + 0.5) / n_roots; prev = -1
        for s in range(3):
            nodes.append(P3(form, th, zlo + s * step)); parent.append(prev); prev = len(nodes) - 1
    Vs = {}
    alive = np.ones(len(src), bool); tags = [None] * len(src); first = [-1] * len(src); age = [0] * len(src); links = []
    for it in range(iters):
        if not alive.any(): break
        N = np.array(nodes); tree = cKDTree(N); pairs = []
        live = np.nonzero(alive)[0]
        if mode == 'open':
            d, ix = tree.query(src[live], distance_upper_bound=infl)
            pairs = [(s, i) for s, i, dd in zip(live, ix, d) if np.isfinite(dd)]
        else:
            nb = tree.query_ball_point(src[live], infl)
            for s, cand in zip(live, nb):
                if tags[s] is not None:
                    pairs += [(s, t) for t in tags[s]]; continue
                if not cand: continue
                cand = np.array(cand); ds = np.linalg.norm(N[cand] - src[s], axis=1); o = np.argsort(ds)[:24]; cand, ds = cand[o], ds[o]
                V = []
                for a in range(len(cand)):
                    ok = True
                    for b in range(a):      # every closer node u: exclude v when u is also closer to v than s is (Eq. 2)
                        if np.linalg.norm(N[cand[b]] - N[cand[a]]) < ds[a]: ok = False; break
                    if ok: V.append(int(cand[a]))
                Vs[s] = V; pairs += [(s, v) for v in V]
        acc = {}
        for s, i in pairs:
            v = src[s] - N[i]; l = np.linalg.norm(v)
            if l < 1e-9: continue
            a = acc.setdefault(i, np.zeros(3)); a += v / l
        if not acc: break
        child = {}
        for i, a in acc.items():
            l = np.linalg.norm(a)
            if l < 1e-3: continue
            q = proj(N[i] + a / l * step)
            if np.linalg.norm(q - N[i]) < 0.3 * step: continue
            nodes.append(q); parent.append(i); child[i] = len(nodes) - 1
        N = np.array(nodes); tree = cKDTree(N)
        if mode == 'open':
            d, _ = tree.query(src[live]); alive[live[d < kill]] = False
        else:
            for s in live:
                if tags[s] is not None:
                    tags[s] = {child.get(t, t) for t in tags[s]}
                else:
                    d, i = tree.query(src[s])
                    if d >= kill: continue
                    first[s] = int(i); tags[s] = {child.get(v, v) for v in Vs.get(s, [])}
                age[s] += 1
                for t in list(tags[s]):
                    if t == first[s] or _kin(parent, t, first[s], 3): tags[s].discard(t); continue
                    dd = np.linalg.norm(N[t] - src[s]); df = np.linalg.norm(N[t] - N[first[s]])
                    if dd < kill or df < kill * 1.6: links.append((t, first[s])); tags[s].discard(t)
                    elif dd > infl: tags[s].discard(t)
                if not tags[s] or age[s] > 60: alive[s] = False
    return np.array(nodes), np.array(parent), links


def _kin(parent, a, b, g):
    x = a
    for _ in range(g):
        if x < 0: break
        if x == b: return True
        x = parent[x]
    x = b
    for _ in range(g):
        if x < 0: break
        if x == a: return True
        x = parent[x]
    return False


def prune_and_width(nodes, parent, links, min_steps=3, ex=2.6):
    """drop twigs shorter than min_steps that carry no link; Murray widths from the tips, normalised 0..1"""
    n = len(nodes); kids = np.zeros(n, int)
    for p in parent:
        if p >= 0: kids[p] += 1
    linked = set(a for l in links for a in l); dead = np.zeros(n, bool); cut = np.zeros(n)
    for i in range(n):
        if kids[i] or parent[i] < 0 or i in linked: continue
        chain = [i]; x = i
        while parent[x] >= 0 and kids[parent[x]] == 1 and parent[parent[x]] >= 0: x = parent[x]; chain.append(x)
        if len(chain) < min_steps and not any(c in linked for c in chain):
            dead[chain] = True; cut[parent[chain[-1]]] += 1
    w = np.zeros(n)
    kids2 = np.zeros(n, int)
    for i in range(n):
        if not dead[i] and parent[i] >= 0: kids2[parent[i]] += 1
    for i in range(n - 1, -1, -1):
        if dead[i]: continue
        if kids2[i] == 0: w[i] = 1.0
        w[i] = (w[i] ** ex + cut[i]) ** (1 / ex)
        if parent[i] >= 0: w[parent[i]] = (w[parent[i]] ** ex + w[i] ** ex) ** (1 / ex)
    wn = np.clip((w - 1) / max(1e-9, np.percentile(w[~dead], 99.5) - 1), 0, 1)
    return dead, wn


def sample_edges(A, B, wa, wb, pitch=0.5):
    out = []; hw = []
    for a, b, x, y in zip(A, B, wa, wb):
        n = max(2, int(np.linalg.norm(b - a) / pitch) + 1); t = np.linspace(0, 1, n)[:, None]
        out.append(a + (b - a) * t); hw.append((x + (y - x) * t[:, 0]) / 2)
    return np.concatenate(out), np.concatenate(hw)


# ------------------------------------------------------------------ patterns from the page (graph.json contract)
def load_pattern(path):
    pat = json.load(open(path, encoding='utf-8')); g = pat['graph']
    xy = np.array([[n['x'], n['y']] for n in g['nodes']], float) if g['nodes'] else np.zeros((0, 2))
    w = np.array([n['w'] for n in g['nodes']], float) if g['nodes'] else np.zeros(0)
    E = np.array([[e['parent'], e['child']] for e in g['edges']], int) if g['edges'] else np.zeros((0, 2), int)
    out = np.array(pat['outline'], float)
    cen = np.array([np.mean(c, axis=0) for c in g['cells']], float) if g['cells'] else np.zeros((0, 2))
    return dict(xy=xy, w=w, E=E, outline=out, cen=cen, stat=pat.get('stat'))


def polar_mapper(pat, zlo, zhi):
    o = pat['outline']; c = (o.max(0) + o.min(0)) / 2; R = (o[:, 0].max() - o[:, 0].min()) / 2
    def m(xy):
        d = xy - c; return np.arctan2(d[:, 1], d[:, 0]), zlo + np.clip(np.hypot(d[:, 0], d[:, 1]) / R, 0, 1) * (zhi - zlo)
    return m


def panel_frame(pat):
    o = pat['outline']; x0, x1 = o[:, 0].min(), o[:, 0].max(); ym = (o[:, 1].max() + o[:, 1].min()) / 2; yh = (o[:, 1].max() - o[:, 1].min()) / 2
    return x0, x1, ym, yh


def panel_mapper(pat, thc, hs, zlo, zhi):
    x0, x1, ym, yh = panel_frame(pat)
    def m(xy): return thc + (xy[:, 1] - ym) / yh * hs, zlo + (xy[:, 0] - x0) / (x1 - x0) * (zhi - zlo)
    return m


def graph_samples(form, pat, mapper, polar=False):
    th, z = mapper(pat['xy']); E = pat['E']
    if not len(E): return np.zeros((0, 3)), np.zeros(0)
    wn = np.clip(pat['w'] / max(1e-9, np.percentile(pat['w'], 99.5)), 0, 1); wmm = VMIN + wn * (VMAX - VMIN)
    P = []; HW = []
    for a, b in E:
        dth = th[b] - th[a]
        if polar: dth = (dth + np.pi) % (2 * np.pi) - np.pi
        L = math.hypot(dth * form.rmax, z[b] - z[a]); n = max(2, int(L / 0.5) + 1); t = np.linspace(0, 1, n)
        P.append(P3(form, th[a] + dth * t, z[a] + (z[b] - z[a]) * t)); HW.append((wmm[a] + (wmm[b] - wmm[a]) * t) / 2)
    return np.concatenate(P), np.concatenate(HW)


# ------------------------------------------------------------------ the builder
def wrap_gauss(a, sig): return ndi.gaussian_filter1d(a, sig, mode='wrap')


def build(par, seed, log):
    f = par['form']
    form = Egg(**f.get('args', {})) if f['type'] == 'egg' else Cyl(**f.get('args', {})) if f['type'] == 'cyl' else Mound(**f.get('args', {}))
    H = form.H; rng = np.random.default_rng(seed); foot_w = float(par.get('foot_w', FOOT_W))
    NT = int(round(2 * np.pi * (form.rmax + RELIEF) / DZ)); NZ = int(round(H / DZ)); dth = 2 * np.pi / NT
    th = np.arange(NT) * dth; z = (np.arange(NZ) + 0.5) * DZ; TH, Z = np.meshgrid(th, z, indexing='ij')
    Rb = form.Rb(TH, Z); X = np.stack([Rb * np.cos(TH), Rb * np.sin(TH), Z], -1); Xf = X.reshape(-1, 3)
    arc = Rb * dth                                   # arc length of one theta step
    dRdz = np.gradient(Rb, DZ, axis=1); dRdt = np.gradient(Rb, dth, axis=0) / np.maximum(Rb, 1)
    cosl = 1 / np.sqrt(1 + dRdz ** 2 + dRdt ** 2)    # cos of the angle between the radial direction and the surface normal
    here = os.path.dirname(os.path.abspath(par['_path'])); pdir = os.path.join(here, 'patterns')
    VP = [np.zeros((0, 3))]; VH = [np.zeros(0)]; seeds = [np.zeros((0, 3))]; panel_in = None; outer = None; stats = {}
    zlo = FOOT_H - 4.0
    src = par['source']

    if src['kind'] == 'surface':                     # L1, L5: grown on the base surface
        nodes, parent, links = grow_on_surface(form, rng, src['mode'], src['spacing'], src['step'], src['kill'], zlo, H - 1.0, src['roots'])
        kids_ = np.bincount(parent[parent >= 0], minlength=len(nodes)); only = np.full(len(nodes), -1); only[parent[parent >= 0]] = np.nonzero(parent >= 0)[0]
        mid = (parent >= 0) & (kids_ == 1)
        for _ in range(6):                           # ease the zigzag of the growth steps: average along each chain, then back onto the surface
            q = nodes.copy(); q[mid] = 0.25 * nodes[parent[mid]] + 0.5 * nodes[mid] + 0.25 * nodes[only[mid]]
            nodes = P3(form, np.arctan2(q[:, 1], q[:, 0]), np.clip(q[:, 2], zlo, H - 1.0))
        dead, wn = prune_and_width(nodes, parent, links)
        wmm = VMIN + wn * (VMAX - VMIN); idx = [i for i in range(len(nodes)) if not dead[i] and parent[i] >= 0]
        A = nodes[parent[idx]]; B = nodes[idx]; p, h = sample_edges(A, B, wmm[parent[idx]], wmm[idx]); VP.append(p); VH.append(h)
        la = [l for l in links if not dead[l[0]] and not dead[l[1]]]
        if la:
            p, h = sample_edges(nodes[[l[0] for l in la]], nodes[[l[1] for l in la]], np.full(len(la), VMIN), np.full(len(la), VMIN)); VP.append(p); VH.append(h)
        stats.update(vein_nodes=int((~dead).sum()), pruned_nodes=int(dead.sum()), loop_links=len(la))
        if src.get('cells'):                         # open veins enclose nothing: Voronoi cells on the surface give the holes
            seeds.append(surface_sources(form, rng, src['cells'], FOOT_H + 2, H - 2))
    elif src['kind'] == 'polar':                     # L4, L6: a disk study unrolled, centre at the foot
        pat = load_pattern(os.path.join(pdir, '%s_s%02d.pattern.json' % (src['pattern'], seed))); m = polar_mapper(pat, 6.0, H)
        p, h = graph_samples(form, pat, m, polar=True); VP.append(p); VH.append(h)
        t_, z_ = m(pat['cen']); seeds.append(P3(form, t_, z_)); stats.update(page=pat['stat'])
    elif src['kind'] == 'panels':                    # L2, L3: outlines wrapped as panels, alternate panels outside
        n = src['count']; hs = np.pi / n + (src.get('overlap', 6.0) / 2) / form.rmax
        from matplotlib.path import Path as MPath
        panel_in = np.zeros((NT, NZ), bool); outer = np.zeros((NT, NZ), bool); pan_id = np.full((NT, NZ), -1)
        pats = [load_pattern(os.path.join(pdir, '%s_s%02d.pattern.json' % (nm, seed))) for nm in src['patterns']]
        order = list(range(0, n, 2)) + list(range(1, n, 2))          # outer panels first, they hide what lies under them
        for k in order:
            pat = pats[k % len(pats)]; thc = 2 * np.pi * (k + 0.5) / n; x0, x1, ym, yh = panel_frame(pat)
            un = (Z - zlo) / (H - zlo); vn = ((TH - thc + np.pi) % (2 * np.pi) - np.pi) / hs
            poly = MPath(np.c_[(pat['outline'][:, 0] - x0) / (x1 - x0), (pat['outline'][:, 1] - ym) / yh])
            ins = poly.contains_points(np.c_[un.ravel(), vn.ravel()]).reshape(NT, NZ) & (np.abs(vn) <= 1.0)
            vis = ins & ~outer if k % 2 else ins
            if k % 2 == 0: outer |= ins
            pan_id[vis] = k; panel_in |= ins
            m = panel_mapper(pat, thc, hs, zlo, H)
            p, h = graph_samples(form, pat, m)
            oc = np.r_[pat['outline'], pat['outline'][:1]]; ta, za = m(oc)        # the outline as a rim vein
            rp, rh = sample_edges(P3(form, ta[:-1], za[:-1]), P3(form, ta[1:], za[1:]), np.full(len(ta) - 1, VMIN), np.full(len(ta) - 1, VMIN))
            p = np.r_[p, rp]; h = np.r_[h, rh]
            ii = np.round((np.arctan2(p[:, 1], p[:, 0]) % (2 * np.pi)) / dth).astype(int) % NT; jj = np.clip((p[:, 2] / DZ).astype(int), 0, NZ - 1)
            keepv = (pan_id[ii, jj] == k) | (pan_id[ii, jj] == -1) if k % 2 else np.ones(len(p), bool)
            VP.append(p[keepv]); VH.append(h[keepv])
            if src.get('cells') and len(pat['cen']):
                t_, z_ = m(pat['cen']); s3 = P3(form, t_, z_)
                si = np.round((t_ % (2 * np.pi)) / dth).astype(int) % NT; sj = np.clip((z_ / DZ).astype(int), 0, NZ - 1)
                seeds.append(s3[pan_id[si, sj] == k])
        stats.update(panels=n)
    VP = np.concatenate(VP); VH = np.concatenate(VH); seeds = np.concatenate(seeds)

    # ---- distance to the veins (dv <= 0 inside a vein) and to the cell walls
    if len(VP):
        d, ix = cKDTree(VP).query(Xf, k=min(8, len(VP))); dv = (d - VH[ix]).min(1).reshape(NT, NZ)
    else: dv = np.full((NT, NZ), 99.0)
    if len(seeds) > 3:
        d, ix = cKDTree(seeds).query(Xf, k=2); sep = np.linalg.norm(seeds[ix[:, 0]] - seeds[ix[:, 1]], axis=1)
        dw = ((d[:, 1] ** 2 - d[:, 0] ** 2) / (2 * np.maximum(sep, 1e-6))).reshape(NT, NZ)
    else: dw = np.full((NT, NZ), 99.0)

    # ---- the shell before holes
    amid = float(np.median(arc))
    if panel_in is not None:
        M0 = panel_in | (Z < FOOT_H)
    else:                                            # torn top: the shell ends just above the highest vein or cell seed at each bearing
        feat = VP if len(VP) else seeds; fb = (np.arctan2(feat[:, 1], feat[:, 0]) % (2 * np.pi) / dth).astype(int) % NT
        zmax = np.full(NT, H - 30.0); np.maximum.at(zmax, fb, feat[:, 2])
        win = max(3, int(round(math.radians(8) / dth))); zt = wrap_gauss(ndi.maximum_filter1d(zmax, win, mode='wrap'), win / 3) + 2.0
        zt = np.clip(zt, H - 30.0, H); M0 = Z <= zt[:, None]
    # every piece of shell needs shell under it within 42 degrees: fill straight down where it does not
    LOOK = 5
    for j in range(NZ - 1 - LOOK, -1, -1):
        w = max(1, int(0.8 * LOOK * DZ / max(1e-6, float(arc[:, j].mean()))))
        S = ndi.maximum_filter1d(M0[:, j].astype(np.uint8), 2 * w + 1, mode='wrap') > 0
        need = M0[:, j + LOOK] & ~S; M0[need, j] = True
    lab, _ = ndi.label(np.concatenate([M0, M0], 0)); good = np.unique(lab[:, 0]); good = good[good > 0]
    M0 = np.isin(lab, good)[:NT] | np.isin(lab, good)[NT:]
    sm = (arc.mean(), DZ)
    edge = np.where(M0, _edt_wrap(M0, sm, True, False), -_edt_wrap(~M0, sm, False, True))

    # ---- holes: positive inside
    hf = np.minimum(dv - (FLANK + FLANGE), dw - WALL_HALF) if len(seeds) > 3 else dv - (FLANK + FLANGE)
    if not len(VP): hf = dw - WALL_HALF
    hf = np.minimum(hf, np.minimum(Z - (FOOT_H + 3.0), edge - EDGE_KEEP))
    hf2 = np.concatenate([hf, hf], 0); lab, nlab = ndi.label(hf2 > 0); out = np.full((NT, NZ), -1.0); n_open = n_closed = 0
    arc2 = np.concatenate([arc, arc], 0)
    for L, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None or sl[0].start >= NT: continue
        if sl[0].stop - sl[0].start >= NT: n_closed += 1; continue
        sub = lab[sl] == L; h = np.where(sub, hf2[sl], -1.0)
        if h.max() < HOLE_MIN / 2: n_closed += 1; continue
        ii = (np.arange(sl[0].start, sl[0].stop) % NT)
        blk = out[ii, sl[1]]; out[ii, sl[1]] = np.where(sub, np.maximum(blk, h), blk); n_open += 1
    out = np.minimum(out, _row_tent(out, arc))       # every hole roof no flatter than WEDGE_K, from a pointed top
    hole = out
    mf = np.minimum(edge, -hole)
    # cable notch at theta = 0: 3 wide, 4 tall, pointed top
    a0 = ((TH + np.pi) % (2 * np.pi) - np.pi) * Rb; nf = np.minimum(NOTCH_W / 2 - np.abs(a0), WEDGE_K * (NOTCH_H - Z) + (NOTCH_W / 2 - WEDGE_K * (NOTCH_H - 1.5)) - np.abs(a0))
    nf = np.where(Z < NOTCH_H, nf, -1.0); mf = np.minimum(mf, -nf)
    mfc = np.clip(mf / CH_IN, -1, 1)

    # ---- radii
    relief = RELIEF * np.clip(1 - np.maximum(dv, 0) / FLANK, 0, 1)
    step = np.zeros((NT, NZ))
    if outer is not None:
        so = np.where(outer, _edt_wrap(outer, sm, True, False), -_edt_wrap(~outer, sm, False, True)); step = STEP * np.clip(1 + so / STEP, 0, 1)
    r_out = Rb + (relief + step) / cosl
    for j in range(NZ - 2, -1, -1): r_out[:, j] = np.maximum(r_out[:, j], r_out[:, j + 1] - SLOPE * DZ)
    r_in = Rb - T_SHELL / cosl
    foot = Z < FOOT_H; r_in = np.where(foot, np.maximum(HOLE_R, np.minimum(r_in, Rb - foot_w)), r_in)
    for j in range(1, NZ): r_in[:, j] = np.maximum(r_in[:, j], r_in[:, j - 1] - SLOPE * DZ)

    def mesh_from(mfc):
        # ---- marching cubes in parameter space: layers k = 0 (inside air), 1, 2 (wall), 3 (outside air)
        F = -np.ones((NT + 1, NZ + 2, 4), np.float32); F[:NT, 1:-1, 1] = mfc; F[NT, 1:-1, 1] = mfc[0]; F[:, :, 2] = F[:, :, 1]
        v, fc, _, _ = marching_cubes(F, 0.0)
        vi, vj, vk = v[:, 0], v[:, 1] - 1.0, v[:, 2]
        ext = lambda a: np.concatenate([a, a[:1]], 0)
        co = np.stack([vi, np.clip(vj, 0, NZ - 1)]); ri = ndi.map_coordinates(ext(r_in), co, order=1, mode='nearest'); ro = ndi.map_coordinates(ext(r_out), co, order=1, mode='nearest')
        rho = np.interp(vk, [0.5, 1.0, 2.0, 2.5], [0, 1, 2, 3])            # piecewise: inner face, inner chamfer, outer chamfer, outer face
        knots = np.stack([ri, np.minimum(ri + CH_IN, ro), np.maximum(ro - CH_OUT, ri), ro], 1)
        lo = np.clip(np.floor(rho).astype(int), 0, 2); fr = rho - lo; rr = knots[np.arange(len(v)), lo] * (1 - fr) + knots[np.arange(len(v)), lo + 1] * fr
        tt = np.where(vi >= NT - 1e-6, 0.0, vi) * dth; zz = np.clip((vj + 0.5) * DZ, 0, H)
        V3 = np.stack([rr * np.cos(tt), rr * np.sin(tt), zz], 1)
        mesh = trimesh.Trimesh(V3, fc, process=False); mesh.merge_vertices(digits_vertex=4); mesh.update_faces(mesh.nondegenerate_faces()); mesh.remove_unreferenced_vertices()
        if mesh.volume < 0: mesh.invert()
        return mesh

    mesh = mesh_from(mfc); stats['remesh'] = 0
    for sig in (0.5, 0.8, 1.2):                  # a ring of four cells that meet at one corner gives a non-manifold edge: soften the field a little and mesh again
        if mesh.is_watertight: break
        mesh = mesh_from(np.clip(ndi.gaussian_filter(np.concatenate([mfc, mfc, mfc], 0), sig)[NT:2 * NT], -1, 1)); stats['remesh'] = sig

    stats.update(grid=[NT, NZ], holes_open=n_open, cells_kept_closed=n_closed, tris_raw=len(mesh.faces),
                 web_fail_mm2=_web_check(mf, arc, DZ), shell_mm2=float((M0 * arc * DZ).sum()))
    return mesh, form, stats


def _sdf1d(f, s, Lt):
    """signed distance along one ring (positive inside f > 0), periodic, with the runs of f > 0 as (lo, hi) arc intervals"""
    n = len(f); fp = np.roll(f, -1); sp = np.roll(s, -1); sp[-1] += Lt; ch = (f > 0) != (fp > 0)
    if not ch.any(): return (np.full(n, 1e3) if f[0] > 0 else np.full(n, -1e3)), ([(0.0, Lt)] if f[0] > 0 else [])
    pos = s[ch] + (sp[ch] - s[ch]) * f[ch] / (f[ch] - fp[ch]); rising = ~(f[ch] > 0)
    ext = np.concatenate([pos - Lt, pos, pos + Lt]); k = np.searchsorted(ext, s)
    d = np.minimum(np.abs(s - ext[np.clip(k - 1, 0, len(ext) - 1)]), np.abs(ext[np.clip(k, 0, len(ext) - 1)] - s))
    runs = []
    for q in range(len(pos)):
        if rising[q]:
            hi = pos[(q + 1) % len(pos)]; runs.append((float(pos[q]), float(hi if hi > pos[q] else hi + Lt)))
    return np.where(f > 0, d, -d), runs


def _row_tent(hsel, arc, K=WEDGE_K, bridge=0.1):
    """walk the rings from the top down: a hole may be at most K * DZ wider (each side) than the hole in the ring above,
    and a new hole starts as a point (bridge mm wide). Returns the lateral field to intersect with the hole field."""
    NT, NZ = hsel.shape; out = np.full(hsel.shape, -1.0); prev = np.full(NT, -1e3)
    for j in range(NZ - 1, -1, -1):
        f = hsel[:, j]
        if not (f > 0).any(): prev = np.full(NT, -1e3); continue
        a = arc[:, j]; s = np.cumsum(a) - a[0]; Lt = float(a.sum()); lat, runs = _sdf1d(f, s, Lt)
        cand = prev + K * DZ; seed = np.full(NT, -1e3)
        for lo, hi in runs:
            inrun = ((s - lo) % Lt) <= (hi - lo)
            if inrun.any() and cand[inrun].max() <= 0:
                c = ((lo + hi) / 2) % Lt; d = np.abs((s - c + Lt / 2) % Lt - Lt / 2); seed[inrun] = np.maximum(seed[inrun], bridge / 2 - d[inrun])
        L = np.minimum(lat, np.maximum(cand, seed)); Lr, _ = _sdf1d(L, s, Lt); out[:, j] = np.clip(Lr, -1, 1e3); prev = Lr
    return out


def _edt_wrap(mask, sampling, below=False, above=False):
    """euclidean distance (mm) to the nearest False cell, periodic in theta; below / above = the value assumed past the bottom and the top row"""
    NT = mask.shape[0]; t = np.concatenate([mask, mask, mask], 0)
    t = np.concatenate([np.full((3 * NT, 1), below), t, np.full((3 * NT, 1), above)], 1)
    return ndi.distance_transform_edt(t, sampling=sampling)[NT:2 * NT, 1:-1]


def _web_check(mf, arc, dz):
    """area of shell that an opening of radius 1.0 mm removes (webs and tips under 2.0 mm), mm2"""
    M = mf > 0; sm = (float(arc.mean()), dz); er = _edt_wrap(M, sm, True, False) >= 1.0
    back = _edt_wrap(~er, sm, False, True) <= 1.0 + 0.6
    thin = M & ~back; return float((thin * arc * dz).sum())


# ------------------------------------------------------------------ label, checks, export
def label_solid(text, r_mid, depth=0.6, size=4.2):
    """mirrored text on an arc, as prisms from z = -0.2 to depth, to subtract from the underside"""
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from shapely.geometry import Polygon
    from shapely import affinity
    from shapely.ops import unary_union
    fp = FontProperties(family='DejaVu Sans', weight='bold'); parts = []; x = 0.0; adv = []
    for ch in text:
        tp = TextPath((0, 0), ch if ch != ' ' else 'n', size=size, prop=fp); bb = tp.get_extents(); adv.append((ch, tp, bb.x0, bb.width));
    total = sum(a[3] + size * 0.14 for a in adv); ang0 = -total / 2 / r_mid
    for ch, tp, x0, wdt in adv:
        if ch != ' ':
            polys = [Polygon(p) for p in tp.to_polygons() if len(p) >= 4]; polys = [p.buffer(0) for p in polys if p.area > 1e-4]
            polys.sort(key=lambda p: -p.area); g = None
            for p in polys: g = p if g is None else (g.difference(p) if g.contains(p.representative_point()) else g.union(p))
            g = affinity.translate(g, -x0 - wdt / 2, -size * 0.36)
            g = affinity.scale(g, -1, 1, origin=(0, 0))                 # mirror: reads right from below
            a = ang0 + (x + wdt / 2) / r_mid
            g = affinity.translate(g, 0, -r_mid); g = affinity.rotate(g, -math.degrees(a), origin=(0, 0)); g = affinity.rotate(g, 180, origin=(0, 0))
            for q in (g.geoms if hasattr(g, 'geoms') else [g]):
                m = trimesh.creation.extrude_polygon(q, depth + 0.2); m.apply_translation([0, 0, -0.2]); parts.append(m)
        x += wdt + size * 0.14
    return parts


def checks(mesh, name):
    c = {}
    c['watertight'] = bool(mesh.is_watertight); c['shells'] = int(mesh.body_count)
    e = mesh.edges_sorted; _, cnt = np.unique(e, axis=0, return_counts=True); c['nonmanifold_edges'] = int((cnt != 2).sum())
    ext = mesh.extents; c['dims_mm'] = [round(float(x), 1) for x in ext]; c['dims_in'] = [round(float(x) / 25.4, 2) for x in ext]
    c['footprint_ok'] = bool(ext[0] <= 203 and ext[1] <= 203); c['margin_mm'] = [round((256 - float(ext[0])) / 2, 1), round((256 - float(ext[1])) / 2, 1)]
    c['height_ok'] = bool(ext[2] <= 256)
    n = mesh.face_normals; cz = mesh.triangles_center[:, 2]; a = mesh.area_faces
    down = (n[:, 2] < -math.sin(math.radians(45.5))) & (cz > 0.75)
    c['overhang_mm2'] = round(float(a[down].sum()), 2); c['overhang_faces'] = int(down.sum())
    big = 0.0
    if down.any():
        idx = np.nonzero(down)[0]; adj = mesh.face_adjacency; m = down[adj[:, 0]] & down[adj[:, 1]]
        import networkx as nx
        G = nx.Graph(); G.add_nodes_from(idx.tolist()); G.add_edges_from(adj[m].tolist())
        wide = 0.0
        for cc in nx.connected_components(G):
            cc = list(cc); ar = float(a[cc].sum()); big = max(big, ar)
            wide = max(wide, ar / max(0.4, float(np.ptp(mesh.vertices[mesh.faces[cc].ravel()], axis=0).max())))   # strip width = area over its longest extent
        c['overhang_widest_strip_mm'] = round(wide, 2)
    c.setdefault('overhang_widest_strip_mm', 0.0); c['overhang_largest_patch_mm2'] = round(big, 2)
    c['volume_cm3'] = round(float(mesh.volume) / 1000, 1); c['area_cm2'] = round(float(mesh.area) / 100, 1)
    solid = min(float(mesh.volume), float(mesh.area) * 0.85 + 0.15 * float(mesh.volume))
    c['grams_est'] = round(solid * PLA, 0); layers = float(ext[2]) / 0.2
    c['hours_est'] = round(c['grams_est'] / 22.0 + layers * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
    return c


def overlay_png(mesh, path, title, c):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from scipy.spatial import ConvexHull
    xy = mesh.vertices[:, :2] - (mesh.bounds[0][:2] + mesh.bounds[1][:2]) / 2; h = xy[ConvexHull(xy).vertices]
    fig, ax = plt.subplots(figsize=(5, 5.4), dpi=130)
    for s, ls, lb in ((256, '-', 'bed 256 mm'), (228.6, '--', '9 in'), (203, '--', '8 in (203 mm)')):
        ax.add_patch(plt.Rectangle((-s / 2, -s / 2), s, s, fill=False, ls=ls, lw=0.9, ec='#333')); ax.text(-s / 2 + 2, s / 2 - 7, lb, fontsize=6, family='monospace')
    ax.fill(h[:, 0], h[:, 1], fc='#9a4a2c55', ec='#9a4a2c', lw=1.0)
    ax.set_xlim(-135, 135); ax.set_ylim(-135, 135); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('%s\n%s x %s x %s mm (%s x %s x %s in) · margin to bed edge %s / %s mm · %s' % (title, *c['dims_mm'], *c['dims_in'], *c['margin_mm'], 'PASS' if c['pass'] else 'FAIL'), fontsize=6.5, family='monospace')
    fig.savefig(path, bbox_inches='tight'); plt.close(fig)


def main():
    ppath, seed, outdir, tile = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    par = json.load(open(ppath, encoding='utf-8')); par['_path'] = ppath; t0 = time.time()
    stem = '%s_%s_%s_s%02d_%dmm_v01' % (tile, par['mode_field'], par['shape_field'], seed, par['size_mm'])
    os.makedirs(outdir, exist_ok=True); stl = os.path.join(outdir, stem + '.stl')
    if os.path.exists(stl) and '--force' not in sys.argv: print('exists, skip', stem); return
    mesh, form, stats = build(par, seed, print)
    # decimate, keep the result only if it is still one closed manifold
    try:
        import manifold3d as m3
        M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32), tri_verts=np.asarray(mesh.faces, np.uint32)))
        if str(M.status()).endswith('NoError'):
            o = M.simplify(float(par.get('simplify_mm', 0.03))).to_mesh(); m2 = trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False)
            if m2.is_watertight and m2.body_count == mesh.body_count: mesh = m2; stats['decimated'] = 'manifold simplify %.2f mm' % float(par.get('simplify_mm', 0.03))
            else: stats['decimated'] = 'rejected'
        else: stats['decimated'] = 'input not manifold: ' + str(M.status())
    except Exception as ex: stats['decimated'] = 'error ' + str(ex)[:80]
    mesh.vertices[:, 2] = np.where(mesh.vertices[:, 2] < 0.02, 0.0, mesh.vertices[:, 2])
    # underside label
    label = '%s v01 s%02d' % (par['id'], seed); stats['label'] = label
    try:
        fw = float(par.get('foot_w', FOOT_W)); best = None
        for phi in np.radians(np.arange(20, 341, 5)):                      # the bearing where the foot ring is most even, clear of the notch
            win = phi + np.linspace(-0.5, 0.5, 21) * (len(label) * 3.6) / 40.0; rb = form.Rb(win, np.full(21, 0.2))
            if best is None or np.ptp(rb) < best[0]: best = (float(np.ptp(rb)), float(phi), float(rb.min()), float(rb.max()))
        _, phi, rbmin, rbmax = best; rin0 = max(HOLE_R, min(rbmax - T_SHELL, rbmax - fw)); rmid = (rbmin + rin0) / 2
        stats['label_ring_mm'] = [round(rin0, 1), round(rbmin, 1)]
        cutters = label_solid(label, rmid)
        cut = trimesh.boolean.union(cutters, engine='manifold') if len(cutters) > 1 else cutters[0]
        cut.apply_transform(trimesh.transformations.rotation_matrix(phi - math.pi / 2, [0, 0, 1]))
        m3 = trimesh.boolean.difference([mesh, cut], engine='manifold')
        if m3.is_watertight and len(m3.faces) > 1000: mesh = m3; stats['label_cut'] = True
        else: stats['label_cut'] = 'rejected'
    except Exception as ex: stats['label_cut'] = 'error ' + str(ex)[:120]
    c = checks(mesh, stem)
    c['min_wall_design_mm'] = dict(shell=T_SHELL, vein=VMIN, cell_wall=2 * WALL_HALF, web_across_vein=VMIN + 2 * (FLANK + FLANGE))
    c['web_under_2mm_mm2'] = round(stats['web_fail_mm2'], 1); c['web_under_2mm_pct'] = round(100 * stats['web_fail_mm2'] / max(1, stats['shell_mm2']), 2)
    c['pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok']
                     and c['overhang_widest_strip_mm'] <= 1.0 and c['web_under_2mm_pct'] <= 1.0 and stats.get('label_cut') is True)
    mesh.export(stl)
    try:
        sc = trimesh.Scene(); m4 = mesh.copy(); m4.apply_translation([128 - (m4.bounds[0][0] + m4.bounds[1][0]) / 2, 128 - (m4.bounds[0][1] + m4.bounds[1][1]) / 2, 0])
        sc.add_geometry(m4, node_name=stem, geom_name=stem); sc.export(os.path.join(outdir, stem + '_plate.3mf')); c['plate_3mf'] = True
    except Exception as ex: c['plate_3mf'] = 'error ' + str(ex)[:120]
    overlay_png(mesh, os.path.join(outdir, stem + '_bed.png'), stem, c)
    rep = dict(stem=stem, id=par['id'], tile=tile, seed=seed, form=par['form'], source=par['source'], source_study=par.get('source_study'), stats=stats, checks=c,
               tris=len(mesh.faces), build_s=round(time.time() - t0, 1), built=time.strftime('%Y-%m-%d %H:%M'))
    json.dump(rep, open(os.path.join(outdir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str)
    print(stem, 'PASS' if c['pass'] else 'FAIL', json.dumps({k: c[k] for k in ('watertight', 'shells', 'nonmanifold_edges', 'dims_mm', 'overhang_mm2', 'overhang_largest_patch_mm2', 'overhang_widest_strip_mm', 'web_under_2mm_pct', 'grams_est', 'hours_est')}),
          'holes', stats['holes_open'], 'closed', stats['cells_kept_closed'], 'tris', len(mesh.faces), 'label', stats.get('label_cut'), 'dec', stats.get('decimated'), '%.0fs' % (time.time() - t0))


if __name__ == '__main__': main()
