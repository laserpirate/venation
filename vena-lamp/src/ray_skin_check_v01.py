"""ray_skin_check_v01.py : wall thickness of a lamp mesh along 4000 horizontal rays from the axis, at bearings and heights
drawn at random (not on the mesh raster). Prints the percentiles of the radial thickness of the first wall each ray crosses.
Radial thickness is larger than normal thickness where the wall leans. usage: python ray_skin_check_v01.py <stl>. No em dashes."""
import sys, numpy as np, trimesh
m = trimesh.load(sys.argv[1]); rng = np.random.default_rng(1); n = 4000; H = m.bounds[1][2]
th = rng.uniform(0, 2 * np.pi, n); z = rng.uniform(22, H * 0.8, n)
o = np.c_[np.zeros(n), np.zeros(n), z]; d = np.c_[np.cos(th), np.sin(th), np.zeros(n)]
loc, ir, _ = m.ray.intersects_location(o, d, multiple_hits=True); r = np.hypot(loc[:, 0], loc[:, 1]); t = []
for i in range(n):
    rr = np.sort(r[ir == i])
    if len(rr) >= 2 and len(rr) % 2 == 0: t.append(rr[1] - rr[0])
t = np.array(t); print(__import__('os').path.basename(sys.argv[1]),'rays with a wall', len(t), 'of', n, 'radial thickness mm: min %.2f p1 %.2f p10 %.2f median %.2f p90 %.2f max %.2f' % (t.min(), *np.percentile(t, [1, 10, 50, 90]), t.max()), 'share under 0.80: %.2f pct' % (100 * (t < 0.80).mean()))
