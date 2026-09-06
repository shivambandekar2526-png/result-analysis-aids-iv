import json, glob, re, sys
sys.stdout.reconfigure(encoding="utf-8")

for p in [17, 18, 20, 22, 25, 27, 30, 31, 35, 36, 44, 46]:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"=== PAGE {p} ===")
    for b in data["boxes"]:
        txt = b["text"]
        if "MU" in txt or "ERN" in txt or "COLLEGE" in txt or re.search(r"\b1014\d{5}\b", txt):
            print(f"  y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] : {txt}")
