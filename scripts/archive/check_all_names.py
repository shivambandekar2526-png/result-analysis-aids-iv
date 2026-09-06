import json, re, glob, os, sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

STOP_WORDS = {
    "REGULAR", "REPEATER", "FEMALE", "MALE", "MUMBAI", "COLLEGE", "SEAT", "NO", "NAME", "STATUS", "GENDER", "ERN",
    "TOT", "GP", "GC", "C", "G", "CREDIT", "CREDITS", "GRADE", "POINTS", "MARKS", "SUM", "SGPI", "RESULT", "REMARK",
    "THEORY", "TERMWORK", "ORAL", "INTERNAL", "EXTERNAL"
}

def clean_student_name(boxes, s_y):
    # Only boxes strictly in y [s_y - 10, s_y + 12] and x [180, 560]
    name_boxes = [b for b in boxes if abs(b["ymin"] - s_y) <= 12 and 180 <= b["xmin"] <= 560]
    name_boxes.sort(key=lambda x: x["xmin"])
    
    parts = []
    for b in name_boxes:
        words = re.findall(r"[A-Za-z]+", b["text"])
        for w in words:
            wu = w.upper()
            if wu not in STOP_WORDS and len(wu) > 1:
                parts.append(wu)
    return " ".join(parts)

all_names = []
for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
        cname = clean_student_name(boxes, sb["ymin"])
        all_names.append((p, seat, cname))

print(f"Total students: {len(all_names)}")
for p, s, n in all_names:
    print(f"Page {p:2d} | Seat: {s} | Name: '{n}'")
