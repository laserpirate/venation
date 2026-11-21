"""stage_repo_v01.py : copy the public set into _repo/venation by an explicit list and write MANIFEST.txt (one repo path per line).
Nothing is added to git here. Run from the project root. The layout: src/ is what Pages serves (index.html = venation-lab_v03.html and
its images); p1-studies, p2-lamps, p3-dfly, p4-ornithopter hold the phases. No em dashes."""
import os, io, glob, shutil, sys
R = '_repo/venation'; M = []


def put(src, dst):
    assert os.path.isfile(src), src; d = os.path.join(R, dst); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(src, d); M.append(dst)


def many(pattern, dst_dir, rename=None):
    fs = sorted(glob.glob(pattern)); assert fs, pattern
    for f in fs: put(f, dst_dir + '/' + (rename(os.path.basename(f)) if rename else os.path.basename(f)))


for d in ('src', 'p1-studies', 'p2-lamps', 'p3-dfly', 'p4-ornithopter', 'docs', '.github'):
    shutil.rmtree(os.path.join(R, d), ignore_errors=True)
# ---- the page Pages serves
put('00_src/venation-lab_v03.html', 'src/index.html'); put('00_src/wing_geom.js', 'src/wing_geom.js'); many('00_src/studies/VS0?-??.png', 'src/studies')
# ---- P1 studies
for f in ('venation-lab_v01.html', 'venation-lab_v02.html', 'venation-lab_v02b.html', 'venation-lab_v02c.html', 'venation-lab_v03.html', 'wing_geom.js', 'contact_sheet_v02.py', 'contact_sheet_v03.py',
          'cut_tiles_v01.py', 'image_sheet_v01.py', 'build_v03.py', 'check_v03.py', 'privacy_scan_v01.py', 'stage_repo_v01.py'):
    put('00_src/' + f, 'p1-studies/src/' + f)
many('00_src/specs/*.json', 'p1-studies/src/specs'); many('00_src/studies/VS0?.json', 'p1-studies/src/studies')
many('00_contacts/*.png', 'p1-studies/contacts'); many('00_contacts/*_check.json', 'p1-studies/contacts'); many('00_export_svg/VS02-10_*', 'p1-studies/export_svg')
# ---- P2 lamps
for f in ('lamp_build_v01.py', 'export_patterns_v01.py', 'render_v01.py', 'lamp_sheet_v01.py', 'make_specs.py'): put('00_src/lamps/' + f, 'p2-lamps/src/' + f)
many('00_src/lamps/L?.json', 'p2-lamps/params'); many('00_src/lamps/patterns/*.json', 'p2-lamps/params/patterns')
many('00_print/lamps-v01/*_plate.3mf', 'p2-lamps/print'); many('00_print/lamps-v01/*_check.json', 'p2-lamps/print'); many('00_print/lamps-v01/*_bed.png', 'p2-lamps/print')
many('00_print/lamps-v01/*_render.png', 'p2-lamps/renders'); put('00_print/lamps-v01/README.md', 'p2-lamps/README.md')
# ---- P3 dragonfly
for f in ('dfly_build_v01.py', 'dfly_sheet_v01.py'): put('00_src/dfly/' + f, 'p3-dfly/src/' + f)
many('00_src/dfly/patterns/*.json', 'p3-dfly/patterns')
put('00_src/dfly/' + 'STU' + '1211_E1_A1_dragonfly_print_v01.stl', 'p3-dfly/source/clubtail_print_E1_v01_source.stl')      # renamed: the source name carries a course code
many('00_print/dfly-v01/*.stl', 'p3-dfly/print'); many('00_print/dfly-v01/*_plate.3mf', 'p3-dfly/print'); many('00_print/dfly-v01/*_check.json', 'p3-dfly/print'); many('00_print/dfly-v01/*_bed.png', 'p3-dfly/print')
many('00_print/dfly-v01/*_render.png', 'p3-dfly/renders'); many('00_print/dfly-v01/*_top.png', 'p3-dfly/renders'); put('00_print/dfly-v01/README.md', 'p3-dfly/README.md')
# ---- written for the repo
for f in ('README.md', 'LICENSE', '.gitattributes', '.github/workflows/pages.yml', 'p4-ornithopter/README.md', 'p1-studies/README.md'):
    put('00_src/repo_files/' + f, f)
put('docs/DECISIONS.md', 'docs/DECISIONS.md')
io.open(os.path.join(R, 'MANIFEST.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(M)) + '\n'); M.append('MANIFEST.txt')
io.open('_work/repo_manifest.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(M)) + '\n')
print(len(M), 'files staged in', R, '%.1f MB' % (sum(os.path.getsize(os.path.join(R, f)) for f in M) / 1e6))
