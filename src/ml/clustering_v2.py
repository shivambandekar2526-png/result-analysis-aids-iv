"""
src/ml/clustering_v2.py
=====================================================================
Student Competency Clustering Analysis (V2)
Semester IV AI & Data Science Results

Academic Clustering Strategy:
  Instead of relying on administrative pass/fail rules (where a single 1-credit
  lab KT zeroes out SGPI and masks a student's true competency), this model
  clusters ALL students based on multidimensional academic performance features:
    - Subject-wise percentages across all 11 courses (Theory, Labs, Coursework)
    - Category averages: Theory Average, Practical Average, Coursework Average
    - Performance Consistency (Subject Standard Deviation)
    - Exam Strategy Balance (External vs Internal Gap)
    - Cumulative Percentage

Reads  : data/processed/AI_DS_SEM4_MASTER_RESULTS.csv
Writes : data/processed/AI_DS_SEM4_STUDENT_CLUSTERS_V2.csv
         reports/figures/clustering_v2_elbow.png
         reports/figures/clustering_v2_silhouette.png
         reports/figures/clustering_v2_pca.png
         reports/figures/clustering_v2_radar.png
         reports/figures/clustering_v2_silhouette_detail.png
         reports/figures/clustering_v2_boxplot.png
         reports/clustering_v2_summary.txt
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# ---- Robust Project Paths ---------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_IN = ROOT / "data" / "processed" / "AI_DS_SEM4_MASTER_RESULTS.csv"
DATA_OUT = ROOT / "data" / "processed" / "AI_DS_SEM4_STUDENT_CLUSTERS_V2.csv"
FIG_DIR = ROOT / "reports" / "figures"
RPT_OUT = ROOT / "reports" / "clustering_v2_summary.txt"


def run_clustering_v2(data_path: Path | str | None = None) -> pd.DataFrame:
    """Execute the K-Means V2 competency clustering pipeline."""
    warnings.filterwarnings("ignore", category=FutureWarning)
    np.random.seed(42)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = Path(data_path) if data_path else DATA_IN
    if not csv_path.exists():
        raise FileNotFoundError(f"Master results CSV not found at: {csv_path}")

    # ---- 1. Load Data -------------------------------------------------------
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} students, {df.shape[1]} columns.")

    # ---- 2. Feature Engineering ---------------------------------------------
    THEORY = {
        "CT":   {"total": "CT_total",   "ext": "CT_external",   "int": "CT_internal",   "max_t": 100, "max_ext": 60, "max_int": 40, "cr": 3},
        "DBMS": {"total": "DBMS_total", "ext": "DBMS_external", "int": "DBMS_internal", "max_t": 100, "max_ext": 60, "max_int": 40, "cr": 3},
        "OS":   {"total": "OS_total",   "ext": "OS_external",   "int": "OS_internal",   "max_t": 100, "max_ext": 60, "max_int": 40, "cr": 3},
        "FTS":  {"total": "FTS_total",  "ext": "FTS_external",  "int": "FTS_internal",  "max_t": 100, "max_ext": 60, "max_int": 40, "cr": 3},
        "OE":   {"total": "OE_total",   "ext": "OE_external",   "int": "OE_internal",   "max_t":  50, "max_ext": 30, "max_int": 20, "cr": 2},
    }
    PRACTICALS = {
        "DBMS_LAB": {"total": "DBMS_LAB_total", "max_t": 50, "cr": 1},
        "OS_LAB":   {"total": "OS_LAB_total",   "max_t": 50, "cr": 1},
        "TC_LAB":   {"total": "TC_LAB_total",   "max_t": 50, "cr": 1},
    }
    COURSEWORK = {
        "MINIPROJ": {"total": "MINIPROJ_total", "max_t": 75, "cr": 2},
        "BMD":      {"total": "BMD_total",      "max_t": 50, "cr": 2},
        "DT":       {"total": "DT_total",       "max_t": 50, "cr": 2},
    }

    ALL_SUBJECTS = {**THEORY, **PRACTICALS, **COURSEWORK}

    # Normalise every course to 0-100%
    for subj, info in ALL_SUBJECTS.items():
        df[f"{subj}_pct"] = (pd.to_numeric(df[info["total"]], errors="coerce") / info["max_t"]) * 100

    theory_pcts  = [f"{s}_pct" for s in THEORY]
    prac_pcts    = [f"{s}_pct" for s in PRACTICALS]
    cw_pcts      = [f"{s}_pct" for s in COURSEWORK]
    all_pct_cols = [f"{s}_pct" for s in ALL_SUBJECTS]

    df["theory_avg"]     = df[theory_pcts].mean(axis=1)
    df["practical_avg"]  = df[prac_pcts].mean(axis=1)
    df["coursework_avg"] = df[cw_pcts].mean(axis=1)
    df["subject_std"]    = df[all_pct_cols].std(axis=1)

    # External vs Internal Gap
    for subj, info in THEORY.items():
        df[f"{subj}_ext_pct"] = (pd.to_numeric(df[info["ext"]], errors="coerce") / info["max_ext"]) * 100
        df[f"{subj}_int_pct"] = (pd.to_numeric(df[info["int"]], errors="coerce") / info["max_int"]) * 100

    ext_pct_cols = [f"{s}_ext_pct" for s in THEORY]
    int_pct_cols = [f"{s}_int_pct" for s in THEORY]
    df["avg_ext_pct"] = df[ext_pct_cols].mean(axis=1)
    df["avg_int_pct"] = df[int_pct_cols].mean(axis=1)
    df["ext_int_gap"] = df["avg_ext_pct"] - df["avg_int_pct"]

    # ---- 3. Feature Matrix --------------------------------------------------
    FEATURE_COLS = (
        all_pct_cols
        + ["theory_avg", "practical_avg", "coursework_avg"]
        + ["subject_std"]
        + ["ext_int_gap"]
        + ["percentage"]
    )
    X_raw = df[FEATURE_COLS].fillna(0.0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)
    print(f"Feature matrix shape: {X_scaled.shape}")

    # ---- 4. Determine Optimal K ---------------------------------------------
    K_RANGE = range(2, 9)
    inertias, sil_scores = [], []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, n_init=30, max_iter=500, random_state=42)
        lbl = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        sil_scores.append(silhouette_score(X_scaled, lbl))

    # Elbow Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(list(K_RANGE), inertias, "o-", lw=2, color="#1f77b4")
    ax.set_xlabel("Number of Clusters (K)")
    ax.set_ylabel("Inertia")
    ax.set_title("Elbow Method (Academic Performance Clustering)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_elbow.png", dpi=150)
    plt.close(fig)

    # Silhouette Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(list(K_RANGE), sil_scores, "s-", lw=2, color="#ff7f0e")
    ax.set_xlabel("Number of Clusters (K)")
    ax.set_ylabel("Mean Silhouette Score")
    ax.set_title("Silhouette Analysis")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_silhouette.png", dpi=150)
    plt.close(fig)

    CHOSEN_K = 4
    print(f"-> Selected K = {CHOSEN_K} for meaningful academic stratification.")

    # ---- 5. Fit Final K-Means Model -----------------------------------------
    final_km = KMeans(n_clusters=CHOSEN_K, n_init=50, max_iter=1000, random_state=42)
    raw_clusters = final_km.fit_predict(X_scaled)
    df["raw_cluster_id"] = raw_clusters
    final_sil = silhouette_score(X_scaled, raw_clusters)
    print(f"Overall Silhouette Score (K={CHOSEN_K}): {final_sil:.4f}")

    # Rank clusters by descending mean percentage so Cluster 0 = Top, Cluster 3 = Lowest
    ordered_cids = (
        df.groupby("raw_cluster_id")["percentage"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )
    cid_mapping = {old_cid: new_cid for new_cid, old_cid in enumerate(ordered_cids)}
    df["cluster_id"] = df["raw_cluster_id"].map(cid_mapping)

    # ---- 6. Cluster Profiling & Interpretation ------------------------------
    centroids_orig = scaler.inverse_transform(final_km.cluster_centers_)
    cent_df = pd.DataFrame(centroids_orig, columns=FEATURE_COLS)

    cluster_profiles = {}
    cluster_label_map = {
        0: "High Achievers (Consistent Top Performers)",
        1: "Above Average / Solid Performers",
        2: "Developing / Needs Academic Support",
        3: "Critical Intervention (Severe Underperformance / Absent)",
    }

    for new_cid in range(CHOSEN_K):
        old_cid = ordered_cids[new_cid]
        mask = df["cluster_id"] == new_cid
        grp = df[mask]
        c = cent_df.iloc[old_cid]

        cluster_profiles[new_cid] = {
            "count": len(grp),
            "pct_of_class": f"{len(grp) / len(df) * 100:.1f}%",
            "avg_percentage": grp["percentage"].mean(),
            "min_pct": grp["percentage"].min(),
            "max_pct": grp["percentage"].max(),
            "avg_sgpi": grp["sgpi"].mean(),
            "pass_count": int((grp["result"] == "SUCCESSFUL").sum()),
            "fail_count": int((grp["result"] != "SUCCESSFUL").sum()),
            "theory_avg": c["theory_avg"],
            "practical_avg": c["practical_avg"],
            "coursework_avg": c["coursework_avg"],
            "subject_std": c["subject_std"],
            "ext_int_gap": c["ext_int_gap"],
        }

    df["cluster_label"] = df["cluster_id"].map(cluster_label_map)

    # ---- 7. Write Comprehensive Summary Report ------------------------------
    lines = []
    lines.append("=" * 95)
    lines.append("STUDENT ACADEMIC CLUSTERING ANALYSIS -- Semester IV AI & Data Science")
    lines.append("Independent Implementation V2 (Competency-Based Clustering)")
    lines.append("=" * 95)
    lines.append(f"Source Dataset    : {csv_path.name}")
    lines.append(f"Total Students    : {len(df)}")
    lines.append(f"Features Used     : {len(FEATURE_COLS)} (Theory, Labs, Coursework, Consistency, Ext/Int Gap)")
    lines.append(f"Total Clusters    : {CHOSEN_K}")
    lines.append(f"Silhouette Score  : {final_sil:.4f}")
    lines.append("")

    for cid in range(CHOSEN_K):
        p = cluster_profiles[cid]
        label = cluster_label_map[cid]
        grp = df[df["cluster_id"] == cid].sort_values("percentage", ascending=False)

        lines.append("-" * 95)
        lines.append(f"CLUSTER {cid}: {label}")
        lines.append("-" * 95)
        lines.append(f"  Students Count : {p['count']} ({p['pct_of_class']})")
        lines.append(f"  Percentage     : Mean = {p['avg_percentage']:.2f}% (Range: {p['min_pct']:.2f}% to {p['max_pct']:.2f}%)")
        lines.append(f"  Result Split   : {p['pass_count']} Successful, {p['fail_count']} with KT/Absent")
        lines.append(f"  Theory Avg     : {p['theory_avg']:.1f}%")
        lines.append(f"  Practical Avg  : {p['practical_avg']:.1f}%")
        lines.append(f"  Coursework Avg : {p['coursework_avg']:.1f}%")
        lines.append(f"  Consistency    : Subject StdDev = {p['subject_std']:.1f} (lower = more balanced)")
        lines.append(f"  Ext-Int Gap    : {p['ext_int_gap']:+.1f} pp")
        lines.append("")
        lines.append(f"  {'Seat No':<12} | {'Student Name':<35} | {'Gender':<6} | {'Percentage':<10} | {'SGPI':<6} | {'Result':<14}")
        lines.append(f"  {'-'*12}-+-{'-'*35}-+-{'-'*6}-+-{'-'*10}-+-{'-'*6}-+-{'-'*14}")
        for _, r in grp.iterrows():
            lines.append(f"  {r['seat_no']:<12} | {r['name']:<35} | {r['gender']:<6} | {r['percentage']:>9.2f}% | {r['sgpi']:>6.2f} | {r['result']:<14}")
        lines.append("")

    report = "\n".join(lines)
    RPT_OUT.write_text(report, encoding="utf-8")
    print(f"Report written to: {RPT_OUT}")

    # ---- 8. Visualisations --------------------------------------------------
    colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"]

    # 8a. PCA Scatter Plot
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df["pca1"] = X_pca[:, 0]
    df["pca2"] = X_pca[:, 1]

    fig, ax = plt.subplots(figsize=(10, 7))
    for cid in range(CHOSEN_K):
        m = df["cluster_id"] == cid
        ax.scatter(
            df.loc[m, "pca1"], df.loc[m, "pca2"],
            c=colors[cid], s=60, alpha=0.85, edgecolors="k", lw=0.4,
            label=f"C{cid}: {cluster_label_map[cid]} (n={m.sum()})"
        )

    # Centroids in PCA space
    centroids_ordered = np.array([final_km.cluster_centers_[old_cid] for old_cid in ordered_cids])
    centroids_pca = pca.transform(centroids_ordered)
    ax.scatter(
        centroids_pca[:, 0], centroids_pca[:, 1],
        marker="X", s=220, c="black", zorder=5, label="Cluster Centroids"
    )

    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    ax.set_title("Student Academic Competency Clusters (PCA Projection)")
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_pca.png", dpi=150)
    plt.close(fig)

    # 8b. Radar Chart of Domain Averages
    radar_feats  = ["theory_avg", "practical_avg", "coursework_avg"]
    radar_labels = ["Theory", "Practical", "Coursework"]
    N_r = len(radar_feats)
    angles = np.linspace(0, 2 * np.pi, N_r, endpoint=False).tolist() + [0]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for cid in range(CHOSEN_K):
        p = cluster_profiles[cid]
        vals = [p["theory_avg"], p["practical_avg"], p["coursework_avg"], p["theory_avg"]]
        ax.plot(angles, vals, "o-", lw=2.2, color=colors[cid], label=f"C{cid}: {cluster_label_map[cid]}")
        ax.fill(angles, vals, alpha=0.12, color=colors[cid])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_labels, fontsize=12)
    ax.set_title("Cluster Performance Profiles Across Domains", y=1.08, fontsize=13)
    ax.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.45, 1.15))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_radar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 8c. Boxplot of Percentage Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    box_data = [df.loc[df["cluster_id"] == cid, "percentage"].values for cid in range(CHOSEN_K)]
    box_labels = [f"C{cid}\n({cluster_label_map[cid][:18]}...)" for cid in range(CHOSEN_K)]

    bp = ax.boxplot(box_data, tick_labels=box_labels, patch_artist=True, widths=0.55)
    for patch, col in zip(bp["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.7)

    ax.set_ylabel("Overall Percentage (%)", fontsize=11)
    ax.set_title("Grade Percentage Distribution Across Academic Clusters", fontsize=12)
    ax.grid(True, alpha=0.2, axis="y")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_boxplot.png", dpi=150)
    plt.close(fig)

    # 8d. Silhouette Plot per Cluster
    fig, ax = plt.subplots(figsize=(8, 6))
    sil_vals = silhouette_samples(X_scaled, df["cluster_id"])
    y_lo = 10
    for cid in range(CHOSEN_K):
        ith = np.sort(sil_vals[df["cluster_id"] == cid])
        y_hi = y_lo + len(ith)
        ax.fill_betweenx(np.arange(y_lo, y_hi), 0, ith, facecolor=colors[cid], edgecolor=colors[cid], alpha=0.7)
        ax.text(-0.05, y_lo + len(ith) / 2, f"C{cid}", fontsize=9)
        y_lo = y_hi + 10
    ax.axvline(final_sil, color="red", ls="--", label=f"Mean Silhouette = {final_sil:.3f}")
    ax.set_xlabel("Silhouette coefficient")
    ax.set_ylabel("Students (sorted within cluster)")
    ax.set_title("Silhouette Plot Across Clusters")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_v2_silhouette_detail.png", dpi=150)
    plt.close(fig)

    # ---- 9. Export Clean Clustered Dataset -----------------------------------
    drop_cols = [c for c in df.columns if c.endswith("_ext_pct") or c.endswith("_int_pct")] + ["pca1", "pca2", "raw_cluster_id"]
    export_df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
    export_df.to_csv(DATA_OUT, index=False)
    print(f"Clustered dataset exported to: {DATA_OUT}")

    # ---- 10. Summary --------------------------------------------------------
    print("\n" + "=" * 80)
    print("ACADEMIC CLUSTERING SUMMARY (V2)")
    print("=" * 80)
    for cid in range(CHOSEN_K):
        p = cluster_profiles[cid]
        lbl = cluster_label_map[cid]
        print(f"  C{cid} | {lbl:<52s} | n={p['count']:>2} | Mean%={p['avg_percentage']:>5.1f}% [{p['min_pct']:.1f}%-{p['max_pct']:.1f}%]")
    print("=" * 80)

    return export_df


if __name__ == "__main__":
    run_clustering_v2()
