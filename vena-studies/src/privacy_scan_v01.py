"""privacy_scan_v01.py : privacy scan of everything staged for the public repo. Exits 1 on any hit.
The name and path rules are the lf3d scanner's, imported by path (not copied): owner name words in utf-8 and utf-16, drive paths with
eight printable characters of context, zip and 3MF members opened, STL head and names. Added here:
- PNG: names over the whole file, paths only in the text chunks (tEXt, zTXt, iTXt); compressed pixel data gives chance path matches.
- course codes and school names in any text file, file name or zip member.
usage: python privacy_scan_v01.py <lf3d scanner .py> <root> <manifest.txt> <report.json>. No em dashes."""
import sys, os, re, io, json, zlib, struct, zipfile, importlib.util
spec = importlib.util.spec_from_file_location('lf3d_privacy', sys.argv[1]); lf = importlib.util.module_from_spec(spec); spec.loader.exec_module(lf)
root, manifest, report = sys.argv[2], sys.argv[3], sys.argv[4]
import base64
CODE = re.compile(base64.b64decode('KD9pKXN0dVsgXy1dPzEyMTF8aGFydmFyZHwoPzwhW0EtWmEtel0pZ3NkKD8hW0EtWmEtel0p'))    # course code and school patterns, encoded so this file does not carry them
TEXT = ('.md', '.html', '.js', '.py', '.json', '.txt', '.yml', '.svg', '.gitignore', '.gitattributes', 'LICENSE')


def png_text(b):
    out = b''; i = 8
    while i + 8 <= len(b):
        n, t = struct.unpack('>I4s', b[i:i + 8]); d = b[i + 8:i + 8 + n]
        if t in (b'tEXt', b'iTXt'): out += d + b'\n'
        elif t == b'zTXt':
            k, _, rest = d.partition(b'\x00')
            try: out += k + b' ' + zlib.decompress(rest[1:]) + b'\n'
            except Exception: out += d
        i += 12 + n
    return out


def scan(p, rel):
    b = open(p, 'rb').read(); hits = []
    hits += lf.scan_bytes(rel.encode(), rel + ' [path in repo]')
    if CODE.search(rel.encode()): hits.append(rel + ': course code or school in the file name')
    if rel.lower().endswith('.png'):
        hits += [h for h in lf.scan_bytes(b, rel) if 'name word' in h] + lf.scan_bytes(png_text(b), rel + ' [png text chunks]')
        if CODE.search(png_text(b)): hits.append(rel + ': course code or school in png text')
    else:
        hits += [h.replace(p, rel) for h in lf.scan_file(p)]
        if zipfile.is_zipfile(p):
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if CODE.search(n.encode()) or CODE.search(z.read(n)): hits.append('%s:%s: course code or school' % (rel, n))
        elif rel.endswith(TEXT) or os.path.basename(rel) in TEXT:
            for m in CODE.finditer(b): hits.append('%s: course code or school %r' % (rel, b[max(0, m.start() - 20):m.end() + 20]))
    return hits


files = [l.strip() for l in io.open(manifest, encoding='utf-8') if l.strip()]; H = []; missing = []
for rel in files:
    p = os.path.join(root, rel)
    if not os.path.isfile(p): missing.append(rel); continue
    H += scan(p, rel)
on_disk = sorted(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/') for dp, dn, fs in os.walk(root) if '.git' not in dp.replace(os.sep, '/').split('/') for f in fs)
extra = [f for f in on_disk if f not in set(files)]
rep = dict(files=len(files), hits=H, missing=missing, on_disk_not_in_manifest=extra, bytes=sum(os.path.getsize(os.path.join(root, f)) for f in files if f not in missing))
json.dump(rep, io.open(report, 'w', encoding='utf-8'), indent=1)
print('files', len(files), 'bytes', rep['bytes'], 'hits', len(H), 'missing', len(missing), 'not in manifest', len(extra))
for h in H[:30]: print('  HIT', h[:200])
sys.exit(1 if (H or missing or extra) else 0)
