import json, re, glob, os

files = sorted(glob.glob("ocr_cache/page_*.json"))
print(f"Available files: {len(files)}")

# Let's inspect subjects and columns on pages 2, 3, 4, 12, 13
for fpath in files:
    page_num = int(re.search(r"page_(\d+)", fpath).group(1))
    if page_num not in [2, 3, 12]:
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n==================== PAGE {page_num} ====================")
    # Print header subjects (usually y between 200 and 450 or 650 and 850)
    for b in data["boxes"]:
        if ("THEORY" in b["text"] or "WORK" in b["text"] or "ORAL" in b["text"]) and b["ymin"] < 900:
            print(f"SubjHeader: y=[{b['ymin']:.0f}-{b['ymax']:.0f}] x=[{b['xmin']:.0f}-{b['xmax']:.0f}] {b['text']}")
