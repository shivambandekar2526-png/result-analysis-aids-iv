import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PROCESSED_DATA_PATH, FIGURES_DIR, SUBJECTS

def load_data():
    return pd.read_csv(PROCESSED_DATA_PATH)

def generate_eda_charts():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    df = load_data()
    
    # 1. SGPA Distribution Plot
    plt.figure(figsize=(9, 5))
    passed_df = df[df["result"] == "SUCCESSFUL"]
    plt.hist(passed_df["sgpi"], bins=12, color="#2b5c8f", edgecolor="black", alpha=0.85)
    plt.axvline(passed_df["sgpi"].mean(), color="#e74c3c", linestyle="--", linewidth=2, label=f"Mean SGPA: {passed_df['sgpi'].mean():.2f}")
    plt.axvline(passed_df["sgpi"].median(), color="#f39c12", linestyle=":", linewidth=2, label=f"Median SGPA: {passed_df['sgpi'].median():.2f}")
    plt.title("SGPA Distribution (Passing Students)", fontsize=14, fontweight="bold")
    plt.xlabel("SGPA (SGPI)", fontsize=12)
    plt.ylabel("Number of Students", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "sgpa_distribution.png"), dpi=200)
    plt.close()
    
    # 2. Result Breakdown Pie Chart
    plt.figure(figsize=(7, 6))
    res_counts = df["result"].value_counts()
    colors = ["#2ecc71", "#e74c3c", "#95a5a6"]
    plt.pie(res_counts, labels=res_counts.index, autopct="%1.1f%%", startangle=140, colors=colors[:len(res_counts)],
            explode=[0.05 if i == 0 else 0 for i in range(len(res_counts))], textprops={"fontsize": 12, "weight": "bold"})
    plt.title("Overall Examination Result Breakdown (N=88)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "result_breakdown.png"), dpi=200)
    plt.close()
    
    # 3. Subject-wise Average Marks & Pass Rates
    subj_names = []
    avg_pcts = []
    pass_rates = []
    
    for s in SUBJECTS:
        pfx = s["prefix"]
        tot_col = f"{pfx}_total"
        grd_col = f"{pfx}_grade"
        
        avg_pct = (df[tot_col].mean() / s["max_tot"]) * 100.0
        pass_rate = (df[grd_col] != "F").mean() * 100.0
        
        subj_names.append(s["prefix"])
        avg_pcts.append(avg_pct)
        pass_rates.append(pass_rate)
        
    x = np.arange(len(subj_names))
    width = 0.38
    
    plt.figure(figsize=(12, 6))
    plt.bar(x - width/2, avg_pcts, width, label="Average Score (%)", color="#3498db", edgecolor="black")
    plt.bar(x + width/2, pass_rates, width, label="Pass Rate (%)", color="#2ecc71", edgecolor="black")
    plt.xticks(x, subj_names, rotation=35, ha="right", fontsize=10, fontweight="bold")
    plt.ylabel("Percentage (%)", fontsize=12)
    plt.title("Subject Performance: Average Score vs Pass Rate", fontsize=14, fontweight="bold")
    plt.ylim(0, 105)
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "subject_performance_comparison.png"), dpi=200)
    plt.close()
    
    print(f"Successfully generated and saved EDA figures to {FIGURES_DIR}")

if __name__ == "__main__":
    generate_eda_charts()
