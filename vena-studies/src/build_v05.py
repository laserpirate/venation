"""build_v05.py : split venation-lab_v04.html into vena-engine.js (growth, cells, faces, build, channels, svg, graph: the same functions,
moved, not rewritten) and venation-lab_v05.html (the Lab: controls, draw, stat, exports, galleries). v05 adds a top bar that links
Lab, Land, Lamp and Studies, an Open in Land link that carries the current state, and removes course codes from the page text.
Reads 00_src/venation-lab_v04.html. Writes 00_src/vena-engine.js and 00_src/venation-lab_v05.html. Run from the project root. No em dashes."""
import io
L = io.open('00_src/venation-lab_v04.html', encoding='utf-8').read().split('\n')
ln = lambda n: L[n - 1]
# engine line ranges in v04 (1 based, inclusive), each checked against how it starts
RANGES = [(179, 179, 'const W=1000,H=640;'), (182, 187, 'const PRESETS={'), (190, 190, 'const isWing='), (192, 467, 'function rng(seed)'),
          (489, 513, '/* ---------------- channels'), (532, 532, 'const pad2='), (534, 561, 'function ridgeList(res)')]
eng = []; take = set()
for a, b, s in RANGES:
    assert ln(a).startswith(s), (a, ln(a)[:60]); eng += L[a - 1:b] + ['']; take |= set(range(a, b + 1))
assert ln(467).rstrip().endswith('return ch}') and ln(513).rstrip().endswith('return[a,b]}') and ln(561).rstrip().endswith('}})}')
HEAD = '''/* vena-engine.js : the pattern engine of the Venation Lab, shared by the Lab, Land and Lamp pages.
   Moved line for line out of venation-lab_v04.html (build_v05.py); same functions, same seeds, same output for every v04 mode.
   v05 adds three modes at the end of this file (xylem, radiolaria, delaunay) and one line at the top of build() that hands them over.
   Needs d3-delaunay (global d3) and wing_geom.js (global WingGeom) loaded first. The page that loads it declares VERSION.
   Licence: see LICENSE in the repository root. */
'use strict';
'''
body = '\n'.join(eng).rstrip('\n') + '\n'
hook = 'function build(p){const t0=performance.now();'
assert body.count(hook) == 1
body = body.replace(hook, 'function build(p){if(EXTRA_MODES[p.mode])return EXTRA_MODES[p.mode](p);/* v05: the three added modes */const t0=performance.now();')
io.open('00_src/vena-engine.js', 'w', encoding='utf-8', newline='\n').write(HEAD + body + io.open('00_src/vena-engine_v05-modes.src.js', encoding='utf-8').read())
src = '\n'.join(l for i, l in enumerate(L, 1) if i not in take)


def rep(a, b, n=1):
    global src
    assert src.count(a) == n, (src.count(a), a[:70]); src = src.replace(a, b)


rep('      <option value="hybrid" selected>Hybrid: veins + cells</option>', '      <option value="hybrid" selected>Hybrid: veins + cells</option>\n      <option value="xylem">Xylem: dense closed veins, strong hierarchy</option>\n      <option value="radiolaria">Radiolaria: rounded openings, graded walls</option>\n      <option value="delaunay">Delaunay: triangulation of the cell seeds</option>')
rep('<title>Venation Lab v04</title>', '<title>Venation Lab v05</title>')
rep('<span class="sub">v04 ', '<span class="sub">v05 ')
rep("const VERSION='v04';", "const VERSION='v05';")
rep('from the C3 E1 model', 'from the Clubtail model')
rep('full (E1, 13)', 'full (13)')
rep('<script src="wing_geom.js"></script>', '<script src="wing_geom.js"></script>\n<script src="vena-engine.js"></script>')
rep('<nav class="tabs"><button data-tab="lab" class="on">Lab</button><button data-tab="studies">Studies</button><button data-tab="lamps">Lamps</button></nav>',
    '<nav class="tabs"><button data-tab="lab" class="on">Lab</button><a class="nb" href="land.html">Land</a><a class="nb" href="lamp.html">Lamp</a><button data-tab="studies">Studies</button></nav>')
rep('.tabs{display:flex;gap:6px;margin-left:auto}', '.tabs{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto}a.nb{font:13px var(--sans);color:var(--ink);background:var(--panel);border:1px solid var(--line);padding:6px 10px;text-decoration:none}a.nb:hover{border-color:var(--ink)}')
rep('      <button id="study">Study grid ×8</button>', '      <button id="study">Study grid ×8</button>\n      <button id="toland">Open in Land</button>')
# the old Lamps tab (L1 to L6) now sits under Studies; the top bar entry Lamp is the new page
rep("$('tab-lamps').hidden=k!=='lamps'}", "$('tab-lamps').hidden=k!=='studies'}")
rep("buildTabs();", "buildTabs();\n$('toland').onclick=()=>{location.href='land.html#p='+encodeURIComponent(JSON.stringify(params()))};\nfunction fromHash(){const h=location.hash.replace('#','');if(h==='studies')showTab('studies');else if(h.indexOf('p=')===0){try{const q=JSON.parse(decodeURIComponent(h.slice(2)));['mode','shape','view','veinset','wingpass','nde','preset'].forEach(k=>{if(q[k]!=null)$(k).value=String(q[k])});P.forEach(k=>{if(q[k]!=null){$(k).value=q[k];$(k+'v').textContent=$(k).value}});if(q.sid)$('sid').value=q.sid}catch(e){}}}\nfromHash();window.addEventListener('hashchange',()=>{fromHash();run()});")
# gallery captions: episode codes out of the page text (the sheet images keep what was issued)
src = src.replace('E1 Clubtail', 'Clubtail').replace('keeps the E1 overhang', 'keeps the source model overhang')
import re
assert not re.search(r'E[1-4]|C3|STU1', src), re.search(r'.{30}(E[1-4]|C3|STU1).{30}', src).group(0)
assert '—' not in src
for bad in ('C3', ' E1', 'STU1'):
    body = src[:src.index('const SITE=')] + src[src.index('function fig(t)'):]
    assert bad not in body, bad
io.open('00_src/venation-lab_v05.html', 'w', encoding='utf-8', newline='\n').write(src)
print('engine lines', len(eng), 'lab v05 chars', len(src))
