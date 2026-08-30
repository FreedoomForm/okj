#!/usr/bin/env python3
"""Download searched images for manifest candidates only -> research/images/{id}_old_NN.ext"""
import json, os, sys, hashlib, urllib.request, ssl
sys.path.insert(0, "/home/z/my-project/scripts")
from manifest import CANDIDATES

SRC = "/home/z/my-project/research/searches"
DST = "/home/z/my-project/research/images"
os.makedirs(DST, exist_ok=True)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ids = {c["id"] for c in CANDIDATES}
if len(sys.argv) > 1:
    ids = {i for i in ids if i in sys.argv[1:]}

tasks = []
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".json"):
        continue
    base = fn[:-5]
    cid, suffix = base.rsplit("_", 1)
    if cid not in ids or suffix not in ("old", "new"):
        continue
    try:
        data = json.load(open(os.path.join(SRC, fn)))
    except Exception:
        continue
    if not data.get("success"):
        continue
    for idx, r in enumerate(data.get("results", [])):
        url = r.get("original_url")
        if url:
            tasks.append((cid, suffix, idx, url))

def fetch(t):
    cid, suffix, idx, url = t
    ext = ".jpg"
    low = url.lower().split("?")[0]
    for e in (".png", ".jpeg", ".webp", ".gif"):
        if low.endswith(e):
            ext = ".png" if e == ".jpeg" else e
            break
    path = os.path.join(DST, f"{cid}_{suffix}_{idx:02d}{ext}")
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        return path, "exists"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            raw = resp.read()
        if len(raw) < 3000:
            return None, f"too-small {len(raw)}"
        with open(path, "wb") as f:
            f.write(raw)
        return path, f"ok {len(raw)//1024}KB"
    except Exception as e:
        return None, f"err {str(e)[:60]}"

from concurrent.futures import ThreadPoolExecutor, as_completed
stats = {"ok": 0, "exists": 0, "fail": 0}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(fetch, t): t for t in tasks}
    for f in as_completed(futs):
        path, status = f.result()
        if status in ("ok", "exists") or status.startswith("ok"):
            stats["ok" if status == "ok" else "exists"] += 1
        else:
            stats["fail"] += 1
print(f"tasks={len(tasks)} downloaded={stats['ok']} existing={stats['exists']} failed={stats['fail']}")
