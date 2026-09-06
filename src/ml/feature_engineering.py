import os, sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUBJECTS, PROCESSED_DATA_PATH

def load_and_engineer_features():
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    # Identify subject subsets
    theory_subjs = [s for s in SUBJECTS if s["type"] == "THEORY"]
    lab_subjs = [s for s in SUBJECTS if s["type"] in ["TW_ORAL", "TW_ONLY"]]
    
    # 1. Total Theory Scores & Percentage
    theory_totals = [f"{s['prefix']}_total" for s in theory_subjs]
    theory_max = sum(s["max_tot"] for s in theory_subjs) # 450
    df["theory_total_score"] = df[theory_totals].sum(axis=1)
    df["theory_avg_pct"] = (df["theory_total_score"] / theory_max) * 100.0
    
    # 2. Total Lab / Project Scores & Percentage
    lab_totals = [f"{s['prefix']}_total" for s in lab_subjs]
    lab_max = sum(s["max_tot"] for s in lab_subjs) # 325
    df["lab_total_score"] = df[lab_totals].sum(axis=1)
    df["lab_avg_pct"] = (df["lab_total_score"] / lab_max) * 100.0
    
    # 3. Internal vs External Theory Marks
    ext_cols = [f"{s['prefix']}_external" for s in theory_subjs]
    int_cols = [f"{s['prefix']}_internal" for s in theory_subjs]
    df["external_total_score"] = df[ext_cols].sum(axis=1)
    df["internal_total_score"] = df[int_cols].sum(axis=1)
    df["internal_to_external_ratio"] = df["internal_total_score"] / (df["external_total_score"] + 1e-5)
    df["lab_to_theory_ratio"] = (df["lab_avg_pct"]) / (df["theory_avg_pct"] + 1e-5)
    
    # 4. Academic Health & Failure Metrics
    grade_cols = [f"{s['prefix']}_grade" for s in SUBJECTS]
    df["failed_subjects_count"] = (df[grade_cols] == "F").sum(axis=1)
    df["is_passed"] = (df["result"] == "SUCCESSFUL").astype(int)
    df["is_at_risk"] = ((df["failed_subjects_count"] > 0) | (df["sgpi"] < 6.0)).astype(int)
    df["is_distinction"] = ((df["is_passed"] == 1) & (df["sgpi"] >= 7.75)).astype(int)
    
    return df

if __name__ == "__main__":
    feat_df = load_and_engineer_features()
    print(f"Feature engineering completed: {feat_df.shape}")
    print(feat_df[["name", "theory_avg_pct", "lab_avg_pct", "failed_subjects_count", "is_at_risk"]].head())
