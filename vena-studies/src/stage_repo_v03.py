"""stage_repo_v03.py : add the v05 site (Lab v05, Land, Lamp, the shared engine) to the staged repo by an explicit list. Unlike v02 this
touches only the files listed here; everything else in _repo/venation stays as pushed. MANIFEST.txt gains the new paths.
Nothing is added to git here. Run from the project root. Optional argument: a text file with extra 'source<TAB>repo path' lines. No em dashes."""
import os, io, sys, shutil, hashlib
R = '_repo/venation'
SRC = [('00_src/venation-lab_v05.html', 'src/index.html'), ('00_src/land_v02.html', 'src/land.html'), ('00_src/lamp_v01.html', 'src/lamp.html'), ('00_src/vena-engine.js', 'src/vena-engine.js')]
STUDY = ['venation-lab_v05.html', 'vena-engine.js', 'vena-engine_v05-modes.src.js', 'build_v05.py', 'build_site_v05.py', 'check_engine_v05.py', 'land_page_v01.src.html', 'land_v01.html', 'land_page_v02.src.html',
         'make_land_page_v02.py', 'land_v02.html', 'lamp_page_v01.src.html', 'lamp_v01.html', 'check_land_v01.py', 'check_land_v02.py', 'check_lamp_v01.py', 'smoke_land_v01.py', 'stage_repo_v03.py']
CONTACT = ['VS09_contact_site-land-v01_1842.png', 'VS09_contact_site-land-v01_1842_check.json', 'VS09_contact_site-land-v02_1859.png', 'VS09_contact_site-land-v02_1859_add2.png', 'VS09_contact_site-land-v02_1859_check.json',
           'VS10_contact_site-lamp-v01_1848.png', 'VS10_contact_site-lamp-v01_1848_check.json', 'VS10_contact_site-lamp-v01b_1900.png', 'VS10_contact_site-lamp-v01b_1900_check.json']
pairs = SRC + [('00_src/' + f, 'vena-studies/src/' + f) for f in STUDY] + [('00_contacts/' + f, 'vena-studies/contacts/' + f) for f in CONTACT]
if len(sys.argv) > 1:
    for line in io.open(sys.argv[1], encoding='utf-8').read().splitlines():
        if line.strip(): a, b = line.split('\t'); pairs.append((a, b))
M = [l for l in io.open(os.path.join(R, 'MANIFEST.txt'), encoding='utf-8').read().splitlines() if l.strip()]; new = []; sha = lambda p: hashlib.sha1(open(p, 'rb').read()).hexdigest()
for src, dst in pairs:
    assert os.path.isfile(src), src; d = os.path.join(R, dst); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(src, d); assert sha(src) == sha(d), dst
    if dst not in M: M.append(dst); new.append(dst)
M = sorted(set(M)); io.open(os.path.join(R, 'MANIFEST.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(M) + '\n')
tracked = ['.gitattributes', '.github/workflows/pages.yml', 'MANIFEST.txt'] if os.path.isfile(os.path.join(R, '.gitattributes')) else ['MANIFEST.txt']
io.open('_work/repo_manifest_v03.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(set(M + tracked))) + '\n')
io.open('_work/repo_stage_v03_list.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(set(dst for _, dst in pairs)) + ['MANIFEST.txt']) + '\n')
sz = sum(os.path.getsize(os.path.join(R, f)) for f in M if os.path.isfile(os.path.join(R, f)))
print(len(pairs), 'files staged,', len(new), 'new paths; manifest', len(M), 'paths, %.1f MB' % (sz / 1e6))
for src, dst in SRC: print(sha(src), src, '=', dst)
