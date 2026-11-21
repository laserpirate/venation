"""build_v04.py : venation-lab_v04.html = v03 plus (a) Load study: every 2D study on VS02 and VS03 loads into the Lab with its stored
parameters, from a select or by a click on its gallery tile; (b) exports PNG at 2x and 4x and a vector PDF (jsPDF 2.5.1 from jsdelivr,
the one added library); (c) a Note field and Copy for chat (study ID, parameters changed against the stored ones, the note);
(d) galleries for VS06a, VS06b, VS06c, VS07, VS08 with artifact IDs. Reads 00_src/venation-lab_v03.html, 00_src/specs, the sheet JSON files
in _work/v03b and _work/v03c. Writes 00_src/venation-lab_v04.html and gallery images into 00_src/studies/. Run from the project root. No em dashes."""
import io, json, os
from PIL import Image
src = io.open('00_src/venation-lab_v03.html', encoding='utf-8').read()
def rep(a, b):
    global src
    assert src.count(a) == 1, (src.count(a), a[:70]); src = src.replace(a, b)

# ---- stored parameters of the 2D studies (the specs the sheets were drawn from, on this page's rules)
stud = {}
for sid, f in (('VS02', '00_src/specs/VS02_on_v02c.json'), ('VS03', '00_src/specs/VS03.json')):
    for i, sp in enumerate(json.load(io.open(f, encoding='utf-8'))):
        sp = {k: v for k, v in sp.items() if k != 'cmpNde'}; stud['%s-%02d' % (sid, i + 1)] = sp
# ---- new galleries
new = []
for sid, sj in (('VS06a', '_work/v03b/VS06a_sheet.json'), ('VS06b', '_work/v03b/VS06b_sheet.json'), ('VS06c', '_work/v03c/VS06c_sheet.json'), ('VS07', '_work/v03c/VS07_sheet.json'), ('VS08', '_work/v03c/VS08_sheet.json')):
    sp = json.load(io.open(sj, encoding='utf-8')); tiles = []
    for i, t in enumerate(sp['tiles']):
        name = '%s-%02d.jpg' % (sid, i + 1); im = Image.open(t['img']).convert('RGB'); im.thumbnail((800, 800)); im.save('00_src/studies/' + name, quality=86, optimize=True)
        tiles.append(dict(id=t['lines'][0], img='studies/' + name, lines=t['lines']))
    new.append(dict(id=sid, sheet=sp['title'].split(' · ')[1] if ' · ' in sp['title'] else sid, tiles=tiles))
a = src.index('const SITE=') + len('const SITE='); b = src.index(';\nfunction fig(t)'); site = json.loads(src[a:b].replace('<\\/', '</'))
site['sheets'] += new
src = src[:a] + json.dumps(site, ensure_ascii=False).replace('</', '<\\/') + src[b:]

rep('<title>Venation Lab v03</title>', '<title>Venation Lab v04</title>')
rep('<span class="sub">v03 ', '<span class="sub">v04 ')
rep("const VERSION='v03';", "const VERSION='v04';")
rep('      <button id="graph">graph.json</button>', '      <button id="graph">graph.json</button>\n      <button id="png2">PNG 2x</button>\n      <button id="png4">PNG 4x</button>\n      <button id="pdf">PDF, vector</button>')
rep('    <label class="row">Study ID<input id="sid"', '    <label class="row">Load study<select id="loadstudy" style="grid-column:1/3"><option value="">choose a study on VS02 or VS03</option></select></label>\n    <label class="row">Study ID<input id="sid"')
rep('    <textarea id="out" readonly', '    <label class="row">Note<textarea id="note" rows="3" style="grid-column:1/3;font:12px var(--mono);background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:6px" placeholder="What to change or keep on this study."></textarea></label>\n    <div class="btns"><button id="copychat">Copy for chat</button><span class="note" id="copystate"></span></div>\n    <textarea id="out" readonly')
rep('.gal figure{margin:0;', '.gal figure.load{cursor:pointer}.gal figure.load:hover{border-color:var(--ink)}\n.gal figure{margin:0;')
rep("function fig(t){const f=document.createElement('figure');", "function fig(t){const f=document.createElement('figure');if(STUDIES[t.id]){f.className='load';f.title='click to load '+t.id+' into the Lab';f.addEventListener('click',()=>loadStudy(t.id))}")
JS = r'''/* ---------------- v04: stored studies, load, PNG, PDF, note ---------------- */
const STUDIES=__STUD__;
let loaded=null;
function storedParams(id){const p={...DEFAULTS,...STUDIES[id],sid:id};const pr=PRESETS[p.preset];if(pr&&pr.mm)p.mm=pr.mm;return p}
function loadStudy(id){if(!STUDIES[id])return;const p=storedParams(id);['mode','shape','view','veinset','wingpass','nde','preset'].forEach(k=>{$(k).value=String(p[k])});
 P.forEach(k=>{$(k).value=p[k];$(k+'v').textContent=$(k).value});$('sid').value=id;$('loadstudy').value=id;loaded=id;showTab('lab');run();window.scrollTo({top:0})}
function changedParams(){const id=loaded&&STUDIES[loaded]?loaded:null;const now=params();if(!id)return {id:now.sid,changes:null};const st=storedParams(id);const ch=[];
 Object.keys(now).forEach(k=>{if(k==='sid')return;const a=st[k],b=now[k];if(String(a)!==String(b))ch.push(k+' '+a+' to '+b)});return {id,changes:ch}}
function chatText(){const c=changedParams();const note=$('note').value.trim();
 const first=c.changes===null?c.id+' · not a stored study · '+JSON.stringify(params()):c.id+' · '+(c.changes.length?'changed: '+c.changes.join(', '):'no parameters changed');
 return first+(note?'\nnote: '+note:'')}
function pngAt(k){if(!current)run();const c=document.createElement('canvas');c.width=1400*k;c.height=896*k;const ctx=c.getContext('2d');ctx.fillStyle='#ffffff';ctx.fillRect(0,0,c.width,c.height);draw(ctx,current,c.width/W);
 c.toBlob(b=>{const url=URL.createObjectURL(b);const a=document.createElement('a');a.href=url;a.download=fname(current,'png').replace('.png','_'+k+'x.png');document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),4000)},'image/png');return [c.width,c.height]}
function pdfDoc(){if(!current)run();if(!window.jspdf)return null;const res=current;const sc=res.mmPerU;const wmm=W*sc,hmm=640*sc;
 const doc=new window.jspdf.jsPDF({orientation:wmm>hmm?'landscape':'portrait',unit:'mm',format:[wmm,hmm],compress:true});
 const dom=new DOMParser().parseFromString(svg(res),'image/svg+xml');let n=0;const num=s=>s.trim().split(/[\s,]+/).map(Number);
 doc.setDrawColor(0);doc.setFillColor(0);doc.setLineCap('round');doc.setLineJoin('round');
 const poly=(pts,closed,style)=>{if(pts.length<4)return;const d=[];for(let i=2;i<pts.length;i+=2)d.push([pts[i]-pts[i-2],pts[i+1]-pts[i-1]]);doc.lines(d,pts[0],pts[1],[1,1],style,closed);n++};
 dom.querySelectorAll('g').forEach(g=>{const id=g.getAttribute('id');if(id==='ridges'||id==='channels')return;const gw=parseFloat(g.getAttribute('stroke-width')||'0.2');const fill=id==='pterostigma';
  Array.from(g.children).forEach(e=>{const w=parseFloat(e.getAttribute('stroke-width')||gw);doc.setLineWidth(Math.max(0.02,w));
   if(e.tagName==='line'){doc.line(+e.getAttribute('x1'),+e.getAttribute('y1'),+e.getAttribute('x2'),+e.getAttribute('y2'));n++}
   else if(e.tagName==='polyline')poly(num(e.getAttribute('points')),false,'S');
   else if(e.tagName==='polygon')poly(num(e.getAttribute('points')),true,fill?'F':'S');
   else if(e.tagName==='path'){(e.getAttribute('d')||'').split('M').filter(Boolean).forEach(sub=>poly(num(sub.replace(/Z/g,'').replace(/L/g,' ')),true,'S'))}})});
 return {doc,n,wmm,hmm}}
$('png2').onclick=()=>pngAt(2);$('png4').onclick=()=>pngAt(4);
$('pdf').onclick=()=>{const r=pdfDoc();if(!r){$('stat').textContent='PDF library did not load (needs network for jsdelivr).';return}r.doc.save(fname(current,'pdf'))};
$('copychat').onclick=()=>{const t=chatText();$('out').value=t;const done=()=>{$('copystate').textContent='copied'};
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(done,()=>{$('out').select();document.execCommand('copy');done()});else{$('out').select();document.execCommand('copy');done()}};
Object.keys(STUDIES).forEach(id=>{const o=document.createElement('option');o.value=id;o.textContent=id+' · '+STUDIES[id].mode+' · '+STUDIES[id].shape;$('loadstudy').appendChild(o)});
$('loadstudy').addEventListener('change',()=>{if($('loadstudy').value)loadStudy($('loadstudy').value)});
'''.replace('__STUD__', json.dumps(stud))
rep("/* ---------------- tabs: Studies (VS sheets as tile galleries) and Lamps (L1 to L6) ---------------- */", JS + "/* ---------------- tabs: Studies (VS sheets as tile galleries) and Lamps (L1 to L6) ---------------- */")
rep("window.VL={SITE,showTab,VERSION,", "window.VL={STUDIES,loadStudy,storedParams,changedParams,chatText,pngAt,pdfDoc,params,SITE,showTab,VERSION,")
# the one added library, loaded after d3-delaunay
i = src.index('d3-delaunay'); j = src.index('</script>', i) + len('</script>')
src = src[:j] + '\n<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>' + src[j:]
assert '—' not in src
io.open('00_src/venation-lab_v04.html', 'w', encoding='utf-8', newline='\n').write(src)
print('v04', len(src), 'chars', 'studies', len(stud), 'sheets', [(s['id'], len(s['tiles'])) for s in site['sheets']])
