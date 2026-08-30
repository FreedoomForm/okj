#!/usr/bin/env python3
"""CI: generate pair-page HTML (template from scripts/pages_gen.py) + render via html2poster.js.
Usage: python3 ci/gen_html.py --shard 0 --shards 8
work/pages/*.html -> work/pages/*.pdf -> output/*.pdf
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "work", "pages")
OUT = os.path.join(ROOT, "output")
os.makedirs(PAGES, exist_ok=True); os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import pages_gen

# patch module paths to CI layout
pages_gen.BASE = ROOT
pages_gen.IMG = os.path.join(ROOT, "work", "pair_images")
pages_gen.QR = os.path.join(ROOT, "work", "qr")
pages_gen.OUT = PAGES
os.makedirs(pages_gen.QR, exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
args = ap.parse_args()

pairs = json_pairs = __import__("json").load(open(os.path.join(ROOT, "album", "selected_pairs.json")))
pairs = [p for n, p in enumerate(pairs) if n % args.shards == args.shard]

ok = fail = 0
for p in pairs:
    p["img_old"] = os.path.join(pages_gen.IMG, f"{p['id']}_old.jpg")
    p["img_new"] = os.path.join(pages_gen.IMG, f"{p['id']}_new.jpg")
    if not (os.path.exists(p["img_old"]) and os.path.exists(p["img_new"])):
        print(f"SKIP {p['id']}: images missing")
        fail += 1
        continue
    hp = os.path.join(PAGES, f"pair_{p['num']:03d}_{p['id']}.html")
    pp = os.path.join(OUT, f"pair_{p['num']:03d}_{p['id']}.pdf")
    with open(hp, "w") as f:
        f.write(pages_gen.pair_page_html(p))
    r = subprocess.run(
        ["node", os.path.join(ROOT, "ci", "html2poster.js"), hp, "--output", pp, "--width", "297mm"],
        capture_output=True, text=True, timeout=240, cwd=ROOT)
    if r.returncode == 0 and os.path.exists(pp) and os.path.getsize(pp) > 30000:
        ok += 1
        print(f"OK {p['id']} -> {os.path.basename(pp)} ({os.path.getsize(pp)//1024}KB)")
    else:
        fail += 1
        print(f"RENDER FAIL {p['id']}: {(r.stderr or r.stdout)[-200:]}")
print(f"shard {args.shard}: ok={ok} fail={fail}")
