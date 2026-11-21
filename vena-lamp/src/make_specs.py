"""collect page_specs of every L*.json, one entry per seed, for export_patterns_v01.py"""
import json, glob, os
here = os.path.dirname(os.path.abspath(__file__)); out = {}
for f in sorted(glob.glob(os.path.join(here, 'L?.json'))):
    p = json.load(open(f, encoding='utf-8'))
    for name, sp in p.get('page_specs', {}).items():
        for s in p['seeds']: out['%s_s%02d' % (name, s)] = dict(sp, seed=s)
json.dump(out, open(os.path.join(here, 'patterns', '_specs.json'), 'w'), indent=1); print(len(out), 'specs')
