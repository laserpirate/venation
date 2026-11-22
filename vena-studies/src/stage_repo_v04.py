"""stage_repo_v04.py : copy an explicit list of files into the staged repo (_repo/venation), check sha1 after each copy, add new paths to
MANIFEST.txt, and write the git path list for `git add`. usage: python stage_repo_v04.py <pairs.txt> <gitlist_out.txt>
pairs.txt: one 'source<TAB>repo path' per line. Nothing is added to git here. Run from the project root. No em dashes."""
import os, io, sys, shutil, hashlib
R = '_repo/venation'; sha = lambda p: hashlib.sha1(open(p, 'rb').read()).hexdigest()
pairs = [l.split('\t') for l in io.open(sys.argv[1], encoding='utf-8').read().splitlines() if l.strip()]
M = [l for l in io.open(os.path.join(R, 'MANIFEST.txt'), encoding='utf-8').read().splitlines() if l.strip()]; new = []
for src, dst in pairs:
    assert os.path.isfile(src), src; d = os.path.join(R, dst); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copyfile(src, d); assert sha(src) == sha(d), dst
    if dst not in M: M.append(dst); new.append(dst)
M = sorted(set(M)); io.open(os.path.join(R, 'MANIFEST.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(M) + '\n')
io.open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(set(d for _, d in pairs)) + ['MANIFEST.txt']) + '\n')
io.open('_work/repo_manifest_v04.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(sorted(set(M + ['.gitattributes', '.github/workflows/pages.yml', 'MANIFEST.txt']))) + '\n')
print(len(pairs), 'files staged,', len(new), 'new paths; manifest', len(M), 'paths')
for src, dst in pairs:
    if dst.startswith('src/') and not dst.startswith('src/studies/'): print(sha(src)[:8], src, '=', dst)
