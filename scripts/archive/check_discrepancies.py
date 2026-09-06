import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

SUBJECTS_INFO = [
    {
        "code": "1313311", "prefix": "OE", "name": "Administrative Policy of Chhatrapati Shivaji Maharaja",
        "type": "THEORY", "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "credits": 2,
        "col_x": (50, 225)
    },
    {
        "code": "2014411", "prefix": "MINIPROJ", "name": "Mini Project",
        "type": "TW_ORAL", "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "credits": 2,
        "col_x": (225, 395)
    },
    {
        "code": "2114111", "prefix": "CT", "name": "Computational Theory",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "col_x": (395, 560)
    },
    {
        "code": "2114112", "prefix": "DBMS", "name": "Database Management System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "col_x": (560, 730)
    },
    {
        "code": "2114113", "prefix": "OS", "name": "Operating System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "col_x": (730, 905)
    },
    {
        "code": "2114114", "prefix": "DBMS_LAB", "name": "Database Management System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "col_x": (905, 1075)
    },
    {
        "code": "2114115", "prefix": "OS_LAB", "name": "Operating System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "col_x": (1075, 1245)
    },
    {
        "code": "2304211", "prefix": "FTS", "name": "Fundamentals of Telecommunication Systems",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "col_x": (1245, 1415)
    },
    {
        "code": "2304212", "prefix": "TC_LAB", "name": "Basic Telecommunication Experiments",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "col_x": (1415, 1585)
    },
    {
        "code": "2994511", "prefix": "BMD", "name": "Business Model Development",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "col_x": (1585, 1755)
    },
    {
        "code": "2994512", "prefix": "DT", "name": "Design Thinking",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "col_x": (1755, 1925)
    }
]

def clean_name(raw_text):
    # Remove leading/trailing numbers, status words, gender words
    # Keep only capital words of the student name
    tokens = raw_text.split()
    cleaned = []
    for t in tokens:
        t_clean = re.sub(r"[^A-Za-z]", "", t)
        if t_clean.upper() in ["REGULAR", "REPEATER", "FEMALE", "MALE", "MUMBAI", "COLLEGE"]:
            continue
        if len(t_clean) > 0:
            cleaned.append(t_clean.upper())
    return " ".join(cleaned)

def extract_student_marks(boxes, s_y):
    # Return dictionary of all 11 subjects
    res = {}
    
    # Let's extract marks in specific vertical bands relative to s_y:
    # Band 1: T1 row -> dy in [15, 42]
    # Band 2: O1 row -> dy in [38, 62]
    # Band 3: E1 row -> dy in [58, 85]
    # Band 4: I1 row -> dy in [78, 105]
    # Band 5: TOT & Grade row -> dy in [100, 160]
    
    for subj in SUBJECTS_INFO:
        pfx = subj["prefix"]
        xmin, xmax = subj["col_x"]
        
        # boxes in this column
        s_boxes = [b for b in boxes if xmin - 15 <= b["xmin"] < xmax + 15 and b["ymin"] > s_y + 10]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        
        stype = subj["type"]
        if stype in ["TW_ORAL", "TW_ONLY"]:
            # TW in dy [15, 42]
            tw_cands = [b for b in s_boxes if 15 <= (b["ymin"] - s_y) <= 42]
            for b in tw_cands:
                nums = re.findall(r"\b\d{1,2}\b", b["text"])
                if nums:
                    tw = int(nums[0])
            if stype == "TW_ORAL":
                # Oral in dy [38, 62]
                oral_cands = [b for b in s_boxes if 38 <= (b["ymin"] - s_y) <= 62]
                for b in oral_cands:
                    nums = re.findall(r"\b\d{1,2}\b", b["text"])
                    if nums:
                        oral = int(nums[-1])
        elif stype == "THEORY":
            # Ext in dy [58, 85]
            ext_cands = [b for b in s_boxes if 58 <= (b["ymin"] - s_y) <= 85]
            for b in ext_cands:
                nums = re.findall(r"\b\d{1,2}\b", b["text"])
                if nums:
                    ext = int(nums[-1])
            # Int in dy [78, 105]
            int_cands = [b for b in s_boxes if 78 <= (b["ymin"] - s_y) <= 105]
            for b in int_cands:
                nums = re.findall(r"\b\d{1,2}\b", b["text"])
                if nums:
                    int_m = int(nums[-1])

        # Compute Subject Total
        if stype == "THEORY":
            tot = (ext + int_m) if (ext is not None and int_m is not None) else None
            is_pass = (ext is not None and ext >= subj["min_ext"]) and (int_m is not None and int_m >= subj["min_int"])
        elif stype == "TW_ORAL":
            tot = (tw + oral) if (tw is not None and oral is not None) else None
            is_pass = (tw is not None and tw >= subj["min_tw"]) and (oral is not None and oral >= subj["min_oral"])
        else: # TW_ONLY
            tot = tw if tw is not None else None
            is_pass = (tw is not None and tw >= subj["min_tw"])

        # Determine Grade, GP, GC
        max_tot = subj["max_tot"]
        credits = subj["credits"]
        
        if tot is None or not is_pass:
            grade = "F"
            gp = 0
            gc = 0.0
        else:
            pct = (tot / max_tot) * 100.0
            if pct >= 90.0:
                grade, gp = "O", 10
            elif pct >= 80.0:
                grade, gp = "A+", 9
            elif pct >= 70.0:
                grade, gp = "A", 8
            elif pct >= 60.0:
                grade, gp = "B+", 7
            elif pct >= 55.0:
                grade, gp = "B", 6
            elif pct >= 50.0:
                grade, gp = "C", 5
            elif pct >= 40.0:
                grade, gp = "D", 4
            else:
                grade, gp = "F", 0
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

# Test on 10 random students and check matching with PDF summary
test_students = []
for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        test_students.append((p, sb, boxes))

print(f"Total students found: {len(test_students)}")
discrepancies = 0
for p, sb, boxes in test_students:
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    s_y = sb["ymin"]
    
    # Extract marks
    s_marks = extract_student_marks(boxes, s_y)
    
    # Calculate sum of marks and sum of GC
    calc_tot_marks = sum(s_marks[f"{subj['prefix']}_total"] for subj in SUBJECTS_INFO if s_marks[f"{subj['prefix']}_total"] is not None)
    calc_aCG = sum(s_marks[f"{subj['prefix']}_gc"] for subj in SUBJECTS_INFO)
    has_f = any(s_marks[f"{subj['prefix']}_grade"] == "F" for subj in SUBJECTS_INFO)
    calc_aC = 23 if not has_f else sum(subj["credits"] for subj in SUBJECTS_INFO if s_marks[f"{subj['prefix']}_grade"] != "F")
    calc_sgpi = round(calc_aCG / 23.0, 5) if not has_f else 0.0
    
    # Find PDF summary values for comparison
    sum_boxes = [b for b in boxes if abs(b["ymin"] - (s_y + 80)) < 70 and b["xmin"] >= 1920]
    pdf_tot = None
    pdf_result = "PASS"
    for b in sum_boxes:
        tm = re.search(r"\((\d{2,3})\)", b["text"])
        if tm:
            pdf_tot = int(tm.group(1))
        if any(w in b["text"].upper() for w in ["FAIL", "UNSUCCESSFUL"]):
            pdf_result = "FAIL"
            
    if pdf_tot is not None and pdf_tot != calc_tot_marks:
        discrepancies += 1
        print(f"Discrepancy at Page {p:2d} Seat {seat}: PDF Total={pdf_tot} vs Calc Total={calc_tot_marks} (diff={calc_tot_marks - pdf_tot})")

print(f"Total discrepancies: {discrepancies} / {len(test_students)}")
