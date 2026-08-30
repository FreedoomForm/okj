#!/usr/bin/env python3
"""CI: download ONLY the selected pair photos (from album/selected_pairs.json), preprocess.
Usage: python3 ci/fetch_pair_images.py --shard 0 --shards 8
old_url/new_url -> work/pair_images/{id}_old.jpg, {id}_new.jpg  (flattened RGB, max 1700px, q88)
"""
import argparse, io, json, os, ssl, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "work", "pair_images")
os.makedirs(DST, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
args = ap.parse_args()

pairs = json.load(open(os.path.join(ROOT, "album", "selected_pairs.json")))
pairs = [p for n, p in enumerate(pairs) if n % args.shards == args.shard]

def prep(raw, path):
    im = Image.open(io.BytesIO(raw))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 253, 246))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if max(im.size) > 1700:
        im.thumbnail((1700, 1700), Image.LANCZOS)
    im.save(path, quality=88)
    return im.size

def fetch(p):
    out_old = os.path.join(DST, f"{p['id']}_old.jpg")
    out_new = os.path.join(DST, f"{p['id']}_new.jpg")
    res = []
    for key, out in (("old_url", out_old), ("new_url", out_new)):
        if os.path.exists(out) and os.path.getsize(out) > 20000:
            res.append(f"{key}:exists")
            continue
        url = p.get(key)
        if not url:
            res.append(f"{key}:NO-URL")
            continue
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                raw = resp.read()
            if len(raw) < 20000:
                res.append(f"{key}:too-small")
                continue
            size = prep(raw, out)
            res.append(f"{key}:ok{size[0]}x{size[1]}")
        except Exception as e:
            res.append(f"{key}:err {str(e)[:40]}")
    return p["id"], res

ok = fail = 0
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = [ex.submit(fetch, p) for p in pairs]
    for f in as_completed(futs):
        pid, res = f.result()
        bad = [r for r in res if ":err" in r or ":NO-URL" in r or ":too-small" in r]
        if bad:
            fail += 1
            print(f"FAIL {pid}: {bad}")
        else:
            ok += 1
print(f"shard {args.shard}: pairs={len(pairs)} ok={ok} fail={fail}")
