import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS, parse_num

with open("ocr_cache/page_003.json", "r", encoding="utf-8") as f:
    data = json.load(f)
boxes = data["boxes"]

for seat_target in ["101410023", "101410024"]:
    sb = [b for b in boxes if seat_target in b["text"]][0]
    s_y = sb["ymin"]
    m_boxes = [b for b in boxes if 10 < (b["ymin"] - s_y) <= 165]
    
    print(f"\n==================== Seat {seat_target} ====================")
    total_sum = 0
    for subj in SUBJECTS:
        pfx = subj["prefix"]
        xmin, xmax = subj["x_range"]
        stype = subj["type"]
        c_boxes = [b for b in m_boxes if xmin <= b["xmin"] < xmax]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        
        # Slot 1: T1 (dy 12..33)
        if stype in ["TW_ORAL", "TW_ONLY"]:
            for b in c_boxes:
                if 12 <= (b["ymin"] - s_y) <= 33:
                    v = parse_num(b["text"])
                    if v is not None and v <= subj["max_tw"]: tw = v
        # Slot 2: O1 (dy 34..55)
        if stype == "TW_ORAL":
            for b in c_boxes:
                if 34 <= (b["ymin"] - s_y) <= 55:
                    v = parse_num(b["text"])
                    if v is not None and v <= subj["max_oral"]: oral = v
        # Slot 3: E1 (dy 56..78)
        if stype == "THEORY":
            for b in c_boxes:
                if 56 <= (b["ymin"] - s_y) <= 78:
                    v = parse_num(b["text"])
                    if v is not None and v <= subj["max_ext"]: ext = v
        # Slot 4: I1 (dy 79..102)
        if stype == "THEORY":
            for b in c_boxes:
                if 79 <= (b["ymin"] - s_y) <= 102:
                    v = parse_num(b["text"])
                    if v is not None and v <= subj["max_int"]: int_m = v
                    
        if stype == "THEORY": tot = (ext + int_m) if (ext is not None and int_m is not None) else None
        elif stype == "TW_ORAL": tot = (tw + oral) if (tw is not None and oral is not None) else None
        else: tot = tw
        
        if tot is not None: total_sum += tot
        print(f"  {pfx:10s} -> Ext={ext} Int={int_m} TW={tw} Oral={oral} => Tot={tot}")
        
    print(f"Total calculated: {total_sum}")
