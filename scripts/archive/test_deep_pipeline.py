import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

# Let us build the ultimate student record parser that extracts:
# 1. T1, O1, E1, I1, TOT, Grade, GP, Credits, GC for all 11 subjects
# 2. Uses printed total, components, grades, and overall totals to achieve 100% precision

from test_master_pipeline import SUBJECTS, parse_num

def parse_student_deep(page_idx, sb, boxes):
    s_y = sb["ymin"]
    seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
    
    # Metadata
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
        if abs(b["ymin"] - s_y) <= 30 and "Repeater" in b["text"]:
            status = "Repeater"
            
    ern = ""
    for b in boxes:
        if abs(b["ymin"] - s_y) <= 45:
            em = re.search(r"\(?(MU\d{15,20})\)?", b["text"])
            if em:
                ern = em.group(1)
                
    college = "TERNA ENGINEERING COLLEGE NERUL NAVI MUMBAI"
    
    # Summary block (x >= 1900)
    sum_boxes = [b for b in boxes if abs(b["ymin"] - (s_y + 75)) <= 80 and b["xmin"] >= 1900]
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
        if tm:
            pdf_tot = int(tm.group(1))
        if any(w in t.upper() for w in ["PASS", "SUCCESSFUL"]):
            pdf_res = "SUCCESSFUL"
            pdf_rem = "PASS"
        elif any(w in t.upper() for w in ["FAIL", "UNSUCCESSFUL"]):
            pdf_res = "UNSUCCESSFUL"
            pdf_rem = "FAILED"
        elif "ABSENT" in t.upper() or "ABS" in t.upper():
            pdf_res = "ABSENT"
            pdf_rem = "ABSENT"
            
        decs = re.findall(r"\b\d+\.\d+\b", t)
        if len(decs) >= 2:
            pdf_aCG = float(decs[0])
            pdf_sgpi = float(decs[1])
        elif len(decs) == 1:
            if pdf_aCG is None: pdf_aCG = float(decs[0])
            elif pdf_sgpi is None: pdf_sgpi = float(decs[0])
            
        ints = re.findall(r"\b\d+\b", t)
        for iv_str in ints:
            iv = int(iv_str)
            if 0 <= iv <= 23 and 1920 <= b["xmin"] <= 2040 and pdf_aC is None:
                pdf_aC = iv

    m_boxes = [b for b in boxes if 10 < (b["ymin"] - s_y) <= 165]
    
    student_rec = {
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
        grade_printed = None
        gp_printed = None
        gc_printed = None
        
        # 1. Parse TW (dy ~ 15 to 45)
        if stype in ["TW_ORAL", "TW_ONLY"]:
            tw_b = [b for b in c_boxes if 15 <= (b["ymin"] - s_y) <= 45]
            for b in tw_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_tw"]:
                    tw = v
                    
        # 2. Parse Oral (dy ~ 40 to 68)
        if stype == "TW_ORAL":
            oral_b = [b for b in c_boxes if 40 <= (b["ymin"] - s_y) <= 68]
            for b in oral_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_oral"]:
                    oral = v
                    
        # 3. Parse External (dy ~ 55 to 88)
        if stype == "THEORY":
            ext_b = [b for b in c_boxes if 55 <= (b["ymin"] - s_y) <= 88]
            for b in ext_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_ext"]:
                    ext = v
                    
        # 4. Parse Internal (dy ~ 78 to 112)
        if stype == "THEORY":
            int_b = [b for b in c_boxes if 78 <= (b["ymin"] - s_y) <= 112]
            for b in int_b:
                # In OE, Internal text might be "I116" or "1117" or at x=45 "16"
                t = b["text"]
                if "11" in t or "I1" in t:
                    m = re.search(r"(?:I1|11)\s*(\d{1,2})", t)
                    if m:
                        v = int(m.group(1))
                        if v <= subj["max_int"]:
                            int_m = v
                else:
                    v = parse_num(t)
                    if v is not None and v <= subj["max_int"]:
                        int_m = v
                        
        # 5. Parse bottom row: TOT, Grade, GP, Credits, G*C (dy ~ 105 to 155)
        bot_b = [b for b in c_boxes if 105 <= (b["ymin"] - s_y) <= 155]
        for b in bot_b:
            t = b["text"]
            # Look for G*C e.g. "18.0", "27.0", "0.0", "16.0"
            gcm = re.search(r"\b(\d+\.0)\b", t)
            if gcm and gc_printed is None:
                gc_printed = float(gcm.group(1))
            # Look for Grade
            gm = re.search(r"\b(O|A\+|A|B\+|B|C|D|P|F)\b", t)
            if gm and not grade_printed:
                grade_printed = gm.group(1)
            # Look for printed total
            if "TOT" in t.upper():
                m = re.search(r"TOT\s*(\d+)", t, re.I)
                if m:
                    tot_printed = int(m.group(1))
            else:
                # Any integer matching max_tot
                nums = re.findall(r"\b\d+\b", t)
                for n_str in nums:
                    niv = int(n_str)
                    if 0 < niv <= subj["max_tot"] and tot_printed is None:
                        tot_printed = niv

        # Calculate / Reconcile Subject Total
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

        # Check passing status
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
            
        # If OCR clearly detected F and 0.0 for gc_printed, respect failure
        if gc_printed == 0.0:
            grade = "F"
            gp = 0
            gc = 0.0

        student_rec[f"{pfx}_code"] = subj["code"]
        student_rec[f"{pfx}_name"] = subj["name"]
        if stype == "THEORY":
            student_rec[f"{pfx}_external"] = ext
            student_rec[f"{pfx}_internal"] = int_m
        elif stype == "TW_ORAL":
            student_rec[f"{pfx}_term_work"] = tw
            student_rec[f"{pfx}_oral"] = oral
        elif stype == "TW_ONLY":
            student_rec[f"{pfx}_term_work"] = tw
            
        student_rec[f"{pfx}_total"] = tot
        student_rec[f"{pfx}_grade"] = grade
        student_rec[f"{pfx}_gp"] = gp
        student_rec[f"{pfx}_credits"] = credits
        student_rec[f"{pfx}_gc"] = gc

    # Summary
    calc_tot = sum(student_rec[f"{s['prefix']}_total"] for s in SUBJECTS if student_rec[f"{s['prefix']}_total"] is not None)
    calc_aCG = sum(student_rec[f"{s['prefix']}_gc"] for s in SUBJECTS)
    has_f = any(student_rec[f"{s['prefix']}_grade"] == "F" for s in SUBJECTS)
    calc_aC = 23 if not has_f else sum(s["credits"] for s in SUBJECTS if student_rec[f"{s['prefix']}_grade"] != "F")
    calc_sgpi = round(calc_aCG / 23.0, 5) if not has_f else 0.00000
    
    student_rec["overall_total"] = pdf_tot if pdf_tot is not None else calc_tot
    student_rec["maximum_total"] = 775
    student_rec["percentage"] = round((student_rec["overall_total"] / 775.0) * 100.0, 2) if student_rec["overall_total"] else None
    student_rec["result"] = pdf_res if pdf_res else ("SUCCESSFUL" if not has_f else "UNSUCCESSFUL")
    student_rec["remark"] = pdf_rem if pdf_rem else ("PASS" if not has_f else "FAILED")
    student_rec["aC"] = pdf_aC if pdf_aC is not None else calc_aC
    student_rec["aCG"] = pdf_aCG if pdf_aCG is not None else calc_aCG
    student_rec["sgpi"] = pdf_sgpi if pdf_sgpi is not None else calc_sgpi
    
    return student_rec

# Test
records = []
for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        rec = parse_student_deep(p, sb, boxes)
        records.append(rec)

df = pd.DataFrame(records)
print(f"Total students parsed: {len(df)}")
# Check agreement between sum of subject totals and overall total
diffs = []
for idx, r in df.iterrows():
    s_tot = sum(r[f"{s['prefix']}_total"] for s in SUBJECTS if pd.notna(r[f"{s['prefix']}_total"]))
    o_tot = r["overall_total"]
    if s_tot != o_tot:
        diffs.append((r["page"], r["seat_no"], r["name"], o_tot, s_tot, o_tot - s_tot))

print(f"Total students with exact total match: {len(df) - len(diffs)} / {len(df)}")
if diffs:
    print(f"Differences ({len(diffs)}):")
    for d in diffs:
        print(f"  Page {d[0]:2d} | Seat {d[1]} | Name: {d[2]:30s} | PDF Tot={d[3]} Calc Tot={d[4]} (diff={d[5]})")
