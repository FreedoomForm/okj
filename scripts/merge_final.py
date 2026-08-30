#!/usr/bin/env python3
"""Final merge v3: cover + author's word + NEW unified TOC (all 37 pairs)
+ original album pages (3 dividers + 20 pairs, original cover/TOC skipped)
+ 17 new verified pairs (21..37) — pikepdf. The old 'Qo'shimcha to'plam — davomi'
mini-TOC page is REMOVED (user request: full TOC lists every page).
Output: download/Toshkent_kecha_va_bugun_TANLOV.pdf (43 pages, 37 pairs, 74 photos)."""
import glob, os, pikepdf

BASE = "/home/z/my-project"
SRC = f"{BASE}/upload/Toshkent_kecha_va_bugun.pdf"
COVER = f"{BASE}/download/tashkent-album-src/muqova_tanlov.pdf"
STATE = f"{BASE}/download/tashkent-album-src/muallif_suzi.pdf"
TOC = f"{BASE}/research/new_pages/mundarija.pdf"
PAGES = sorted(glob.glob(f"{BASE}/research/pages_ci/pair_*.pdf"))
OUT = f"{BASE}/download/Toshkent_kecha_va_bugun_TANLOV.pdf"

assert len(PAGES) == 17, f"expected 17 new pair pages, got {len(PAGES)}"

out = pikepdf.new()
pdf_cover = pikepdf.open(COVER)
pdf_state = pikepdf.open(STATE)
pdf_toc = pikepdf.open(TOC)
pdf_orig = pikepdf.open(SRC)
pdf_new = [pikepdf.open(p) for p in PAGES]  # keep refs alive!

out.pages.append(pdf_cover.pages[0])
out.pages.append(pdf_state.pages[0])
out.pages.append(pdf_toc.pages[0])     # NEW unified TOC (all 37 pairs)
out.pages.extend(pdf_orig.pages[2:])   # 3 dividers + 20 pairs (orig cover & TOC skipped)
for d in pdf_new:
    out.pages.append(d.pages[0])

# Match new pages' height exactly to the original album (595.9pt crop):
# original A4L pages are 841.89x595.96; new renders are 841.92x595.92.
for i in (0, 1, 2):
    out.pages[i].MediaBox = pikepdf.Array([0, 0.94, 841.92, 595.9])
for i in range(26, 26 + len(PAGES)):
    out.pages[i].MediaBox = pikepdf.Array([0, 0.94, 841.92, 595.9])

with out.open_metadata() as meta:
    meta["dc:title"] = "Toshkent — Kecha va Bugun. Mustaqillikning 35 yilligiga bag'ishlangan ijodiy fotoalbom"
    meta["dc:creator"] = ["Asilbekov Ozodbek"]
    meta["dc:description"] = ("ToshTech ijodiy tanlovi: 37 joyning eski (1865-2010-yillar) va hozirgi suratlari, "
                              "Google Maps koordinatalari bilan")
out.docinfo["/Title"] = "Toshkent — Kecha va Bugun. Mustaqillikning 35 yilligiga bag'ishlangan ijodiy fotoalbom"
out.docinfo["/Author"] = "Asilbekov Ozodbek"
out.docinfo["/Creator"] = "Z.ai"
out.docinfo["/Subject"] = "ToshTech ijodiy tanlovi: 37 joyning eski va hozirgi suratlari, Google Maps koordinatalari bilan"
out.save(OUT)

chk = pikepdf.open(OUT)
print("pages:", len(chk.pages))
print("size:", os.path.getsize(OUT) // (1024 * 1024), "MB")
