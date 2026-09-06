import json, glob, re, sys
sys.stdout.reconfigure(encoding="utf-8")

files = sorted(glob.glob("ocr_cache/page_*.json"))
for fpath in files:
    page_num = int(re.search(r"page_(\d+)", fpath).group(1))
    if page_num in [0, 1]:
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    # Find 7 digit codes appearing in the table headers (y between 200 and 850)
    codes_in_page = []
    for b in boxes:
        m = re.findall(r"\b\d{7}\b", b["text"])
        for c in m:
            if b["ymin"] < 850 and c != "1014100":
                codes_in_page.append((b["ymin"], b["xmin"], c))
    codes_in_page.sort(key=lambda x: (x[0]//200, x[1]))
    print(f"Page {page_num:02d}: found {len(codes_in_page)} subject codes -> {[c[2] for c in codes_in_page]}")
