import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

from test_master_pipeline import SUBJECTS
from test_deep_pipeline_v2 import parse_mark_token
from test_dynamic_anchors import extract_row_anchors

def parse_student_chained(page_idx, sb, boxes):
    s_y = sb["ymin"]
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    
    # Clean Name
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
    
    # Summary block
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
    
    # Extract components
    comp_data = {}
    for i, subj in enumerate(SUBJECTS):
        pfx = subj["prefix"]
        xmin, xmax = subj["x_range"]
        stype = subj["type"]
        c_boxes = [b for b in m_boxes if xmin <= b["xmin"] < xmax]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        
        # T1 (abs(y - y_T1) <= 10)
        if stype in ["TW_ORAL", "TW_ONLY"]:
            for b in c_boxes:
                if abs(b["ymin"] - y_T1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_tw"])
                    if v is not None: tw = v
        # O1 (abs(y - y_O1) <= 10)
        if stype == "TW_ORAL":
            for b in c_boxes:
                if abs(b["ymin"] - y_O1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_oral"])
                    if v is not None: oral = v
        # E1 (abs(y - y_E1) <= 10)
        if stype == "THEORY":
            for b in c_boxes:
                if abs(b["ymin"] - y_E1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_ext"])
                    if v is not None: ext = v
        # I1 (abs(y - y_I1) <= 10)
        if stype == "THEORY":
            for b in c_boxes:
                if abs(b["ymin"] - y_I1) <= 10:
                    v = parse_mark_token(b["text"], subj["max_int"])
                    if v is not None: int_m = v
                    
        comp_data[pfx] = {"tw": tw, "oral": oral, "ext": ext, "int": int_m}
        
    # Extract bottom row chain:
    bot_boxes = [b for b in m_boxes if abs(b["ymin"] - y_TOT) <= 18 and b["xmin"] < 1920]
    bot_boxes.sort(key=lambda b: b["xmin"])
    
    # 1. Look for OE Total (at left x < 100)
    oe_tot = None
    for b in bot_boxes:
        if b["xmin"] < 100:
            if "TOT" in b["text"].upper():
                m = re.search(r"TOT\s*(\d+)", b["text"], re.I)
                if m: oe_tot = int(m.group(1))
            else:
                nums = re.findall(r"\b\d+\b", b["text"])
                if nums and int(nums[-1]) <= 50: oe_tot = int(nums[-1])
                
    # 2. Reconstruct subject totals for all 11 subjects
    subj_totals = [None] * 11
    if oe_tot is not None:
        subj_totals[0] = oe_tot
    elif comp_data["OE"]["ext"] is not None and comp_data["OE"]["int"] is not None:
        subj_totals[0] = comp_data["OE"]["ext"] + comp_data["OE"]["int"]
        
    # Bottom boxes between x=100 and 1920 carry totals for subject 1..10
    # Let us extract the trailing integer from each column's bottom box
    for i in range(10):
        # The total for subject i+1 is printed in bottom box of column i (or start of column i+1)
        # column i x_range
        curr_subj = SUBJECTS[i]
        next_subj = SUBJECTS[i+1]
        
        # Look for boxes in curr_subj x_range or crossing into next_subj
        c_bot = [b for b in bot_boxes if curr_subj["x_range"][0] <= b["xmin"] < curr_subj["x_range"][1] + 40]
        for b in c_bot:
            t = b["text"]
            # match number at the end of the text
            # e.g. "A+ 2 18.0 60" -> 60
            m_end = re.search(r"\b(\d{1,3})\s*$", t)
            if m_end:
                niv = int(m_end.group(1))
                if 0 < niv <= next_subj["max_tot"] and niv != next_subj["credits"]:
                    subj_totals[i+1] = niv
                    
    # Also reconcile with components
    for i, s in enumerate(SUBJECTS):
        pfx = s["prefix"]
        stype = s["type"]
        cd = comp_data[pfx]
        if stype == "THEORY":
            if cd["ext"] is not None and cd["int"] is not None:
                comp_tot = cd["ext"] + cd["int"]
                if subj_totals[i] is None:
                    subj_totals[i] = comp_tot
            elif subj_totals[i] is not None:
                if cd["ext"] is not None and cd["int"] is None:
                    cd["int"] = subj_totals[i] - cd["ext"]
                elif cd["int"] is not None and cd["ext"] is None:
                    cd["ext"] = subj_totals[i] - cd["int"]
        elif stype == "TW_ORAL":
            if cd["tw"] is not None and cd["oral"] is not None:
                comp_tot = cd["tw"] + cd["oral"]
                if subj_totals[i] is None:
                    subj_totals[i] = comp_tot
            elif subj_totals[i] is not None:
                if cd["tw"] is not None and cd["oral"] is None:
                    cd["oral"] = subj_totals[i] - cd["tw"]
                elif cd["oral"] is not None and cd["tw"] is None:
                    cd["tw"] = subj_totals[i] - cd["oral"]
        else: # TW_ONLY
            if cd["tw"] is not None:
                subj_totals[i] = cd["tw"]
            elif subj_totals[i] is not None:
                cd["tw"] = subj_totals[i]

    # Build final record
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
    
    for i, subj in enumerate(SUBJECTS):
        pfx = subj["prefix"]
        stype = subj["type"]
        cd = comp_data[pfx]
        tot = subj_totals[i]
        
        # Check passing
        if stype == "THEORY":
            is_pass = (cd["ext"] is not None and cd["ext"] >= subj["min_ext"]) and (cd["int"] is not None and cd["int"] >= subj["min_int"])
        elif stype == "TW_ORAL":
            is_pass = (cd["tw"] is not None and cd["tw"] >= subj["min_tw"]) and (cd["oral"] is not None and cd["oral"] >= subj["min_oral"])
        else:
            is_pass = (cd["tw"] is not None and cd["tw"] >= subj["min_tw"])
            
        max_tot = subj["max_tot"]
        credits = subj["credits"]
        
        if tot is None or not is_pass:
            grade = "F"; gp = 0; gc = 0.0
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
            
        student_dict[f"{pfx}_code"] = subj["code"]
        student_dict[f"{pfx}_name"] = subj["name"]
        if stype == "THEORY":
            student_dict[f"{pfx}_external"] = cd["ext"]
            student_dict[f"{pfx}_internal"] = cd["int"]
        elif stype == "TW_ORAL":
            student_dict[f"{pfx}_term_work"] = cd["tw"]
            student_dict[f"{pfx}_oral"] = cd["oral"]
        elif stype == "TW_ONLY":
            student_dict[f"{pfx}_term_work"] = cd["tw"]
            
        student_dict[f"{pfx}_total"] = tot
        student_dict[f"{pfx}_grade"] = grade
        student_dict[f"{pfx}_gp"] = gp
        student_dict[f"{pfx}_credits"] = credits
        student_dict[f"{pfx}_gc"] = gc

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
        rec = parse_student_chained(p, sb, boxes)
        records.append(rec)

df = pd.DataFrame(records)
diffs = []
for idx, r in df.iterrows():
    s_tot = sum(r[f"{s['prefix']}_total"] for s in SUBJECTS if pd.notna(r[f"{s['prefix']}_total"]))
    o_tot = r["overall_total"]
    if s_tot != o_tot:
        diffs.append((r["page"], r["seat_no"], r["name"], o_tot, s_tot, o_tot - s_tot))

print(f"Chained Validation summary: {len(df) - len(diffs)} / {len(df)} EXACT total matches!")
if diffs:
    print(f"Differences ({len(diffs)}):")
    for d in diffs:
        print(f"  Page {d[0]:2d} | Seat {d[1]} | Name: {d[2]:30s} | PDF Tot={d[3]} Calc Tot={d[4]} (diff={d[5]})")
