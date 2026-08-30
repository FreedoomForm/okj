#!/usr/bin/env python3
"""Build labeled contact sheets from research/images for visual QA."""
import os, math
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/z/my-project/research/images"
OUT = "/home/z/my-project/research/sheets"
os.makedirs(OUT, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try:
    font = ImageFont.truetype(FONT, 22)
    font_s = ImageFont.truetype(FONT, 16)
except Exception:
    font = font_s = ImageFont.load_default()

TH_W, TH_H, LABEL = 300, 220, 34

def sheets_for(prefix):
    files = sorted(f for f in os.listdir(SRC) if f.startswith(prefix) and
                   f.lower().endswith((".jpg", ".png", ".webp", ".jpeg")))
    if not files:
        return None
    per_sheet = 12
    outs = []
    for s in range(math.ceil(len(files) / per_sheet)):
        chunk = files[s * per_sheet:(s + 1) * per_sheet]
        cols = 4
        rows = math.ceil(len(chunk) / cols)
        sheet = Image.new("RGB", (cols * TH_W, rows * (TH_H + LABEL)), "#222")
        d = ImageDraw.Draw(sheet)
        for i, fn in enumerate(chunk):
            try:
                im = Image.open(os.path.join(SRC, fn)).convert("RGB")
            except Exception:
                continue
            im.thumbnail((TH_W - 8, TH_H - 8))
            x = (i % cols) * TH_W
            y = (i // cols) * (TH_H + LABEL)
            sheet.paste(im, (x + (TH_W - im.width) // 2, y + (TH_H - im.height) // 2))
            tag = fn.replace(prefix + "_", "").rsplit(".", 1)[0]
            d.text((x + 8, y + TH_H + 5), tag, fill="#ffd54a", font=font)
        out = os.path.join(OUT, f"sheet_{prefix}_{s}.png")
        sheet.save(out)
        outs.append(out)
    return outs

if __name__ == "__main__":
    import sys
    prefixes = sys.argv[1:] if len(sys.argv) > 1 else sorted(
        {f.rsplit("_", 1)[0] for f in os.listdir(SRC)
         if f.lower().endswith((".jpg", ".png", ".webp", ".jpeg"))})
    for p in prefixes:
        outs = sheets_for(p)
        print(p, "->", outs)
