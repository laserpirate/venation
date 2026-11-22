"""samples_sheet_v01.py : for the sample plates: a shaded image from above per plate (from the tile heightfields), a plate map per plate
(which ID sits where), two close-ups, the README, and the VS11 contact sheet. Type is IBM Plex through a headless browser.
The images are stand-ins made from heights, not ray-traced renders, and say so. usage: python samples_sheet_v01.py <samples_dir> <sheet.png>. No em dashes."""
import sys, os, io, json, time
import numpy as np
from PIL import Image
from pathlib import Path
from playwright.sync_api import sync_playwright
out = Path(sys.argv[1]).resolve(); sheet = Path(sys.argv[2]).resolve(); S = json.load(open(out / 'vena-samples_set_v01.json', encoding='utf-8')); G = S['rules']['grid_mm']; T = {t['id']: t for t in S['tiles']}
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&display=swap">'


def shade(z, vmax):
    gy, gx = np.gradient(z, G); n = np.sqrt(gx * gx + gy * gy + 1); l = (-gx * -0.6 + -gy * -0.6 + 0.55) / n / np.sqrt(0.6 * 0.6 * 2 + 0.55 * 0.55)     # light from the upper left
    return np.clip(0.22 + 0.5 * np.clip(l, 0, 1) + 0.3 * np.clip(z / vmax, 0, 1), 0, 1)


def backlit(z):
    t = np.exp(-(z - 0.6) / 0.9); rgb = np.stack([t * 255, t * 232, t * 196], -1); return np.clip(8 + rgb * 0.96, 0, 255).astype(np.uint8)       # brightness from thickness alone


for pl in S['plates']:
    W, H = pl['size_mm']; nx, ny = int(round(W / G)), int(round(H / G)); Z = np.zeros((ny, nx), np.float32)
    for t in pl['tiles']:
        z = np.load(out / 'height' / (t['id'] + '.npy')); x0 = int(round(t['x'] / G)); y0 = ny - int(round((t['y'] + t['h']) / G)); Z[y0:y0 + z.shape[0], x0:x0 + z.shape[1]] = z
    im = Image.fromarray((shade(Z, 8.0 if pl['set'] == 'VS08' else 2.4) * 255).astype(np.uint8)).resize((nx // 2, ny // 2), Image.LANCZOS); im.save(out / (pl['name'] + '_top.png'))
Image.fromarray(backlit(np.load(out / 'height' / 'VS02-10.npy'))).resize((1080, 1080), Image.LANCZOS).save(out / 'vena-samples--VS02-10_backlit_v01.png')
zl = np.load(out / 'height' / 'VS08-05.npy'); Image.fromarray((shade(zl, 8.0) * 255).astype(np.uint8)).resize((1080, 1080), Image.LANCZOS).save(out / 'vena-samples--VS08-05_close_v01.png')

pat = [t for t in S['tiles'] if t['info']['kind'] == 'pattern']; shares = [t['info']['kept_share'] for t in pat]; npass = sum(1 for t in S['tiles'] if t['checks']['pass']); nfail = len(S['tiles']) - npass
hours = [p['checks']['hours_est'] for p in S['plates']]; grams = [p['checks']['grams_est'] for p in S['plates']]; a = b = 0.0
for h in sorted(hours, reverse=True):
    if a <= b: a += h
    else: b += h
kept = lambda t: ('%d of %d kept' % (t['info']['kept'], t['info']['total'])) if t['info']['kind'] == 'pattern' else 'relief x %.2f' % t['info']['relief_scale']
with sync_playwright() as pw:
    br = pw.chromium.launch()
    for pl in S['plates']:                                   # plate maps
        W, H = pl['size_mm']; k = 5.0; cells = ''.join('<div class="t" style="left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx"><b>%s</b><span>%s x %s mm</span><span>%s</span><span>%s</span></div>' % (t['x'] * k, (H - t['y'] - t['h']) * k, t['w'] * k, t['h'] * k, t['id'], round(t['w']), round(t['h']), kept(T[t['id']]), 'PASS' if T[t['id']]['checks']['pass'] else 'FAIL') for t in pl['tiles'])
        html = '<!doctype html><meta charset="utf-8">%s<style>body{margin:0;padding:24px;background:#fff;color:#111;font:400 16px/1.3 "IBM Plex Mono",monospace}h1{font:500 19px "IBM Plex Mono",monospace;margin:0 0 6px}p{margin:0 0 14px}.b{position:relative;width:%.0fpx;height:%.0fpx;outline:1px dashed #777;outline-offset:%.0fpx;margin:%.0fpx}.t{position:absolute;border:1.5px solid #111;box-sizing:border-box;padding:6px;display:flex;flex-direction:column;gap:2px;font-size:16px}.t b{font-weight:500;font-size:19px}</style><h1>%s · plate map · seen from above, front of the bed at the bottom</h1><p>%d tiles · %s x %s mm inside the 203 mm square (dashed) · %s g and %s h estimated · every ID stands on the lower edge of its tile</p><div class="b">%s</div>' % (FONT, W * k, H * k, (203 - W) / 2 * k, (203 - min(W, H)) / 2 * k + 6, pl['name'], len(pl['tiles']), W, H, pl['checks']['grams_est'], pl['checks']['hours_est'], cells)
        (out / '_map.html').write_text(html, encoding='utf-8'); pg = br.new_page(viewport={'width': 1120, 'height': 400}); pg.goto((out / '_map.html').as_uri()); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(400); pg.screenshot(path=str(out / (pl['name'] + '_map.png')), full_page=True); pg.close()
    (out / '_map.html').unlink()
    figs = ''.join('<figure><img src="%s"><figcaption><b>%s</b> · %d tiles, %s x %s mm · %s<br>%s g, %s h estimated · %s<br>shaded height image from above, made from the tile heightfields; not a ray-traced render</figcaption></figure>' % ((out / (p['name'] + '_top.png')).as_uri(), p['name'], len(p['tiles']), p['size_mm'][0], p['size_mm'][1], ', '.join(t['id'] for t in p['tiles']), p['checks']['grams_est'], p['checks']['hours_est'], 'tiles PASS %d, FAIL %d' % (p['tiles_pass'], p['tiles_fail'])) for p in S['plates'])
    plate_of = lambda i: [p['name'] for p in S['plates'] if i in [t['id'] for t in p['tiles']]][0]
    t10 = T['VS02-10']; figs += '<figure><img src="%s"><figcaption><b>%s</b> · close-up of VS02-10 · %d of %d veins and links kept · back-lit stand-in: brightness from thickness alone (0.6 mm membrane, ribs 1.2 to 2.0 mm), guessed material</figcaption></figure>' % ((out / 'vena-samples--VS02-10_backlit_v01.png').as_uri(), plate_of('VS02-10'), t10['info']['kept'], t10['info']['total'])
    figs += '<figure><img src="%s"><figcaption><b>%s</b> · close-up of VS08-05 (%s) · relief scaled to 6.0 mm on a 2.0 mm base · shaded height image, not a render</figcaption></figure>' % ((out / 'vena-samples--VS08-05_close_v01.png').as_uri(), plate_of('VS08-05'), T['VS08-05']['full_id'])
    title = 'VS11 · %s · vena-samples · %d plates, %d tiles (PASS %d, FAIL %d) · fine, below lab minimum · nothing sliced, nothing printed' % (sheet.stem.replace('VS11_', ''), len(S['plates']), len(S['tiles']), npass, nfail)
    html = '<!doctype html><meta charset="utf-8">%s<style>body{margin:0;padding:28px;background:#f3f1ec;color:#1d1c1a;font:400 19px/1.35 "IBM Plex Mono",monospace}h1{font:500 22px "IBM Plex Mono",monospace;margin:0 0 18px}.g{display:grid;grid-template-columns:repeat(4,820px);gap:22px;align-items:start}figure{margin:0;border:1px solid #c9c5bb;background:#111}img{display:block;width:820px;height:820px;object-fit:contain;background:#111}figcaption{padding:8px 10px 10px;min-height:150px;border-top:1px solid #c9c5bb;background:#f3f1ec}figcaption b{font-weight:500}</style><h1>%s</h1><div class="g">%s</div>' % (FONT, title, figs)
    (out / '_sheet.html').write_text(html, encoding='utf-8'); pg = br.new_page(viewport={'width': 3430, 'height': 1000}); pg.goto((out / '_sheet.html').as_uri()); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(800)
    plex = pg.evaluate('document.fonts.check("19px \\"IBM Plex Mono\\"")'); pg.screenshot(path=str(sheet), full_page=True); pg.close(); br.close(); (out / '_sheet.html').unlink()

R = S['rules']; L = []
L.append('# vena-samples · sample plates of the flat studies · v01 · %s\n' % time.strftime('%d %b %Y'))
L.append('**Fine, below lab minimum.** Membranes are %.1f mm and ribs start at %.1f mm wide; the lab recommends 2.0 mm. Nothing here is sliced or printed; grams and hours are estimates from solid volume (1.24 g per cm3, 22 g per hour, 8 s per layer at 0.20 mm).\n' % (R['membrane_mm'], R['rib_width_mm'][0]))
L.append('## What a tile is')
L.append('- Pattern tile (VS02, VS03): 45 x 45 mm, wings 95 x 45 mm. Frame %.1f mm wide and %.1f mm tall, %.1f mm wide on the lower edge, where the study ID stands %.1f mm proud at 3 mm cap height. Membrane %.1f mm inside the frame. Ribs %.1f to %.1f mm wide and %.1f to %.1f mm tall in all, by Murray width (width by its square, so only the main veins are wide). Flat underside; the ID is engraved mirrored, 0.6 mm deep, under the wide edge.' % (R['frame'][0], R['frame'][1], R['id_edge_mm'], 0.4, R['membrane_mm'], R['rib_width_mm'][0], R['rib_width_mm'][1], R['rib_height_mm'][0], R['rib_height_mm'][1]))
L.append('- Thinning, one rule for every tile: links, then veins from the thinnest, and cells from the smallest, are dropped until gaps under %.1f mm are no more than %d percent of the rib area and at least %d percent of the outline is open membrane. Named wing veins and the outline always stay. Gaps under %.1f mm that remain (the wedges where ribs meet) are closed as rib. Nothing is redrawn. Kept share of the 32 pattern tiles: %.0f to %.0f percent; each tile`s count is on the plate map and in its check file.' % (R['gap_min_mm'], R['gap_share'] * 100, 45, R['gap_min_mm'], min(shares) * 100, max(shares) * 100))
L.append('- Six VS02 wing tiles (01, 02, 03, 05, 06, 07) do not reach the open-membrane share even with every cell dropped: their named veins alone, at one width by the VS02 rule, cover more than 55 percent. They are kept as the rule requires and print as dense plates.')
L.append('- Landform tile (VS08): the heightfield as a solid, 45 x 45 mm, base %.1f mm, relief scaled to %.1f mm at its highest, landform 38 x 38 mm inside the same frame at base level; the sheet number (VS08-01 to 16) stands on the lower edge and the full ID is engraved mirrored underneath in two lines.\n' % (R['base_mm'], R['relief_mm']))
L.append('## Plates and print order')
L.append('| order | plate | tiles | size mm | grams est. | hours est. | cost est. USD | tiles PASS / FAIL | IDs |'); L.append('|---|---|---|---|---|---|---|---|---|')
for i, p in enumerate(S['plates']): L.append('| %d | `%s` | %d | %s x %s | %s | %s | %s | %d / %d | %s |' % (i + 1, p['name'], len(p['tiles']), p['size_mm'][0], p['size_mm'][1], p['checks']['grams_est'], p['checks']['hours_est'], p['checks']['cost_usd_est'], p['tiles_pass'], p['tiles_fail'], ', '.join(t['id'] for t in p['tiles'])))
L.append('\nSet: %.0f g, %.1f h, %.2f USD estimated. Wall clock on two printers: %.1f h (one runs the landform plate, the other the four pattern plates).' % (sum(grams), sum(hours), sum(grams) * 0.033, max(a, b)))
L.append('Print the first VS02 plate first: it is the test of the 0.6 mm membrane and the 0.8 mm ribs. Flat side down, no supports, no brim needed. Filament: white PLA shows the relief; a translucent PLA shows the membrane against light. SimplyPrint, the fine-detail profile, 0.20 mm layers or finer.\n')
L.append('## Files')
L.append('- Per tile: `vena-samples--<ID>_t<w>x<h>mm_v01.stl` and `_check.json` (the checks are run on the STL as saved and reloaded).')
L.append('- Per plate: `<plate>_plate.3mf` (tiles arranged, centred on the 256 mm bed), `_bed.png` (footprint against the 203 mm square), `_map.png` (which ID sits where), `_top.png` (shaded height image from above; not a render).')
L.append('- `vena-samples_set_v01.json`: every number above. `height\\`: the tile heightfields the images are made from.')
L.append('\n## Checks')
L.append('%d tiles: PASS %d, FAIL %d. Rule: %s' % (len(S['tiles']), npass, nfail, S['tiles'][0]['checks']['pass_rule']))
L.append('Plates: footprint inside 203 x 203 mm with the margins printed on each bed overlay; height under 256 mm. A plate is several parts on one 3MF because they fit the square together.')
io.open(out / 'README.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
json.dump(dict(png=sheet.name, plates=[p['name'] for p in S['plates']], tiles=len(S['tiles']), tiles_pass=npass, tiles_fail=nfail, kept_share_range=[min(shares), max(shares)], grams=round(sum(grams), 1), hours=round(sum(hours), 1), two_printers_h=round(max(a, b), 1), plex_mono_loaded=plex, captions_lead_with_plate=True, built=time.strftime('%Y-%m-%d %H:%M')), open(str(sheet)[:-4] + '_check.json', 'w', encoding='utf-8'), indent=1)
print('plates', len(S['plates']), 'tiles', len(S['tiles']), 'PASS', npass, 'FAIL', nfail, 'kept share', min(shares), max(shares), 'g', round(sum(grams), 1), 'h', round(sum(hours), 1), 'two printers', round(max(a, b), 1), 'plex', plex)
