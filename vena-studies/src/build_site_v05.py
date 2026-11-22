"""build_site_v05.py : write the Land and Lamp pages from their sources and assemble the site folder as Pages will serve it.
Reads 00_src/venation-lab_v05.html (stored studies, gallery captions), 00_src/land_page_v02.src.html, 00_src/lamp_page_v01.src.html (when present),
00_src/vena-lamp/VS06_specs_v01.json and VS06c_specs_v01.json. Writes 00_src/land_v02.html, 00_src/lamp_v01.html and _work/v05/site/
(index.html, land.html, lamp.html, vena-engine.js, wing_geom.js, studies/). Run from the project root. No em dashes."""
import io, json, os, re, shutil, glob
lab = io.open('00_src/venation-lab_v05.html', encoding='utf-8').read()
a = lab.index('const STUDIES=') + len('const STUDIES='); b = lab.index(';\nlet loaded=null'); studies = json.loads(lab[a:b])
a = lab.index('const SITE=') + len('const SITE='); b = lab.index(';\nfunction fig(t)'); site = json.loads(lab[a:b].replace('<\\/', '</'))
sheets = {s['id']: s for s in site['sheets']}
J = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')


def page(src, dst, subs):
    s = io.open(src, encoding='utf-8').read()
    for k, v in subs.items():
        assert s.count(k) == 1, (k, s.count(k)); s = s.replace(k, v)
    assert '—' not in s and '__' + 'STUD' not in s
    assert not re.search(r'\bE[1-4]\b|C3|STU1|[A-Z]:\\\\|Users', s), re.search(r'.{30}(\bE[1-4]\b|C3|STU1|[A-Z]:\\\\|Users).{30}', s).group(0)
    for k in ('localStorage', 'sessionStorage', 'document.cookie'): assert k not in s, k
    io.open(dst, 'w', encoding='utf-8', newline='\n').write(s); print(dst, len(s), 'chars')


vs08 = [dict(id=t['id'], img=t['img'], lines=t['lines']) for t in sheets['VS08']['tiles']]; assert len(vs08) == 16
page('00_src/land_page_v02.src.html', '00_src/land_v02.html', {'__STUDIES__': J(studies), '__VS08__': J(vs08)})
have_lamp = os.path.isfile('00_src/lamp_page_v01.src.html')
if have_lamp:
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
    print('lamps with print files', len(lamps), 'of', len(specs), 'specs;', 'with a gallery render', sum(1 for l in lamps if l['tile']))
    page('00_src/lamp_page_v01.src.html', '00_src/lamp_v01.html', {'__LAMPS__': J(lamps)})
S = '_work/v05/site'; os.makedirs(S + '/studies', exist_ok=True)
shutil.copyfile('00_src/venation-lab_v05.html', S + '/index.html'); shutil.copyfile('00_src/land_v02.html', S + '/land.html')
if have_lamp: shutil.copyfile('00_src/lamp_v01.html', S + '/lamp.html')
shutil.copyfile('00_src/vena-engine.js', S + '/vena-engine.js'); shutil.copyfile('00_src/wing_geom.js', S + '/wing_geom.js')
n = 0
for f in glob.glob('00_src/studies/VS0*-??.*'):
    d = S + '/studies/' + os.path.basename(f)
    if not os.path.isfile(d) or os.path.getsize(d) != os.path.getsize(f): shutil.copyfile(f, d)
    n += 1
print('site folder', S, 'images', n)
