from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
df = pd.read_csv(ROOT / 'data' / 'processed' / 'AI_DS_SEM4_MASTER_RESULTS.csv')
shivam = df[df['name'].str.contains('SHIVAM', case=False, na=False)].iloc[0]

passed_df = df[df['remark'] == 'PASS']
all_df = df

print("=== SHIVAM OVERVIEW ===")
print("Name:", shivam['name'])
print("Seat No:", shivam['seat_no'])
print("Rank in Class:", (df['sgpi'] > shivam['sgpi']).sum() + 1)
print(f"SGPI: {shivam['sgpi']:.2f}")
print(f"Overall Total Marks: {shivam['overall_total']} / {shivam['maximum_total']} ({shivam['percentage']:.2f}%)")
print(f"Credits Earned (aC): {shivam['aC']}, Total Credit Points (aCG): {shivam['aCG']}")

print("\n=== COHORT OVERVIEW ===")
print(f"Total Cohort: {len(df)} | Passed (All Cleared): {len(passed_df)} ({len(passed_df)/len(df)*100:.1f}%) | KTs / Failed: {len(df)-len(passed_df)}")
print(f"Class Mean SGPI (Passed): {passed_df['sgpi'].mean():.2f} (Median: {passed_df['sgpi'].median():.2f}, Std: {passed_df['sgpi'].std():.2f})")
print(f"Class Max SGPI: {df['sgpi'].max():.2f} (Shivam Vilas Bandekar)")
print(f"Class Mean Marks (Passed): {passed_df['overall_total'].mean():.1f} / 775 ({passed_df['percentage'].mean():.2f}%) | (All Students): {all_df['overall_total'].mean():.1f} ({all_df['percentage'].mean():.2f}%)")
print(f"Class Mean Credit Points aCG (Passed): {passed_df['aCG'].mean():.1f} | Shivam: {shivam['aCG']}")

subjects = [
    ('OE', 'OE_total', 'OE_gp', 'OE_grade', 'Open Elective (Admin Policy)', 50),
    ('MINIPROJ', 'MINIPROJ_total', 'MINIPROJ_gp', 'MINIPROJ_grade', 'Mini Project 2A', 75),
    ('CT', 'CT_total', 'CT_gp', 'CT_grade', 'Computational Theory (CT)', 100),
    ('DBMS', 'DBMS_total', 'DBMS_gp', 'DBMS_grade', 'Database Management System (DBMS)', 100),
    ('OS', 'OS_total', 'OS_gp', 'OS_grade', 'Operating System (OS)', 100),
    ('DBMS_LAB', 'DBMS_LAB_total', 'DBMS_LAB_gp', 'DBMS_LAB_grade', 'DBMS Lab', 50),
    ('OS_LAB', 'OS_LAB_total', 'OS_LAB_gp', 'OS_LAB_grade', 'OS Lab', 50),
    ('FTS', 'FTS_total', 'FTS_gp', 'FTS_grade', 'Fundamentals of Telecom Systems (FTS)', 100),
    ('TC_LAB', 'TC_LAB_total', 'TC_LAB_gp', 'TC_LAB_grade', 'Telecom Experiments Lab', 50),
    ('BMD', 'BMD_total', 'BMD_gp', 'BMD_grade', 'Business Model Development (BMD)', 50),
    ('DT', 'DT_total', 'DT_gp', 'DT_grade', 'Design Thinking (DT)', 50)
]

print("\n=== DETAILED SUBJECT BREAKDOWN ===")
for prefix, tot_c, gp_c, grd_c, name, max_m in subjects:
    s_tot = shivam[tot_c]
    s_gp = shivam[gp_c]
    s_grd = shivam[grd_c]
    
    p_avg_tot = passed_df[tot_c].mean()
    p_avg_gp = passed_df[gp_c].mean()
    all_avg_tot = all_df[tot_c].mean()
    max_tot = df[tot_c].max()
    
    rank = (df[tot_c] > s_tot).sum() + 1
    diff = s_tot - p_avg_tot
    pct_diff = ((s_tot - p_avg_tot) / p_avg_tot) * 100
    
    print(f"{prefix} - {name} (Max {max_m}):")
    print(f"  Shivam: {s_tot} marks (Grade: {s_grd}, GP: {s_gp}) -> Rank #{rank} in class")
    print(f"  Passed Avg: {p_avg_tot:.1f} marks (GP: {p_avg_gp:.2f}) | All Avg: {all_avg_tot:.1f} | Class Highest: {max_tot}")
    print(f"  Difference vs Passed Avg: +{diff:.1f} marks (+{pct_diff:.1f}%)\n")
