#!/usr/bin/env python3
"""Generate album pair pages + TOC + cover in the original vintage design.
Original design tokens sampled from Toshkent_kecha_va_bugun.pdf:
  bg #f6efe0, title #3d2b1f, frame #896033, kicker #ac9983, rule #c9b391,
  captions #5c4531, Playfair Display (900) + PT Serif.
Page: A4 landscape 297x210mm. Pair pages numbered from 21 (original 1-20 kept).
"""
import json, os, subprocess, sys

BASE = "/home/z/my-project"
SRC = f"{BASE}/download/tashkent-album-src"
IMG = f"{BASE}/research/pair_images"       # selected pair photos (processed)
QR = f"{SRC}/assets/qr"
OUT = f"{BASE}/research/new_pages"
os.makedirs(IMG, exist_ok=True); os.makedirs(QR, exist_ok=True); os.makedirs(OUT, exist_ok=True)

FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,600&family=PT+Serif:ital@0;1&display=swap" rel="stylesheet">'

CHAPTER_KICK = {1: "I BOB &middot; 1900&ndash;1930", 2: "II BOB &middot; 1930&ndash;1960", 3: "III BOB &middot; 1960&ndash;2000"}

def gen_qr(lat, lng, cid):
    import qrcode
    url = f"https://www.google.com/maps?q={lat},{lng}"
    path = f"{QR}/{cid}.png"
    if not os.path.exists(path):
        qr = qrcode.QRCode(border=1, box_size=10)
        qr.add_data(url); qr.make()
        img = qr.make_image(fill_color="#3d2b1f", back_color="white")
        img.save(path)
    return path

def pair_page_html(p):
    """p: dict(num, ch, title, old_era, old_cap, new_cap, lat, lng, img_old, img_new)"""
    rel_old = os.path.relpath(p["img_old"], OUT)
    rel_new = os.path.relpath(p["img_new"], OUT)
    rel_qr = os.path.relpath(gen_qr(p["lat"], p["lng"], p["id"]), OUT)
    coords = f"{p['lat']:.4f}, {p['lng']:.4f}"
    return f"""<!DOCTYPE html>
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
    position: absolute; top: 12.6mm; left: 0; right: 0; text-align: center;
    font-size: 3.55mm; letter-spacing: 1.5mm; color: #ac9983; font-weight: 700;
  }}
  h1 {{
    position: absolute; top: 16.4mm; left: 20mm; right: 20mm; margin: 0; text-align: center;
    font-family: 'Playfair Display', Georgia, serif; font-weight: 900; font-size: 8.4mm;
    line-height: 1.1; color: #3d2b1f;
  }}
  .label {{
    position: absolute; top: 30.6mm; width: 131mm; text-align: center;
    font-size: 3.3mm; letter-spacing: 1.15mm; color: #ac9983; font-weight: 700;
  }}
  .label.l {{ left: 13mm; }} .label.r {{ left: 153mm; }}
  .card {{
    position: absolute; top: 36.4mm; width: 131mm; height: 117.6mm; background: #fffdf6;
    box-shadow: 0 1.2mm 3.2mm rgba(61,43,31,.30); box-sizing: border-box; padding: 2.4mm;
  }}
  .card.l {{ left: 13mm; }} .card.r {{ left: 153mm; }}
  .card img {{ width: 126.2mm; height: 112.8mm; object-fit: contain; display: block; background: #fffdf6; }}
  .cap {{
    position: absolute; top: 157.6mm; width: 131mm; text-align: center;
    font-style: italic; font-size: 3.55mm; line-height: 1.42; color: #5c4531;
  }}
  .cap.l {{ left: 13mm; }} .cap.r {{ left: 153mm; }}
  .rule {{ position: absolute; top: 182.6mm; left: 13mm; right: 13mm; height: 0.22mm; background: #c9b391; }}
  .foot-name {{
    position: absolute; top: 190.2mm; left: 13mm; width: 90mm; font-weight: 700; font-size: 3.7mm;
  }}
  .foot-coords {{
    position: absolute; top: 190.2mm; left: 90mm; right: 70mm; text-align: center;
    font-size: 3.55mm; color: #3d2b1f;
  }}
  .foot-coords .gm {{ color: #896033; font-weight: 700; }}
  .qr {{ position: absolute; top: 187.6mm; left: 251.5mm; width: 13.4mm; height: 13.4mm; }}
  .qr-label {{
    position: absolute; top: 188.6mm; left: 266.5mm; width: 18mm;
    font-size: 2.9mm; letter-spacing: 0.42mm; color: #896033; font-weight: 700; line-height: 1.5;
  }}
  .pagenum {{
    position: absolute; top: 201.4mm; left: 0; right: 0; text-align: center;
    font-size: 3.4mm; color: #5c4531;
  }}
</style>
</head>
<body>
  <div class="poster">
    <div class="frame"></div><div class="frame2"></div>
    <div class="kicker">{CHAPTER_KICK[p['ch']]}</div>
    <h1>{p['title']}</h1>
    <div class="label l">E S K I&nbsp;&nbsp;S U R A T&nbsp;&nbsp;&middot;&nbsp;&nbsp;{p['old_era']}</div>
    <div class="label r">B U G U N G I&nbsp;&nbsp;K O&lsquo; R I N I S H</div>
    <div class="card l"><img src="{rel_old}" alt=""></div>
    <div class="card r"><img src="{rel_new}" alt=""></div>
    <div class="cap l">{p['old_cap']}</div>
    <div class="cap r">{p['new_cap']}</div>
    <div class="rule"></div>
    <div class="foot-name">{p['title']}</div>
    <div class="foot-coords">{coords} &nbsp;&middot;&nbsp; <span class="gm">Google Maps</span></div>
    <img class="qr" src="{rel_qr}" alt="QR">
    <div class="qr-label">XARITADA<br>OCHISH</div>
    <div class="pagenum">{p['num']}</div>
  </div>
</body>
</html>"""

def render(html_path, out_pdf):
    r = subprocess.run(
        ["node", "/home/z/my-project/skills/pdf/scripts/html2poster.js", html_path,
         "--output", out_pdf, "--width", "297mm"],
        capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"RENDER FAIL {html_path}:\n{r.stdout[-400:]}\n{r.stderr[-400:]}")
        return False
    return True

if __name__ == "__main__":
    pairs_file = sys.argv[1] if len(sys.argv) > 1 else f"{BASE}/research/selected_pairs.json"
    pairs = json.load(open(pairs_file))
    ok = fail = 0
    for p in pairs:
        hp = f"{OUT}/pair_{p['num']:03d}_{p['id']}.html"
        pp = f"{OUT}/pair_{p['num']:03d}_{p['id']}.pdf"
        open(hp, "w").write(pair_page_html(p))
        if render(hp, pp):
            ok += 1; print(f"pair {p['num']:3d} [{p['id']}] OK")
        else:
            fail += 1
    print(f"RENDERED ok={ok} fail={fail}")
