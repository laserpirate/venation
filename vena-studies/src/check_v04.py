"""check_v04.py : headless check of venation-lab_v04.html from disk. Every stored study loads and reproduces its sheet statistics
(cells, loops, vein nodes against the page's own sheet build with the same spec), the gallery images load, PNG 2x and 4x sizes,
the PDF is a vector PDF, Copy for chat text. usage: python check_v04.py <page.html> <out.json>. No em dashes."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
page = Path(sys.argv[1]).resolve(); rep = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1400, 'height': 1000}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(page.as_uri()); pg.wait_for_function('window.VL && typeof d3!=="undefined"', timeout=30000)
    rep['jspdf_loaded'] = pg.evaluate('!!window.jspdf')
    ids = pg.evaluate('Object.keys(VL.STUDIES)'); rep['studies'] = len(ids); bad = []
    for i in ids:
        r = pg.evaluate('''(id) => { VL.loadStudy(id); const now = VL.params(); const st = VL.storedParams(id); const same = Object.keys(now).every(k => String(now[k]) === String(st[k]));
            const a = VL.build(now), b2 = VL.build(st); return {same, sid: now.sid, statSame: JSON.stringify(VL.statText(a).slice(0, 6)) === JSON.stringify(VL.statText(b2).slice(0, 6)), stat: VL.statText(a).slice(0, 5), changed: VL.changedParams().changes.length} }''', i)
        if not (r['same'] and r['statSame'] and r['sid'] == i and r['changed'] == 0): bad.append((i, r))
    rep['studies_loaded_exact'] = len(ids) - len(bad); rep['studies_bad'] = bad
    rep['select_options'] = pg.evaluate('document.getElementById("loadstudy").options.length')
    pg.evaluate('VL.loadStudy("VS03-04")'); pg.evaluate('document.getElementById("seed").value=12; document.getElementById("seed").dispatchEvent(new Event("change")); document.getElementById("note").value="finer cells near the tip"')
    rep['chat_text'] = pg.evaluate('VL.chatText()')
    rep['png2'] = pg.evaluate('VL.pngAt(2)'); rep['png4'] = pg.evaluate('VL.pngAt(4)')
    pdf = pg.evaluate('''() => { const r = VL.pdfDoc(); if (!r) return null; const s = r.doc.output(); return {head: s.slice(0, 8), bytes: s.length, drawn: r.n, page_mm: [r.wmm, r.hmm], has_image: s.indexOf('/Subtype /Image') >= 0} }''')
    rep['pdf'] = pdf
    pg.evaluate('VL.showTab("studies")'); pg.wait_for_timeout(300)
    pg.evaluate('document.querySelectorAll("#tab-studies img").forEach(i => i.loading = "eager")'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(1500)
    im = pg.evaluate('[...document.querySelectorAll("#tab-studies img")].map(i => i.naturalWidth > 0)'); rep['gallery_images'] = len(im); rep['gallery_images_loaded'] = sum(im)
    rep['load_tiles'] = pg.evaluate('document.querySelectorAll("#tab-studies figure.load").length')
    pg.evaluate('document.querySelector("#tab-studies figure.load").click()'); rep['click_loads'] = pg.evaluate('document.getElementById("sid").value')
    rep['sideways_scroll'] = pg.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth'); rep['page_errors'] = errs
    rep['storage_calls'] = [k for k in ('localStorage', 'sessionStorage', 'document.cookie') if k in page.read_text(encoding='utf-8')]
    b.close()
Path(sys.argv[2]).write_text(json.dumps(rep, indent=1), encoding='utf-8'); print(json.dumps({k: v for k, v in rep.items() if k != 'studies_bad'})); print('bad', rep['studies_bad'][:2])
