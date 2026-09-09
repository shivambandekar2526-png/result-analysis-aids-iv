from pathlib import Path
import json, re, sys, os
import pandas as pd
import numpy as np
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / 'data' / 'processed' / 'AI_DS_SEM4_MASTER_RESULTS.csv')
print(f"Loaded master CSV with {len(df)} rows and {len(df.columns)} columns.")

# Subject Catalog Definition
SUBJECTS = [
    {
        "code_col": "OE_code", "name_col": "OE_name", "prefix": "OE",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 30, "min_ext": 12, "max_int": 20, "min_int": 8, "max_tot": 50, "min_tot": 20, "credits": 2
    },
    {
        "code_col": "MINIPROJ_code", "name_col": "MINIPROJ_name", "prefix": "MINIPROJ",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 50, "min_tw": 20, "max_oral": 25, "min_oral": 10, "max_tot": 75, "min_tot": 30, "credits": 2
    },
    {
        "code_col": "CT_code", "name_col": "CT_name", "prefix": "CT",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    {
        "code_col": "DBMS_code", "name_col": "DBMS_name", "prefix": "DBMS",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    {
        "code_col": "OS_code", "name_col": "OS_name", "prefix": "OS",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    {
        "code_col": "DBMS_LAB_code", "name_col": "DBMS_LAB_name", "prefix": "DBMS_LAB",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    {
        "code_col": "OS_LAB_code", "name_col": "OS_LAB_name", "prefix": "OS_LAB",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    {
        "code_col": "FTS_code", "name_col": "FTS_name", "prefix": "FTS",
        "has_ext": True, "has_int": True, "has_tw": False, "has_oral": False,
        "max_ext": 60, "min_ext": 24, "max_int": 40, "min_int": 16, "max_tot": 100, "min_tot": 40, "credits": 3
    },
    {
        "code_col": "TC_LAB_code", "name_col": "TC_LAB_name", "prefix": "TC_LAB",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": True,
        "max_tw": 25, "min_tw": 10, "max_oral": 25, "min_oral": 10, "max_tot": 50, "min_tot": 20, "credits": 1
    },
    {
        "code_col": "BMD_code", "name_col": "BMD_name", "prefix": "BMD",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": False,
        "max_tw": 50, "min_tw": 20, "max_tot": 50, "min_tot": 20, "credits": 2
    },
    {
        "code_col": "DT_code", "name_col": "DT_name", "prefix": "DT",
        "has_ext": False, "has_int": False, "has_tw": True, "has_oral": False,
        "max_tw": 50, "min_tw": 20, "max_tot": 50, "min_tot": 20, "credits": 2
    }
]

def get_expected_grade_gp(tot, max_tot, fail=False):
    if fail or tot is None or tot < 0:
        return "F", 0.0
    pct = (tot / max_tot) * 100.0
    if pct >= 90: return "O", 10.0
    elif pct >= 80: return "A+", 9.0
    elif pct >= 70: return "A", 8.0
    elif pct >= 60: return "B+", 7.0
    elif pct >= 55: return "B", 6.0
    elif pct >= 50: return "C", 5.0
    elif pct >= 40: return "D", 4.0
    else: return "F", 0.0

discrepancies = []

for idx, row in df.iterrows():
    sid = row['student_id']
    name = row['name']
    page = row['page']
    
    # Check 1: Student Metadata
    if pd.isna(row['seat_no']) or str(row['seat_no']) == '':
        discrepancies.append((page, sid, name, "seat_no", row['seat_no'], "Missing seat number", "High"))
    if pd.isna(row['ern']) or str(row['ern']) == '' or len(str(row['ern'])) < 10:
        discrepancies.append((page, sid, name, "ern", row['ern'], "Invalid/missing ERN", "High"))
    if row['gender'] not in ['MALE', 'FEMALE']:
        discrepancies.append((page, sid, name, "gender", row['gender'], "Invalid gender format", "Medium"))
        
    # Check 2: Subjects
    calc_overall_tot = 0.0
    calc_total_acg = 0.0
    calc_total_ac = 0
    all_passed = True
    
    for subj in SUBJECTS:
        pfx = subj['prefix']
        max_tot = subj['max_tot']
        credits = subj['credits']
        
        # Check component sums
        tot_val = row[f"{pfx}_total"]
        if pd.isna(tot_val):
            discrepancies.append((page, sid, name, f"{pfx}_total", tot_val, "Missing total marks", "High"))
            tot_val = 0.0
        calc_overall_tot += tot_val
        
        is_sub_fail = False
        
        if subj['has_ext'] and subj['has_int']:
            ext_val = row[f"{pfx}_external"]
            int_val = row[f"{pfx}_internal"]
            
            if pd.isna(ext_val):
                discrepancies.append((page, sid, name, f"{pfx}_external", ext_val, "Missing external marks", "High"))
            elif ext_val > subj['max_ext'] or ext_val < 0:
                discrepancies.append((page, sid, name, f"{pfx}_external", ext_val, f"External marks out of bounds [0, {subj['max_ext']}]", "High"))
            elif ext_val < subj['min_ext']:
                is_sub_fail = True
                
            if pd.isna(int_val):
                discrepancies.append((page, sid, name, f"{pfx}_internal", int_val, "Missing internal marks", "High"))
            elif int_val > subj['max_int'] or int_val < 0:
                discrepancies.append((page, sid, name, f"{pfx}_internal", int_val, f"Internal marks out of bounds [0, {subj['max_int']}]", "High"))
            elif int_val < subj['min_int']:
                is_sub_fail = True
                
            if not pd.isna(ext_val) and not pd.isna(int_val):
                if ext_val + int_val != tot_val:
                    discrepancies.append((page, sid, name, f"{pfx}_total_mismatch", f"{ext_val}+{int_val}!={tot_val}", "Component sum does not match total", "High"))
                    
        elif subj['has_tw']:
            tw_val = row[f"{pfx}_term_work"]
            if pd.isna(tw_val):
                discrepancies.append((page, sid, name, f"{pfx}_term_work", tw_val, "Missing term work marks", "High"))
            elif tw_val > subj['max_tw'] or tw_val < 0:
                discrepancies.append((page, sid, name, f"{pfx}_term_work", tw_val, f"Term work marks out of bounds [0, {subj['max_tw']}]", "High"))
            elif tw_val < subj['min_tw']:
                is_sub_fail = True
                
            if subj['has_oral']:
                oral_val = row[f"{pfx}_oral"]
                if pd.isna(oral_val):
                    discrepancies.append((page, sid, name, f"{pfx}_oral", oral_val, "Missing oral marks", "High"))
                elif oral_val > subj['max_oral'] or oral_val < 0:
                    discrepancies.append((page, sid, name, f"{pfx}_oral", oral_val, f"Oral marks out of bounds [0, {subj['max_oral']}]", "High"))
                elif oral_val < subj['min_oral']:
                    is_sub_fail = True
                    
                if not pd.isna(tw_val) and not pd.isna(oral_val):
                    if tw_val + oral_val != tot_val:
                        discrepancies.append((page, sid, name, f"{pfx}_total_mismatch", f"{tw_val}+{oral_val}!={tot_val}", "Component sum does not match total", "High"))
            else:
                if not pd.isna(tw_val):
                    if tw_val != tot_val:
                        discrepancies.append((page, sid, name, f"{pfx}_total_mismatch", f"{tw_val}!={tot_val}", "Term work does not match total", "High"))
                        
        if tot_val < subj['min_tot']:
            is_sub_fail = True
            
        if is_sub_fail:
            all_passed = False
            
        # Grade & GP Check
        actual_grade = row[f"{pfx}_grade"]
        actual_gp = row[f"{pfx}_gp"]
        actual_gc = row[f"{pfx}_gc"]
        
        exp_grd, exp_gp = get_expected_grade_gp(tot_val, max_tot, fail=is_sub_fail)
        if actual_grade != exp_grd:
            discrepancies.append((page, sid, name, f"{pfx}_grade", f"Actual: {actual_grade}, Expected: {exp_grd}", "Grade mismatch with marks/fail status", "Medium"))
        if actual_gp != exp_gp:
            discrepancies.append((page, sid, name, f"{pfx}_gp", f"Actual: {actual_gp}, Expected: {exp_gp}", "Grade point mismatch", "Medium"))
        if actual_gc != exp_gp * credits:
            discrepancies.append((page, sid, name, f"{pfx}_gc", f"Actual: {actual_gc}, Expected: {exp_gp * credits}", "Credit point calculation mismatch", "High"))
            
        if not is_sub_fail:
            calc_total_ac += credits
            calc_total_acg += exp_gp * credits
            
    # Overall Marks Check
    if row['overall_total'] != calc_overall_tot:
        discrepancies.append((page, sid, name, "overall_total", f"Actual: {row['overall_total']}, Sum: {calc_overall_tot}", "Overall total does not equal sum of subjects", "High"))
    if row['maximum_total'] != 775:
        discrepancies.append((page, sid, name, "maximum_total", row['maximum_total'], "Maximum total is not 775", "High"))
        
    # Check percentage
    exp_pct = round((calc_overall_tot / 775.0) * 100, 2)
    if abs(row['percentage'] - exp_pct) > 0.05:
        discrepancies.append((page, sid, name, "percentage", f"Actual: {row['percentage']}, Exp: {exp_pct}", "Percentage calculation mismatch", "Medium"))
        
    # Check SGPI & Remark
    if all_passed:
        exp_sgpi = round(calc_total_acg / 23.0, 5)
        if abs(row['sgpi'] - exp_sgpi) > 0.01:
            discrepancies.append((page, sid, name, "sgpi", f"Actual: {row['sgpi']}, Exp: {exp_sgpi}", "Passed student SGPI mismatch", "High"))
        if row['remark'] != "PASS" or row['result'] != "SUCCESSFUL":
            discrepancies.append((page, sid, name, "remark", f"{row['remark']}/{row['result']}", "Remark should be PASS / SUCCESSFUL", "High"))
    else:
        if row['sgpi'] != 0.0:
            discrepancies.append((page, sid, name, "sgpi", f"Actual: {row['sgpi']}, Exp: 0.0", "Failed student SGPI should be 0.0", "High"))
        if row['remark'] not in ["FAILED", "ABSENT"]:
            discrepancies.append((page, sid, name, "remark", row['remark'], "Remark should be FAILED/ABSENT", "High"))

print(f"\nAudit complete across all 88 students and 113 columns.")
print(f"Total Discrepancies / Anomalies Found: {len(discrepancies)}")
if len(discrepancies) > 0:
    disc_df = pd.DataFrame(discrepancies, columns=["Page", "Student_ID", "Name", "Field", "Value", "Reason", "Confidence"])
    print(disc_df.to_string(index=False))
