from pathlib import Path
import pymupdf, json, os, re, sys
from PIL import Image
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
doc = pymupdf.open(ROOT / 'data' / 'raw' / 'AI&DS_SEM4_RESULTS.pdf')
os.makedirs(ROOT / 'scratch' / 'audit_crops', exist_ok=True)

df = pd.read_csv(ROOT / 'data' / 'processed' / 'AI_DS_SEM4_MASTER_RESULTS.csv')

# Let's crop all students who have discrepancies
discrepant_sids = [
    101410022, 101410036, 101410037, 101410039, 101410052, 101410053,
    101410063, 101410079, 101410080, 101410083, 101410085, 101410934,
    101410944, 101410945, 101410946, 101410947, 101410948, 101410952,
    101410953, 101410954
]

for p_idx in range(len(doc)):
    fn = ROOT / 'data' / 'cache' / 'ocr_cache' / f'page_{p_idx:03d}.json'
    if not os.path.exists(fn):
        continue
    with open(fn, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
        
    boxes = cache_data['boxes']
    seat_boxes = [b for b in boxes if re.search(r'\b1014\d{5}\b', b['text'])]
    
    for sb in seat_boxes:
        m = re.search(r'\b1014\d{5}\b', sb['text'])
        if not m:
            continue
        sid = int(m.group(0))
        if sid in discrepant_sids:
            page = doc[p_idx]
            pix = page.get_pixmap(dpi=250)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            scale_y = pix.height / cache_data['height']
            y1 = max(0, int((sb['ymin'] - 40) * scale_y))
            y2 = min(pix.height, int((sb['ymin'] + 175) * scale_y))
            
            crop = img.crop((0, y1, pix.width, y2))
            crop_path = f'scratch/audit_crops/sid_{sid}_page_{p_idx+1}.png'
            crop.save(crop_path)
            print(f"Saved {crop_path} for SID {sid}")
