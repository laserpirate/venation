"""build_site_v06.py : write the v06 site. Lab v06 (venation-lab_v06.html, with its Studies list cut to the flat pattern sheets VS02, VS03,
the dragonfly sheets VS05, VS07 and the sample plates VS11), Land v03 (land_page_v03.src.html -> land_v03.html, with VS08), Lamp v02
(lamp_page_v02.src.html -> lamp_v02.html, with VS06a, VS06b, VS06c and VS04 marked superseded), the shared engine and the shared shell.
Writes 00_src/index_v06.html, land_v03.html, lamp_v02.html and the site folder _work/v06/site/. Run from the project root.
Optional argument: the lamp builder named on the Lamp page (default lamp_build_v03.py). No em dashes."""
import io, json, os, re, shutil, glob, sys
BUILDER = sys.argv[1] if len(sys.argv) > 1 else 'lamp_build_v03.py'
lab = io.open('00_src/venation-lab_v06.html', encoding='utf-8').read()
a = lab.index('const STUDIES=') + len('const STUDIES='); b = lab.index(';\nlet loaded=null'); studies = json.loads(lab[a:b])
a = lab.index('const SITE=') + len('const SITE='); b = lab.index(';\nfunction fig(t)'); site = json.loads(lab[a:b].replace('<\\/', '</'))
sheets = {s['id']: s for s in site['sheets']}
J = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
BAD = r'\bE[1-4]\b|C3|STU1|[A-Z]:[\\/]|Users[\\/]|gmail'
# school, plug-in and owner names are read from a local list that stays out of the repo (one regex per line)
if os.path.isfile('_work/v06/gate_terms.txt'): BAD += '|' + '|'.join(l.strip() for l in io.open('_work/v06/gate_terms.txt', encoding='utf-8') if l.strip())
else: print('warning: _work/v06/gate_terms.txt not found; school, plug-in and owner names are not gated')


def check(s, name):
    assert chr(0x2014) not in s and '__' + 'STUD' not in s and '__SHEETS__' not in s and '__BUILDER__' not in s, name
    m = re.search(BAD, s); assert not m, (name, s[max(0, m.start() - 40):m.end() + 40])
    for k in ('localStorage', 'sessionStorage', 'document.cookie'): assert k not in s, (name, k)


def page(src, dst, subs):
    s = io.open(src, encoding='utf-8').read()
    for k, v in subs.items():
        assert s.count(k) >= 1, (k, s.count(k)); s = s.replace(k, v)
    check(s, dst); io.open(dst, 'w', encoding='utf-8', newline='\n').write(s); print(dst, len(s), 'chars')


# Lab: Studies keeps VS02, VS03, VS05, VS07 and adds VS11; the lamp sheets and the L1 to L6 tab go to the Lamp page, VS08 to Land
vs11 = [('vena-samples--VS02__01_top.png', 'VS02 plate 1 of 2 · 9 tiles'), ('vena-samples--VS02__02_top.png', 'VS02 plate 2 of 2 · 7 tiles'),
        ('vena-samples--VS03__01_top.png', 'VS03 plate 1 of 2 · 8 tiles'), ('vena-samples--VS03__02_top.png', 'VS03 plate 2 of 2 · 8 tiles'),
        ('vena-samples--VS08__01_top.png', 'VS08 plate · 16 tiles'), ('vena-samples--VS08-05_close_v01.png', 'VS08-05 close-up')]
t11 = []
for i, (f, line) in enumerate(vs11):
    t11.append(dict(id='VS11-%02d' % (i + 1), img='studies/VS11-%02d.png' % (i + 1), src=f,
                    lines=['VS11-%02d · %s' % (i + 1, f.replace('.png', '').replace('_top', '')), line, 'from the tile heightfields, not a render', 'not sliced, not printed']))
keep = [sheets[k] for k in ('VS02', 'VS03', 'VS05', 'VS07')] + [dict(id='VS11', sheet='VS11_contact_vena-samples-v01_1915.png', tiles=[{k: v for k, v in t.items() if k != 'src'} for t in t11])]
site2 = dict(sheets=keep, lamps=[])
a = lab.index('const SITE=') + len('const SITE='); b = lab.index(';\nfunction fig(t)')
lab2 = lab[:a] + J(site2) + lab[b:]
check(lab2, 'index'); io.open('00_src/index_v06.html', 'w', encoding='utf-8', newline='\n').write(lab2); print('00_src/index_v06.html', len(lab2), 'chars')

vs08 = [dict(id=t['id'], img=t['img'], lines=t['lines']) for t in sheets['VS08']['tiles']]; assert len(vs08) == 16
page('00_src/land_page_v03.src.html', '00_src/land_v03.html', {'__STUDIES__': J(studies), '__VS08__': J(vs08)})

specs = {}
for f in ('00_src/vena-lamp/VS06_specs_v01.json', '00_src/vena-lamp/VS06c_specs_v01.json'): specs.update(json.load(io.open(f, encoding='utf-8')))
tiles = {}
for sid in ('VS06a', 'VS06b', 'VS06c'):
    for t in sheets[sid]['tiles']: tiles[t['id']] = dict(img=t['img'], lines=t['lines'], sheet=sid)
built = sorted(os.path.basename(f) for f in glob.glob('00_print/vena-lamp/*.stl'))
lamps = []
for key, sp in specs.items():
    stl = [f for f in built if f.startswith(sp['id'] + '_')]
    if not stl: continue
    lamps.append(dict(key=key, spec=sp, tile=tiles.get(sp['id']), stl=stl[0]))
lsheets = [dict(id=k, sheet=sheets[k]['sheet'], tiles=[dict(id=t['id'], img=t['img'], lines=t['lines']) for t in sheets[k]['tiles']]) for k in ('VS06a', 'VS06b', 'VS06c', 'VS04')]
old = [dict(id=l['id'], file=l['file'], params=l['params'], tiles=[t['id'] for t in l['tiles']]) for l in site['lamps']]
print('lamps with print files', len(lamps), 'of', len(specs), '; lamp sheets', [(s['id'], len(s['tiles'])) for s in lsheets], '; old lamp files', len(old))
page('00_src/lamp_page_v02.src.html', '00_src/lamp_v02.html', {'__LAMPS__': J(lamps), '__SHEETS__': J(lsheets), '__OLDLAMPS__': J(old), '__BUILDER__': BUILDER})

S = '_work/v06/site'; os.makedirs(S + '/studies', exist_ok=True)
for src, dst in (('00_src/index_v06.html', 'index.html'), ('00_src/land_v03.html', 'land.html'), ('00_src/lamp_v02.html', 'lamp.html'), ('00_src/vena-engine.js', 'vena-engine.js'),
                 ('00_src/wing_geom.js', 'wing_geom.js'), ('00_src/vena-shell_v01.js', 'vena-shell.js'), ('00_src/vena-shell_v01.css', 'vena-shell.css')):
    shutil.copyfile(src, S + '/' + dst)
for s in ('vena-shell.js', 'vena-shell.css'): check(io.open(S + '/' + s, encoding='utf-8').read(), s)
n = 0
for f in glob.glob('00_src/studies/VS0*-??.*'):
    d = S + '/studies/' + os.path.basename(f)
    if not os.path.isfile(d) or os.path.getsize(d) != os.path.getsize(f): shutil.copyfile(f, d)
    n += 1
for t in t11:
    shutil.copyfile('00_print/vena-samples/' + t['src'], '00_src/studies/' + os.path.basename(t['img'])); shutil.copyfile('00_print/vena-samples/' + t['src'], S + '/' + t['img']); n += 1
print('site folder', S, 'images', n)
