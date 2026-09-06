import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS
from test_dynamic_anchors import extract_row_anchors

for p, seat_target in [(2, "101410022"), (7, "101410031"), (28, "101410074"), (36, "101410926")]:
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    sb = [b for b in boxes if seat_target in b["text"]][0]
    s_y = sb["ymin"]
    y_T1, y_O1, y_E1, y_I1, y_TOT = extract_row_anchors(boxes, s_y)
    
    print(f"\n==================== Page {p} Seat {seat_target} (s_y={s_y:.1f}) ====================")
    print(f"Row anchors: T1={y_T1:.1f}, O1={y_O1:.1f}, E1={y_E1:.1f}, I1={y_I1:.1f}, TOT={y_TOT:.1f}")
    m_boxes = [b for b in boxes if 10 < (b["ymin"] - s_y) <= 170]
    m_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
    for b in m_boxes:
        # Determine which row and col this box belongs to
        row_name = "?"
        if abs(b["ymin"] - y_T1) <= 12: row_name = "T1"
        elif abs(b["ymin"] - y_O1) <= 12: row_name = "O1"
        elif abs(b["ymin"] - y_E1) <= 12: row_name = "E1"
        elif abs(b["ymin"] - y_I1) <= 12: row_name = "I1"
        elif abs(b["ymin"] - y_TOT) <= 20: row_name = "TOT"
        
        col_name = "?"
        for s in SUBJECTS:
            if s["x_range"][0] <= b["xmin"] < s["x_range"][1]:
                col_name = s["prefix"]
        if b["xmin"] >= 1900: col_name = "SUMMARY"
        
        print(f"  y={b['ymin']:5.1f} ({row_name:3s}) x={b['xmin']:5.1f} ({col_name:10s}) : '{b['text']}'")
