import os, sys, json, pymupdf, numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from concurrent.futures import ProcessPoolExecutor

PDF_PATH = r'AI&DS_SEM4_RESULTS.pdf'
CACHE_DIR = r'ocr_cache'

def ocr_page(page_idx):
    ocr = RapidOCR()
    doc = pymupdf.open(PDF_PATH)
    page = doc[page_idx]
    pix = page.get_pixmap(dpi=200)
    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    res, _ = ocr(np.array(img))
    
    boxes = []
    if res:
        for item in res:
            pts, text, conf = item
            ymin = min(p[1] for p in pts)
            xmin = min(p[0] for p in pts)
            ymax = max(p[1] for p in pts)
            xmax = max(p[0] for p in pts)
            boxes.append({
                'ymin': round(ymin, 2),
                'xmin': round(xmin, 2),
                'ymax': round(ymax, 2),
                'xmax': round(xmax, 2),
                'text': text.strip(),
                'conf': round(conf, 4)
            })
    return page_idx, pix.width, pix.height, boxes

def run_all(max_pages=None, workers=10):
    os.makedirs(CACHE_DIR, exist_ok=True)
    doc = pymupdf.open(PDF_PATH)
    total_pages = len(doc)
    doc.close()
    
    pages_to_do = list(range(total_pages if max_pages is None else min(max_pages, total_pages)))
    print(f'Starting parallel OCR for {len(pages_to_do)} pages with {workers} workers...', flush=True)
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for page_idx, width, height, boxes in executor.map(ocr_page, pages_to_do):
            cache_file = os.path.join(CACHE_DIR, f'page_{page_idx:03d}.json')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'page_idx': page_idx,
                    'width': width,
                    'height': height,
                    'boxes': boxes
                }, f, ensure_ascii=False, indent=2)
            print(f'Finished page {page_idx+1}/{total_pages} ({len(boxes)} boxes)', flush=True)

if __name__ == '__main__':
    max_p = int(sys.argv[1]) if len(sys.argv) > 1 else None
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run_all(max_pages=max_p, workers=w)
