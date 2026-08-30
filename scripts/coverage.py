#!/usr/bin/env python3
"""Coverage check: which manifest candidates have old+new search results."""
import json, os, sys
sys.path.insert(0, "/home/z/my-project/scripts")
from manifest import CANDIDATES

SRC = "/home/z/my-project/research/searches"
cov = {}
for fn in os.listdir(SRC):
    if not fn.endswith(".json"):
        continue
    cid, suf = fn[:-5].rsplit("_", 1)
    if suf not in ("old", "new"):
        continue
    try:
        d = json.load(open(os.path.join(SRC, fn)))
        n = len(d.get("results", [])) if d.get("success") else 0
    except Exception:
        n = 0
    prev = cov.get((cid, suf), 0)
    cov[(cid, suf)] = max(prev, n)

total = 0
missing = []
for c in CANDIDATES:
    o = cov.get((c["id"], "old"), 0)
    n = cov.get((c["id"], "new"), 0)
    if o > 0 and n > 0:
        total += 1
    else:
        missing.append(f"  {c['id']}: old={o} new={n}")
print(f"complete: {total}/{len(CANDIDATES)}")
print("\n".join(missing) if missing else "ALL COMPLETE")
