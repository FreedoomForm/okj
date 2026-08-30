#!/usr/bin/env python3
"""Shared: resolve site-id list for sharded CI scripts (single source of truth)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def resolve_ids(ids_arg=""):
    """Explicit space-separated ids (validated), or complete-set from manifest
    (both old+new searches exist with >=1 result). Mirrors fetch_images logic."""
    from manifest import CANDIDATES
    all_ids = {c["id"] for c in CANDIDATES}
    if ids_arg and ids_arg.strip():
        return sorted(s for s in ids_arg.split() if s in all_ids)
    ids = []
    for c in CANDIDATES:
        ok = {"old": False, "new": False}
        for suf in ok:
            p = os.path.join(ROOT, "research", "searches", f"{c['id']}_{suf}.json")
            if os.path.exists(p):
                try:
                    d = json.load(open(p))
                    if d.get("success") and len(d.get("results", [])) > 0:
                        ok[suf] = True
                except Exception:
                    pass
        if ok["old"] and ok["new"]:
            ids.append(c["id"])
    return sorted(ids)


def shard_ids(ids, shard, shards):
    return [i for n, i in enumerate(ids) if n % shards == shard]
