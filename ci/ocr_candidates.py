#!/usr/bin/env python3
"""CI: Mistral OCR over candidate images (single job, ~1 RPS).
Reads work/images/{id}_{old|new}_{NN}.* (search candidates, top N) and
work/images/{id}_{cold|cnew}_{NN}.* (Commons candidates, top N).
Writes output/ocr/{stem}.json  +  output/ocr_index.json (per-site summary).

OCR gives hard same-place evidence: signage, plaques, captions, dates
visible in the photos themselves.
"""
import base64, glob as globmod, io, json, os, time
import urllib.request, urllib.error
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "images")
OUT = os.path.join(ROOT, "output", "ocr")
os.makedirs(OUT, exist_ok=True)

API_URL = "https://api.mistral.ai/v1/ocr"
MODEL = "mistral-ocr-latest"
KEY = os.environ.get("MISTRAL_API_KEY", "")
# caps per site
N_OLD, N_NEW, N_COLD, N_CNEW = 4, 4, 2, 1
SLEEP = 1.15

sys_ids = []
sys_path = os.path.join(ROOT, "scripts")
sys_ids.append(sys_path)
import sys
sys.path.insert(0, sys_path)
from manifest import CANDIDATES

def prep(path, max_px=1600, quality=85):
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    if max(im.size) > max_px:
        im.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return buf.getvalue()

def ocr(data, tries=7):
    b64 = base64.b64encode(data).decode()
    body = json.dumps({"model": MODEL,
                       "document": {"type": "image_url",
                                    "image_url": f"data:image/jpeg;base64,{b64}"},
                       "include_image_base64": False}).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and a < tries - 1:
                wait = min(90, 10 * (a + 1))
                print(f"    HTTP {e.code} retry {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise
    return None

def pick(cid, prefix, n):
    files = []
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        files += globmod.glob(os.path.join(IMG, f"{cid}_{prefix}[0-9][0-9]{ext}"))
    return sorted(files)[:n]

tasks = []  # (site_id, kind, path)
for c in CANDIDATES:
    cid = c["id"]
    for p, n in ((f"old_", N_OLD), (f"new_", N_NEW),
                 (f"cold_", N_COLD), (f"cnew_", N_CNEW)):
        tasks += [(cid, p.strip("_"), f) for f in pick(cid, p, n)]

print(f"OCR queue: {len(tasks)} images", flush=True)
index, done = {}, 0
for n, (cid, kind, path) in enumerate(tasks):
    stem = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(OUT, f"{stem}.json")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 50:
        done += 1
        continue
    try:
        resp = ocr(prep(path)) or {}
        md = "\n".join(p.get("markdown", "") for p in resp.get("pages", [])).strip()
        json.dump({"source": stem, "site": cid, "kind": kind, "text": md,
                   "model": resp.get("model", MODEL)},
                  open(out_path, "w"), ensure_ascii=False, indent=1)
        index[stem] = md[:400]
        print(f"[{n+1}/{len(tasks)}] {stem}: {md[:80]!r}", flush=True)
    except Exception as e:
        json.dump({"source": stem, "site": cid, "kind": kind, "error": str(e)[:200]},
                  open(out_path, "w"), ensure_ascii=False, indent=1)
        print(f"[{n+1}/{len(tasks)}] {stem}: ERROR {str(e)[:80]}", flush=True)
    time.sleep(SLEEP)

with open(os.path.join(OUT, "..", "ocr_index.json"), "w") as f:
    json.dump(index, f, ensure_ascii=False, indent=1)
print(f"OCR done: {len(index)} extracted, {done} pre-existing", flush=True)
