import pymupdf, json, numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
doc = pymupdf.open('AI&DS_SEM4_RESULTS.pdf')

for page_idx in [1]:
    pix = doc[page_idx].get_pixmap(dpi=200)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    res, _ = ocr(np.array(img))

    boxes = []
    for pts, text, conf in res:
        ymin = min(p[1] for p in pts)
        xmin = min(p[0] for p in pts)
        ymax = max(p[1] for p in pts)
        xmax = max(p[0] for p in pts)
        boxes.append({'ymin': ymin, 'xmin': xmin, 'ymax': ymax, 'xmax': xmax, 'text': text, 'conf': conf})

    boxes.sort(key=lambda b: (b['ymin'], b['xmin']))
    print(f"=== PAGE {page_idx} (Total {len(boxes)} boxes) ===")
    for b in boxes:
        print(f"[{b['ymin']:4.0f}, {b['xmin']:4.0f}] {b['text']}")
