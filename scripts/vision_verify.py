#!/usr/bin/env python3
"""Verify candidate pairs with z-ai vision: same place? is old photo truly historical?
Usage: python3 vision_verify.py <pairs_json> [batch_size]
pairs_json: [{"id","img_old","img_new"}, ...] — writes results to research/verify/<id>.json
"""
import json, os, subprocess, sys, time

BASE = "/home/z/my-project"
VOUT = f"{BASE}/research/verify"
os.makedirs(VOUT, exist_ok=True)

PROMPT = """You are a strict photo-verification expert for a historical photo album about Tashkent, Uzbekistan.
Image 1 = a photograph claimed to be HISTORICAL (early 1900s-1990s) showing a specific place in Tashkent.
Image 2 = a photograph claimed to be MODERN (2015-2026) showing the SAME place.

Tasks:
1. same_place: Does image 2 show the SAME building/complex/location as image 1? Judge by architecture, distinctive landmarks, building shape, minarets/domes/towers, layout, surroundings. If image 2 shows a DIFFERENT building or a generic unrelated view, answer false.
2. image1_historical: Is image 1 actually an old/historical photograph (black&white, sepia, faded color, Soviet-era photo, vintage postcard)? If it is a crisp modern digital photo, answer false.
3. image2_modern: Is image 2 a modern, good-quality photo of the place? (crisp, not a scan of an old postcard) If it is actually an old/historical photo, answer false.

Answer with STRICT JSON only, no markdown:
{"same_place": true/false, "confidence": 0-100, "image1_historical": true/false, "image2_modern": true/false, "landmark_1": "short description of what image 1 shows", "landmark_2": "short description of what image 2 shows", "reasoning": "1-2 sentences"}
"""

def verify_one(item):
    out = os.path.join(VOUT, f"{item['id']}.json")
    if os.path.exists(out) and os.path.getsize(out) > 100:
        return item['id'], "cached"
    for attempt in range(3):
        r = subprocess.run(
            ["z-ai", "vision", "-p", PROMPT,
             "-i", item["img_old"], "-i", item["img_new"], "-o", out],
            capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 100:
            return item['id'], "ok"
        err = (r.stderr or "") + (r.stdout or "")
        if "429" in err:
            wait = 20 * (attempt + 1)
            print(f"  {item['id']}: 429, wait {wait}s", flush=True)
            time.sleep(wait)
            continue
        return item['id'], f"fail: {err[:120]}"
    return item['id'], "exhausted"

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))
    t0 = time.time()
    for i, it in enumerate(items):
        qid, status = verify_one(it)
        print(f"[{i+1}/{len(items)}] {qid}: {status} ({(time.time()-t0)/60:.1f}min)", flush=True)
        time.sleep(4)
    print("ALL DONE")
