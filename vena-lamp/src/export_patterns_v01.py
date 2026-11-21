"""export_patterns_v01.py : run the venation-lab page headless and write one pattern JSON per spec.
A pattern = the page's graph.json (the P2 contract: nodes, edges, cells, units mm) plus the outline polygon in the same mm frame.
usage: python export_patterns_v01.py <page.html> <specs.json> <out_dir>
specs.json: {"name": {page params}, ...}. No em dashes."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
page, specs, out = Path(sys.argv[1]).resolve(), json.loads(Path(sys.argv[2]).read_text(encoding='utf-8')), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
JS = '''(sp) => { const p = {...VL.DEFAULTS, ...sp}; const res = VL.build(p);
  return {graph: JSON.parse(VL.graph(res)), outline: res.poly.map(q => [q[0]*res.mmPerU, q[1]*res.mmPerU]), stat: VL.statText(res)} }'''
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    pg.goto(page.as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    for name, sp in specs.items():
        r = pg.evaluate(JS, sp); r['spec'] = sp; r['page'] = page.name
        (out / (name + '.pattern.json')).write_text(json.dumps(r), encoding='utf-8')
        print(name, 'nodes', len(r['graph']['nodes']), 'edges', len(r['graph']['edges']), 'cells', len(r['graph']['cells']))
    b.close()
