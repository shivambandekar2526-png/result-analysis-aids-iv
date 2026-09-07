import sys, os, re, json
import fitz # PyMuPDF
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

missing_ids = [101410023, 101410033, 101410034, 101410047, 101410048, 101410052, 101410053, 101410057, 101410061, 101410062, 101410067, 101410068, 101410071, 101410072, 101410078, 101410080, 101410088, 101410927, 101410949, 101410954]

ocr = RapidOCR()
doc = fitz.open('data/raw/AI&DS_SEM4_RESULTS.pdf')

results = {}

for p_idx in range(len(doc)):
    fn = f'data/cache/ocr_cache/page_{p_idx:03d}.json'
    with open(fn, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    boxes = cache_data['boxes']
    seat_boxes = [b for b in boxes if re.search(r'\b1014\d{5}\b', b['text'])]
    
    # Check if any missing id is on this page
    sids_on_page = []
    for sb in seat_boxes:
        m = re.search(r'\b1014\d{5}\b', sb['text'])
        if m:
            sid = int(m.group(0))
            if sid in missing_ids:
                sids_on_page.append((sid, sb))
                
    if not sids_on_page:
        continue
        
    page = doc[p_idx]
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    
    # ratio between 300 dpi and cache coordinates (cache was at 200 dpi)
    scale_x = pix.width / cache_data['width']
    scale_y = pix.height / cache_data['height']
    
    for sid, sb in sids_on_page:
        # Define crop region for the metadata line
        # The ERN and College are to the right of student name and gender
        # Let's crop y from sb['ymin'] - 20 to sb['ymin'] + 50 (scaled)
        # and x from sb['xmin'] to full width
        ymin = max(0, int((sb['ymin'] - 30) * scale_y))
        ymax = min(pix.height, int((sb['ymin'] + 50) * scale_y))
        xmin = max(0, int(300 * scale_x))
        xmax = pix.width
        
        crop = img.crop((xmin, ymin, xmax, ymax))
        res, _ = ocr(np.array(crop))
        
        extracted_text = " ".join([item[1] for item in res]) if res else ""
        print(f"Page {p_idx+1}: SID {sid}")
        print(f"   Raw OCR: {extracted_text}")
        
        # Also try wider y crop if nothing or no ERN found
        ern = None
        # Look for MU pattern: MU followed by digits / O / o
        em = re.search(r'\(?(MU[0-9OIl]{12,20})\)?', extracted_text, re.IGNORECASE)
        if em:
            raw_ern = em.group(1).upper().replace('O', '0').replace('I', '1').replace('L', '1')
            ern = raw_ern
        else:
            # Let's do a wider crop: [ymin - 40, ymax + 40]
            ymin_w = max(0, int((sb['ymin'] - 60) * scale_y))
            ymax_w = min(pix.height, int((sb['ymin'] + 80) * scale_y))
            crop_w = img.crop((0, ymin_w, pix.width, ymax_w))
            res_w, _ = ocr(np.array(crop_w))
            extracted_text_w = " ".join([item[1] for item in res_w]) if res_w else ""
            em_w = re.search(r'\(?(MU[0-9OIl]{12,20})\)?', extracted_text_w, re.IGNORECASE)
            if em_w:
                raw_ern = em_w.group(1).upper().replace('O', '0').replace('I', '1').replace('L', '1')
                ern = raw_ern
            else:
                # search for any 16-digit number starting with 202
                em_num = re.search(r'\b(202\d{13})\b', extracted_text_w)
                if em_num:
                    ern = "MU" + em_num.group(1)
                else:
                    print(f"   Wider OCR: {extracted_text_w}")
                    
        results[sid] = ern
        print(f"   -> Extracted ERN: {ern}\n")

print("=== FINAL SUMMARY OF EXTRACTED ERNs ===")
for sid in missing_ids:
    print(f"SID {sid}: {results.get(sid)}")
