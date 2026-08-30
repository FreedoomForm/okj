#!/usr/bin/env python3
"""Render key pages of the album PDF to PNG for design reference + extract cover bg image."""
import pypdfium2 as pdfium
import os

PDF = "/home/z/my-project/upload/Toshkent_kecha_va_bugun.pdf"
OUT = "/home/z/my-project/research/orig_pages"
os.makedirs(OUT, exist_ok=True)

pdf = pdfium.PdfDocument(PDF)
for idx in [0, 1, 4]:  # cover, TOC, first pair page
    page = pdf[idx]
    bmp = page.render(scale=1.6)
    img = bmp.to_pil()
    img.save(f"{OUT}/page_{idx+1}.png")
    print(f"page {idx+1}: {img.size}")
pdf.close()
