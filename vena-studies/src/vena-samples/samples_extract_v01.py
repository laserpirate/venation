"""samples_extract_v01.py : the 32 stored studies (VS02, VS03) as the page's engine builds them, one JSON each, for the sample tiles.
Lab units, y down. usage: python samples_extract_v01.py <lab page .html> <out_dir>. No em dashes."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
JS = r'''(id) => { const p = VL.storedParams(id); const res = VL.build({...p}); const r3 = v => Math.round(v * 1000) / 1000; const P = q => [r3(q[0]), r3(q[1])];
 const o = {id, mode: p.mode, shape: p.shape, wing: !!res.frame, outline: res.poly.map(P), tip: p.tip, maxw: p.maxw, fixed: [], segs: [], links: [], cells: []};
 if (res.fixed) res.fixed.forEach(f => o.fixed.push({name: f.name, pts: f.pts.map(P), w: f.ws ? f.ws.map(r3) : f.pts.map(() => r3(f.w))}));
 if (res.veins) { const N = res.veins.nodes; N.forEach(n => { if (n.p >= 0) { const q = N[n.p]; o.segs.push([r3(q.x), r3(q.y), r3(n.x), r3(n.y), r3(q.w || n.w), r3(n.w), (n.fixed && q.fixed) ? 1 : 0]) } }); res.veins.links.forEach(([i, j]) => o.links.push([r3(N[i].x), r3(N[i].y), r3(N[j].x), r3(N[j].y)])) }
 if (res.cel) res.cel.polys.forEach(c => o.cells.push(c.map(P)));
 o.stat = VL.statText(res).slice(0, 6); return o }'''
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(); pg.goto(Path(sys.argv[1]).resolve().as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    for i in pg.evaluate('Object.keys(VL.STUDIES)'):
        o = pg.evaluate(JS, i); (out / (i + '.pattern.json')).write_text(json.dumps(o), encoding='utf-8'); print(i, o['mode'], o['shape'], 'fixed', len(o['fixed']), 'segs', len(o['segs']), 'links', len(o['links']), 'cells', len(o['cells']))
    b.close()
