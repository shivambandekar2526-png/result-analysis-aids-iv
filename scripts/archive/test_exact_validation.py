import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

SUBJECTS = [
    {
        "code": "1313311", "prefix": "OE", "name": "Administrative Policy of Chhatrapati Shivaji Maharaja",
        "type": "THEORY", "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "credits": 2,
        "x_range": (0, 190)
    },
    {
        "code": "2014411", "prefix": "MINIPROJ", "name": "Mini Project",
        "type": "TW_ORAL", "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "credits": 2,
        "x_range": (190, 360)
    },
    {
        "code": "2114111", "prefix": "CT", "name": "Computational Theory",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_range": (360, 530)
    },
    {
        "code": "2114112", "prefix": "DBMS", "name": "Database Management System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_range": (530, 700)
    },
    {
        "code": "2114113", "prefix": "OS", "name": "Operating System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_range": (700, 875)
    },
    {
        "code": "2114114", "prefix": "DBMS_LAB", "name": "Database Management System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_range": (875, 1045)
    },
    {
        "code": "2114115", "prefix": "OS_LAB", "name": "Operating System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_range": (1045, 1215)
    },
    {
        "code": "2304211", "prefix": "FTS", "name": "Fundamentals of Telecommunication Systems",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_range": (1215, 1385)
    },
    {
        "code": "2304212", "prefix": "TC_LAB", "name": "Basic Telecommunication Experiments",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_range": (1385, 1555)
    },
    {
        "code": "2994511", "prefix": "BMD", "name": "Business Model Development",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "x_range": (1555, 1725)
    },
    {
        "code": "2994512", "prefix": "DT", "name": "Design Thinking",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "x_range": (1725, 1900)
    }
]

def extract_mark_number(text, prefix_to_strip=""):
    # Clean OCR string and extract numeric value or ABS/NULL
    t = text.strip()
    if "ABS" in t.upper() or "AA" in t.upper():
        return 0 # or None with absent flag
    # Find all integers
    nums = re.findall(r"\b\d+\b", t)
    if nums:
        # If prefix was stripped (like E1, I1, T1, O1), take the number
        return int(nums[-1])
    return None

def extract_student_all(boxes, s_y):
    res = {}
    for subj in SUBJECTS:
        pfx = subj["prefix"]
        xmin, xmax = subj["x_range"]
        stype = subj["type"]
        
        c_boxes = [b for b in boxes if xmin <= b["xmin"] < xmax and b["ymin"] > s_y + 10]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        
        if stype in ["TW_ORAL", "TW_ONLY"]:
            # T1: dy in [15, 42]
            tw_boxes = [b for b in c_boxes if 15 <= (b["ymin"] - s_y) <= 42]
            for b in tw_boxes:
                val = extract_mark_number(b["text"])
                if val is not None and val <= subj["max_tw"]:
                    tw = val
            if stype == "TW_ORAL":
                # O1: dy in [38, 62]
                oral_boxes = [b for b in c_boxes if 38 <= (b["ymin"] - s_y) <= 62]
                for b in oral_boxes:
                    val = extract_mark_number(b["text"])
                    if val is not None and val <= subj["max_oral"]:
                        oral = val
        elif stype == "THEORY":
            # E1: dy in [55, 82]
            ext_boxes = [b for b in c_boxes if 55 <= (b["ymin"] - s_y) <= 82]
            for b in ext_boxes:
                val = extract_mark_number(b["text"])
                if val is not None and val <= subj["max_ext"]:
                    ext = val
            # I1: dy in [78, 106]
            int_boxes = [b for b in c_boxes if 78 <= (b["ymin"] - s_y) <= 106]
            for b in int_boxes:
                val = extract_mark_number(b["text"])
                if val is not None and val <= subj["max_int"]:
                    int_m = val

        # Calculate totals
        if stype == "THEORY":
            tot = (ext + int_m) if (ext is not None and int_m is not None) else None
            is_pass = (ext is not None and ext >= subj["min_ext"]) and (int_m is not None and int_m >= subj["min_int"])
        elif stype == "TW_ORAL":
            tot = (tw + oral) if (tw is not None and oral is not None) else None
            is_pass = (tw is not None and tw >= subj["min_tw"]) and (oral is not None and oral >= subj["min_oral"])
        else:
            tot = tw if tw is not None else None
            is_pass = (tw is not None and tw >= subj["min_tw"])

        max_tot = subj["max_tot"]
        credits = subj["credits"]
        
        if tot is None or not is_pass:
            grade = "F"
            gp = 0
            gc = 0.0
        else:
            pct = (tot / max_tot) * 100.0
            if pct >= 90.0: grade, gp = "O", 10
            elif pct >= 80.0: grade, gp = "A+", 9
            elif pct >= 70.0: grade, gp = "A", 8
            elif pct >= 60.0: grade, gp = "B+", 7
            elif pct >= 55.0: grade, gp = "B", 6
            elif pct >= 50.0: grade, gp = "C", 5
            elif pct >= 40.0: grade, gp = "D", 4
            else: grade, gp = "F", 0
            gc = float(gp * credits)

        res[f"{pfx}_code"] = subj["code"]
        res[f"{pfx}_name"] = subj["name"]
        if stype == "THEORY":
            res[f"{pfx}_external"] = ext
            res[f"{pfx}_internal"] = int_m
        elif stype == "TW_ORAL":
            res[f"{pfx}_term_work"] = tw
            res[f"{pfx}_oral"] = oral
        elif stype == "TW_ONLY":
            res[f"{pfx}_term_work"] = tw
        res[f"{pfx}_total"] = tot
        res[f"{pfx}_grade"] = grade
        res[f"{pfx}_gp"] = gp
        res[f"{pfx}_credits"] = credits
        res[f"{pfx}_gc"] = gc
        
    return res

# Now run validation on all 88 students!
total_checked = 0
perfect_matches = 0
discrepancies = []

for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    
    for sb in seat_boxes:
        seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
        s_y = sb["ymin"]
        total_checked += 1
        
        s_marks = extract_student_all(boxes, s_y)
        calc_tot = sum(s_marks[f"{s['prefix']}_total"] for s in SUBJECTS if s_marks[f"{s['prefix']}_total"] is not None)
        
        # Look for PDF total marks in summary column
        sum_boxes = [b for b in boxes if abs(b["ymin"] - (s_y + 80)) < 70 and b["xmin"] >= 1900]
        pdf_tot = None
        for b in sum_boxes:
            tm = re.search(r"\((\d{2,3})\)", b["text"])
            if tm:
                pdf_tot = int(tm.group(1))
                
        if pdf_tot is not None:
            if pdf_tot == calc_tot:
                perfect_matches += 1
            else:
                discrepancies.append((p, seat, pdf_tot, calc_tot, pdf_tot - calc_tot))

print(f"Validation summary: {perfect_matches} / {total_checked} EXACT total matches!")
if discrepancies:
    print(f"Remaining discrepancies: {len(discrepancies)}")
    for d in discrepancies[:20]:
        print(f"  Page {d[0]:2d} Seat {d[1]}: PDF={d[2]} Calc={d[3]} (diff={d[4]})")
