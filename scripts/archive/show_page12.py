import sys, json
sys.stdout.reconfigure(encoding="utf-8")

with open("ocr_cache/page_012.json", "r", encoding="utf-8") as f:
    data = json.load(f)

boxes = data["boxes"]
boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
print(f"Page 12 (width={data['width']}, height={data['height']}, total boxes={len(boxes)}):")
for b in boxes:
    print(f"[{b['ymin']:6.1f}, {b['xmin']:6.1f}, {b['ymax']:6.1f}, {b['xmax']:6.1f}] conf={b['conf']:0.2f} : {b['text']}")
