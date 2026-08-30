#!/usr/bin/env python3
"""CI: build per-candidate old+new selection sheets as JPEG (sharded).
Usage: python3 ci/build_sheets.py --shard 0 --shards 6 [--ids "id1 id2 ..."]
work/images/* -> output/{id}.jpg
"""
import argparse, math, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import resolve_ids, shard_ids

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "images")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except Exception:
    font = title_font = ImageFont.load_default()

TH_W, TH_H, LABEL = 320, 240, 30
VALID = (".jpg", ".png", ".webp", ".jpeg")

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
ap.add_argument("--ids", default="")
args = ap.parse_args()

want = shard_ids(resolve_ids(args.ids), args.shard, args.shards)

def grid(files, cols=4):
    rows = math.ceil(len(files) / cols) if files else 1
    g = Image.new("RGB", (cols * TH_W, rows * (TH_H + LABEL)), "#1a1a1a")
    d = ImageDraw.Draw(g)
    for i, fn in enumerate(files):
        try:
            im = Image.open(os.path.join(IMG, fn)).convert("RGB")
        except Exception:
            continue
        im.thumbnail((TH_W - 8, TH_H - 8))
        x = (i % cols) * TH_W
        y = (i // cols) * (TH_H + LABEL)
        g.paste(im, (x + (TH_W - im.width) // 2, y + (TH_H - im.height) // 2))
        d.text((x + 6, y + TH_H + 3), fn.rsplit(".", 1)[0], fill="#ffd54a", font=font)
    return g

for cid in want:
    olds = sorted(f for f in os.listdir(IMG) if f.startswith((f"{cid}_old_", f"{cid}_cold_")) and f.lower().endswith(VALID))
    news = sorted(f for f in os.listdir(IMG) if f.startswith((f"{cid}_new_", f"{cid}_cnew_")) and f.lower().endswith(VALID))
    if not olds and not news:
        continue
    g_old, g_new = grid(olds), grid(news)
    W = max(g_old.width, g_new.width)
    TITLE = 46
    sheet = Image.new("RGB", (W, TITLE + g_old.height + g_new.height), "#111")
    d = ImageDraw.Draw(sheet)
    d.text((10, 6), f"{cid}  OLD+cold ({len(olds)}) top  /  NEW+cnew ({len(news)}) bottom", fill="#4dd0e1", font=title_font)
    sheet.paste(g_old, (0, TITLE))
    sheet.paste(g_new, (0, TITLE + g_old.height))
    sheet.save(os.path.join(OUT, f"{cid}.jpg"), quality=82)
    print(f"sheet {cid}: old={len(olds)} new={len(news)}")
print("done", len(want))
