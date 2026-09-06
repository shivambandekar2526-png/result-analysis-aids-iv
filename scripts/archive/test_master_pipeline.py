import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

SUBJECTS = [
    {
        "code": "1313311", "prefix": "OE", "name": "Administrative Policy of Chhatrapati Shivaji Maharaja",
        "type": "THEORY", "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "credits": 2,
        "x_center": 100, "x_range": (0, 190)
    },
    {
        "code": "2014411", "prefix": "MINIPROJ", "name": "Mini Project",
        "type": "TW_ORAL", "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "credits": 2,
        "x_center": 270, "x_range": (190, 360)
    },
    {
        "code": "2114111", "prefix": "CT", "name": "Computational Theory",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_center": 440, "x_range": (360, 530)
    },
    {
        "code": "2114112", "prefix": "DBMS", "name": "Database Management System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_center": 615, "x_range": (530, 700)
    },
    {
        "code": "2114113", "prefix": "OS", "name": "Operating System",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_center": 785, "x_range": (700, 875)
    },
    {
        "code": "2114114", "prefix": "DBMS_LAB", "name": "Database Management System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_center": 960, "x_range": (875, 1045)
    },
    {
        "code": "2114115", "prefix": "OS_LAB", "name": "Operating System Lab",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_center": 1130, "x_range": (1045, 1215)
    },
    {
        "code": "2304211", "prefix": "FTS", "name": "Fundamentals of Telecommunication Systems",
        "type": "THEORY", "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "credits": 3,
        "x_center": 1300, "x_range": (1215, 1385)
    },
    {
        "code": "2304212", "prefix": "TC_LAB", "name": "Basic Telecommunication Experiments",
        "type": "TW_ORAL", "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "credits": 1,
        "x_center": 1470, "x_range": (1385, 1555)
    },
    {
        "code": "2994511", "prefix": "BMD", "name": "Business Model Development",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "x_center": 1640, "x_range": (1555, 1725)
    },
    {
        "code": "2994512", "prefix": "DT", "name": "Design Thinking",
        "type": "TW_ONLY", "max_tw": 50, "min_tw": 20, "max_tot": 50, "credits": 2,
        "x_center": 1810, "x_range": (1725, 1900)
    }
]

def parse_num(t):
    # Strip non digits
    # Handle grace marks like "20 *4" -> 24 or 20
    # Handle "E1 24" -> 24
    # Handle "I116" or "11 17" -> 16 or 17
    # Handle "TOT 40" -> 40
    if not t:
        return None
    t = t.strip()
    if any(w in t.upper() for w in ["ABS", "AA", "AB"]):
        return 0
    if "E1" in t.upper():
        m = re.search(r"E1\s*(\d+)", t, re.I)
        if m: return int(m.group(1))
    if "I1" in t.upper():
        m = re.search(r"I1\s*(\d+)", t, re.I)
        if m: return int(m.group(1))
    if "T1" in t.upper():
        m = re.search(r"T1\s*(\d+)", t, re.I)
        if m: return int(m.group(1))
    if "O1" in t.upper():
        m = re.search(r"O1\s*(\d+)", t, re.I)
        if m: return int(m.group(1))
    if "TOT" in t.upper():
        m = re.search(r"TOT\s*(\d+)", t, re.I)
        if m: return int(m.group(1))
        
    # check for * grace marks: e.g. "20 *4" -> 24 or 20
    if "*" in t:
        parts = re.findall(r"\d+", t)
        if len(parts) >= 2:
            return int(parts[0]) + int(parts[1])
        elif len(parts) == 1:
            return int(parts[0])
            
    # Generic integer
    nums = re.findall(r"\b\d+\b", t)
    if nums:
        # If last num is reasonable mark
        return int(nums[-1])
    return None

def extract_student_record(page_idx, seat_box, boxes):
    s_y = seat_box["ymin"]
    seat = re.search(r"\b1014\d{5}\b", seat_box["text"]).group(0)
    
    # Metadata line: y around s_y (-15 to +20)
    meta_boxes = [b for b in boxes if abs(b["ymin"] - s_y) < 25]
    meta_boxes.sort(key=lambda x: x["xmin"])
    
    # Name extraction
    name_parts = []
    for b in meta_boxes:
        if 180 <= b["xmin"] <= 550 and not re.search(r"\b1014\d{5}\b", b["text"]):
            words = re.findall(r"[A-Za-z]+", b["text"])
            for w in words:
                if w.upper() not in ["REGULAR", "REPEATER", "FEMALE", "MALE", "MUMBAI", "COLLEGE", "SEAT", "NO", "NAME", "STATUS", "GENDER", "ERN"]:
                    name_parts.append(w.upper())
    name = " ".join(name_parts)
    
    # Gender
    gender = ""
    for b in meta_boxes:
        if "FEMALE" in b["text"].upper(): gender = "FEMALE"
        elif "MALE" in b["text"].upper(): gender = "MALE"
    if not gender:
        # search within student box
        for b in boxes:
            if abs(b["ymin"] - s_y) < 40:
                if "FEMALE" in b["text"].upper(): gender = "FEMALE"
                elif "MALE" in b["text"].upper(): gender = "MALE"
                
    # Status
    status = "Regular"
    for b in meta_boxes:
        if "Repeater" in b["text"]: status = "Repeater"
        
    # ERN & College
    ern = ""
    college = "TERNA ENGINEERING COLLEGE NERUL NAVI MUMBAI"
    for b in boxes:
        if abs(b["ymin"] - s_y) < 45:
            em = re.search(r"\(?(MU\d{15,20})\)?", b["text"])
            if em:
                ern = em.group(1)
                
    # Summary Column (x >= 1900)
    sum_boxes = [b for b in boxes if abs(b["ymin"] - (s_y + 80)) < 75 and b["xmin"] >= 1900]
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
        elif "ABSENT" in t.upper():
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

    # Marks for each subject
    # Student marks area is s_y < y <= s_y + 160
    m_boxes = [b for b in boxes if 10 < (b["ymin"] - s_y) <= 160]
    
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
        
        # All boxes in this column
        c_boxes = [b for b in m_boxes if xmin <= b["xmin"] < xmax]
        
        tw = None
        oral = None
        ext = None
        int_m = None
        tot = None
        
        if stype in ["TW_ORAL", "TW_ONLY"]:
            # T1: dy in [15, 45]
            tw_b = [b for b in c_boxes if 15 <= (b["ymin"] - s_y) <= 45]
            for b in tw_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_tw"]:
                    tw = v
            if stype == "TW_ORAL":
                # O1: dy in [40, 68]
                oral_b = [b for b in c_boxes if 40 <= (b["ymin"] - s_y) <= 68]
                for b in oral_b:
                    v = parse_num(b["text"])
                    if v is not None and v <= subj["max_oral"]:
                        oral = v
            if stype == "TW_ORAL":
                tot = (tw + oral) if (tw is not None and oral is not None) else None
            else:
                tot = tw
        elif stype == "THEORY":
            # E1: dy in [55, 88]
            ext_b = [b for b in c_boxes if 55 <= (b["ymin"] - s_y) <= 88]
            for b in ext_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_ext"]:
                    ext = v
            # I1: dy in [80, 112]
            int_b = [b for b in c_boxes if 80 <= (b["ymin"] - s_y) <= 112]
            for b in int_b:
                v = parse_num(b["text"])
                if v is not None and v <= subj["max_int"]:
                    int_m = v
            tot = (ext + int_m) if (ext is not None and int_m is not None) else None

        # Check for explicitly printed subject total in dy in [105, 150]
        tot_b = [b for b in c_boxes if 105 <= (b["ymin"] - s_y) <= 150]
        extracted_tot_print = None
        for b in tot_b:
            # Look for number that matches max_tot range
            nums = re.findall(r"\b\d+\b", b["text"])
            for n_str in nums:
                niv = int(n_str)
                if niv <= subj["max_tot"] and niv > 0:
                    extracted_tot_print = niv
                    
        # If computed tot is None, fallback to printed total
        if tot is None and extracted_tot_print is not None:
            tot = extracted_tot_print
            
        # Determine is_pass
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

    # Overall Summary
    calc_total = sum(student_dict[f"{s['prefix']}_total"] for s in SUBJECTS if student_dict[f"{s['prefix']}_total"] is not None)
    calc_aCG = sum(student_dict[f"{s['prefix']}_gc"] for s in SUBJECTS)
    has_f = any(student_dict[f"{s['prefix']}_grade"] == "F" for s in SUBJECTS)
    calc_aC = 23 if not has_f else sum(s["credits"] for s in SUBJECTS if student_dict[f"{s['prefix']}_grade"] != "F")
    calc_sgpi = round(calc_aCG / 23.0, 5) if not has_f else 0.00000
    
    student_dict["overall_total"] = pdf_tot if pdf_tot is not None else calc_total
    student_dict["maximum_total"] = 775
    student_dict["percentage"] = round((student_dict["overall_total"] / 775.0) * 100.0, 2) if student_dict["overall_total"] else None
    student_dict["result"] = pdf_res if pdf_res else ("SUCCESSFUL" if not has_f else "UNSUCCESSFUL")
    student_dict["remark"] = pdf_rem if pdf_rem else ("PASS" if not has_f else "FAILED")
    student_dict["aC"] = pdf_aC if pdf_aC is not None else calc_aC
    student_dict["aCG"] = pdf_aCG if pdf_aCG is not None else calc_aCG
    student_dict["sgpi"] = pdf_sgpi if pdf_sgpi is not None else calc_sgpi
    
    return student_dict

# Run across all pages
all_rows = []
for p in range(2, 47):
    with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    boxes = data["boxes"]
    seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
    seat_boxes.sort(key=lambda b: b["ymin"])
    for sb in seat_boxes:
        rec = extract_student_record(p, sb, boxes)
        all_rows.append(rec)

master_df = pd.DataFrame(all_rows)
print(f"Master DataFrame successfully constructed: {master_df.shape}")
print(master_df[["seat_no", "name", "gender", "status", "overall_total", "result", "sgpi"]].head(20))
