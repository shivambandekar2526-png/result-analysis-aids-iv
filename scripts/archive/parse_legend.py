import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

def extract_legend():
    subjects = {}
    for p in [0, 1]:
        with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        boxes = data["boxes"]
        boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
        
        # Look for subject patterns: (code): code: name or 7-digit numbers
        # Let's inspect all lines
        for b in boxes:
            txt = b["text"]
            # e.g. (1051312):1051312 :Logic and Data Interpretation-1(0E)
            # or (1081313) : 1081313 : Introduction to Business Statistics-l
            m = re.search(r"\(?(\d{7})\)?\s*:\s*\d{7}\s*:\s*(.+)", txt)
            if m:
                code, name = m.group(1), m.group(2).strip()
                subjects[code] = name
            elif re.match(r"^\d{7}$", txt):
                code = txt
                # find closest text to the right on similar y
                y = b["ymin"]
                cands = [b2 for b2 in boxes if abs(b2["ymin"] - y) < 15 and b2["xmin"] > b["xmax"]]
                cands.sort(key=lambda x: x["xmin"])
                if cands:
                    name = cands[0]["text"].strip()
                    if len(name) > 3 and not re.match(r"^[\d\.\s]+$", name):
                        if code not in subjects or len(name) > len(subjects[code]):
                            subjects[code] = name

    print(f"Total distinct subjects in legend: {len(subjects)}")
    for c, n in sorted(subjects.items()):
        print(f"  Code: {c} -> {n}")

extract_legend()
