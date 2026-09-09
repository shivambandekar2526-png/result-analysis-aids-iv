from pathlib import Path
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / 'data' / 'cache' / 'ocr_cache' / 'page_001.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for b in d['boxes']:
    print(f"y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] : {b['text']}")
