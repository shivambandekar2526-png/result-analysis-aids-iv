import json, re, glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")

# Define the 11 column x-intervals on 2200-width image:
# Column 0: Subject 1 (1313311 - OE) -> x approx [50, 225]
# Column 1: Subject 2 (2014411 - Mini Project) -> x approx [225, 395]
# Column 2: Subject 3 (2114111 - CT) -> x approx [395, 560]
# Column 3: Subject 4 (2114112 - DBMS) -> x approx [560, 730]
# Column 4: Subject 5 (2114113 - OS) -> x approx [730, 905]
# Column 5: Subject 6 (2114114 - DBMS Lab) -> x approx [905, 1075]
# Column 6: Subject 7 (2114115 - OS Lab) -> x approx [1075, 1245]
# Column 7: Subject 8 (2304211 - FTS) -> x approx [1245, 1415]
# Column 8: Subject 9 (2304212 - TC Lab) -> x approx [1415, 1585]
# Column 9: Subject 10 (2994511 - BMD) -> x approx [1585, 1755]
# Column 10: Subject 11 (2994512 - DT) -> x approx [1755, 1925]
# Summary Column: x approx [1925, 2200]

COL_BOUNDS = [
    (50, 225),
    (225, 395),
    (395, 560),
    (560, 730),
    (730, 905),
    (905, 1075),
    (1075, 1245),
    (1245, 1415),
    (1415, 1585),
    (1585, 1755),
    (1755, 1925)
]

SUBJ_PREFIXES = [
    "OE_1313311",
    "MINIPROJ_2014411",
    "CT_2114111",
    "DBMS_2114112",
    "OS_2114113",
    "DBMS_LAB_2114114",
    "OS_LAB_2114115",
    "FTS_2304211",
    "TC_LAB_2304212",
    "BMD_2994511",
    "DT_2994512"
]

def test_parse_student(page_idx, student_idx=0):
    with open(f"ocr_cache/page_{page_idx:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    
    sb = seat_boxes[student_idx]
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    s_y = sb["ymin"]
    
    # y ranges for marks
    # Metadata row is at s_y (e.g. y=500 or y=900)
    # Marks rows are below s_y, up to s_y + 150
    m_boxes = [b for b in boxes if s_y < b["ymin"] <= s_y + 160]
    m_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
    
    print(f"=== Page {page_idx} Student {student_idx+1}: Seat {seat} (y={s_y:.1f}) ===")
    for b in m_boxes:
        print(f"  y=[{b['ymin']:5.1f}-{b['ymax']:5.1f}] x=[{b['xmin']:5.1f}-{b['xmax']:5.1f}] {b['text']}")

test_parse_student(3, 0)
test_parse_student(3, 1)
test_parse_student(12, 1)
