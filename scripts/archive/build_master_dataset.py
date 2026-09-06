import json, re, glob, os, sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")

SUBJECTS_CATALOG = {
    "1313311": {
        "prefix": "OE",
        "name": "Administrative Policy of Chhatrapati Shivaji Maharaja",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "min_tot": 20, "credits": 2
    },
    "2014411": {
        "prefix": "MINIPROJ",
        "name": "Mini Project",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "min_tot": 30, "credits": 2
    },
    "2114111": {
        "prefix": "CT",
        "name": "Computational Theory",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    "2114112": {
        "prefix": "DBMS",
        "name": "Database Management System",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    "2114113": {
        "prefix": "OS",
        "name": "Operating System",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    "2114114": {
        "prefix": "DBMS_LAB",
        "name": "Database Management System Lab",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    "2114115": {
        "prefix": "OS_LAB",
        "name": "Operating System Lab",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    "2304211": {
        "prefix": "FTS",
        "name": "Fundamentals of Telecommunication Systems",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    "2304212": {
        "prefix": "TC_LAB",
        "name": "Basic Telecommunication Experiments",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    "2994511": {
        "prefix": "BMD",
        "name": "Business Model Development",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": False,
        "max_tw": 50, "min_tw": 20, "max_tot": 50, "min_tot": 20, "credits": 2
    },
    "2994512": {
        "prefix": "DT",
        "name": "Design Thinking",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": False,
        "max_tw": 50, "min_tw": 20, "max_tot": 50, "min_tot": 20, "credits": 2
    }
}

COL_BOUNDS = [
    ("1313311", 50, 225),
    ("2014411", 225, 395),
    ("2114111", 395, 560),
    ("2114112", 560, 730),
    ("2114113", 730, 905),
    ("2114114", 905, 1075),
    ("2114115", 1075, 1245),
    ("2304211", 1245, 1415),
    ("2304212", 1415, 1585),
    ("2994511", 1585, 1755),
    ("2994512", 1755, 1925)
]

def parse_all():
    records = []
    
    for p in range(2, 47):
        with open(f"ocr_cache/page_{p:03d}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        boxes = data["boxes"]
        
        # Find student blocks
        seat_boxes = [b for b in boxes if re.search(r"\b1014\d{5}\b", b["text"])]
        seat_boxes.sort(key=lambda b: b["ymin"])
        
        for s_idx, sb in enumerate(seat_boxes):
            seat = re.search(r"\b1014\d{5}\b", sb["text"]).group(0)
            s_y = sb["ymin"]
            
            # student row bounds
            if s_idx == 0 and len(seat_boxes) == 2:
                s_ymin = s_y - 20
                s_ymax = seat_boxes[1]["ymin"] - 40
            elif s_idx == 1:
                s_ymin = s_y - 20
                s_ymax = 1200
            else:
                s_ymin = s_y - 20
                s_ymax = 1200
                
            s_boxes = [b for b in boxes if s_ymin <= b["ymin"] <= s_ymax]
            
            # Extract metadata
            meta_row = [b for b in s_boxes if abs(b["ymin"] - s_y) < 25]
            meta_row.sort(key=lambda x: x["xmin"])
            
            # Name
            name_parts = []
            for b in meta_row:
                if 180 <= b["xmin"] <= 550 and not re.search(r"\b1014\d{5}\b", b["text"]):
                    # clean up status words if attached
                    t = re.sub(r"\b(Regular|Repeater|FEMALE|MALE)\b", "", b["text"]).strip()
                    if t:
                        name_parts.append(t)
            name = " ".join(name_parts)
            
            # Gender
            gender = ""
            for b in meta_row:
                if "FEMALE" in b["text"].upper():
                    gender = "FEMALE"
                elif "MALE" in b["text"].upper():
                    gender = "MALE"
                    
            # Status
            status = "Regular"
            for b in meta_row:
                if "Repeater" in b["text"]:
                    status = "Repeater"
                    
            # ERN & College
            ern = ""
            college = ""
            for b in meta_row:
                em = re.search(r"\(?(MU\d{15,20})\)?", b["text"])
                if em:
                    ern = em.group(1)
                if "TERNA" in b["text"].upper() or "MU-0237" in b["text"]:
                    college = b["text"]
            if not ern:
                # check surrounding boxes
                for b in s_boxes:
                    em = re.search(r"\(?(MU\d{15,20})\)?", b["text"])
                    if em:
                        ern = em.group(1)
                        break

            # Subject Marks Extraction
            # We classify mark boxes by their relative vertical position and horizontal column
            # T1 row: y around s_y + 20 to s_y + 35
            # O1 row: y around s_y + 40 to s_y + 55
            # E1 row: y around s_y + 60 to s_y + 78
            # I1 row: y around s_y + 80 to s_y + 98
            # TOT / Grade row: y around s_y + 100 to s_y + 145
            
            student_rec = {
                "student_id": seat,
                "seat_no": seat,
                "name": name,
                "gender": gender,
                "status": status,
                "ern": ern,
                "page": p
            }
            
            # Extract summary column (x >= 1920)
            sum_boxes = [b for b in s_boxes if b["xmin"] >= 1920]
            sum_boxes.sort(key=lambda b: (b["ymin"], b["xmin"]))
            
            tot_marks = None
            result_str = ""
            remark_str = ""
            aC_val = None
            aCG_val = None
            sgpi_val = None
            
            for b in sum_boxes:
                t = b["text"]
                # Total marks like (553) or (616) or (387)
                tm = re.search(r"\((\d{2,3})\)", t)
                if tm:
                    tot_marks = int(tm.group(1))
                if any(w in t.upper() for w in ["PASS", "SUCCESSFUL"]):
                    result_str = "SUCCESSFUL"
                    remark_str = "PASS"
                elif any(w in t.upper() for w in ["FAIL", "UNSUCCESSFUL"]):
                    result_str = "UNSUCCESSFUL"
                    remark_str = "FAILED"
                elif "ABSENT" in t.upper() or "ABS" in t.upper():
                    result_str = "ABSENT"
                    remark_str = "ABSENT"
                elif "NULL" in t.upper():
                    remark_str = "NULL"
                    
                # aC, aCG, SGPI e.g. "179.0 7.78261" or "23 196.0 8.52174" or "81.0 0.00000"
                # Numbers with decimals
                dec_matches = re.findall(r"\b\d+\.\d+\b", t)
                int_matches = re.findall(r"\b\d+\b", t)
                if len(dec_matches) >= 2:
                    aCG_val = float(dec_matches[0])
                    sgpi_val = float(dec_matches[1])
                elif len(dec_matches) == 1:
                    if aCG_val is None:
                        aCG_val = float(dec_matches[0])
                    elif sgpi_val is None:
                        sgpi_val = float(dec_matches[0])
                
                # Check for 22 or 23 as aC (earned credits)
                for im in int_matches:
                    iv = int(im)
                    if iv in [23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
                        if 1930 <= b["xmin"] <= 2020 and aC_val is None:
                            aC_val = iv
                            
            # Process each subject column
            for scode, xmin_col, xmax_col in COL_BOUNDS:
                info = SUBJECTS_CATALOG[scode]
                pfx = info["prefix"]
                
                # Find all boxes in this column
                c_boxes = [b for b in s_boxes if xmin_col - 10 <= b["xmin"] < xmax_col + 10 and b["ymin"] > s_y + 10]
                c_boxes.sort(key=lambda b: b["ymin"])
                
                # We will extract marks based on y-offset from s_y
                tw_val = None
                oral_val = None
                ext_val = None
                int_val = None
                tot_val = None
                grade_val = ""
                gp_val = None
                c_val = info["credits"]
                gc_val = None
                
                for b in c_boxes:
                    dy = b["ymin"] - s_y
                    txt = b["text"]
                    
                    # T1 row: dy in [15, 40]
                    if 15 <= dy <= 40 and (info["has_tw"]):
                        # match integer
                        nums = re.findall(r"\b\d{1,2}\b", txt)
                        if nums:
                            tw_val = int(nums[0])
                    # O1 row: dy in [35, 58]
                    elif 35 <= dy <= 58 and (info["has_oral"]):
                        nums = re.findall(r"\b\d{1,2}\b", txt)
                        if nums:
                            oral_val = int(nums[-1])
                    # E1 row: dy in [55, 80]
                    elif 55 <= dy <= 80 and (info["has_ext"]):
                        # txt might be "E1 24" or "42"
                        nums = re.findall(r"\b\d{1,2}\b", txt)
                        if nums:
                            ext_val = int(nums[-1])
                    # I1 row: dy in [75, 102]
                    elif 75 <= dy <= 102 and (info["has_int"]):
                        # txt might be "I1 16" or "11 17" or "34"
                        nums = re.findall(r"\b\d{1,2}\b", txt)
                        if nums:
                            int_val = int(nums[-1])
                    # TOT & Grade row: dy in [98, 150]
                    elif 98 <= dy <= 150:
                        # Extract grades (O, A+, A, B+, B, C, D, P, F)
                        gm = re.search(r"\b(O|A\+|A|B\+|B|C|D|P|F)\b", txt)
                        if gm and not grade_val:
                            grade_val = gm.group(1)
                        # GP, C, G*C e.g. "A+ 2 18.0 53" or "3 24.0 41" or "10 02 20.0 23"
                        # G*C is float like 18.0, 27.0, 0.0, etc.
                        gcm = re.search(r"\b(\d+\.0)\b", txt)
                        if gcm and gc_val is None:
                            gc_val = float(gcm.group(1))
                        # Total marks for this subject: usually 2 digits
                        # In theory/lab, total is integer
                        # Let's extract integers
                        nums = re.findall(r"\b\d{1,3}\b", txt)
                        for nm in nums:
                            niv = int(nm)
                            if niv <= info["max_tot"] and niv > 0 and tot_val is None:
                                # if theory, tot should be close to ext+int
                                if info["has_ext"] and info["has_int"]:
                                    if ext_val is not None and int_val is not None and niv == ext_val + int_val:
                                        tot_val = niv
                                elif info["has_tw"] and info["has_oral"]:
                                    if tw_val is not None and oral_val is not None and niv == tw_val + oral_val:
                                        tot_val = niv
                                elif info["has_tw"] and not info["has_oral"]:
                                    if tw_val is not None and niv == tw_val:
                                        tot_val = niv
                                        
                student_rec[f"{pfx}_code"] = scode
                student_rec[f"{pfx}_name"] = info["name"]
                if info["has_ext"]: student_rec[f"{pfx}_external"] = ext_val
                if info["has_int"]: student_rec[f"{pfx}_internal"] = int_val
                if info["has_tw"]: student_rec[f"{pfx}_term_work"] = tw_val
                if info["has_oral"]: student_rec[f"{pfx}_oral"] = oral_val
                student_rec[f"{pfx}_total"] = tot_val
                student_rec[f"{pfx}_grade"] = grade_val
                student_rec[f"{pfx}_gp"] = gp_val
                student_rec[f"{pfx}_credits"] = c_val
                student_rec[f"{pfx}_gc"] = gc_val

            student_rec["overall_total"] = tot_marks
            student_rec["maximum_total"] = 775
            student_rec["percentage"] = round(tot_marks / 775.0 * 100, 2) if tot_marks else None
            student_rec["result"] = result_str
            student_rec["remark"] = remark_str
            student_rec["aC"] = aC_val
            student_rec["aCG"] = aCG_val
            student_rec["sgpi"] = sgpi_val
            
            records.append(student_rec)

    df = pd.DataFrame(records)
    print(f"Extracted DataFrame Shape: {df.shape}")
    print(df[["seat_no", "name", "gender", "status", "overall_total", "result", "sgpi"]].head(15))
    return df

df = parse_all()
