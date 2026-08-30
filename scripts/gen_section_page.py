#!/usr/bin/env python3
"""Generate the expansion section page (mini-TOC of new pairs) in album design.
Output: research/new_pages/qoshimcha_toc.html/.pdf  (A4 landscape 297x210mm)."""
import json, os, subprocess, sys

BASE = "/home/z/my-project"
pairs = json.load(open(f"{BASE}/repo-okj/album/selected_pairs.json"))
OUT = f"{BASE}/research/new_pages"
os.makedirs(OUT, exist_ok=True)

FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,600&family=PT+Serif:ital@0;1&display=swap" rel="stylesheet">'

CH_LABEL = {1: "I BOB &middot; QADIMGI TOSHKENT", 2: "II BOB &middot; YANGI DAVR", 3: "III BOB &middot; BUYUK QURILISH DAVRI"}
CH_COLOR = {1: "#896033", 2: "#896033", 3: "#896033"}

cols_html = ""
per = [p for p in pairs]
chunks = [per[0:6], per[6:11], per[11:17]]
for cnum, chunk in zip((1, 2, 3), chunks):
    if not chunk:
        continue
    rows = "".join(
        f'<div class="row"><span class="no">{p["num"]}</span>'
        f'<span class="nm">{p["title"]}</span>'
        f'<span class="yr">{p["old_era"]}</span></div>'
        for p in chunk)
    cols_html += f'''<div class="col">
      <div class="chh">{CH_LABEL[cnum]}</div>
      <div class="rule"></div>
      {rows}
    </div>'''

html = f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
{FONTS_LINK}
<style>
  @page {{ size: 297mm 210mm; margin: 0; }}
  html, body {{ margin: 0; padding: 0; background: #f6efe0; }}
  .poster {{
    position: relative; width: 297mm; height: 210mm; background: #f6efe0; overflow: hidden;
    font-family: 'PT Serif', Georgia, serif; color: #3d2b1f;
  }}
  .frame  {{ position: absolute; inset: 6mm;   border: 0.65mm solid #896033; }}
  .frame2 {{ position: absolute; inset: 8.4mm; border: 0.22mm solid #896033; }}
  .kicker {{
    position: absolute; top: 13.5mm; left: 0; right: 0; text-align: center;
    font-size: 3.55mm; letter-spacing: 1.5mm; color: #ac9983; font-weight: 700;
  }}
  h1 {{
    position: absolute; top: 17.5mm; left: 20mm; right: 20mm; margin: 0; text-align: center;
    font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 9.2mm;
    color: #3d2b1f;
  }}
  .sub {{
    position: absolute; top: 29.6mm; left: 0; right: 0; text-align: center;
    font-style: italic; font-size: 4.1mm; color: #5c4531;
  }}
  .cols {{ position: absolute; top: 37.5mm; left: 17mm; right: 17mm; bottom: 16mm;
          display: flex; gap: 9mm; }}
  .col {{ flex: 1; }}
  .chh {{ font-size: 3.5mm; letter-spacing: 0.85mm; font-weight: 700; color: #896033;
         text-align: center; margin-bottom: 1.6mm; }}
  .rule {{ height: 0.22mm; background: #c9b391; margin: 0 2mm 2.4mm; }}
  .row {{ display: flex; align-items: baseline; gap: 2.6mm; padding: 1.35mm 0.5mm;
         font-size: 3.42mm; }}
  .row .no {{ min-width: 7.5mm; text-align: right; font-weight: 700; color: #ac9983;
             font-family: 'Playfair Display', serif; }}
  .row .nm {{ flex: 1; border-bottom: 0.18mm dotted #c9b391; padding-bottom: 0.7mm; }}
  .row .yr {{ color: #5c4531; font-style: italic; font-size: 2.95mm; }}
  .note {{ position: absolute; bottom: 11.2mm; left: 0; right: 0; text-align: center;
          font-size: 2.95mm; color: #ac9983; font-style: italic; }}
  .pagenum {{ position: absolute; top: 201.4mm; left: 0; right: 0; text-align: center;
             font-size: 3.4mm; color: #5c4531; }}
</style>
</head>
<body>
  <div class="poster">
    <div class="frame"></div><div class="frame2"></div>
    <div class="kicker">Q O &lsquo; S H I M C H A&nbsp;&nbsp;T O &lsquo; P L A M</div>
    <h1>Kecha va bugun &mdash; davomi</h1>
    <div class="sub">Yana {len(pairs)} ta joy: har bir juftlik xuddi shu manzilning eski va bugungi surati</div>
    <div class="cols">{cols_html}</div>
    <div class="note">Har bir sahifada joyning Google Maps ko&lsquo;rsatkichlari va QR kodi berilgan</div>
  </div>
</body>
</html>"""

open(f"{OUT}/qoshimcha_toc.html", "w").write(html)
r = subprocess.run(["node", f"{BASE}/skills/pdf/scripts/html2poster.js",
                    f"{OUT}/qoshimcha_toc.html", "--output", f"{OUT}/qoshimcha_toc.pdf",
                    "--width", "297mm"], capture_output=True, text=True, timeout=180)
sz = os.path.getsize(f"{OUT}/qoshimcha_toc.pdf") if os.path.exists(f"{OUT}/qoshimcha_toc.pdf") else 0
print("render rc:", r.returncode, "size:", sz)
if r.returncode != 0:
    print((r.stdout or "")[-300:], (r.stderr or "")[-300:])
