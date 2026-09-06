import sys, os, json, pymupdf, numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

def process_range(start_idx, end_idx):
    os.makedirs("ocr_cache", exist_ok=True)
    ocr = RapidOCR()
    doc = pymupdf.open("AI&DS_SEM4_RESULTS.pdf")
    
    for page_idx in range(start_idx, min(end_idx, len(doc))):
        out_file = os.path.join("ocr_cache", f"page_{page_idx:03d}.json")
        if os.path.exists(out_file):
            print(f"[Worker {start_idx}-{end_idx}] Page {page_idx} already exists, skipping.", flush=True)
            continue
            
        page = doc[page_idx]
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
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
                    "ymin": round(float(ymin), 2),
                    "xmin": round(float(xmin), 2),
                    "ymax": round(float(ymax), 2),
                    "xmax": round(float(xmax), 2),
                    "text": str(text).strip(),
                    "conf": round(float(conf), 4)
                })
        
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "page_idx": page_idx,
                "width": pix.width,
                "height": pix.height,
                "boxes": boxes
            }, f, ensure_ascii=False, indent=2)
            
        print(f"[Worker {start_idx}-{end_idx}] Done page {page_idx} ({len(boxes)} boxes)", flush=True)

if __name__ == "__main__":
    s = int(sys.argv[1])
    e = int(sys.argv[2])
    process_range(s, e)
