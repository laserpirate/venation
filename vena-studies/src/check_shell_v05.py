"""check_shell_v05.py : the site shell. All three pages at 400 and 1400 px (no sideways scroll, measured by scrollWidth), the top bar links,
the Lab's three added modes drawn, no course or episode code in the visible text. usage: python check_shell_v05.py <site_dir> <out.json> <lab.png>. No em dashes."""
import sys, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
site = Path(sys.argv[1]).resolve(); rep = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    for name in ('index.html', 'land.html', 'lamp.html'):
        for wd in (400, 1400):
            pg = b.new_page(viewport={'width': wd, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto((site / name).as_uri()); pg.wait_for_timeout(2500)
            txt = pg.evaluate('document.body.innerText'); nav = pg.evaluate('[...document.querySelectorAll("nav.tabs > *")].map(e => [e.textContent, e.getAttribute("href") || "tab"])')
            rep['%s_%d' % (name, wd)] = dict(scroll=pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]'), errors=errs, nav=nav, codes=re.findall(r'\bC3\b|\bE[1-4]\b|STU ?1211', txt)[:5], clubtail_model='Clubtail model' in txt)
            if name == 'index.html' and wd == 1400:
                rep['lab_modes'] = pg.evaluate('''() => { const out = {}; for (const m of ['xylem', 'radiolaria', 'delaunay']) { document.getElementById('mode').value = m; document.getElementById('shape').value = 'ovate'; document.getElementById('run').click(); out[m] = document.getElementById('stat').innerText.replace(/\\n/g, ' | ').slice(0, 160) } return out }''')
                pg.screenshot(path=sys.argv[3])
                pg.click('nav.tabs button[data-tab="studies"]'); rep['studies_tab'] = pg.evaluate('[!document.getElementById("tab-studies").hidden, !document.getElementById("tab-lamps").hidden, document.querySelectorAll("#tab-studies figure").length, document.querySelectorAll("#tab-lamps figure").length]')
            pg.close()
    b.close()
Path(sys.argv[2]).write_text(json.dumps(rep, indent=1), encoding='utf-8')
for k, v in rep.items(): print(k, json.dumps(v, ensure_ascii=True)[:330])
