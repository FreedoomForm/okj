#!/usr/bin/env python3
"""One combined selection sheet per candidate: old candidates (left) + modern (right).
Usage: python3 pair_sheets.py [id ...]  (default: all ids present in images dir)"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/z/my-project/research/images"
OUT = "/home/z/my-project/research/pair_sheets"
os.makedirs(OUT, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try:
    font = ImageFont.truetype(FONT, 20)
    title_font = ImageFont.truetype(FONT, 30)
except Exception:
    font = title_font = ImageFont.load_default()

TH_W, TH_H, LABEL = 320, 240, 30

def grid(files, cols=4, tag_prefix=""):
    rows = math.ceil(len(files) / cols) if files else 1
    g = Image.new("RGB", (cols * TH_W, rows * (TH_H + LABEL)), "#1a1a1a")
    d = ImageDraw.Draw(g)
    for i, fn in enumerate(files):
        try:
            im = Image.open(os.path.join(SRC, fn)).convert("RGB")
        except Exception:
            continue
        im.thumbnail((TH_W - 8, TH_H - 8))
        x = (i % cols) * TH_W
        y = (i // cols) * (TH_H + LABEL)
        g.paste(im, (x + (TH_W - im.width) // 2, y + (TH_H - im.height) // 2))
        tag = fn.rsplit(".", 1)[0]
        d.text((x + 6, y + TH_H + 3), tag, fill="#ffd54a", font=font)
    return g

def sheet_for(cid):
    olds = sorted(f for f in os.listdir(SRC)
                  if f.startswith(f"{cid}_old_") and f.lower().endswith((".jpg", ".png", ".webp", ".jpeg")))
    news = sorted(f for f in os.listdir(SRC)
                  if f.startswith(f"{cid}_new_") and f.lower().endswith((".jpg", ".png", ".webp", ".jpeg")))
    if not olds and not news:
        return None
    g_old = grid(olds)
    g_new = grid(news)
    W = max(g_old.width, g_new.width)
    TITLE = 46
    out = Image.new("RGB", (W, TITLE + g_old.height + g_new.height), "#111")
    d = ImageDraw.Draw(out)
    d.text((10, 6), f"{cid}  OLD ({len(olds)})  -- top,  NEW ({len(news)}) -- bottom", fill="#4dd0e1", font=title_font)
    out.paste(g_old, (0, TITLE))
    out.paste(g_new, (0, TITLE + g_old.height))
    path = os.path.join(OUT, f"{cid}.png")
    out.save(path)
    return path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ids = sys.argv[1:]
    else:
        ids = sorted({f.split("_old_")[0].split("_new_")[0] for f in os.listdir(SRC)
                      if f.lower().endswith((".jpg", ".png", ".webp", ".jpeg"))})
    for cid in ids:
        p = sheet_for(cid)
        print(f"{cid}: {p}")
