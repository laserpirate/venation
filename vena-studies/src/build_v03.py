"""build_v03.py : venation-lab_v03.html = v02c plus a Studies tab (VS02 to VS05 tile galleries) and a Lamps tab (L1 to L6, parameter JSON, renders).
Reads 00_src/venation-lab_v02c.html, 00_src/studies/VS02.json and VS03.json (cut_tiles_v01.py), the VS04 and VS05 sheet check files in
00_contacts, the renders in 00_print, and 00_src/lamps/L*.json. Writes 00_src/venation-lab_v03.html and the tile PNGs for VS04 and VS05
into 00_src/studies/. Run from the project root. No em dashes."""
import io, json, glob, os, re
from PIL import Image
D = '·'
src = io.open('00_src/venation-lab_v02c.html', encoding='utf-8').read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:70]); src = src.replace(a, b)

def newest(pat):
    f = sorted(glob.glob(pat)); assert f, pat; return f[-1]

sheets = []
for sid in ('VS02', 'VS03'):
    chk = json.load(io.open(newest('00_contacts/%s_contact_*_check.json' % sid), encoding='utf-8'))
    tiles = json.load(io.open('00_src/studies/%s.json' % sid, encoding='utf-8'))
    sheets.append(dict(id=sid, sheet=os.path.basename(chk['png']).replace('\\', '/').split('/')[-1], tiles=[dict(id=t['id'], img='studies/' + t['img'], lines=t['lines']) for t in tiles]))
for sid, spec in (('VS04', '_work/VS04_sheet.json'), ('VS05', '_work/VS05_sheet.json')):
    chk = json.load(io.open(newest('00_contacts/%s_contact_*_check.json' % sid), encoding='utf-8')); sp = json.load(io.open(spec, encoding='utf-8')); tiles = []
    for i, (t, cap) in enumerate(zip(sp['tiles'], chk['captions'])):
        name = '%s-%02d.png' % (sid, i + 1); im = Image.open(t['img']).convert('RGB'); im.thumbnail((800, 800)); im.save('00_src/studies/' + name, optimize=True)
        tiles.append(dict(id=name[:-4], img='studies/' + name, lines=cap.split('\n')))
    sheets.append(dict(id=sid, sheet=chk['png'], tiles=tiles))
lamps = []
vs04 = {t['id']: t for t in sheets[2]['tiles']}
for f in sorted(glob.glob('00_src/lamps/L?.json')):
    p = json.load(io.open(f, encoding='utf-8')); mine = [t for t in sheets[2]['tiles'] if (' ' + p['id'] + ' ') in t['lines'][0]]
    lamps.append(dict(id=p['id'], file=os.path.basename(f), params=p, tiles=mine))
site = json.dumps(dict(sheets=sheets, lamps=lamps), ensure_ascii=False).replace('</', '<\\/')

rep('<title>Venation Lab v02c</title>', '<title>Venation Lab v03</title>')
rep('<span class="sub">v02c ' + D, '<span class="sub">v03 ' + D)
rep("const VERSION='v02c';", "const VERSION='v03';")
rep('body.sheet-mode>header,body.sheet-mode>.wrap{display:none}',
    'body.sheet-mode>header,body.sheet-mode>.wrap,body.sheet-mode>section{display:none}\n'
    '.tabs{display:flex;gap:6px;margin-left:auto}.tabs button.on{border-color:var(--ink);background:var(--bg)}\n'
    'section.tab{margin-top:16px}section.tab h2{font:500 13px var(--mono);letter-spacing:.04em;margin:22px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line)}\n'
    '.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}\n'
    '.gal figure{margin:0;border:1px solid var(--line);background:var(--panel);min-width:0}.gal img{display:block;width:100%;height:auto}\n'
    '.gal figcaption{font:11.5px/1.4 var(--mono);padding:6px 8px 8px;border-top:1px solid var(--line);background:var(--bg);overflow-wrap:anywhere}\n'
    'pre.params{font:11px/1.45 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;max-height:260px;overflow:auto;border:1px solid var(--line);background:var(--panel);padding:8px;margin:8px 0 0}\n'
    'details summary{font:12px var(--mono);cursor:pointer;margin-top:8px}')
rep('  <span class="sub">v03 ', '  <nav class="tabs"><button data-tab="lab" class="on">Lab</button><button data-tab="studies">Studies</button><button data-tab="lamps">Lamps</button></nav>\n  <span class="sub">v03 ')
rep('<div id="sheet"></div>', '<section class="tab" id="tab-studies" hidden></section>\n<section class="tab" id="tab-lamps" hidden></section>\n\n<div id="sheet"></div>')
rep("window.VL={VERSION,", '''/* ---------------- tabs: Studies (VS sheets as tile galleries) and Lamps (L1 to L6) ---------------- */
const SITE=''' + site + ''';
function fig(t){const f=document.createElement('figure');const im=document.createElement('img');im.loading='lazy';im.src=t.img;im.alt=t.id;f.appendChild(im);
 const c=document.createElement('figcaption');t.lines.forEach(x=>{const d=document.createElement('div');d.textContent=x;c.appendChild(d)});f.appendChild(c);return f}
function buildTabs(){const S=$('tab-studies');SITE.sheets.forEach(sh=>{const h=document.createElement('h2');h.textContent=sh.id+' \\u00b7 '+sh.sheet;S.appendChild(h);const g=document.createElement('div');g.className='gal';sh.tiles.forEach(t=>g.appendChild(fig(t)));S.appendChild(g)});
 const Lp=$('tab-lamps');SITE.lamps.forEach(l=>{const h=document.createElement('h2');h.textContent=l.id+' \\u00b7 '+l.params.source_study;Lp.appendChild(h);
  const n=document.createElement('p');n.className='note';n.textContent=l.params.note;Lp.appendChild(n);const g=document.createElement('div');g.className='gal';l.tiles.forEach(t=>g.appendChild(fig(t)));Lp.appendChild(g);
  const d=document.createElement('details');const s=document.createElement('summary');s.textContent=l.file;d.appendChild(s);const pre=document.createElement('pre');pre.className='params';pre.textContent=JSON.stringify(l.params,null,1);d.appendChild(pre);Lp.appendChild(d)})}
function showTab(k){document.querySelectorAll('.tabs button').forEach(b=>b.classList.toggle('on',b.dataset.tab===k));document.querySelector('.wrap').style.display=k==='lab'?'':'none';$('tab-studies').hidden=k!=='studies';$('tab-lamps').hidden=k!=='lamps'}
document.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>showTab(b.dataset.tab)));buildTabs();
window.VL={SITE,showTab,VERSION,''')
assert '—' not in src
io.open('00_src/venation-lab_v03.html', 'w', encoding='utf-8', newline='\n').write(src)
print('v03', len(src), 'chars', 'sheets', [(s['id'], len(s['tiles'])) for s in sheets], 'lamps', [(l['id'], len(l['tiles'])) for l in lamps])
