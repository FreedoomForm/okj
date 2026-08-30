#!/usr/bin/env python3
"""Rebuild MUNDARIJA (TOC) with ALL 37 pairs (replaces original 20-entry TOC page
and the removed 'Qo'shimcha to'plam — davomi' mini-TOC page).
Design replicates the original album TOC: kicker + Playfair title + ornament,
Roman-numeral chapter headers with rule, dotted-leader rows, bold page numbers.
Page numbers = printed folio numbers on the pair pages (1-20 original, 21-37 new).
Output: research/new_pages/mundarija.pdf + download/tashkent-album-src/mundarija.html
"""
import json, os, subprocess

BASE = "/home/z/my-project"
OUT_PDF = f"{BASE}/research/new_pages/mundarija.pdf"
OUT_HTML = f"{BASE}/download/tashkent-album-src/mundarija.html"

FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,600&family=PT+Serif:ital@0;1&display=swap" rel="stylesheet">'

CH1 = ("I", "Qadimgi Toshkent", "1900&ndash;1930", [
    ("Amir Temur xiyoboni", "1910-yillar", 1),
    ("Eski shahar ko&lsquo;chalari", "1900-yillar oxiri", 2),
    ("Toshkent sirkining birinchi binosi", "1920-yillar", 3),
])
CH2 = ("II", "Yangi davr bo&lsquo;sag&lsquo;asi", "1930&ndash;1960", [
    ("Alisher Navoiy nomidagi katta teatr", "1950&ndash;60-yillar", 4),
    ("Mustaqillik maydoni", "1950&ndash;60-yillar", 5),
    ("Toshkent zooparki", "1950&ndash;60-yillar", 6),
])
CH3 = ("III", "Buyuk qurilish davri", "1960&ndash;2000", [
    ("Toshkent sirki", "1980-yillar", 7),
    ("Toshkent temir yo&lsquo;l vokzali", "1980-yillar", 8),
    ("Chorsu bozori", "1970&ndash;80-yillar", 9),
    ("Toshkent tramvayi", "1970&ndash;80-yillar", 10),
    ("O&lsquo;zbekiston mehmonxonasi", "1970-yillar", 11),
    ("O&lsquo;zbekiston Davlat san&rsquo;at muzeyi", "1980-yillar", 12),
    ("Xalqlar Do&lsquo;stligi saroyi", "1980-yillar", 13),
    ("Toshkent metropoliteni", "1977&ndash;80-yillar", 14),
    ("Sayilgoh ko&lsquo;chasi (Brovey)", "1992-yil", 15),
    ("1966-yil zilzilasi va Jasorat monumenti", "1966-yil", 16),
    ("Mustaqillik maydoni (Lenin maydoni)", "1970&ndash;80-yillar", 17),
    ("Romanov saroyi", "1970&ndash;90-yillar", 18),
    ("Toshkent xalqaro aeroporti", "1990-yillar", 19),
    ("Chilonzor massivi", "1970-yillar", 20),
])

# Qo'shimcha to'plam (21-37) from selected_pairs.json
pairs = json.load(open(f"{BASE}/repo-okj/album/selected_pairs.json"))
Q = ("\u2740", "Qo&lsquo;shimcha to&lsquo;plam", "1865&ndash;2010", [
    (p["title"], p["old_era"], p["num"]) for p in pairs
])

def grp_html(ch):
    mark, name, yrs, items = ch
    rows = "".join(
        f'<div class="row"><span class="t">{t}&nbsp;<i class="era">&middot; {e}</i></span>'
        f'<span class="dots"></span><span class="pg">{n}</span></div>'
        for t, e, n in items)
    return (f'<div class="grp"><div class="chh"><span class="rn">{mark}</span>'
            f'<span class="nm">{name}&nbsp;&middot; <span class="yr">{yrs}</span></span></div>'
            f'<div class="hrule"></div>{rows}</div>')

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
  .kicker {{
    position: absolute; top: 13.2mm; left: 0; right: 0; text-align: center;
    font-size: 3.55mm; letter-spacing: 1.6mm; color: #ac9983; font-weight: 700;
  }}
  h1 {{
    position: absolute; top: 17.2mm; left: 0; right: 0; margin: 0; text-align: center;
    font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 11.2mm;
    color: #3d2b1f; line-height: 1.05;
  }}
  .orn {{ display: flex; align-items: center; gap: 4mm; margin: 0 auto; width: 78mm;
          position: absolute; top: 31.4mm; left: 0; right: 0; }}
  .orn .rule {{ flex: 1; height: 0.3mm; background: #c9b391; }}
  .orn .mid {{ font-size: 4.6mm; color: #896033; line-height: 1; }}
  .cols {{ position: absolute; top: 38.6mm; left: 15mm; right: 15mm;
           display: flex; gap: 7mm; align-items: flex-start; }}
  .col {{ width: 74mm; }}
  .col.w2 {{ width: 92mm; }}
  .col.w3 {{ width: 87mm; }}
  .grp {{ margin-bottom: 6.2mm; }}
  .chh {{ display: flex; align-items: baseline; gap: 3.2mm; margin-bottom: 1.6mm; }}
  .rn {{ font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 6.8mm;
         color: #896033; min-width: 10.5mm; line-height: 1; }}
  .nm {{ font-weight: 700; font-size: 4.35mm; color: #3d2b1f; letter-spacing: 0.12mm; }}
  .nm .yr {{ font-weight: 700; font-size: 3.6mm; color: #5c4531; white-space: nowrap; }}
  .hrule {{ height: 0.3mm; background: #c9b391; margin: 0 0 2.6mm; }}
  .row {{ display: flex; padding: 1.32mm 0;
          font-size: 3.15mm; line-height: 1.25; }}
  .row .t {{ flex: 0 1 auto; min-width: 0; }}
  .row .era {{ font-style: italic; color: #896033; font-size: 2.95mm; }}
  .dots {{ flex: 1 0 3.5mm; border-bottom: 0.18mm dotted #b39b76;
           margin: 0 1.6mm 0.9mm; align-self: flex-end; }}
  .pg {{ flex: 0 0 auto; font-weight: 700; font-size: 3.35mm; color: #3d2b1f; align-self: flex-end; }}
  .note {{ position: absolute; top: 186mm; left: 0; right: 0; text-align: center;
           font-style: italic; font-size: 3.3mm; color: #5c4531; }}
</style>
</head>
<body>
  <div class="poster">
    <div class="kicker">M U N D A R I J A</div>
    <h1>Mundarija</h1>
    <div class="orn"><span class="rule"></span><span class="mid">&#10087;</span><span class="rule"></span></div>
    <div class="cols">
      <div class="col">{grp_html(CH1)}{grp_html(CH2)}</div>
      <div class="col w2">{grp_html(CH3)}</div>
      <div class="col w3">{grp_html(Q)}</div>
    </div>
    <div class="note">Har bir sahifada: eski surat (chapda), xuddi shu joyning bugungi ko&lsquo;rinishi (o&lsquo;ngda), joy nomi, koordinatalari va Google Maps QR kodi.</div>
  </div>
</body>
</html>"""

open(OUT_HTML, "w").write(html)
r = subprocess.run(["node", f"{BASE}/skills/pdf/scripts/html2poster.js", OUT_HTML,
                    "--output", OUT_PDF, "--width", "297mm"],
                   capture_output=True, text=True, timeout=180)
sz = os.path.getsize(OUT_PDF) if os.path.exists(OUT_PDF) else 0
print("render rc:", r.returncode, "size:", sz)
if r.returncode != 0:
    print((r.stdout or "")[-300:], (r.stderr or "")[-300:])
