#!/usr/bin/env python3
"""Merge competition cover + author's word + original album pages (2..25) — pikepdf version."""
import pikepdf, os

SRC = "/home/z/my-project/upload/Toshkent_kecha_va_bugun.pdf"
COVER = "/home/z/my-project/download/tashkent-album-src/muqova_tanlov.pdf"
STATE = "/home/z/my-project/download/tashkent-album-src/muallif_suzi.pdf"
OUT = "/home/z/my-project/download/Toshkent_kecha_va_bugun_TANLOV.pdf"

out = pikepdf.new()
pdf_cover = pikepdf.open(COVER)
pdf_state = pikepdf.open(STATE)
pdf_orig = pikepdf.open(SRC)
out.pages.append(pdf_cover.pages[0])
out.pages.append(pdf_state.pages[0])
out.pages.extend(pdf_orig.pages[1:])

# Match page height exactly to the original album (594.96pt): trim 0.94pt at
# the bottom of the two new pages (blank cream margin — visually invisible).
import pikepdf as _pk
for i in (0, 1):
    out.pages[i].MediaBox = _pk.Array([0, 0.94, 841.92, 595.9])

with out.open_metadata() as meta:
    meta["dc:title"] = "Toshkent — Kecha va Bugun. Mustaqillikning 35 yilligiga bag'ishlangan ijodiy fotoalbom"
    meta["dc:creator"] = ["Asilbekov Ozodbek"]
    meta["dc:description"] = "ToshTech ijodiy tanlovi: 20 joyning eski (1900-2000) va hozirgi suratlari, Google Maps koordinatalari bilan"
out.docinfo["/Title"] = "Toshkent — Kecha va Bugun. Mustaqillikning 35 yilligiga bag'ishlangan ijodiy fotoalbom"
out.docinfo["/Author"] = "Asilbekov Ozodbek"
out.docinfo["/Creator"] = "Z.ai"
out.docinfo["/Subject"] = "ToshTech ijodiy tanlovi: 20 joyning eski va hozirgi suratlari, Google Maps koordinatalari bilan"
out.save(OUT)
print("pages:", len(pikepdf.open(OUT).pages))
print("size:", os.path.getsize(OUT) // 1024, "KB")
