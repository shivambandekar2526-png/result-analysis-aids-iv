import pymupdf
from PIL import Image
import os, json, re

doc = pymupdf.open('data/raw/AI&DS_SEM4_RESULTS.pdf')
os.makedirs('scratch/student_crops', exist_ok=True)

sids = [101410043, 101410080, 101410926, 101410928, 101410946, 101410947, 101410952, 101410953, 101410954]

for p_idx in range(len(doc)):
    fn = f'data/cache/ocr_cache/page_{p_idx:03d}.json'
    with open(fn, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    boxes = cache_data['boxes']
    seat_boxes = [b for b in boxes if re.search(r'\b1014\d{5}\b', b['text'])]
    
    for sb in seat_boxes:
        m = re.search(r'\b1014\d{5}\b', sb['text'])
        if not m:
            continue
        sid = int(m.group(0))
        if sid in sids:
            page = doc[p_idx]
            pix = page.get_pixmap(dpi=250)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            scale_y = pix.height / cache_data['height']
            
            # Crop the entire student section: from seat_y - 40 to seat_y + 160 (scaled)
            y1 = max(0, int((sb['ymin'] - 40) * scale_y))
            y2 = min(pix.height, int((sb['ymin'] + 170) * scale_y))
            
            crop = img.crop((0, y1, pix.width, y2))
            crop_path = f'scratch/student_crops/sid_{sid}_page_{p_idx+1}.png'
            crop.save(crop_path)
            print(f"Saved {crop_path}")
