#!/usr/bin/env python3
"""Batch image search for Tashkent album (old + modern pairs)."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT = "/home/z/my-project/research/searches"
os.makedirs(OUT, exist_ok=True)

# (id, query) — old photos first block, modern second block
QUERIES = [
    # --- OLD (1900-2000) ---
    ("old_amirtemur",  "Amir Timur square Tashkent old historical photograph 1900s"),
    ("old_chorsu",     "Chorsu bazaar Tashkent old historical photo Soviet era"),
    ("old_kukeldash",  "Kukeldash madrasah Tashkent old photograph"),
    ("old_hazratimom", "Hazrat Imam complex Tashkent old historical photograph"),
    ("old_navoiteatr", "Alisher Navoi opera ballet theater Tashkent 1950s historical photo"),
    ("old_lenin_sq",   "Lenin square Tashkent Soviet era monument historical photo"),
    ("old_quake",      "Tashkent 1966 earthquake destruction historical photo"),
    ("old_vokzal",     "Tashkent railway station old historical photograph"),
    ("old_chilonzor",  "Chilonzor Tashkent 1970s Soviet residential district photo"),
    ("old_tv_tower",   "Tashkent TV tower 1980s historical photo"),
    ("old_hotel_uz",   "Hotel Uzbekistan Tashkent 1970s Soviet photo"),
    ("old_broadway",   "Tashkent Broadway Sayilgoh street 1990s photo"),
    ("old_anhor",      "Anhor canal Tashkent historical photograph"),
    ("old_eski",       "Old Tashkent street mahalla adobe houses historical photo 1900s"),
    ("old_tram",       "Tashkent tram 1970s vintage historical photo"),
    ("old_circus",     "Tashkent circus building old historical photo"),
    ("old_romanov",    "Romanov palace Tashkent historical photograph"),
    ("old_muzey",      "Lenin museum Tashkent history museum old Soviet photo"),
    ("old_panorama",   "Tashkent cityscape panorama 1980s Soviet photo"),
    ("old_metro",      "Tashkent metro subway station 1980s Soviet photo"),
    # --- MODERN ---
    ("new_amirtemur",  "Amir Timur square Tashkent modern view"),
    ("new_chorsu",     "Chorsu bazaar Tashkent modern blue dome"),
    ("new_kukeldash",  "Kukeldash madrasah Tashkent today modern photo"),
    ("new_hazratimom", "Hazrati Imam complex Tashkent modern photo"),
    ("new_navoiteatr", "Alisher Navoi theater Tashkent modern fountains"),
    ("new_mustaqillik","Mustaqillik square Tashkent modern monument"),
    ("new_jasorat",    "Courage monument Tashkent earthquake memorial modern"),
    ("new_vokzal",     "Tashkent railway station modern building"),
    ("new_chilonzor",  "Chilonzor district Tashkent modern"),
    ("new_tv_tower",   "Tashkent television tower modern view"),
    ("new_hotel_uz",   "Hotel Uzbekistan Tashkent modern"),
    ("new_broadway",   "Sayilgoh street Tashkent modern Broadway"),
    ("new_anhor",      "Anhor canal Tashkent modern promenade"),
    ("new_eski",       "Old town Tashkent restored mahalla street modern photo"),
    ("new_tram",       "Tashkent modern tram 2021 Navoi street"),
    ("new_circus",     "Tashkent circus modern building photo"),
    ("new_romanov",    "Prince Romanov palace Tashkent modern photo"),
    ("new_muzey",      "State History Museum Uzbekistan Tashkent modern"),
    ("new_panorama",   "Tashkent City modern skyline"),
    ("new_metro",      "Tashkent metro station modern beautiful interior"),
]

def run(qid, q):
    out = os.path.join(OUT, f"{qid}.json")
    if os.path.exists(out) and os.path.getsize(out) > 200:
        return qid, "cached"
    for attempt in range(4):
        try:
            r = subprocess.run(
                ["z-ai", "image-search", "-q", q, "--count", "8", "--no-rank",
                 "--gl", "us", "-o", out],
                capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 200:
                return qid, "ok"
            if "429" in (r.stderr or ""):
                wait = 25 * (attempt + 1)
                print(f"  {qid}: 429, wait {wait}s (attempt {attempt+1})", flush=True)
                time.sleep(wait)
                continue
            return qid, f"fail: {(r.stderr or '')[:150]}"
        except subprocess.TimeoutExpired:
            return qid, "timeout"
        except Exception as e:
            return qid, f"err: {e}"
    return qid, "exhausted-retries"

if __name__ == "__main__":
    import time
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    todo = [(i, q) for i, q in QUERIES if not only or i in only]
    done = 0
    for i, q in todo:
        qid, status = run(i, q)
        done += 1
        print(f"[{done}/{len(todo)}] {qid}: {status}", flush=True)
        time.sleep(18)
    print("ALL DONE")
