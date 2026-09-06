import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("ocr_cache/page_003.json", "r", encoding="utf-8") as f:
    data = json.load(f)

boxes = data["boxes"]
# Let's inspect all boxes on page 3
boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
for b in boxes:
    print(f"y=[{b['ymin']:5.1f}-{b['ymax']:5.1f}] x=[{b['xmin']:5.1f}-{b['xmax']:5.1f}] : {b['text']}")
