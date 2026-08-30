#!/usr/bin/env python3
"""Download all searched images, dedupe, save under research/images/."""
import json, os, hashlib, urllib.request, ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC = "/home/z/my-project/research/searches"
DST = "/home/z/my-project/research/images"
os.makedirs(DST, exist_ok=True)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

seen_hashes = set()
tasks = []

for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".json"):
        continue
    qid = fn[:-5]
    try:
        data = json.load(open(os.path.join(SRC, fn)))
    except Exception:
        continue
    if not data.get("success"):
        continue
    for idx, r in enumerate(data.get("results", [])):
        url = r.get("original_url")
        if url:
            tasks.append((qid, idx, url))

def fetch(t):
    qid, idx, url = t
    ext = ".jpg"
    low = url.lower().split("?")[0]
    for e in (".png", ".jpeg", ".webp", ".gif"):
        if low.endswith(e):
            ext = ".png" if e == ".jpeg" else e
            break
    path = os.path.join(DST, f"{qid}_{idx:02d}{ext}")
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        return path, "exists"
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
            raw = resp.read()
        if len(raw) < 3000:
            return None, f"too-small {len(raw)}"
        h = hashlib.md5(raw).hexdigest()
        if h in seen_hashes:
            return None, "dup"
        seen_hashes.add(h)
        with open(path, "wb") as f:
            f.write(raw)
        return path, f"ok {len(raw)//1024}KB"
    except Exception as e:
        return None, f"err {str(e)[:60]}"

results = {"ok": 0, "skip": 0, "fail": 0}
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = {ex.submit(fetch, t): t for t in tasks}
    for f in as_completed(futs):
        path, status = f.result()
        if status.startswith(("ok", "exists")):
            results["ok"] += 1
        elif status.startswith(("too-small", "dup")):
            results["skip"] += 1
        else:
            results["fail"] += 1
            print(f"FAIL {t[0]}_{t[1]}: {status}")

print(f"tasks={len(tasks)} ok={results['ok']} skipped={results['skip']} failed={results['fail']}")
