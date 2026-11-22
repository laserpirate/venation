"""lamp_build_v04.py : v03 with the oblique planar rim on every pattern (surface patterns as well as panel wraps): the cut is set
before the pattern grows, a surface pattern runs up to the cut, and the torn-top rim rules are skipped under a cut. Every v03 spec without
a cut builds the same here; v03 stays as issued.
lamp_build_v03.py text follows : v02 plus the VS06c pieces (rows VLL-23 and up): an oblique planar rim on panel wraps (pattern.cut),
window below and open above (tech T1T2), a wide cylinder on a 45 degree shoulder (form cylw), and the window test piece
(form.R, pattern.sector_mm, window_bands). Every v02 spec builds the same here; v02 stays as issued.
lamp_build_v02.py text follows : vena-lamp mockups for FDM (Bambu P2S, translucent or clear PLA, no supports). Rows VLL-10 and up.
Second pass of the lamp builder. It imports lamp_build_v01 (00_src/lamps) for the shared helpers and leaves that file untouched.
Two techniques:
  T1 window : closed surface. Ribs (veins, cell walls) are 2.0 mm deep plus relief; every cell is closed by a thin window
              at mid depth of the rib. No holes, so no hole roofs.
  T2 open   : open holes with pointed roofs (the v01 ring by ring rule), veins and cells graded from foot to rim.
Pattern engine, one for every piece: fixed veins (named wing veins, a leaf midrib, foot roots), open colonization on the
surface from those veins, every free tip joined to the nearest vein that is not its own branch (no vein ends in a field),
and optional Voronoi cells cut on the surface. Fields live on a (bearing, height) grid of the base surface at 0.4 mm.
usage: python lamp_build_v04.py <specs.json> <piece key> <out_dir> [--force]
Units mm. No em dashes."""
import sys, os, json, math, time
import numpy as np
from scipy.spatial import cKDTree
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lamps'))
import lamp_build_v01 as v1

DZ = 0.4
T_SHELL = 2.0        # rib depth below the base surface
SLOPE = 0.9          # largest radial change per mm of height on any face that would look down (42 degrees)
FLANK = 0.5          # run from a rib edge to the full window
WIN_MIN = 1.5        # least window width (T1); smaller cells are closed as rib
HOLE_MIN = 2.0       # least hole (T2)
FLANGE = 0.3         # T2: shell kept each side of a rib before the hole starts
STEP = 1.2           # outer panels sit this far proud
IN = 25.4
PATDIR = os.path.join(HERE, '..', 'lamps', 'patterns')


class Form:
    """egg or cylinder over a base cylinder. The foot sleeves over the base: internal diameter = base + 0.5 mm."""
    def __init__(s, f):
        s.type = f['type']; s.H = float(f['H']); s.base_in = float(f['base_in']); s.rbase = (s.base_in * IN + 0.5) / 2
        s.collar = float(f.get('collar_in', 0.25 if s.base_in >= 6 else 0.5)) * IN
        s.zp0 = s.collar + 2.0                         # the pattern starts here
        if s.type == 'egg':
            s.r0 = s.rbase + float(f.get('foot_wall', 3.0)); s.Rmax = float(f['W']) / 2
            s.zc = float(f.get('zc', 0.365 * s.H)); rtop = float(f.get('rtop', 0.4 * s.Rmax))
            s.a = (s.H - s.zc) / math.sqrt(1 - (rtop / s.Rmax) ** 2)
        elif s.type == 'cylw':                         # wide cylinder: collar at the base radius, a shoulder of 0.85 mm out per mm up (40 degrees off vertical), then straight
            s.R0 = s.rbase + T_SHELL; s.R = float(f['W']) / 2; s.Rmax = s.R
        else:
            s.R = float(f['R']) if 'R' in f else s.rbase + T_SHELL; s.Rmax = s.R
            if 'R' in f: s.rbase = s.R - float(f.get('foot_w', 7.0))
    def Rb(s, th, z):
        z = np.asarray(z, float)
        if s.type == 'cylw': return np.clip(s.R0 + 0.85 * (z - s.zp0), s.R0, s.R) + 0 * np.asarray(th)
        if s.type == 'egg':
            lo = s.r0 + (s.Rmax - s.r0) * np.sin(0.5 * np.pi * np.clip(z / s.zc, 0, 1))
            hi = s.Rmax * np.sqrt(np.clip(1 - ((z - s.zc) / s.a) ** 2, 1e-6, 1))
            return np.where(z < s.zc, lo, hi) + 0 * np.asarray(th)
        return s.R + 0 * np.asarray(th) + 0 * z
    rmax = property(lambda s: s.Rmax)
    def tz(s, z, a, b):                               # a at the pattern start, b at the top
        t = np.clip((np.asarray(z, float) - s.zp0) / (s.H - s.zp0), 0, 1); return a + (b - a) * t


def P3(F, th, z):
    r = F.Rb(th, z); return np.stack([r * np.cos(th), r * np.sin(th), z + 0 * r], -1)


def darts(F, rng, sfun, zlo, ztop, accept=None, tries=14):
    """dart throwing on the surface with a spacing that may change with height; ztop(th) is the upper limit per bearing"""
    zz = np.linspace(zlo, F.H, 300); rr = F.Rb(0, zz); area = float(np.trapezoid(2 * np.pi * rr, zz))
    smin = float(min(sfun(zlo), sfun(F.H))); smax = float(max(sfun(zlo), sfun(F.H)))
    n = int(min(600000, tries * area / (smin * smin)))
    cz = rng.uniform(zlo, F.H, n); ct = rng.uniform(0, 2 * np.pi, n); keep = rng.uniform(0, 1, n) < np.interp(cz, zz, rr / rr.max())
    keep &= cz <= ztop(ct)
    if accept is not None: keep &= accept(ct, cz)
    cz, ct = cz[keep], ct[keep]; C = P3(F, ct, cz); S = sfun(cz); grid = {}; out = []
    K = np.floor(C / smax).astype(int)
    for p, s, k in zip(C, S, map(tuple, K)):
        ok = True; s2 = s * s
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for q in grid.get((k[0] + dx, k[1] + dy, k[2] + dz), ()):
                        d = p - q
                        if d[0] * d[0] + d[1] * d[1] + d[2] * d[2] < s2: ok = False; break
                    if not ok: break
                if not ok: break
            if not ok: break
        if ok: grid.setdefault(k, []).append(p); out.append(p)
    return np.array(out).reshape(-1, 3)


def grow_open(F, src, N, P, step, kill, infl, iters=500, closed=False):
    """colonization (Runions 2005) with every new node projected back to the surface. open (section 3): a source pulls its
    nearest node. closed (section 4, simplified): a source pulls every node of its relative neighbourhood among the 6 nearest,
    so veins come at it from several sides; it dies at the first arrival and the veins left short are joined by close_and_width."""
    def proj(q):
        th = np.arctan2(q[:, 1], q[:, 0]); return P3(F, th, np.clip(q[:, 2], F.zp0, F.H - 0.6))
    P = list(P); alive = np.ones(len(src), bool)
    for it in range(iters):
        live = np.nonzero(alive)[0]
        if not len(live): break
        tree = cKDTree(N)
        if closed and len(N) > 6:
            K = 6; d, ix = tree.query(src[live], k=K, distance_upper_bound=infl); val = np.isfinite(d); ixc = np.where(val, ix, 0)
            near = val[:, 0] & (d[:, 0] < kill); alive[live[near]] = False; val &= ~near[:, None]
            Nc = N[ixc]; pair = np.linalg.norm(Nc[:, :, None, :] - Nc[:, None, :, :], axis=3)          # [s, b, a]
            lower = np.triu(np.ones((K, K), bool), 1)[None]                                             # b closer than a
            excl = ((pair < np.where(val, d, 0)[:, None, :]) & val[:, :, None] & lower).any(axis=1); kp = val & ~excl
            si, ki = np.nonzero(kp)
            if not len(si): break
            tgt = ixc[si, ki]; v = src[live[si]] - N[tgt]; v /= np.maximum(np.linalg.norm(v, axis=1), 1e-9)[:, None]
            acc = np.zeros_like(N); np.add.at(acc, tgt, v)
        else:
            d, ix = tree.query(src[live], distance_upper_bound=infl); ok = np.isfinite(d)
            near = ok & (d < kill); alive[live[near]] = False; ok &= ~near
            if not ok.any(): break
            v = src[live[ok]] - N[ix[ok]]; v /= np.linalg.norm(v, axis=1)[:, None]
            acc = np.zeros_like(N); np.add.at(acc, ix[ok], v)
        l = np.linalg.norm(acc, axis=1); g = np.nonzero(l > 1e-3)[0]
        q = proj(N[g] + acc[g] / l[g, None] * step)
        mv = np.linalg.norm(q - N[g], axis=1) > 0.3 * step; d2, _ = tree.query(q); mv &= d2 > 0.35 * step
        g, q = g[mv], q[mv]
        if not len(g): break
        N = np.vstack([N, q]); P.extend(g.tolist())
    return N, np.array(P, int)


def close_and_width(F, N, P, fixedw, spacing, ex=2.6, gens=10, min_twig=3, ztop=None):
    """prune short twigs, join every free tip to the nearest vein that is not its own branch, prune what cannot be joined
    (unless it ends at the rim), then Murray widths from the tips. fixedw: width 0..1 for fixed nodes, nan for grown."""
    n = len(N); kids = np.bincount(P[P >= 0], minlength=n); dead = np.zeros(n, bool); cut = np.zeros(n); fixed = ~np.isnan(fixedw)
    def chain(i):
        c = [i]; x = i
        while P[x] >= 0 and kids[P[x]] == 1 and not fixed[P[x]]: x = P[x]; c.append(x)
        return c
    for i in np.nonzero((kids == 0) & (P >= 0) & ~fixed)[0]:
        c = chain(i)
        if len(c) < min_twig and P[c[-1]] >= 0: dead[c] = True; cut[P[c[-1]]] += 1
    kids2 = np.zeros(n, int)
    for i in range(n):
        if not dead[i] and P[i] >= 0: kids2[P[i]] += 1
    tips = np.nonzero((kids2 == 0) & ~dead & (P >= 0) & ~fixed)[0]; livei = np.nonzero(~dead)[0]; tree = cKDTree(N[livei]); links = []; pruned = 0
    def anc(i):
        s = set(); x = i
        for _ in range(gens):
            if x < 0: break
            s.add(x); x = P[x]
        return s
    if len(tips):
        d, ix = tree.query(N[tips], k=min(24, len(livei)), distance_upper_bound=2.6 * spacing)
        for t, dd, jj in zip(tips, d, ix):
            A = anc(t); done = False
            for q, j in zip(dd, jj):
                if not np.isfinite(q): break
                j = int(livei[j])
                if j in A or (A & anc(j)): continue
                links.append((int(t), j)); done = True; break
            if not done:
                th = math.atan2(N[t, 1], N[t, 0])
                if ztop is not None and N[t, 2] > float(ztop(np.array([th]))[0]) - 2.0 * spacing: continue     # a tip at the rim stays
                c = chain(t)
                if P[c[-1]] >= 0: dead[c] = True; cut[P[c[-1]]] += 1; pruned += 1
    w = np.zeros(n); k3 = np.zeros(n, int)
    for i in range(n):
        if not dead[i] and P[i] >= 0: k3[P[i]] += 1
    for i in range(n - 1, -1, -1):
        if dead[i]: continue
        if k3[i] == 0: w[i] = 1.0
        w[i] = (w[i] ** ex + cut[i]) ** (1 / ex)
        if P[i] >= 0: w[P[i]] = (w[P[i]] ** ex + w[i] ** ex) ** (1 / ex)
    g = ~dead & ~fixed
    wn = np.clip((w - 1) / max(1e-9, (np.percentile(w[g], 99.7) if g.any() else 2) - 1), 0, 1)
    wn = np.where(fixed, np.nan_to_num(fixedw), wn)
    return dead, wn, links, pruned


def smooth(F, N, P, fixed, n=4):
    kids = np.bincount(P[P >= 0], minlength=len(N)); only = np.full(len(N), -1); only[P[P >= 0]] = np.nonzero(P >= 0)[0]
    mid = (P >= 0) & (kids == 1) & ~fixed
    for _ in range(n):
        q = N.copy(); q[mid] = 0.25 * N[P[mid]] + 0.5 * N[mid] + 0.25 * N[only[mid]]
        N = P3(F, np.arctan2(q[:, 1], q[:, 0]), q[:, 2])
    return N


def densify(F, th, z, E, w, maxlen=1.5):
    """graph in (th, z) with edges parent -> child: returns 3D nodes, parent index and width, edges cut to maxlen"""
    N = []; P = []; W = []; idx = {}
    kids = {}
    for a, b in E: kids.setdefault(int(a), []).append(int(b))
    roots = sorted(set(int(a) for a, b in E) - set(int(b) for a, b in E))
    stack = [(r, -1) for r in roots]
    while stack:
        i, par = stack.pop()
        if i in idx: continue
        if par >= 0:
            pa = idx[par]; L = math.hypot((th[i] - th[par]) * F.rmax, z[i] - z[par]); m = max(1, int(math.ceil(L / maxlen)))
            for s in range(1, m):
                t = s / m; N.append((th[par] + (th[i] - th[par]) * t, z[par] + (z[i] - z[par]) * t)); P.append(pa); W.append(w[par] + (w[i] - w[par]) * t); pa = len(N) - 1
            N.append((th[i], z[i])); P.append(pa); W.append(w[i])
        else:
            N.append((th[i], z[i])); P.append(-1); W.append(w[i])
        idx[i] = len(N) - 1
        for c in kids.get(i, ()): stack.append((c, i))
    N = np.array(N).reshape(-1, 2)
    return P3(F, N[:, 0], N[:, 1]), np.array(P, int), np.array(W, float)


def union_wrap(lab):
    """merge the labels that meet across the bearing seam"""
    a, b = lab[0], lab[-1]; m = (a > 0) & (b > 0) & (a != b)
    if not m.any(): return lab
    par = np.arange(lab.max() + 1)
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for x, y in set(zip(a[m].tolist(), b[m].tolist())):
        rx, ry = find(x), find(y)
        if rx != ry: par[max(rx, ry)] = min(rx, ry)
    for i in range(len(par)): par[i] = find(i)
    return par[lab]


def build(sp, log=print):
    F = Form(sp['form']); H = F.H; rng = np.random.default_rng(sp['seed']); tech = sp['tech']; tw = float(sp.get('window_mm', 0.85)); pt = sp['pattern']
    NT = int(round(2 * np.pi * (F.rmax + 1.5) / DZ)); NZ = int(round(H / DZ)); dth = 2 * np.pi / NT
    th = np.arange(NT) * dth; z = (np.arange(NZ) + 0.5) * DZ; TH, Z = np.meshgrid(th, z, indexing='ij')
    Rb = F.Rb(TH, Z); Xf = np.stack([Rb * np.cos(TH), Rb * np.sin(TH), Z], -1).reshape(-1, 3); arc = Rb * dth
    dRdz = np.gradient(Rb, DZ, axis=1); cosl = 1 / np.sqrt(1 + dRdz ** 2)
    stats = {}
    # ---- the torn top: the pattern ends at ztop(bearing), a few smooth waves and an optional tilt
    tear = float(pt.get('tear', 14.0)); tilt = float(pt.get('tilt', 0.0)); ph = rng.uniform(0, 2 * np.pi, 4); am = rng.uniform(0.4, 1.0, 4)
    def ztop(t):
        t = np.asarray(t, float); n = sum(a * np.sin((k + 1) * t + p) for k, (a, p) in enumerate(zip(am, ph))) / am.sum()
        return H - 1.5 - tear * (0.5 + 0.5 * n) - tilt * (0.5 + 0.5 * np.cos(t - ph[0]))
    zcut = None
    if pt.get('cut'):                                # one oblique plane through the top: z = zc + tan(a) * x', x' along bearing phi
        ct = pt['cut']; ta_ = math.tan(math.radians(ct['deg'])); phi = math.radians(ct.get('phi_deg', 200.0))
        def zcut(t):
            t = np.asarray(t, float); zz = np.full(t.shape, float(ct['zc']))
            for _ in range(8): zz = ct['zc'] + ta_ * F.Rb(t, zz) * np.cos(t - phi)
            return zz
        if pt['kind'] == 'surface':                  # v04: a surface pattern grows up to the cut, not to the torn top
            def ztop(t): return np.minimum(zcut(t) - 1.0, H - 1.5)
    vw = pt.get('vein_w', {'foot': [1.4, 4.0], 'rim': [1.2, 2.4]})
    def wmm(wn, zz): return F.tz(zz, vw['foot'][0], vw['rim'][0]) + wn * (F.tz(zz, vw['foot'][1], vw['rim'][1]) - F.tz(zz, vw['foot'][0], vw['rim'][0]))
    VP = []; VH = []; seeds = []; panel_in = None; outer = None; pan_id = None

    def veins(N, P, fixedw, spacing, src):
        """grow from N toward src, close, width, sample"""
        if src is not None and len(src):
            N2, P2 = grow_open(F, src, N, P, float(pt.get('step', 1.5)), float(pt.get('kill_k', 0.55)) * spacing, 4.0 * spacing, closed=pt.get('grow', 'closed') == 'closed')
        else: N2, P2 = N, np.array(P, int)
        fw = np.r_[fixedw, np.full(len(N2) - len(N), np.nan)]; fixed = ~np.isnan(fw)
        N2 = smooth(F, N2, P2, fixed)
        dead, wn, links, pruned = close_and_width(F, N2, P2, fw, spacing, ztop=ztop, min_twig=int(pt.get('min_twig', 1)))
        w = wmm(wn, N2[:, 2]); idx = np.nonzero(~dead & (P2 >= 0))[0]
        if len(idx):
            p, h = v1.sample_edges(N2[P2[idx]], N2[idx], w[P2[idx]], w[idx]); VP.append(p); VH.append(h)
        if links:
            la = np.array(links); wl = np.minimum(w[la[:, 0]], w[la[:, 1]])
            p, h = v1.sample_edges(N2[la[:, 0]], N2[la[:, 1]], wl, wl); VP.append(p); VH.append(h)
        stats['vein_nodes'] = stats.get('vein_nodes', 0) + int((~dead).sum()); stats['tip_links'] = stats.get('tip_links', 0) + len(links)
        stats['tips_pruned'] = stats.get('tips_pruned', 0) + int(pruned)

    kind = pt['kind']
    if kind == 'surface':
        if pt.get('vein_spacing'):
            vs = pt['vein_spacing']; sf = lambda zz: F.tz(zz, vs[0], vs[1])
            src = darts(F, rng, sf, F.zp0 + 2, ztop)
            nr = int(pt.get('roots', 4)); N = []; P = []
            for k in range(nr):
                t0 = 2 * np.pi * (k + rng.uniform(0.2, 0.8)) / nr; prev = -1
                for s in range(3): N.append(P3(F, t0, F.zp0 + s * 1.5)); P.append(prev); prev = len(N) - 1
            veins(np.array(N), P, np.full(len(N), np.nan), float(np.mean(vs)), src); stats['vein_sources'] = len(src)
        if pt.get('cell_spacing'):
            cs = pt['cell_spacing']; seeds.append(darts(F, rng, lambda zz: F.tz(zz, cs[0], cs[1]), F.zp0 + 1, ztop))
    elif kind == 'panels':
        from matplotlib.path import Path as MPath
        n = int(pt['count']); hs = np.pi / n + (float(pt.get('overlap', 6.0)) / 2) / F.rmax
        panel_in = np.zeros((NT, NZ), bool); outer = np.zeros((NT, NZ), bool); pan_id = np.full((NT, NZ), -1)
        pats = [v1.load_pattern(os.path.join(PATDIR, nm + '.pattern.json')) for nm in pt['patterns']]
        zlo = F.zp0; ztp = H - 1.0; order = list(range(0, n, 2)) + list(range(1, n, 2)); info = {}
        for k in order:
            pat = pats[k % len(pats)]; thc = 2 * np.pi * (k + 0.5) / n; x0, x1, ym, yh = v1.panel_frame(pat)
            un = (Z - zlo) / (ztp - zlo); vn = ((TH - thc + np.pi) % (2 * np.pi) - np.pi) / hs
            poly = MPath(np.c_[(pat['outline'][:, 0] - x0) / (x1 - x0), (pat['outline'][:, 1] - ym) / yh])
            ins = poly.contains_points(np.c_[un.ravel(), vn.ravel()]).reshape(NT, NZ) & (np.abs(vn) <= 1.0)
            vis = ins & ~outer if k % 2 else ins
            if k % 2 == 0 and n > 1: outer |= ins
            pan_id[vis] = k; panel_in |= ins; info[k] = (pat, thc, v1.panel_mapper(pat, thc, hs, zlo, ztp))
        if n == 1:                                   # the panel meets itself: a 6 mm lap, raised, 45 degree sides
            seam = np.abs(((TH - np.pi + np.pi) % (2 * np.pi) - np.pi) * Rb); outer = panel_in & (seam < 3.0) & (np.abs(((TH + np.pi) % (2 * np.pi) - np.pi)) > 1.0)
            outer = panel_in & (np.abs((TH - np.pi) * Rb) < 3.0)
        def visacc(k):
            def f(t, zz):
                ii = np.round((t % (2 * np.pi)) / dth).astype(int) % NT; jj = np.clip((zz / DZ).astype(int), 0, NZ - 1); return pan_id[ii, jj] == k
            return f
        def onpan(p, k, odd):
            ii = np.round((np.arctan2(p[:, 1], p[:, 0]) % (2 * np.pi)) / dth).astype(int) % NT; jj = np.clip((p[:, 2] / DZ).astype(int), 0, NZ - 1)
            return (pan_id[ii, jj] == k) | (pan_id[ii, jj] == -1) if odd else np.ones(len(p), bool)
        topf = lambda t: np.full(np.shape(t), H)
        for k in order:
            pat, thc, m = info[k]; x0, x1, ym, yh = v1.panel_frame(pat)
            oc = np.r_[pat['outline'], pat['outline'][:1]]; ta, za = m(oc)          # the outline as a rim vein
            rw = float(pt.get('rim_w', 1.6)); rp, rh = v1.sample_edges(P3(F, ta[:-1], za[:-1]), P3(F, ta[1:], za[1:]), np.full(len(ta) - 1, rw), np.full(len(ta) - 1, rw))
            kp = onpan(rp, k, k % 2); VP.append(rp[kp]); VH.append(rh[kp])
            if pt['fixed'] == 'named':               # wing: the named veins of the stored pattern, stretched with the panel
                t_, z_ = m(pat['xy']); wf = np.clip(pat['w'] / max(1e-9, np.percentile(pat['w'], 99.5)), 0, 1)
                N, P, W = densify(F, t_, z_, pat['E'], wf)
            else:                                    # leaf: a midrib from the foot to the tip
                mz = np.arange(zlo, ztp - 1.0, 1.5); N = P3(F, np.full(len(mz), thc), mz); P = np.r_[-1, np.arange(len(mz) - 1)]; W = np.linspace(1.0, 0.25, len(mz))
                N = list(N); P = list(P); W = list(W); va = visacc(k); ang = math.radians(float(pt.get('secondary_deg', 48))); gap = float(pt.get('secondary_gap', 11.0))
                for q, i0 in enumerate(range(int(6 / 1.5), len(mz) - 8, max(1, int(gap / 2 / 1.5)))):      # pinnate secondaries, alternate sides, 48 degrees off the midrib, curving up to the margin
                    sd = 1 if q % 2 else -1; t_ = thc; z_ = mz[i0]; par = i0; a_ = ang; w_ = 0.55 * W[i0]
                    for st in range(200):
                        r_ = float(F.Rb(0, z_)); t_ += sd * math.sin(a_) * 1.5 / r_; z_ += math.cos(a_) * 1.5; a_ = max(math.radians(12), a_ - math.radians(1.1))
                        if z_ > ztp - 2 or not bool(va(np.array([t_]), np.array([z_]))[0]): break
                        N.append(P3(F, t_, z_)); P.append(par); W.append(max(0.12, w_ * (1 - st / 60.0))); par = len(N) - 1
                N = np.array(N); P = np.array(P, int); W = np.array(W)
            src = None
            if pt.get('vein_spacing') and not pt.get('stored'):
                vs = pt['vein_spacing']; src = darts(F, rng, lambda zz: F.tz(zz, vs[0], vs[1]), zlo + 1, topf, accept=visacc(k))
            nv0 = len(VP); veins(N, P, W, float(np.mean(pt['vein_spacing'])) if pt.get('vein_spacing') else 6.0, src)
            for q in range(nv0, len(VP)):
                kp = onpan(VP[q], k, k % 2); VP[q] = VP[q][kp]; VH[q] = VH[q][kp]
            if pt.get('stored'):                     # warped, not regrown: the stored cells stretched with the panel
                t_, z_ = m(pat['cen']); s3 = P3(F, t_, z_); seeds.append(s3[visacc(k)(t_, z_)])
            elif pt.get('cell_spacing'):
                cs = pt['cell_spacing']; seeds.append(darts(F, rng, lambda zz: F.tz(zz, cs[0], cs[1]), zlo + 1, topf, accept=visacc(k)))
        stats['panels'] = n
    zcutg = None
    if zcut is not None:                             # v04: zcut defined above, before the pattern
        for q in range(len(VP)):
            kp = VP[q][:, 2] <= zcut(np.arctan2(VP[q][:, 1], VP[q][:, 0])) - 0.5; VP[q] = VP[q][kp]; VH[q] = VH[q][kp]
        for q in range(len(seeds)):
            if len(seeds[q]): seeds[q] = seeds[q][seeds[q][:, 2] <= zcut(np.arctan2(seeds[q][:, 1], seeds[q][:, 0])) - 2.0]
        tc = np.linspace(0, 2 * np.pi, 1500, endpoint=False); VP.append(P3(F, tc, zcut(tc) - 1.0)); VH.append(np.full(len(tc), 1.0))      # the cut edge is a 2.0 mm rib
        zcutg = zcut(th); stats['cut_deg'] = ct['deg']; stats['cut_z_mm'] = [round(float(zcutg.min()), 1), round(float(zcutg.max()), 1)]
    VP = np.concatenate(VP) if VP else np.zeros((0, 3)); VH = np.concatenate(VH) if VH else np.zeros(0)
    seeds = np.concatenate(seeds) if seeds else np.zeros((0, 3))
    if len(seeds) and len(VP) and pt.get('cell_spacing'):       # a cell seed too close to a vein makes a sliver: leave it out
        d, ix = cKDTree(VP).query(seeds); cs = pt['cell_spacing']; seeds = seeds[d - VH[ix] > 0.33 * F.tz(seeds[:, 2], cs[0], cs[1])]
    stats['cell_seeds'] = len(seeds); stats['vein_samples'] = len(VP)

    # ---- distance to the rib edge: dr <= 0 inside a rib, and the rib width that owns each grid point
    dr = np.full(NT * NZ, 99.0); wown = np.full(NT * NZ, 1.2)
    if len(VP):
        d, ix = cKDTree(VP).query(Xf, k=min(6, len(VP))); mm = d - VH[ix]; a = mm.argmin(1); dr = mm[np.arange(len(a)), a]; wown = 2 * VH[ix[np.arange(len(a)), a]]
    if len(seeds) > 3:
        d, ix = cKDTree(seeds).query(Xf, k=2); sep = np.linalg.norm(seeds[ix[:, 0]] - seeds[ix[:, 1]], axis=1)
        cw = pt.get('cell_w', [2.0, 1.2]); wh = F.tz(Xf[:, 2], cw[0], cw[1]) / 2
        dwl = (d[:, 1] ** 2 - d[:, 0] ** 2) / (2 * np.maximum(sep, 1e-6)) - wh
        wown = np.where(dwl < dr, 2 * wh, wown); dr = np.minimum(dr, dwl)
    dr = dr.reshape(NT, NZ); wown = wown.reshape(NT, NZ)
    dr = np.minimum(dr, Z - F.zp0)                   # the foot is solid
    sarc = (TH - np.pi) * Rb                         # arc from bearing 180, for the test piece sector
    if pt.get('sector_mm'):
        dr = np.minimum(dr, np.minimum(float(pt['sector_mm']) - 2.0 - np.abs(sarc), (H - 2.4) - Z))       # 2 mm ribs at the two ends and along the top

    # ---- the shell domain
    if zcutg is not None:
        D = Z <= zcutg[:, None]; zt = zcutg          # closed below the cut: panels are pattern, the surface between them is plain skin
    elif pt.get('sector_mm'):
        D = (np.abs(sarc) < float(pt['sector_mm'])) & (Z <= H - 0.4)
    elif panel_in is not None:
        D = panel_in | (Z < F.zp0)
    else:
        feat = np.concatenate([VP, seeds]); fb = (np.arctan2(feat[:, 1], feat[:, 0]) % (2 * np.pi) / dth).astype(int) % NT
        zmax = np.full(NT, H - 60.0); np.maximum.at(zmax, fb, feat[:, 2])
        win = max(3, int(round(math.radians(5) / dth))); zt = v1.wrap_gauss(ndi.maximum_filter1d(zmax, win, mode='wrap'), win / 3) + 1.2
        D = Z <= np.clip(zt, H - 60.0, H)[:, None]
    lab, nl = ndi.label((dr > 0) & D); lab = union_wrap(lab)
    ids = np.unique(lab); ids = ids[ids > 0]
    inscr = 2 * ndi.maximum(dr, lab, ids)            # widest circle that fits each cell (true mm: dr is a 3D distance)
    small = ids[inscr < (WIN_MIN if tech == 'T1' else HOLE_MIN)]
    cutids = np.array([], int)
    if panel_in is None and zcutg is None and not pt.get('sector_mm'):  # the rim (torn top only): cells that reach the top of the domain are left out, the ribs between them stay as tips
        top = D & ~np.roll(D, -1, axis=1); top[:, -1] = D[:, -1]
        near = ndi.binary_dilation(top, iterations=int(pt.get('rim_px', 2))) & D; cutids = np.setdiff1d(np.unique(lab[near]), [0])
        zlow = ndi.minimum(Z, lab, cutids) if len(cutids) else np.array([]); cutids = cutids[zlow > float(np.median(zt)) - 28.0]      # a lane that runs far down the body is not a rim cell
        D = D & ~np.isin(lab, cutids)
    keep = np.setdiff1d(np.setdiff1d(ids, small), cutids)
    dr = np.where(np.isin(lab, small), -0.05, dr)
    stats.update(cells=int(len(keep)), cells_closed_small=int(len(small)), cells_cut_at_rim=int(len(cutids)),
                 least_cell_mm=round(float(inscr[np.isin(ids, keep)].min()), 2) if len(keep) else 0.0,
                 median_cell_mm=round(float(np.median(inscr[np.isin(ids, keep)])), 2) if len(keep) else 0.0)
    M0 = D.copy(); LOOK = 1
    if panel_in is not None: M0 = np.maximum.accumulate(M0[:, ::-1], axis=1)[:, ::-1]      # panels: closed surface, plain skin under every panel down to the foot
    for j in range(NZ - 1 - LOOK, -1, -1):           # shell needs shell under it within one grid step: fill straight down where it does not (v01 looked 5 rows down, which left flat slot tops up to 3 mm wide)
        w = 1
        S = ndi.maximum_filter1d(M0[:, j].astype(np.uint8), 2 * w + 1, mode='wrap') > 0
        need = M0[:, j + LOOK] & ~S; M0[need, j] = True
    if panel_in is None and zcutg is None and not pt.get('sector_mm'):  # rim tips (torn top only): a piece of shell stays only if shell sits under it within one grid step (45 degrees or steeper)
        for rep_ in range(2):                        # second pass after dropping fins under 1.2 mm wide (3 grid steps along the ring)
            for j in range(int(F.zp0 / DZ) + 2, NZ):
                M0[:, j] &= ndi.maximum_filter1d(M0[:, j - 1].astype(np.uint8), 3, mode='wrap') > 0
            if rep_ == 0:
                M3 = np.concatenate([M0, M0, M0], 0); M0 = ndi.binary_opening(M3, structure=np.ones((3, 1), bool))[NT:2 * NT]
    l2, _ = ndi.label(np.concatenate([M0, M0], 0)); good = np.unique(l2[:, 0]); good = good[good > 0]
    M0 = np.isin(l2, good)[:NT] | np.isin(l2, good)[NT:]
    sm = (float(arc.mean()), DZ)
    edge = np.where(M0, v1._edt_wrap(M0, sm, True, False), -v1._edt_wrap(~M0, sm, False, True))
    a0 = ((TH + np.pi) % (2 * np.pi) - np.pi) * Rb   # cable notch at bearing 0: 3 wide, 4 tall, pointed top
    nf = np.minimum(1.5 - np.abs(a0), v1.WEDGE_K * (4.0 - Z) + (1.5 - v1.WEDGE_K * 2.5) - np.abs(a0)); nf = np.where(Z < 4.0, nf, -1.0)

    rel = np.clip(0.35 + 0.45 * (wown - 1.2), 0.35, 1.6)       # relief follows rib width: hierarchy shows in height too
    step = np.zeros((NT, NZ))
    if outer is not None and outer.any():
        so = np.where(outer, v1._edt_wrap(outer, sm, True, False), -v1._edt_wrap(~outer, sm, False, True)); step = STEP * np.clip(1 + so / STEP, 0, 1)
    t = np.clip(dr / FLANK, 0, 1)
    if sp.get('window_bands'):                       # test piece: three window thicknesses side by side along the arc
        wb = sp['window_bands']; third = float(pt['sector_mm']) / 3; tw = np.where(sarc < -third, wb[0], np.where(sarc < third, wb[1], wb[2]))
    if tech == 'T1':
        e_out = rel * (1 - t) + (-(1.0 - tw / 2)) * t; e_in = -T_SHELL * (1 - t) + (-(1.0 + tw / 2)) * t
        mf = np.minimum(edge, -nf); ch = 0.25
    elif tech == 'T1T2':                             # windows below, open cells above, a dissolve between
        zs = float(sp.get('split_z', F.zp0 + (H - F.zp0) / 3)); band = float(sp.get('split_band', 12.0))
        zcen = ndi.mean(Z, lab, keep) if len(keep) else np.array([]); pr = np.clip((zcen - (zs - band)) / (2 * band), 0, 1)
        cand = keep[rng.uniform(0, 1, len(keep)) < pr]; inc = np.isin(lab, cand)
        hf = np.where(inc, np.minimum(dr - FLANGE, edge - 1.5), -1.0); hm = ndi.maximum(hf, lab, cand) if len(cand) else np.array([])
        openi = cand[2 * hm + 2 * FLANGE >= HOLE_MIN] if len(cand) else cand; opn = np.isin(lab, openi)
        out = np.where(opn, hf, -1.0); out = np.minimum(out, v1._row_tent(out, arc))
        stats['holes_open'] = int(len(openi)); stats['windows_kept'] = int(len(keep) - len(openi)); stats['split_z_mm'] = round(zs, 1); stats['split_band_mm'] = band
        stats['above_split_kept_closed'] = int((zcen > zs + band).sum() - np.isin(keep[zcen > zs + band], openi).sum())
        stats['least_hole_mm'] = round(float((2 * hm[np.isin(cand, openi)] + 2 * FLANGE).min()), 2) if len(openi) else 0.0
        e_out = np.where(opn, rel * (1 - t), rel * (1 - t) + (-(1.0 - tw / 2)) * t); e_in = np.where(opn, -T_SHELL, -T_SHELL * (1 - t) + (-(1.0 + tw / 2)) * t)
        mf = np.minimum(np.minimum(edge, -out), -nf); ch = 0.25
    else:
        hf = np.minimum(dr - FLANGE, np.minimum(Z - (F.zp0 + 1.0), edge - 1.5)); hl, _ = ndi.label(hf > 0); hl = union_wrap(hl); hi = np.unique(hl); hi = hi[hi > 0]
        hm = ndi.maximum(hf, hl, hi); openi = hi[2 * hm + 2 * FLANGE >= HOLE_MIN]
        out = np.where(np.isin(hl, openi), hf, -1.0); out = np.minimum(out, v1._row_tent(out, arc))
        stats['holes_open'] = int(len(openi)); stats['least_hole_mm'] = round(float((2 * hm[np.isin(hi, openi)] + 2 * FLANGE).min()), 2) if len(openi) else 0.0
        e_out = rel * (1 - t); e_in = np.full((NT, NZ), -T_SHELL)
        mf = np.minimum(np.minimum(edge, -out), -nf); ch = 0.3
    r_out = Rb + (e_out + step) / cosl; r_in = Rb + (e_in + step) / cosl
    foot = Z < F.collar; r_in = np.where(foot, F.rbase, r_in); r_in = np.where((Z >= F.collar) & (Z < F.zp0), Rb - T_SHELL / cosl, r_in)
    r_out = np.where(Z < F.zp0, Rb, r_out)
    for j in range(NZ - 2, -1, -1):
        r_out[:, j] = np.maximum(r_out[:, j], r_out[:, j + 1] - SLOPE * DZ)
        r_in[:, j] = np.where(Z[:, j] < F.collar, r_in[:, j], np.minimum(r_in[:, j], r_in[:, j + 1] + SLOPE * DZ))
    thick = (r_out - r_in) * cosl
    stats['min_skin_mm'] = round(float(thick[M0 & (Z > F.zp0)].min()), 2); stats['skin_under_window_mm'] = round(float((thick - tw)[M0 & (Z > F.zp0)].min()), 3)
    if tech in ('T1', 'T1T2') and not sp.get('window_bands'):
        wreg = M0 & np.isin(lab, keep); stats['window_area_pct'] = round(100 * float((wreg * arc).sum() / max(1e-9, (M0 * arc).sum())), 1)
        stats['window_clear_pct'] = round(100 * float(((wreg & (thick <= tw + 0.1)) * arc).sum() / max(1e-9, (wreg * arc).sum())), 1)
    mfc = np.clip(mf / ch, -1, 1)

    def mesh_from(mfc):
        Fd = -np.ones((NT + 1, NZ + 2, 4), np.float32); Fd[:NT, 1:-1, 1] = mfc; Fd[NT, 1:-1, 1] = mfc[0]; Fd[:, :, 2] = Fd[:, :, 1]
        v, fc, _, _ = marching_cubes(Fd, 0.0); vi, vj, vk = v[:, 0], v[:, 1] - 1.0, v[:, 2]
        ext = lambda a: np.concatenate([a, a[:1]], 0); co = np.stack([vi, np.clip(vj, 0, NZ - 1)])
        ri = ndi.map_coordinates(ext(r_in), co, order=1, mode='nearest'); ro = ndi.map_coordinates(ext(r_out), co, order=1, mode='nearest')
        rho = np.interp(vk, [0.5, 1.0, 2.0, 2.5], [0, 1, 2, 3]); mid = (ri + ro) / 2
        knots = np.stack([ri, np.minimum(ri + ch, mid), np.maximum(ro - ch, mid), ro], 1)
        lo = np.clip(np.floor(rho).astype(int), 0, 2); fr = rho - lo; rr = knots[np.arange(len(v)), lo] * (1 - fr) + knots[np.arange(len(v)), lo + 1] * fr
        tt = np.where(vi >= NT - 1e-6, 0.0, vi) * dth; zz = np.clip((vj + 0.5) * DZ, 0, H)
        m = trimesh.Trimesh(np.stack([rr * np.cos(tt), rr * np.sin(tt), zz], 1), fc, process=False); m.merge_vertices(digits_vertex=4)
        m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
        if m.volume < 0: m.invert()
        return m
    mesh = mesh_from(mfc); stats['remesh'] = 0
    for sig in (0.5, 0.8, 1.2):
        if mesh.is_watertight: break
        mesh = mesh_from(np.clip(ndi.gaussian_filter(np.concatenate([mfc, mfc, mfc], 0), sig)[NT:2 * NT], -1, 1)); stats['remesh'] = sig
    zz = np.linspace(F.zp0, H, 300); stats.update(grid=[NT, NZ], tris_raw=len(mesh.faces), shell_cm2=round(float((M0 * arc * DZ).sum()) / 100, 1),
                                                  rib_w_mm=[round(float(wown[M0 & (dr <= 0) & (Z > F.zp0)].min()), 2), round(float(wown[M0 & (dr <= 0) & (Z > F.zp0)].max()), 2)])
    return mesh, F, stats


def main():
    specs = json.load(open(sys.argv[1], encoding='utf-8')); key = sys.argv[2]; outdir = sys.argv[3]; sp = specs[key]; t0 = time.time()
    F0 = sp['form']; stem = '%s_s%02d_b%.2fin_h%dmm_%s' % (sp['id'], sp['seed'], F0['base_in'], round(F0['H']), sp.get('ver', 'v01'))
    os.makedirs(outdir, exist_ok=True); stl = os.path.join(outdir, stem + '.stl')
    if os.path.exists(stl) and '--force' not in sys.argv: print('exists, skip', stem); return
    mesh, F, stats = build(sp)
    try:
        import manifold3d as m3
        M = m3.Manifold(m3.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32), tri_verts=np.asarray(mesh.faces, np.uint32)))
        if str(M.status()).endswith('NoError'):
            stats['decimated'] = 'rejected'
            for tol in (0.03, 0.02, 0.012, 0.006):       # keep the first result that is still one closed volume after an STL round trip (float32, vertices merged by position)
                o = M.simplify(tol).to_mesh(); m2 = trimesh.Trimesh(np.asarray(o.vert_properties[:, :3], float), np.asarray(o.tri_verts), process=False)
                rt = trimesh.Trimesh(np.asarray(m2.vertices, np.float32).astype(float), m2.faces, process=True)
                if m2.is_watertight and m2.body_count == mesh.body_count and rt.is_watertight and rt.is_volume: mesh = m2; stats['decimated'] = 'manifold simplify %.3f mm' % tol; break
        else: stats['decimated'] = 'input not manifold: ' + str(M.status())
    except Exception as ex: stats['decimated'] = 'error ' + str(ex)[:80]
    mesh.vertices[:, 2] = np.where(mesh.vertices[:, 2] < 0.02, 0.0, mesh.vertices[:, 2])
    c = v1.checks(mesh, stem)
    c['grams_est'] = round(float(mesh.volume) * v1.PLA, 0); c['hours_est'] = round(c['grams_est'] / 22.0 + float(mesh.extents[2]) / 0.2 * 8 / 3600, 1); c['cost_usd_est'] = round(c['grams_est'] * 0.033, 2)
    tw = float(sp.get('window_mm', 0.85))
    if sp['tech'] == 'T1':
        c['least_window_mm'] = stats['least_cell_mm']; ok2 = stats['skin_under_window_mm'] >= -0.06 and stats['least_cell_mm'] >= WIN_MIN
    elif sp['tech'] == 'T1T2':
        c['least_window_mm'] = stats['least_cell_mm']; c['least_hole_mm'] = stats.get('least_hole_mm', 0.0)
        ok2 = stats['skin_under_window_mm'] >= -0.06 and stats['least_cell_mm'] >= WIN_MIN and stats.get('holes_open', 0) > 0 and c['least_hole_mm'] >= HOLE_MIN
    else:
        c['least_hole_mm'] = stats.get('least_hole_mm', 0.0); ok2 = stats.get('holes_open', 0) > 0 and c['least_hole_mm'] >= HOLE_MIN
    c['pass'] = bool(c['watertight'] and c['shells'] == 1 and c['nonmanifold_edges'] == 0 and c['footprint_ok'] and c['height_ok'] and c['overhang_widest_strip_mm'] <= 1.0 and ok2)
    c['pass_rule'] = 'watertight, one shell, 0 non-manifold edges, footprint in 203 x 203, height in 256, widest down-facing strip 1.0 mm or less (faces over 45.5 deg, above z 0.75), ' + ('skin at least the window thickness, least window 1.5 mm' if sp['tech'] == 'T1' else 'skin at least the window thickness, least window 1.5 mm, least hole 2.0 mm' if sp['tech'] == 'T1T2' else 'least hole 2.0 mm')
    mesh.export(stl)
    rl = trimesh.load(stl); stats['stl_reload_watertight'] = bool(rl.is_watertight and rl.is_volume)      # an STL carries no topology: vertices that share a position are merged on load
    rep = dict(stem=stem, id=sp['id'], key=key, seed=sp['seed'], tech=sp['tech'], window_mm=sp.get('window_bands', tw), form=sp['form'], pattern=sp['pattern'], note=sp.get('note'), stats=stats, checks=c,
               foot=dict(internal_diameter_mm=round(2 * F.rbase, 2), collar_mm=round(F.collar, 2)), tris=len(mesh.faces), build_s=round(time.time() - t0, 1), built=time.strftime('%Y-%m-%d %H:%M'))
    json.dump(rep, open(os.path.join(outdir, stem + '_check.json'), 'w', encoding='utf-8'), indent=1, default=str)
    print(stem, 'PASS' if c['pass'] else 'FAIL', 'cells', stats['cells'], 'small', stats['cells_closed_small'], 'rimcut', stats['cells_cut_at_rim'], 'least', stats['least_cell_mm'], 'med', stats['median_cell_mm'],
          'skin', stats['min_skin_mm'], 'holes', stats.get('holes_open'), 'strip', c['overhang_widest_strip_mm'], 'wt', c['watertight'], c['shells'], c['nonmanifold_edges'], c['dims_mm'],
          'g', c['grams_est'], 'h', c['hours_est'], 'tris', len(mesh.faces), 'links', stats.get('tip_links'), 'pruned', stats.get('tips_pruned'), 'remesh', stats['remesh'], '%.0fs' % (time.time() - t0))


if __name__ == '__main__': main()
