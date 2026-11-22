"""check_engine_v05.py : engine equality. Builds the 32 stored studies (VS02, VS03) in venation-lab_v04.html and in each v05 page that loads
vena-engine.js, and compares a sha1 of every build (vein nodes, links, fixed veins, cells, closed faces, counts) and of the SVG export
without its version comment. usage: python check_engine_v05.py <out.json> <v04.html> <page.html> [<page.html> ...]. No em dashes."""
import sys, json, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
JS = r'''(specs) => { const out = {}; const r5 = v => Math.round(v * 1e5) / 1e5;
 for (const id of Object.keys(specs)) { const p = specs[id]; const res = build({...p});
  const o = {poly: res.poly.map(q => [r5(q[0]), r5(q[1])]), nodes: res.veins ? res.veins.nodes.map(n => [r5(n.x), r5(n.y), n.p, r5(n.w)]) : null, links: res.veins ? res.veins.links : null,
   fixed: res.fixed ? res.fixed.map(f => [f.name, f.pts.map(q => [r5(q[0]), r5(q[1])]), f.ws ? f.ws.map(r5) : r5(f.w)]) : null, cells: res.cel ? res.cel.polys.map(c => c.map(q => [r5(q[0]), r5(q[1])])) : null,
   ponds: res.ponds.map(c => c.map(q => [r5(q[0]), r5(q[1])])), segs: res.segs, clamped: res.clamped, walls: res.walls, u2: res.u2, mmPerU: res.mmPerU};
  out[id] = [JSON.stringify(o), svg(res).replace(/<!--[^>]*-->/, '')] }
 return out }'''
out, v04, pages = sys.argv[1], sys.argv[2], sys.argv[3:]; rep = {'pages': {}}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']); pg = b.new_page()
    pg.goto(Path(v04).resolve().as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    specs = pg.evaluate('(() => { const o = {}; Object.keys(VL.STUDIES).forEach(id => o[id] = VL.storedParams(id)); return o })()')
    h = lambda d: {k: [hashlib.sha1(x.encode()).hexdigest() for x in v] for k, v in d.items()}
    ref = h(pg.evaluate(JS, specs)); rep['studies'] = len(ref); rep['v04'] = ref
    for p in pages:
        pg.goto(Path(p).resolve().as_uri()); pg.wait_for_function('typeof build==="function" && typeof d3!=="undefined"', timeout=30000)
        got = h(pg.evaluate(JS, specs)); bad = [k for k in ref if got.get(k) != ref[k]]
        rep['pages'][Path(p).name] = dict(equal=len(ref) - len(bad), differ=bad)
    b.close()
Path(out).write_text(json.dumps(rep, indent=1), encoding='utf-8')
print('studies', rep['studies'], {k: (v['equal'], v['differ'][:3]) for k, v in rep['pages'].items()})
