#!/usr/bin/env python3
"""Batch image search for NEW Tashkent album candidates (old + modern)."""
import json, os, subprocess, sys, time
sys.path.insert(0, "/home/z/my-project/scripts")
from manifest import CANDIDATES

OUT = "/home/z/my-project/research/searches"
os.makedirs(OUT, exist_ok=True)

def run(c):
    out = os.path.join(OUT, f"{c['id']}_old.json")
    if os.path.exists(out) and os.path.getsize(out) > 200:
        return c['id'] + "_old", "cached"
    for attempt in range(4):
        try:
            r = subprocess.run(
                ["z-ai", "image-search", "-q", c["old_q"], "--count", "8", "--no-rank",
                 "--gl", "us", "-o", out],
                capture_output=True, text=True, timeout=200)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 200:
                return c['id'] + "_old", "ok"
            if "429" in (r.stderr or ""):
                wait = 25 * (attempt + 1)
                print(f"  {c['id']}_old: 429, wait {wait}s (attempt {attempt+1})", flush=True)
                time.sleep(wait)
                continue
            return c['id'] + "_old", f"fail: {(r.stderr or '')[:150]}"
        except subprocess.TimeoutExpired:
            return c['id'] + "_old", "timeout"
        except Exception as e:
            return c['id'] + "_old", f"err: {e}"
    return c['id'] + "_old", "exhausted"

def run_new(c):
    out = os.path.join(OUT, f"{c['id']}_new.json")
    if os.path.exists(out) and os.path.getsize(out) > 200:
        return c['id'] + "_new", "cached"
    for attempt in range(4):
        try:
            r = subprocess.run(
                ["z-ai", "image-search", "-q", c["new_q"], "--count", "8", "--no-rank",
                 "--gl", "us", "-o", out],
                capture_output=True, text=True, timeout=200)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 200:
                return c['id'] + "_new", "ok"
            if "429" in (r.stderr or ""):
                wait = 25 * (attempt + 1)
                print(f"  {c['id']}_new: 429, wait {wait}s (attempt {attempt+1})", flush=True)
                time.sleep(wait)
                continue
            return c['id'] + "_new", f"fail: {(r.stderr or '')[:150]}"
        except subprocess.TimeoutExpired:
            return c['id'] + "_new", "timeout"
        except Exception as e:
            return c['id'] + "_new", f"err: {e}"
    return c['id'] + "_new", "exhausted"

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    todo = [c for c in CANDIDATES if not only or c["id"] in only]
    done = 0
    t0 = time.time()
    for c in todo:
        qid, status = run(c)
        done += 1
        print(f"[{done}/{len(todo)*2}] {qid}: {status}  ({(time.time()-t0)/60:.1f}min)", flush=True)
        time.sleep(8)
        qid, status = run_new(c)
        done += 1
        print(f"[{done}/{len(todo)*2}] {qid}: {status}  ({(time.time()-t0)/60:.1f}min)", flush=True)
        time.sleep(8)
    print("ALL DONE", flush=True)
