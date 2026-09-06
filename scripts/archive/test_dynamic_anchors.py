import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS, parse_num

def extract_row_anchors(boxes, s_y):
    # Column 0 labels or marks on the left (x < 100)
    left_boxes = [b for b in boxes if b["xmin"] < 100 and s_y < b["ymin"] <= s_y + 160]
    left_boxes.sort(key=lambda b: b["ymin"])
    
    y_T1, y_O1, y_E1, y_I1, y_TOT = None, None, None, None, None
    for b in left_boxes:
        t = b["text"]
        dy = b["ymin"] - s_y
        if "T1" in t.upper() or (15 <= dy <= 38 and y_T1 is None):
            y_T1 = b["ymin"]
        elif "O1" in t.upper() or "01" in t or (36 <= dy <= 60 and y_O1 is None):
            y_O1 = b["ymin"]
        elif "E1" in t.upper() or (55 <= dy <= 85 and y_E1 is None):
            y_E1 = b["ymin"]
        elif "I1" in t.upper() or "11" in t or (75 <= dy <= 108 and y_I1 is None):
            y_I1 = b["ymin"]
        elif "TOT" in t.upper() or (105 <= dy <= 145 and y_TOT is None):
            y_TOT = b["ymin"]
            
    # Default fallbacks if any is missing
    if y_E1 is None: y_E1 = s_y + 70
    if y_I1 is None: y_I1 = y_E1 + 24
    if y_T1 is None: y_T1 = y_E1 - 46
    if y_O1 is None: y_O1 = y_E1 - 23
    if y_TOT is None: y_TOT = y_I1 + 24
    
    return y_T1, y_O1, y_E1, y_I1, y_TOT

print("Testing dynamic row anchor detection on page 3 and page 5:")
for p in [3, 5]:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
        anchors = extract_row_anchors(boxes, sb["ymin"])
        print(f"Page {p} Seat {seat} (s_y={sb['ymin']:.1f}): T1={anchors[0]-sb['ymin']:.1f}, O1={anchors[1]-sb['ymin']:.1f}, E1={anchors[2]-sb['ymin']:.1f}, I1={anchors[3]-sb['ymin']:.1f}, TOT={anchors[4]-sb['ymin']:.1f}")
