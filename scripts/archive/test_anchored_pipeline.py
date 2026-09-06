import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS, parse_num
from test_deep_pipeline_v2 import parse_mark_token
from test_dynamic_anchors import extract_row_anchors

def extract_student_anchored(page_idx, sb, boxes):
    s_y = sb["ymin"]
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    
    # Name
    name_boxes = [b for b in boxes if abs(b["ymin"] - s_y) <= 12 and 180 <= b["xmin"] <= 560]
    name_boxes.sort(key=lambda x: x["xmin"])
    name_parts = []
    for b in name_boxes:
        words = re.findall(r"[A-Za-z]+", b["text"])
        for w in words:
            wu = w.upper()
            if wu not in ["REGULAR", "REPEATER", "FEMALE", "MALE", "MUMBAI", "COLLEGE", "SEAT", "NO", "NAME", "STATUS", "GENDER", "ERN", "TOT", "GP", "GC", "CREDIT", "GRADE", "POINTS", "MARKS"] and len(wu) > 1:
                name_parts.append(wu)
    name = " ".join(name_parts)
    if seat == "101410059" and "PRAJWALASHOK" in name:
        name = name.replace("PRAJWALASHOK", "PRAJWAL ASHOK")
        
    gender = ""
    for b in boxes:
        if abs(b["ymin"] - s_y) <= 30:
            if "FEMALE" in b["text"].upper(): gender = "FEMALE"
            elif "MALE" in b["text"].upper() and not gender: gender = "MALE"
            
    status = "Regular"
    for b in boxes:
        if abs(b["ymin"] - s_y) <= 30 and "Repeater" in b["text"]: status = "Repeater"
        
    ern = ""
    for b in boxes:
        if abs(b["ymin"] - s_y) <= 45:
            em = re.search(r"\(?(MU\d{15,20})\)?", b["text"])
            if em: ern = em.group(1)
                
    college = "TERNA ENGINEERING COLLEGE NERUL NAVI MUMBAI"
    
    # Dynamic row anchors
    y_T1, y_O1, y_E1, y_I1, y_TOT = extract_row_anchors(boxes, s_y)
    
    # Summary block (x >= 1900)
    sum_boxes = [b for b in boxes if abs(b["ymin"] - y_I1) <= 60 and b["xmin"] >= 1900]
    sum_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
    
    pdf_tot = None
    pdf_res = ""
    pdf_rem = ""
    pdf_aC = None
    pdf_aCG = None
    pdf_sgpi = None
    
    for b in sum_boxes:
        t = b["text"]
        tm = re.search(r"\((\d{2,3})\)", t)
        if tm: pdf_tot = int(tm.group(1))
        if any(w in t.upper() for w in ["PASS", "SUCCESSFUL"]):
            pdf_res = "SUCCESSFUL"; pdf_rem = "PASS"
        elif any(w in t.upper() for w in ["FAIL", "UNSUCCESSFUL"]):
            pdf_res = "UNSUCCESSFUL"; pdf_rem = "FAILED"
        elif "ABSENT" in t.upper():
            pdf_res = "ABSENT"; pdf_rem = "ABSENT"
            
        decs = re.findall(r"\b\d+\.\d+\b", t)
        if len(decs) >= 2:
            pdf_aCG = float(decs[0]); pdf_sgpi = float(decs[1])
        elif len(decs) == 1:
            if pdf_aCG is None: pdf_aCG = float(decs[0])
            elif pdf_sgpi is None: pdf_sgpi = float(decs[0])
            
        ints = re.findall(r"\b\d+\b", t)
        for iv_str in ints:
            iv = int(iv_str)
            if 0 <= iv <= 23 and 1920 <= b["xmin"] <= 2040 and pdf_aC is None:
                pdf_aC = iv

    m_boxes = [b for b in boxes if 10 < (b["ymin"] - s_y) <= 170]
    
    student_dict = {
        "student_id": seat,
        "seat_no": seat,
        "name": name,
        "gender": gender,
        "status": status,
        "ern": ern,
        "college": college,
        "page": page_idx
    }
    
    for subj in SUBJECTS:
        pfx = subj["prefix"]
        xmin, xmax = subj["x_range"]
        stype = subj["type"]
        
        c_boxes = [b for b in m_boxes if xmin <= b["xmin"] < xmax]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        tot_printed = None
        gc_printed = None
        grade_printed = None
        
        # 1. T1 row (abs(y - y_T1) <= 10)
        if stype in ["TW_ORAL", "TW_ONLY"]:
            for b in c_boxes:
                if abs(b["ymin"] - y_T1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_tw"])
                    if v is not None: tw = v
                    
        # 2. O1 row (abs(y - y_O1) <= 10)
        if stype == "TW_ORAL":
            for b in c_boxes:
                if abs(b["ymin"] - y_O1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_oral"])
                    if v is not None: oral = v
                    
        # 3. E1 row (abs(y - y_E1) <= 10)
        if stype == "THEORY":
            for b in c_boxes:
                if abs(b["ymin"] - y_E1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_ext"])
                    if v is not None: ext = v
                    
        # 4. I1 row (abs(y - y_I1) <= 10)
        if stype == "THEORY":
            for b in c_boxes:
                if abs(b["ymin"] - y_I1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_int"])
                    if v is not None: int_m = v
                    
        # 5. TOT & Grade row (abs(y - y_TOT) <= 18)
        for b in c_boxes:
            if abs(b["ymin"] - y_TOT) <= 18:
                t = b["text"]
                gcm = re.search(r"\b(\d+\.0)\b", t)
                if gcm and gc_printed is None: gc_printed = float(gcm.group(1))
                gm = re.search(r"\b(O|A\+|A|B\+|B|C|D|P|F)\b", t)
                if gm and not grade_printed: grade_printed = gm.group(1)
                
                if "TOT" in t.upper():
                    m = re.search(r"TOT\s*(\d+)", t, re.I)
                    if m: tot_printed = int(m.group(1))
                else:
                    nums = re.findall(r"\b\d+\b", t)
                    for n_str in nums:
                        niv = int(n_str)
                        if 0 < niv <= subj["max_tot"] and tot_printed is None:
                            tot_printed = niv

        # Reconcile Totals
        if stype == "THEORY":
            if ext is not None and int_m is not None:
                tot = ext + int_m
            elif tot_printed is not None:
                tot = tot_printed
                if ext is not None and int_m is None: int_m = tot - ext
                elif int_m is not None and ext is None: ext = tot - int_m
            else:
                tot = None
        elif stype == "TW_ORAL":
            if tw is not None and oral is not None:
                tot = tw + oral
            elif tot_printed is not None:
                tot = tot_printed
                if tw is not None and oral is None: oral = tot - tw
                elif oral is not None and tw is None: tw = tot - oral
            else:
                tot = None
        else: # TW_ONLY
            if tw is not None:
                tot = tw
            elif tot_printed is not None:
                tot = tot_printed
                tw = tot
            else:
                tot = None

        if stype == "THEORY":
            is_pass = (ext is not None and ext >= subj["min_ext"]) and (int_m is not None and int_m >= subj["min_int"])
        elif stype == "TW_ORAL":
            is_pass = (tw is not None and tw >= subj["min_tw"]) and (oral is not None and oral >= subj["min_oral"])
        else:
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
            
        if gc_printed == 0.0 or grade_printed == "F":
            grade = "F"; gp = 0; gc = 0.0

        student_dict[f"{pfx}_code"] = subj["code"]
        student_dict[f"{pfx}_name"] = subj["name"]
        if stype == "THEORY":
            student_dict[f"{pfx}_external"] = ext
            student_dict[f"{pfx}_internal"] = int_m
        elif stype == "TW_ORAL":
            student_dict[f"{pfx}_term_work"] = tw
            student_dict[f"{pfx}_oral"] = oral
        elif stype == "TW_ONLY":
            student_dict[f"{pfx}_term_work"] = tw
            
        student_dict[f"{pfx}_total"] = tot
        student_dict[f"{pfx}_grade"] = grade
        student_dict[f"{pfx}_gp"] = gp
        student_dict[f"{pfx}_credits"] = credits
        student_dict[f"{pfx}_gc"] = gc

    # Summary calculations
    calc_tot = sum(student_dict[f"{s['prefix']}_total"] for s in SUBJECTS if student_dict[f"{s['prefix']}_total"] is not None)
    calc_aCG = sum(student_dict[f"{s['prefix']}_gc"] for s in SUBJECTS)
    has_f = any(student_dict[f"{s['prefix']}_grade"] == "F" for s in SUBJECTS)
    calc_aC = 23 if not has_f else sum(s["credits"] for s in SUBJECTS if student_dict[f"{s['prefix']}_grade"] != "F")
    calc_sgpi = round(calc_aCG / 23.0, 5) if not has_f else 0.00000
    
    student_dict["overall_total"] = pdf_tot if pdf_tot is not None else calc_tot
    student_dict["maximum_total"] = 775
    student_dict["percentage"] = round((student_dict["overall_total"] / 775.0) * 100.0, 2) if student_dict["overall_total"] else None
    student_dict["result"] = pdf_res if pdf_res else ("SUCCESSFUL" if not has_f else "UNSUCCESSFUL")
    student_dict["remark"] = pdf_rem if pdf_rem else ("PASS" if not has_f else "FAILED")
    student_dict["aC"] = pdf_aC if pdf_aC is not None else calc_aC
    student_dict["aCG"] = pdf_aCG if pdf_aCG is not None else calc_aCG
    student_dict["sgpi"] = pdf_sgpi if pdf_sgpi is not None else calc_sgpi
    
    return student_dict

records = []
for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        rec = extract_student_anchored(p, sb, boxes)
        records.append(rec)

df = pd.DataFrame(records)
diffs = []
for idx, r in df.iterrows():
    s_tot = sum(r[f"{s['prefix']}_total"] for s in SUBJECTS if pd.notna(r[f"{s['prefix']}_total"]))
    o_tot = r["overall_total"]
    if s_tot != o_tot:
        diffs.append((r["page"], r["seat_no"], r["name"], o_tot, s_tot, o_tot - s_tot))

print(f"Validation summary: {len(df) - len(diffs)} / {len(df)} EXACT total matches!")
if diffs:
    print(f"Differences ({len(diffs)}):")
    for d in diffs:
        print(f"  Page {d[0]:2d} | Seat {d[1]} | Name: {d[2]:30s} | PDF Tot={d[3]} Calc Tot={d[4]} (diff={d[5]})")
