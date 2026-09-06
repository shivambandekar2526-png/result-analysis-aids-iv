import sys, os, json, re
sys.stdout.reconfigure(encoding="utf-8")

files = [f for f in os.listdir("ocr_cache") if f.endswith(".json")]
print(f"Total cached pages: {len(files)}/47")

for p_idx in [2, 12]:
    fn = f"ocr_cache/page_{p_idx:03d}.json"
    if not os.path.exists(fn):
        continue
    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"=== PAGE {p_idx} ===")
    for b in data["boxes"]:
        if re.search(r"\b1014\d{5}\b", b["text"]):
            print(f"Seat No box: y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] text='{b['text']}'")
        if "MU0" in b["text"] or "ERN" in b["text"] or re.search(r"\(MU\d+\)", b["text"]):
            print(f"ERN box: y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] text='{b['text']}'")
        if any(w in b["text"] for w in ["SUCCESSFUL", "FAILED", "MARKS", "PASSED", "UNSUCCESSFUL"]):
            print(f"Result box: y=[{b['ymin']:.1f}-{b['ymax']:.1f}] x=[{b['xmin']:.1f}-{b['xmax']:.1f}] text='{b['text']}'")
