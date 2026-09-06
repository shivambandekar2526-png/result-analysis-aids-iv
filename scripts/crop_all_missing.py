import sys, os, re, json
import pymupdf
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR

sys.stdout.reconfigure(encoding='utf-8')

ocr = RapidOCR()
doc = pymupdf.open('data/raw/AI&DS_SEM4_RESULTS.pdf')
os.makedirs('scratch/ern_crops', exist_ok=True)

missing_ids = [101410023, 101410033, 101410034, 101410047, 101410048, 101410052, 101410053, 101410057, 101410061, 101410062, 101410067, 101410068, 101410071, 101410072, 101410078, 101410080, 101410088, 101410927, 101410949, 101410954]

# For each missing student, find their page and bounding box
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
        if sid in missing_ids:
            page = doc[p_idx]
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            
            scale_y = pix.height / cache_data['height']
            scale_x = pix.width / cache_data['width']
            
            # y of student header: in cache coordinates it's sb['ymin']
            # crop the header band across the whole page width
            y_center = int(sb['ymin'] * scale_y)
            y1 = max(0, y_center - int(30 * scale_y))
            y2 = min(pix.height, y_center + int(50 * scale_y))
            
            # Let's crop from 30% width to 100% width where ERN and College are
            x1 = int(0.28 * pix.width)
            x2 = int(0.99 * pix.width)
            
            crop = img.crop((x1, y1, x2, y2))
            crop_path = f'scratch/ern_crops/sid_{sid}_page_{p_idx+1}.png'
            crop.save(crop_path)
            
            # Run OCR on this crop
            res, _ = ocr(np.array(crop))
            texts = [item[1] for item in res] if res else []
            full_txt = " | ".join(texts)
            
            print(f"=== SID {sid} (Page {p_idx+1}, y={y_center}) ===")
            print(f"  Crop saved: {crop_path}")
            print(f"  OCR: {full_txt}")
