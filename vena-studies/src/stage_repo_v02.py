"""stage_repo_v02.py : copy the public set into _repo/venation by an explicit list and write MANIFEST.txt (one repo path per line).
Nothing is added to git here. Run from the project root. Layout (v02): src/ is what Pages serves (index.html = venation-lab_v04.html and
its images); vena-studies, vena-lamp, vena-dfly (mech/ is the stub), vena-land hold the branches. No em dashes."""
import os, io, glob, shutil
R = '_repo/venation'; M = []


def put(src, dst):
    assert os.path.isfile(src), src; d = os.path.join(R, dst); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(src, d); M.append(dst)


def many(pattern, dst_dir, rename=None, skip=None):
    fs = [f for f in sorted(glob.glob(pattern)) if not (skip and skip(os.path.basename(f)))]; assert fs, pattern
    for f in fs: put(f, dst_dir + '/' + (rename(os.path.basename(f)) if rename else os.path.basename(f)))


for d in ('src', 'p1-studies', 'p2-lamps', 'p3-dfly', 'p4-ornithopter', 'vena-studies', 'vena-lamp', 'vena-dfly', 'vena-land', 'docs', '.github'):
    shutil.rmtree(os.path.join(R, d), ignore_errors=True)
# ---- the page Pages serves
put('00_src/venation-lab_v04.html', 'src/index.html'); put('00_src/wing_geom.js', 'src/wing_geom.js'); many('00_src/studies/VS0??-??.jpg', 'src/studies'); many('00_src/studies/VS0?-??.png', 'src/studies'); many('00_src/studies/VS0?-??.jpg', 'src/studies')
# ---- vena-studies
for f in ('venation-lab_v01.html', 'venation-lab_v02.html', 'venation-lab_v02b.html', 'venation-lab_v02c.html', 'venation-lab_v03.html', 'venation-lab_v04.html', 'wing_geom.js', 'contact_sheet_v02.py', 'contact_sheet_v03.py',
          'cut_tiles_v01.py', 'image_sheet_v01.py', 'image_sheet_v02.py', 'build_v03.py', 'check_v03.py', 'build_v04.py', 'check_v04.py', 'print_readme_v01.py', 'privacy_scan_v01.py', 'stage_repo_v01.py', 'stage_repo_v02.py'):
    put('00_src/' + f, 'vena-studies/src/' + f)
many('00_src/specs/*.json', 'vena-studies/src/specs'); many('00_src/studies/VS0?.json', 'vena-studies/src/studies')
many('00_contacts/*.png', 'vena-studies/contacts'); many('00_contacts/*_check.json', 'vena-studies/contacts'); many('00_export_svg/VS02-10_*', 'vena-studies/export_svg')
# ---- vena-lamp
for f in ('lamp_build_v01.py', 'export_patterns_v01.py', 'render_v01.py', 'lamp_sheet_v01.py', 'make_specs.py'): put('00_src/lamps/' + f, 'vena-lamp/src/' + f)
many('00_src/vena-lamp/*.py', 'vena-lamp/src'); many('00_src/vena-lamp/*.json', 'vena-lamp/src')
many('00_src/lamps/L?.json', 'vena-lamp/params'); many('00_src/lamps/patterns/*.json', 'vena-lamp/params/patterns')
many('00_print/lamps-v01/*_plate.3mf', 'vena-lamp/v01/print'); many('00_print/lamps-v01/*_check.json', 'vena-lamp/v01/print'); many('00_print/lamps-v01/*_bed.png', 'vena-lamp/v01/print')
many('00_print/lamps-v01/*_render.png', 'vena-lamp/v01/renders'); put('00_print/lamps-v01/README.md', 'vena-lamp/v01/README.md')
for ext in ('_plate.3mf', '_check.json', '_bed.png'): many('00_print/vena-lamp/*' + ext, 'vena-lamp/print')
many('00_print/vena-lamp/*_lit.png', 'vena-lamp/renders'); many('00_print/vena-lamp/*_render.png', 'vena-lamp/renders')
put('00_print/vena-lamp/README.md', 'vena-lamp/README.md'); put('00_print/vena-lamp/SLICE_NOTES_v01.md', 'vena-lamp/SLICE_NOTES_v01.md')
many('00_mockups/vena-lamp/*_check.json', 'vena-lamp/mockups')         # all mockups: check files only; their lit renders are in src/studies as gallery tiles
# ---- vena-dfly
for f in ('dfly_build_v01.py', 'dfly_sheet_v01.py'): put('00_src/dfly/' + f, 'vena-dfly/src/' + f)
many('00_src/vena-dfly/*.py', 'vena-dfly/src'); many('00_src/dfly/patterns/*.json', 'vena-dfly/patterns/v01'); many('00_src/vena-dfly/patterns/*.json', 'vena-dfly/patterns')
put('00_src/dfly/' + 'STU' + '1211_E1_A1_dragonfly_print_v01.stl', 'vena-dfly/source/clubtail_print_E1_v01_source.stl')      # renamed: the source name carries a course code
many('00_print/dfly-v01/*.stl', 'vena-dfly/v01/print'); many('00_print/dfly-v01/*_plate.3mf', 'vena-dfly/v01/print'); many('00_print/dfly-v01/*_check.json', 'vena-dfly/v01/print'); many('00_print/dfly-v01/*_bed.png', 'vena-dfly/v01/print')
many('00_print/dfly-v01/*_render.png', 'vena-dfly/v01/renders'); many('00_print/dfly-v01/*_top.png', 'vena-dfly/v01/renders'); put('00_print/dfly-v01/README.md', 'vena-dfly/v01/README.md')
for ext in ('.stl', '_plate.3mf', '_check.json', '_bed.png'): many('00_print/vena-dfly/*' + ext, 'vena-dfly/print')
for ext in ('_top.png', '_tq.png', '_backlit.png'): many('00_print/vena-dfly/*' + ext, 'vena-dfly/renders')
put('00_print/vena-dfly/README.md', 'vena-dfly/README.md')
# ---- vena-land
many('00_src/vena-land/*.py', 'vena-land/src'); many('00_src/vena-land/patterns/*.json', 'vena-land/patterns')
many('00_export_svg/vena-land/*', 'vena-land/exports')
for ext in ('.stl', '_plate.3mf', '_check.json', '_bed.png'): many('00_print/vena-land/*' + ext, 'vena-land/print')
many('00_print/vena-land/*_render.png', 'vena-land/renders'); put('00_print/vena-land/README.md', 'vena-land/README.md')
# ---- written for the repo
for f in ('README.md', 'LICENSE', '.gitattributes', '.github/workflows/pages.yml', 'vena-dfly/mech/README.md', 'vena-studies/README.md'):
    put('00_src/repo_files_v02/' + f, f)
put('docs/DECISIONS.md', 'docs/DECISIONS.md')
M = sorted(set(M))
io.open(os.path.join(R, 'MANIFEST.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(M) + '\n'); M.append('MANIFEST.txt')
io.open('_work/repo_manifest_v02.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(M)) + '\n')
sz = [(os.path.getsize(os.path.join(R, f)), f) for f in M]
print(len(M), 'files staged in', R, '%.1f MB' % (sum(s for s, _ in sz) / 1e6), 'largest', ['%s %.1f MB' % (f[-50:], s / 1e6) for s, f in sorted(sz)[-3:]])
