import pymupdf, json, os, glob
import pandas as pd
import numpy as np

doc = pymupdf.open('data/raw/AI&DS_SEM4_RESULTS.pdf')
print(f"PDF Page Count: {len(doc)}")

df = pd.read_csv('data/processed/AI_DS_SEM4_MASTER_RESULTS.csv')
print(f"Master Dataset Shape: {df.shape} (Rows: {len(df)}, Columns: {len(df.columns)})")
print(f"Columns: {list(df.columns)}")

# Let's inspect pages 1 and 2 of the PDF for the legend & grading scale
for p in range(min(2, len(doc))):
    with open(f'data/cache/ocr_cache/page_{p:03d}.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"\n--- Page {p+1} Header / Content (Boxes: {len(d['boxes'])}) ---")
    texts = [b['text'] for b in d['boxes']]
    print(" | ".join(texts[:30]))
