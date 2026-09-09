from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / 'data' / 'processed' / 'AI_DS_SEM4_MASTER_RESULTS.csv')
passed_df = df[df['remark'] == 'PASS']

subjects = [
    ('OE', 'Open Elective (Policy of Shivaji Maharaj)', 50, True, 'OE_external', 'OE_internal', 'OE_total', 'OE_grade', 'OE_gp'),
    ('MINIPROJ', 'Mini Project 2A', 75, False, None, None, 'MINIPROJ_total', 'MINIPROJ_grade', 'MINIPROJ_gp'),
    ('CT', 'Computational Theory (CT)', 100, True, 'CT_external', 'CT_internal', 'CT_total', 'CT_grade', 'CT_gp'),
    ('DBMS', 'Database Management System (DBMS)', 100, True, 'DBMS_external', 'DBMS_internal', 'DBMS_total', 'DBMS_grade', 'DBMS_gp'),
    ('OS', 'Operating System (OS)', 100, True, 'OS_external', 'OS_internal', 'OS_total', 'OS_grade', 'OS_gp'),
    ('DBMS_LAB', 'DBMS Lab', 50, False, None, None, 'DBMS_LAB_total', 'DBMS_LAB_grade', 'DBMS_LAB_gp'),
    ('OS_LAB', 'OS Lab', 50, False, None, None, 'OS_LAB_total', 'OS_LAB_grade', 'OS_LAB_gp'),
    ('FTS', 'Fundamentals of Telecom Systems (FTS)', 100, True, 'FTS_external', 'FTS_internal', 'FTS_total', 'FTS_grade', 'FTS_gp'),
    ('TC_LAB', 'Telecom Experiments Lab', 50, False, None, None, 'TC_LAB_total', 'TC_LAB_grade', 'TC_LAB_gp'),
    ('BMD', 'Business Model Development (BMD)', 50, False, None, None, 'BMD_total', 'BMD_grade', 'BMD_gp'),
    ('DT', 'Design Thinking (DT)', 50, False, None, None, 'DT_total', 'DT_grade', 'DT_gp')
]

results = []

for code, name, max_m, is_theory, ext_c, int_c, tot_c, grd_c, gp_c in subjects:
    fail_count = (df[grd_c] == 'F').sum()
    fail_pct = (fail_count / len(df)) * 100
    pass_pct = 100.0 - fail_pct
    
    all_mean_tot = df[tot_c].mean()
    all_pct_mean = (all_mean_tot / max_m) * 100
    all_mean_gp = df[gp_c].mean()
    
    passed_mean_tot = passed_df[tot_c].mean()
    passed_pct_mean = (passed_mean_tot / max_m) * 100
    passed_mean_gp = passed_df[gp_c].mean()
    
    ext_fail_count = 0
    ext_avg = None
    ext_pct = None
    if is_theory and ext_c:
        # Ext max: 60 for CT/DBMS/OS/FTS, 30 for OE
        ext_max = 30 if code == 'OE' else 60
        ext_avg = df[ext_c].mean()
        ext_pct = (ext_avg / ext_max) * 100
        ext_min = 12 if code == 'OE' else 24
        ext_fail_count = (df[ext_c] < ext_min).sum()
        
    results.append({
        'code': code,
        'name': name,
        'max_marks': max_m,
        'is_theory': is_theory,
        'fail_count': fail_count,
        'fail_pct': fail_pct,
        'pass_pct': pass_pct,
        'all_mean_tot': all_mean_tot,
        'all_pct_mean': all_pct_mean,
        'all_mean_gp': all_mean_gp,
        'passed_mean_tot': passed_mean_tot,
        'passed_pct_mean': passed_pct_mean,
        'passed_mean_gp': passed_mean_gp,
        'ext_avg': ext_avg,
        'ext_pct': ext_pct,
        'ext_fail_count': ext_fail_count
    })

res_df = pd.DataFrame(results)

print("=== SUBJECT DIFFICULTY METRICS (ALL 88 STUDENTS) ===")
print(res_df.sort_values(by='fail_count', ascending=False)[['code', 'name', 'fail_count', 'fail_pct', 'all_pct_mean', 'all_mean_gp', 'passed_mean_gp']].to_string(index=False))

print("\n=== THEORY EXTERNAL EXAM PERFORMANCE ===")
theory_df = res_df[res_df['is_theory'] == True].sort_values(by='ext_fail_count', ascending=False)
print(theory_df[['code', 'name', 'ext_fail_count', 'ext_avg', 'ext_pct', 'fail_count', 'all_pct_mean']].to_string(index=False))
