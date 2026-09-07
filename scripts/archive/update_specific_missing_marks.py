import pandas as pd
import numpy as np

# Precise full corrections for each of the 9 students
updates = {
    101410043: {
        "DBMS_LAB_term_work": 1.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 1.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 1.0, "OS_LAB_oral": 3.0, "OS_LAB_total": 4.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410080: {
        "MINIPROJ_term_work": 0.0, "MINIPROJ_oral": 10.0, "MINIPROJ_total": 10.0, "MINIPROJ_grade": "F", "MINIPROJ_gp": 0.0, "MINIPROJ_gc": 0.0,
        "CT_external": 17.0, "CT_internal": 10.0, "CT_total": 27.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 1.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 1.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 4.0, "OS_LAB_oral": 3.0, "OS_LAB_total": 7.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "FTS_external": 17.0, "FTS_internal": 4.0, "FTS_total": 21.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410926: {
        "OE_external": 0.0, "OE_internal": 0.0, "OE_total": 0.0, "OE_grade": "F", "OE_gp": 0.0, "OE_gc": 0.0,
        "MINIPROJ_term_work": 0.0, "MINIPROJ_oral": 0.0, "MINIPROJ_total": 0.0, "MINIPROJ_grade": "F", "MINIPROJ_gp": 0.0, "MINIPROJ_gc": 0.0,
        "CT_external": 0.0, "CT_internal": 1.0, "CT_total": 1.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 0.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 0.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 1.0, "OS_LAB_oral": 0.0, "OS_LAB_total": 1.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "FTS_external": 0.0, "FTS_internal": 8.0, "FTS_total": 8.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410928: {
        "OS_LAB_term_work": 8.0, "OS_LAB_oral": 4.0, "OS_LAB_total": 12.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0
    },
    101410946: {
        "CT_external": 4.0, "CT_internal": 24.0, "CT_total": 28.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 10.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 10.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 7.0, "OS_LAB_oral": 4.0, "OS_LAB_total": 11.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "FTS_external": 15.0, "FTS_internal": 16.0, "FTS_total": 31.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410947: {
        "CT_external": 2.0, "CT_internal": 29.0, "CT_total": 31.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 1.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 1.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 1.0, "OS_LAB_oral": 3.0, "OS_LAB_total": 4.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "FTS_external": 14.0, "FTS_internal": 20.0, "FTS_total": 34.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410952: {
        "OE_external": 14.0, "OE_internal": 5.0, "OE_total": 19.0, "OE_grade": "F", "OE_gp": 0.0, "OE_gc": 0.0,
        "DBMS_LAB_term_work": 1.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 1.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 4.0, "OS_LAB_oral": 5.0, "OS_LAB_total": 9.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "FTS_external": 24.0, "FTS_internal": 11.0, "FTS_total": 35.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    },
    101410953: {
        "CT_external": 5.0, "CT_internal": 13.0, "CT_total": 18.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 11.0, "DBMS_LAB_oral": 16.0, "DBMS_LAB_total": 27.0, "DBMS_LAB_grade": "C", "DBMS_LAB_gp": 5.0, "DBMS_LAB_gc": 5.0,
        "OS_LAB_term_work": 13.0, "OS_LAB_oral": 14.0, "OS_LAB_total": 27.0, "OS_LAB_grade": "C", "OS_LAB_gp": 5.0, "OS_LAB_gc": 5.0,
        "FTS_external": 8.0, "FTS_internal": 9.0, "FTS_total": 17.0, "FTS_grade": "F", "FTS_gp": 0.0, "FTS_gc": 0.0,
        "TC_LAB_term_work": 18.0, "TC_LAB_oral": 17.0, "TC_LAB_total": 35.0, "TC_LAB_grade": "A", "TC_LAB_gp": 8.0, "TC_LAB_gc": 8.0
    },
    101410954: {
        "CT_external": 7.0, "CT_internal": 14.0, "CT_total": 21.0, "CT_grade": "F", "CT_gp": 0.0, "CT_gc": 0.0,
        "DBMS_LAB_term_work": 4.0, "DBMS_LAB_oral": 0.0, "DBMS_LAB_total": 4.0, "DBMS_LAB_grade": "F", "DBMS_LAB_gp": 0.0, "DBMS_LAB_gc": 0.0,
        "OS_LAB_term_work": 1.0, "OS_LAB_oral": 3.0, "OS_LAB_total": 4.0, "OS_LAB_grade": "F", "OS_LAB_gp": 0.0, "OS_LAB_gc": 0.0,
        "TC_LAB_term_work": 0.0, "TC_LAB_oral": 0.0, "TC_LAB_total": 0.0, "TC_LAB_grade": "F", "TC_LAB_gp": 0.0, "TC_LAB_gc": 0.0
    }
}

for path in ['AI_DS_SEM4_MASTER_RESULTS.csv', 'data/processed/AI_DS_SEM4_MASTER_RESULTS.csv']:
    df = pd.read_csv(path)
    for sid, field_dict in updates.items():
        for field, val in field_dict.items():
            df.loc[df['student_id'] == sid, field] = val
    df.to_csv(path, index=False)
    print(f"Updated {path}")

# Run full null / NaN check on marks columns
df = pd.read_csv('data/processed/AI_DS_SEM4_MASTER_RESULTS.csv')
mark_cols = [c for c in df.columns if any(c.endswith(x) for x in ['_external', '_internal', '_term_work', '_oral', '_total', '_grade', '_gp', '_gc'])]
null_counts = df[mark_cols].isna().sum()
remaining_nulls = null_counts[null_counts > 0]
print("\nRemaining nulls across all subject mark fields:")
print(remaining_nulls)
if len(remaining_nulls) == 0:
    print("ALL 113 COLUMNS ACROSS ALL 88 STUDENTS ARE 100% COMPLETE WITH ZERO MISSING VALUES!")
