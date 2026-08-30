#!/usr/bin/env python3
"""CI: download candidate images for given manifest ids (sharded).
Usage: python3 ci/fetch_images.py --shard 0 --shards 6 [--ids "id1 id2 ..."]
Reads research/searches/{id}_{old|new}.json -> work/images/{id}_{old|new}_{idx}.ext
Writes output/stats_shard_{i}.json
"""
import argparse, json, os, ssl, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "images")
OUT = os.path.join(ROOT, "output")
os.makedirs(IMG, exist_ok=True); os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from manifest import CANDIDATES

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

ap = argparse.ArgumentParser()
ap.add_argument("--shard", type=int, default=0)
ap.add_argument("--shards", type=int, default=1)
ap.add_argument("--ids", default="")
args = ap.parse_args()

all_ids = {c["id"] for c in CANDIDATES}
if args.ids.strip():
    ids = {s for s in args.ids.split() if s in all_ids}
else:
    # complete = both old+new searches have >=1 result
    ids = set()
    for c in CANDIDATES:
        ok_old = ok_new = False
        for suf in ("old", "new"):
            p = os.path.join(ROOT, "research", "searches", f"{c['id']}_{suf}.json")
            if os.path.exists(p):
                try:
                    d = json.load(open(p))
                    if d.get("success") and len(d.get("results", [])) > 0:
                        if suf == "old": ok_old = True
                        else: ok_new = True
                except Exception:
                    pass
        if ok_old and ok_new:
            ids.add(c["id"])

shard_ids = sorted(i for n, i in enumerate(ids) if n % args.shards == args.shard)

tasks = []
for cid in shard_ids:
    for suf in ("old", "new"):
        p = os.path.join(ROOT, "research", "searches", f"{cid}_{suf}.json")
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if not d.get("success"):
            continue
        for idx, r in enumerate(d.get("results", [])):
            url = r.get("original_url")
            if url:
                tasks.append((cid, suf, idx, url))

def fetch(t):
    cid, suf, idx, url = t
    ext = ".jpg"
    low = url.lower().split("?")[0]
    for e in (".png", ".jpeg", ".webp", ".gif"):
        if low.endswith(e):
            ext = ".png" if e == ".jpeg" else e
            break
    path = os.path.join(IMG, f"{cid}_{suf}_{idx:02d}{ext}")
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        return "exists"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40, context=ctx) as resp:
            raw = resp.read()
        if len(raw) < 3000:
            return "too-small"
        with open(path, "wb") as f:
            f.write(raw)
        return "ok"
    except Exception as e:
        return f"err {str(e)[:50]}"

stats = {"ok": 0, "exists": 0, "fail": 0, "errors": []}
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(fetch, t): t for t in tasks}
    for f in as_completed(futs):
        s = f.result()
        if s.startswith(("ok", "exists")):
            stats[s] += 1
        else:
            stats["fail"] += 1
            if len(stats["errors"]) < 20:
                stats["errors"].append(f"{futs[f][0]}_{futs[f][1]}_{futs[f][2]}: {s}")

stats["ids_in_shard"] = shard_ids
stats["tasks"] = len(tasks)
with open(os.path.join(OUT, f"stats_shard_{args.shard}.json"), "w") as f:
    json.dump(stats, f, indent=1)
print(f"shard {args.shard}: ids={len(shard_ids)} tasks={len(tasks)} ok={stats['ok']} exists={stats['exists']} fail={stats['fail']}")
