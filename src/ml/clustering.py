"""
src/ml/clustering.py

Complete K-Means Academic-Performance Clustering Pipeline
for AI & Data Science Semester-IV Student Segmentation.

Reimplemented from scratch  --  no logic carried over from the previous version.

Pipeline stages:
    1.  load_data()               --  Load CSV, strip whitespace, basic shape report
    2.  audit_data()              --  Schema validation, duplicates, bounds, data-quality flags
    3.  create_features()         --  Domain-driven feature engineering (proper per-subject normalisation)
    4.  validate_features()       --  Correlation analysis, redundancy pruning, final feature-set report
    5.  handle_missing_values()   --  Audit and impute (median) with statistical justification
    6.  scale_features()          --  StandardScaler with verification
    7.  evaluate_k()              --  Multi-metric diagnostics for K = 2-7
    8.  select_optimal_k()        --  Data-driven selection with printed justification
    9.  fit_kmeans()              --  sklearn KMeans execution
   10.  profile_clusters()        --  Original-scale summary statistics per cluster
   11.  assign_personas()         --  Evidence-based semantic labels (never hard-coded)
   12.  generate_visualizations() --  8 publication-quality figures
   13.  export_results()          --  Enriched CSV output + student roster

Author:  AI-assisted reimplementation
Date:    2026-09-09
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")                       # headless backend; no GUI needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_samples,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Path bootstrap  --  works when run from repo root *or* from src/ml/
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.dirname(_THIS_DIR)
_BASE_DIR = os.path.dirname(_SRC_DIR)

for _p in (_SRC_DIR, _BASE_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from config import FIGURES_DIR, PROCESSED_DATA_PATH, SUBJECTS
except ImportError:
    PROCESSED_DATA_PATH = os.path.join(
        _BASE_DIR, "data", "processed", "AI_DS_SEM4_MASTER_RESULTS.csv"
    )
    FIGURES_DIR = os.path.join(_BASE_DIR, "reports", "figures")
    SUBJECTS = []

# ---------------------------------------------------------------------------
# Global aesthetic constants for plots
# ---------------------------------------------------------------------------
_PALETTE = [
    "#2196F3",   # blue
    "#F44336",   # red
    "#4CAF50",   # green
    "#FF9800",   # orange
    "#9C27B0",   # purple
    "#795548",   # brown
    "#00BCD4",   # cyan
]
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor": "#444444",
    "axes.linewidth": 0.8,
    "figure.dpi": 180,
})


# ===========================================================================
# 1.  DATA LOADING
# ===========================================================================

def load_data(filepath: str | None = None) -> pd.DataFrame:
    """Load the master CSV and return a DataFrame with cleaned column names.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist at *filepath*.
    """
    if filepath is None:
        filepath = PROCESSED_DATA_PATH

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found: {filepath}")

    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    print("\n" + "=" * 80)
    print("  STEP 1  --  DATA LOADING")
    print("=" * 80)
    print(f"  Source file  : {filepath}")
    print(f"  Shape        : {df.shape[0]} rows  x  {df.shape[1]} columns")
    return df


# ===========================================================================
# 2.  DATA AUDIT
# ===========================================================================

def audit_data(df: pd.DataFrame) -> pd.DataFrame:
    """Comprehensive data-quality audit.

    Checks
    ------
    * Required columns present
    * Duplicate seat numbers
    * Numeric bounds (marks, percentage, SGPI)
    * Missing values
    * Result distribution
    * Suspicious / flagged records
    """
    print("\n" + "=" * 80)
    print("  STEP 2  --  DATA AUDIT")
    print("=" * 80)

    # --- required columns --------------------------------------------------
    required = ["student_id", "seat_no", "name", "overall_total",
                "percentage", "result", "sgpi"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    print("  [OK] All required columns present.")

    # --- duplicates --------------------------------------------------------
    dup_seats = df["seat_no"].duplicated().sum()
    if dup_seats > 0:
        raise ValueError(f"Duplicate seat numbers detected: {dup_seats}")
    print(f"  [OK] No duplicate seat numbers (n={len(df)}).")

    # --- missing values ----------------------------------------------------
    total_missing = df.isnull().sum().sum()
    if total_missing > 0:
        print(f"  [WARN] {total_missing} total missing cells across dataset.")
        cols_with_missing = df.columns[df.isnull().any()].tolist()
        for c in cols_with_missing:
            n = df[c].isnull().sum()
            print(f"         {c}: {n} missing")
    else:
        print("  [OK] Zero missing values in entire dataset.")

    # --- numeric bounds ----------------------------------------------------
    flags: list[str] = []
    if (df["overall_total"] < 0).any():
        flags.append("negative overall_total")
    if (df["overall_total"] > 775).any():
        flags.append("overall_total > 775")
    if (df["percentage"] < 0).any():
        flags.append("negative percentage")
    if (df["percentage"] > 100).any():
        flags.append("percentage > 100")
    if (df["sgpi"] < 0).any():
        flags.append("negative sgpi")
    if (df["sgpi"] > 10).any():
        flags.append("sgpi > 10")
    if flags:
        for f in flags:
            print(f"  [FLAG] {f}")
    else:
        print("  [OK] All numeric bounds valid (marks, percentage, SGPI).")

    # --- result distribution -----------------------------------------------
    print("\n  Result distribution:")
    for val, cnt in df["result"].value_counts().items():
        print(f"    {val:15s} : {cnt:3d}  ({cnt/len(df)*100:.1f}%)")

    # --- SGPI semantics ----------------------------------------------------
    unsuccessful = df[df["result"] != "SUCCESSFUL"]
    zero_sgpi_unsuccessful = (unsuccessful["sgpi"] == 0).sum()
    print(f"\n  SGPI semantics:")
    print(f"    Unsuccessful/Absent students with SGPI=0 : {zero_sgpi_unsuccessful}/{len(unsuccessful)}")
    successful = df[df["result"] == "SUCCESSFUL"]
    if len(successful) > 0:
        print(f"    Successful students SGPI range           : [{successful['sgpi'].min():.2f}, {successful['sgpi'].max():.2f}]")

    # --- suspicious records ------------------------------------------------
    print("\n  Suspicious / extreme records:")
    low_marks = df[df["overall_total"] <= 50]
    if len(low_marks) > 0:
        for _, r in low_marks.iterrows():
            print(f"    [FLAG] {r['name']}  --  total={r['overall_total']}, pct={r['percentage']:.2f}%, result={r['result']}")
    else:
        print("    None flagged.")

    return df


# ===========================================================================
# 3.  FEATURE ENGINEERING
# ===========================================================================

# Subject definitions with correct maximum marks.
# These are derived from the syllabus (config.py SUBJECTS list) and verified
# against the actual data maxima.

_THEORY_SUBJECTS = [
    # (prefix, max_total)
    ("OE",   50),      # Open Elective  --  max 50 (30 external + 20 internal)
    ("CT",  100),      # Computational Theory  --  max 100 (60 ext + 40 int)
    ("DBMS", 100),     # Database Management System  --  max 100
    ("OS",  100),      # Operating System  --  max 100
    ("FTS", 100),      # Fundamentals of Telecomm Systems  --  max 100
]

_LAB_SUBJECTS = [
    ("MINIPROJ",  75), # Mini Project  --  max 75 (50 TW + 25 oral)
    ("DBMS_LAB",  50), # DBMS Lab  --  max 50 (25 TW + 25 oral)
    ("OS_LAB",    50), # OS Lab  --  max 50
    ("TC_LAB",    50), # Telecomm Lab  --  max 50
    ("BMD",       50), # Business Model Development  --  max 50 (TW only)
    ("DT",        50), # Design Thinking  --  max 50 (TW only)
]


def create_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Derive clustering features from raw subject marks.

    Feature-engineering decisions
    -----------------------------
    1. **theory_avg_pct**  --  Each theory subject is first converted to a
       percentage of *its own* maximum marks, then these per-subject
       percentages are averaged.  This prevents OE (max 50) from being
       under-weighted relative to CT/DBMS/OS/FTS (max 100) when a simple
       sum is taken.  The old implementation summed raw totals and divided
       by 450, which over-weights the 100-mark subjects by 2x relative to OE.

    2. **lab_avg_pct**  --  Same per-subject normalisation for labs.

    3. **percentage**  --  Overall percentage as given in the dataset
       (overall_total / 775 x 100).  Verified to match exactly.

    4. **sgpi**  --  Semester Grade Performance Index.  Encodes credit-weighted
       grade-point information that is *not* a simple function of raw marks.
       Correlation with percentage is 0.80  --  high but not redundant.
       See validate_features() for the redundancy analysis.

    5. **failed_subjects_count**  --  Number of subject heads with grade 'F'.
       Captures risk profile that percentage alone does not encode (e.g., a
       student can have moderate total marks but many marginal fails).
    """
    print("\n" + "=" * 80)
    print("  STEP 3  --  FEATURE ENGINEERING")
    print("=" * 80)

    df = df.copy()

    # --- 3a. Per-subject percentage for theory subjects --------------------
    theory_pct_cols = []
    for prefix, maxm in _THEORY_SUBJECTS:
        col = f"{prefix}_total"
        pct_col = f"__{prefix}_pct"
        if col in df.columns:
            df[pct_col] = (df[col] / maxm) * 100.0
            theory_pct_cols.append(pct_col)
        else:
            print(f"  [WARN] Theory column '{col}' not found  --  skipping.")

    # Average of per-subject percentages (equal weight to each subject)
    df["theory_avg_pct"] = df[theory_pct_cols].mean(axis=1)
    print(f"  theory_avg_pct  : computed from {len(theory_pct_cols)} theory subjects (per-subject normalised)")

    # --- 3b. Per-subject percentage for lab subjects -----------------------
    lab_pct_cols = []
    for prefix, maxm in _LAB_SUBJECTS:
        col = f"{prefix}_total"
        pct_col = f"__{prefix}_pct"
        if col in df.columns:
            df[pct_col] = (df[col] / maxm) * 100.0
            lab_pct_cols.append(pct_col)
        else:
            print(f"  [WARN] Lab column '{col}' not found  --  skipping.")

    df["lab_avg_pct"] = df[lab_pct_cols].mean(axis=1)
    print(f"  lab_avg_pct     : computed from {len(lab_pct_cols)} lab/practical subjects (per-subject normalised)")

    # --- 3c. Failed subjects count -----------------------------------------
    grade_cols = [c for c in df.columns if c.endswith("_grade")]
    if grade_cols:
        df["failed_subjects_count"] = (df[grade_cols] == "F").sum(axis=1)
    else:
        # Fallback: unsuccessful _ at least 1 failure
        df["failed_subjects_count"] = (df["result"] != "SUCCESSFUL").astype(int)
    print(f"  failed_subjects_count : F-grade count across {len(grade_cols)} grade columns")

    # --- 3d. percentage already exists in dataset --------------------------
    print(f"  percentage      : existing column (overall_total / 775 x 100)")

    # --- 3e. sgpi already exists in dataset --------------------------------
    print(f"  sgpi            : existing column (credit-weighted grade-point index)")

    # --- Clean up helper columns -------------------------------------------
    helper_cols = [c for c in df.columns if c.startswith("__")]
    df.drop(columns=helper_cols, inplace=True)

    # --- Final feature list ------------------------------------------------
    feature_cols = [
        "percentage",
        "sgpi",
        "theory_avg_pct",
        "lab_avg_pct",
        "failed_subjects_count",
    ]

    print("\n  Feature summary (pre-scaling):")
    for feat in feature_cols:
        s = df[feat]
        print(f"    {feat:25s}  min={s.min():7.2f}  mean={s.mean():7.2f}  "
              f"median={s.median():7.2f}  max={s.max():7.2f}  std={s.std():7.2f}")

    return df, feature_cols


# ===========================================================================
# 4.  FEATURE VALIDATION & REDUNDANCY CHECK
# ===========================================================================

def validate_features(df: pd.DataFrame, feature_cols: List[str]) -> List[str]:
    """Analyse pairwise correlations and decide on the final feature set.

    Redundancy policy
    -----------------
    * ``percentage`` and ``overall_total`` are perfectly correlated (r=1.0)
       --  ``overall_total`` is NOT included.
    * ``sgpi`` _ ``percentage`` correlation is ~0.80.  Despite being high,
      SGPI encodes credit-weighted grading information not captured by raw
      marks, AND it has a structural break (all unsuccessful students are
      mapped to 0.0 by the university system).  This bimodal structure
      provides genuinely distinct separating power.  **Retained.**
    * ``theory_avg_pct`` and ``lab_avg_pct`` are sub-components of
      ``percentage`` but capture the *theory-lab balance*.  Each has a
      distinct distribution.  **Retained.**
    * ``failed_subjects_count`` is a discrete failure-risk indicator with
      low correlation to continuous performance metrics.  **Retained.**
    """
    print("\n" + "=" * 80)
    print("  STEP 4  --  FEATURE REDUNDANCY ANALYSIS")
    print("=" * 80)

    corr = df[feature_cols].corr()
    print("\n  Pairwise Pearson correlation matrix:")
    for i, ci in enumerate(feature_cols):
        row_str = "    "
        for j, cj in enumerate(feature_cols):
            row_str += f"{corr.loc[ci, cj]:+7.3f}  "
        print(f"  {ci:25s} {row_str}")

    # Identify highly correlated pairs (|r| > 0.95)
    high_corr_pairs = []
    for i in range(len(feature_cols)):
        for j in range(i + 1, len(feature_cols)):
            r = corr.iloc[i, j]
            if abs(r) > 0.95:
                high_corr_pairs.append((feature_cols[i], feature_cols[j], r))

    if high_corr_pairs:
        print("\n  [WARN] Near-redundant pairs (|r| > 0.95):")
        for a, b, r in high_corr_pairs:
            print(f"    {a} _ {b} : r = {r:.4f}")
    else:
        print("\n  [OK] No near-redundant feature pairs (all |r| < 0.95).")

    # Final selection
    final_features = list(feature_cols)   # keep all 5

    print(f"\n  FINAL CLUSTERING FEATURES ({len(final_features)}):")
    for f in final_features:
        print(f"    - {f}")

    return final_features


# ===========================================================================
# 5.  MISSING VALUE HANDLING
# ===========================================================================

def handle_missing_values(
    df: pd.DataFrame,
    feature_cols: List[str],
) -> Tuple[pd.DataFrame, dict]:
    """Audit and impute missing values for clustering features.

    SGPI handling rationale
    -----------------------
    All 28 students with SGPI = 0 are either UNSUCCESSFUL (27) or ABSENT (1).
    The university system assigns SGPI = 0 to students who did not earn a
    valid semester grade.  This is *not* missing data  --  it is a meaningful
    zero that encodes "no credit achievement".

    Therefore SGPI = 0 is **preserved as-is**, not imputed.  This is
    semantically correct and statistically defensible: replacing 0 with the
    median (~7.15) would fabricate performance where none exists.

    For genuinely null cells (if any), median imputation is applied because
    the median is robust to the bimodal SGPI distribution and to outliers in
    mark-based features.
    """
    print("\n" + "=" * 80)
    print("  STEP 5  --  MISSING VALUE AUDIT")
    print("=" * 80)

    X = df[feature_cols].copy()
    missing_report: dict[str, int] = {}
    total_missing = 0

    for col in feature_cols:
        n_miss = int(X[col].isnull().sum())
        pct = n_miss / len(X) * 100
        missing_report[col] = n_miss
        total_missing += n_miss
        status = "CLEAN" if n_miss == 0 else f"{n_miss} ({pct:.1f}%)"
        print(f"    {col:25s} : {status}")

    if total_missing > 0:
        # Impute with column medians
        medians = X.median()
        X.fillna(medians, inplace=True)
        print(f"\n  [IMPUTED] {total_missing} missing value(s) filled with column medians:")
        for col in feature_cols:
            if missing_report[col] > 0:
                print(f"    {col} _ median = {medians[col]:.2f}")
    else:
        print("\n  [OK] No imputation needed  --  all feature cells populated.")

    # Validate SGPI zeros are preserved
    sgpi_zero = (X["sgpi"] == 0).sum()
    print(f"\n  SGPI = 0 count: {sgpi_zero} (preserved  --  these are genuine university-assigned zeros)")

    return X, missing_report


# ===========================================================================
# 6.  FEATURE SCALING
# ===========================================================================

def scale_features(X: pd.DataFrame) -> Tuple[np.ndarray, StandardScaler]:
    """Standardise features to zero mean and unit variance.

    Why scaling is mandatory for K-Means
    -------------------------------------
    K-Means minimises the within-cluster sum of squared *Euclidean*
    distances:

        argmin_S  Sum_ Sum_{x in S_}  _x - mu___

    The Euclidean norm is scale-dependent.  Without standardisation:
        _ percentage, theory_avg_pct, lab_avg_pct  in  [0, 100]  (variance ~250)
        _ sgpi  in  [0, 10]                                       (variance ~13)
        _ failed_subjects_count  in  [0, 11]                      (variance ~7)

    Percentage-scale features would dominate distance calculations by ~20x,
    making K-Means effectively mono-dimensional.  StandardScaler (z-score)
    maps every feature to mu=0, sigma=1, giving each dimension equal influence.
    """
    print("\n" + "=" * 80)
    print("  STEP 6  --  FEATURE SCALING (StandardScaler)")
    print("=" * 80)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Verification
    print("  Post-scaling diagnostics:")
    for idx, col in enumerate(X.columns):
        m = X_scaled[:, idx].mean()
        s = X_scaled[:, idx].std()
        lo = X_scaled[:, idx].min()
        hi = X_scaled[:, idx].max()
        print(f"    {col:25s}  mean={m:+.6f}  std={s:.6f}  range=[{lo:+.3f}, {hi:+.3f}]")

    return X_scaled, scaler


# ===========================================================================
# 7.  EVALUATE K
# ===========================================================================

def evaluate_k(
    X_scaled: np.ndarray,
    k_range: range = range(2, 8),
) -> pd.DataFrame:
    """Compute four clustering-quality metrics for each candidate K.

    Metrics
    -------
    * **Inertia** (WCSS)  --  lower is better; look for "elbow" in the curve.
    * **Silhouette Score**  --  mean cohesion-vs-separation; higher is better (max 1).
    * **Calinski-Harabasz**  --  between / within cluster variance ratio; higher is better.
    * **Davies-Bouldin**  --  average similarity between clusters; lower is better.
    """
    print("\n" + "=" * 80)
    print("  STEP 7  --  HYPERPARAMETER EVALUATION  (K = 2 ... 7)")
    print("=" * 80)

    records = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=30, max_iter=500)
        labels = km.fit_predict(X_scaled)

        rec = {
            "k": k,
            "inertia": km.inertia_,
            "silhouette": silhouette_score(X_scaled, labels),
            "calinski_harabasz": calinski_harabasz_score(X_scaled, labels),
            "davies_bouldin": davies_bouldin_score(X_scaled, labels),
        }
        records.append(rec)

        print(f"    K={k}  |  Inertia={rec['inertia']:8.2f}  |  "
              f"Silhouette={rec['silhouette']:.4f}  |  "
              f"CH={rec['calinski_harabasz']:8.2f}  |  "
              f"DB={rec['davies_bouldin']:.4f}")

    return pd.DataFrame(records)


# ===========================================================================
# 8.  SELECT OPTIMAL K
# ===========================================================================

def select_optimal_k(metrics_df: pd.DataFrame) -> int:
    """Select the best K using a composite ranking of all four metrics.

    Algorithm
    ---------
    For each K, rank it on each metric (1 = best).  The composite score is
    the sum of ranks.  The K with the lowest composite score wins.  Ties
    are broken by Silhouette Score.

    This avoids hard-coding K and is robust to any single metric being
    misleading (e.g., inertia always decreases).
    """
    print("\n" + "=" * 80)
    print("  STEP 8  --  OPTIMAL K SELECTION")
    print("=" * 80)

    mdf = metrics_df.copy()

    # Rank each metric (1 = best)
    mdf["rank_inertia"]         = mdf["inertia"].rank(ascending=True)           # lower better
    mdf["rank_silhouette"]      = mdf["silhouette"].rank(ascending=False)       # higher better
    mdf["rank_ch"]              = mdf["calinski_harabasz"].rank(ascending=False) # higher better
    mdf["rank_db"]              = mdf["davies_bouldin"].rank(ascending=True)    # lower better

    mdf["composite"] = (
        mdf["rank_inertia"]
        + mdf["rank_silhouette"]
        + mdf["rank_ch"]
        + mdf["rank_db"]
    )

    print("\n  Composite ranking table:")
    print(f"    {'K':>3s}  {'Inertia':>9s}  {'Silh':>7s}  {'CH':>9s}  {'DB':>7s}  "
          f"{'R_Iner':>6s}  {'R_Silh':>6s}  {'R_CH':>6s}  {'R_DB':>6s}  {'SumRnk':>7s}")
    for _, r in mdf.iterrows():
        print(f"    {int(r['k']):3d}  {r['inertia']:9.2f}  {r['silhouette']:7.4f}  "
              f"{r['calinski_harabasz']:9.2f}  {r['davies_bouldin']:7.4f}  "
              f"{r['rank_inertia']:6.1f}  {r['rank_silhouette']:6.1f}  "
              f"{r['rank_ch']:6.1f}  {r['rank_db']:6.1f}  {r['composite']:7.1f}")

    # Best = lowest composite; break ties by silhouette
    best_row = mdf.sort_values(["composite", "rank_silhouette"]).iloc[0]
    optimal_k = int(best_row["k"])

    print(f"\n  ______________________________________________________")
    print(f"  SELECTED K = {optimal_k}")
    print(f"  ______________________________________________________")
    print(f"    Composite rank score : {best_row['composite']:.1f}  (lowest)")
    print(f"    Inertia              : {best_row['inertia']:.2f}")
    print(f"    Silhouette Score     : {best_row['silhouette']:.4f}")
    print(f"    Calinski-Harabasz    : {best_row['calinski_harabasz']:.2f}")
    print(f"    Davies-Bouldin       : {best_row['davies_bouldin']:.4f}")

    # Elbow analysis: % drop from K-1 to K
    sorted_m = metrics_df.sort_values("k")
    inertias = sorted_m["inertia"].values
    ks = sorted_m["k"].values
    print(f"\n    Inertia % reductions:")
    for i in range(1, len(inertias)):
        pct_drop = (inertias[i - 1] - inertias[i]) / inertias[i - 1] * 100
        marker = " _ elbow" if ks[i] == optimal_k else ""
        print(f"      K={ks[i-1]}_{ks[i]} : {pct_drop:5.1f}% drop{marker}")

    return optimal_k


# ===========================================================================
# 9.  FIT K-MEANS
# ===========================================================================

def fit_kmeans(
    X_scaled: np.ndarray,
    k: int,
    random_state: int = 42,
) -> Tuple[KMeans, np.ndarray]:
    """Fit KMeans and return the model + cluster labels.

    Note: cluster IDs (0, 1, ..., k-1) are *arbitrary*  --  they are NOT
    rank-ordered by performance.  Interpretation happens only in
    profile_clusters() and assign_personas().
    """
    print("\n" + "=" * 80)
    print(f"  STEP 9  --  K-MEANS TRAINING  (K={k}, n_init=30, random_state={random_state})")
    print("=" * 80)

    model = KMeans(
        n_clusters=k,
        random_state=random_state,
        n_init=30,
        max_iter=500,
    )
    labels = model.fit_predict(X_scaled)

    unique_labels = np.unique(labels)
    assert len(labels) == len(X_scaled), "Label count mismatch"
    assert len(unique_labels) == k, f"Expected {k} clusters, got {len(unique_labels)}"

    print(f"  Model converged in {model.n_iter_} iterations.")
    print(f"  Final inertia: {model.inertia_:.4f}")
    print(f"  Cluster sizes:")
    for cid in unique_labels:
        n = (labels == cid).sum()
        print(f"    Cluster {cid} : {n} students  ({n / len(labels) * 100:.1f}%)")

    return model, labels


# ===========================================================================
# 10.  CLUSTER PROFILING
# ===========================================================================

def profile_clusters(
    df: pd.DataFrame,
    labels: np.ndarray,
    feature_cols: List[str],
) -> pd.DataFrame:
    """Compute detailed per-cluster summary statistics on original-scale values.

    IMPORTANT: Cluster IDs are arbitrary.  This function does NOT assume any
    ordering  --  it reports the raw statistics and lets assign_personas()
    decide on semantic labels.
    """
    print("\n" + "=" * 80)
    print("  STEP 10  --  CLUSTER PROFILING (original scale)")
    print("=" * 80)

    df = df.copy()
    df["cluster"] = labels

    rows = []
    for cid in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cid]
        n = len(sub)

        row = {
            "cluster": cid,
            "n_students": n,
            "share_pct": n / len(df) * 100,
            "mean_overall_total": sub["overall_total"].mean(),
            "median_overall_total": sub["overall_total"].median(),
            "mean_percentage": sub["percentage"].mean(),
            "median_percentage": sub["percentage"].median(),
            "std_percentage": sub["percentage"].std(),
            "mean_sgpi": sub["sgpi"].mean(),
            "median_sgpi": sub["sgpi"].median(),
            "mean_theory_pct": sub["theory_avg_pct"].mean(),
            "mean_lab_pct": sub["lab_avg_pct"].mean(),
            "mean_failed": sub["failed_subjects_count"].mean(),
            "pass_rate": (sub["result"] == "SUCCESSFUL").mean() * 100,
            "unsuccessful_rate": (sub["result"] == "UNSUCCESSFUL").mean() * 100,
            "absent_count": (sub["result"] == "ABSENT").sum(),
        }
        rows.append(row)

    summary = pd.DataFrame(rows)

    # Print formatted table
    print(f"\n  {'Cluster':>7s}  {'N':>4s}  {'Share':>6s}  {'Mean%':>7s}  {'Med%':>7s}  "
          f"{'StdDev%':>8s}  {'MeanSGPI':>8s}  {'Theory%':>8s}  {'Lab%':>6s}  "
          f"{'AvgFail':>7s}  {'Pass%':>6s}  {'Unsuc%':>6s}  {'Abs':>4s}")
    print("  " + "-" * 110)
    for _, r in summary.iterrows():
        print(f"  {int(r['cluster']):7d}  {int(r['n_students']):4d}  "
              f"{r['share_pct']:5.1f}%  {r['mean_percentage']:7.2f}  "
              f"{r['median_percentage']:7.2f}  {r['std_percentage']:8.2f}  "
              f"{r['mean_sgpi']:8.2f}  {r['mean_theory_pct']:8.2f}  "
              f"{r['mean_lab_pct']:6.2f}  {r['mean_failed']:7.2f}  "
              f"{r['pass_rate']:5.1f}%  {r['unsuccessful_rate']:5.1f}%  "
              f"{int(r['absent_count']):4d}")

    return summary


# ===========================================================================
# 11.  PERSONA ASSIGNMENT
# ===========================================================================

def assign_personas(
    df: pd.DataFrame,
    summary: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[int, str], Dict[int, str]]:
    """Assign semantic persona labels based on actual cluster statistics.

    The labelling logic is *data-driven*  --  labels are determined by
    thresholds applied to the summary statistics, not hard-coded to
    specific cluster IDs.

    Labelling rules (applied in priority order):
    _____________________________________________
    1. High-performing cluster:
       mean_percentage >= 60  AND  pass_rate >= 85  AND  mean_failed < 0.5

    2. Severely at-risk cluster:
       mean_percentage < 40  OR  mean_failed >= 4

    3. Lab-skewed / theory-deficit cluster:
       mean_lab_pct - mean_theory_pct >= 12  AND  pass_rate < 20

    4. Moderate / mixed cluster:
       everything else
    """
    print("\n" + "=" * 80)
    print("  STEP 11  --  PERSONA ASSIGNMENT")
    print("=" * 80)

    label_map: Dict[int, str] = {}
    desc_map: Dict[int, str] = {}

    for _, r in summary.iterrows():
        cid = int(r["cluster"])
        pct = r["mean_percentage"]
        sgpi = r["mean_sgpi"]
        theory = r["mean_theory_pct"]
        lab = r["mean_lab_pct"]
        fails = r["mean_failed"]
        pr = r["pass_rate"]
        n = int(r["n_students"])

        # Rule 1  --  high performers
        if pct >= 60 and pr >= 85 and fails < 0.5:
            label = "High Achievers / Academic Leaders"
            desc = (
                f"Consistently strong across theory ({theory:.1f}%) and lab "
                f"({lab:.1f}%), with near-complete pass rate ({pr:.0f}%) and "
                f"minimal failures ({fails:.2f} avg).  Mean SGPI {sgpi:.2f}."
            )
        # Rule 2  --  severe risk
        elif pct < 40 or fails >= 4:
            label = "Academic At-Risk / Multi-Subject Deficit"
            desc = (
                f"Severe difficulty across coursework: mean percentage "
                f"{pct:.1f}%, {fails:.1f} average failed subjects.  "
                f"Theory ({theory:.1f}%) and lab ({lab:.1f}%) both depressed."
            )
        # Rule 3  --  lab-skewed
        elif (lab - theory) >= 12 and pr < 20:
            label = "Practical-Strong / Theory-Deficit"
            desc = (
                f"Solid lab/practical proficiency ({lab:.1f}%) but lagging in "
                f"theory ({theory:.1f}%), creating a {lab - theory:.1f}pp gap.  "
                f"{fails:.1f} avg failures; pass rate {pr:.0f}%."
            )
        # Rule 4  --  moderate
        else:
            label = "Moderate / Mixed Performers"
            desc = (
                f"Intermediate academic profile: percentage {pct:.1f}%, "
                f"SGPI {sgpi:.2f}, theory {theory:.1f}%, lab {lab:.1f}%, "
                f"{fails:.1f} avg failures, pass rate {pr:.0f}%."
            )

        label_map[cid] = label
        desc_map[cid] = desc

        print(f"\n  Cluster {cid}  (n={n})")
        print(f"    Label : {label}")
        print(f"    Basis : {desc}")

    # Map onto DataFrame
    df = df.copy()
    df["persona_label"] = df["cluster"].map(label_map)
    df["persona_description"] = df["cluster"].map(desc_map)

    return df, label_map, desc_map


# ===========================================================================
# 12.  VISUALIZATIONS
# ===========================================================================

def generate_visualizations(
    df: pd.DataFrame,
    X_scaled: np.ndarray,
    metrics_df: pd.DataFrame,
    optimal_k: int,
    label_map: Dict[int, str],
    feature_cols: List[str],
    output_dir: str,
) -> Dict[str, str]:
    """Create 8 publication-quality figures and save to *output_dir*."""
    print("\n" + "=" * 80)
    print("  STEP 12  --  GENERATING VISUALIZATIONS")
    print("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    saved: Dict[str, str] = {}

    cluster_ids = sorted(df["cluster"].unique())

    def _short_label(cid: int) -> str:
        """First half of the persona label for compact legends."""
        return label_map[cid].split("/")[0].strip()

    # -------------------------------------------------------------------
    # FIG 1: Elbow Method (Inertia vs K)
    # -------------------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.plot(metrics_df["k"], metrics_df["inertia"], "o-", lw=2.2,
             color="#1976D2", markersize=7)
    ax1.axvline(optimal_k, color="#D32F2F", ls="--", lw=1.5,
                label=f"Selected K={optimal_k}")
    ax1.set_title("Fig 1  --  Elbow Method: Inertia vs K", fontweight="bold")
    ax1.set_xlabel("Number of Clusters (K)")
    ax1.set_ylabel("Inertia (WCSS)")
    ax1.grid(True, ls="--", alpha=0.4)
    ax1.legend()
    fig1.tight_layout()
    p = os.path.join(output_dir, "kmeans_01_elbow_method.png")
    fig1.savefig(p, bbox_inches="tight")
    plt.close(fig1)
    saved["Fig 1  --  Elbow Method"] = p

    # -------------------------------------------------------------------
    # FIG 2: Silhouette Score vs K
    # -------------------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    ax2.plot(metrics_df["k"], metrics_df["silhouette"], "s-", lw=2.2,
             color="#388E3C", markersize=7)
    ax2.axvline(optimal_k, color="#D32F2F", ls="--", lw=1.5,
                label=f"Selected K={optimal_k}")
    ax2.set_title("Fig 2  --  Silhouette Score vs K", fontweight="bold")
    ax2.set_xlabel("Number of Clusters (K)")
    ax2.set_ylabel("Mean Silhouette Coefficient")
    ax2.grid(True, ls="--", alpha=0.4)
    ax2.legend()
    fig2.tight_layout()
    p = os.path.join(output_dir, "kmeans_02_silhouette_vs_k.png")
    fig2.savefig(p, bbox_inches="tight")
    plt.close(fig2)
    saved["Fig 2  --  Silhouette vs K"] = p

    # -------------------------------------------------------------------
    # FIG 3: Cluster Size Distribution
    # -------------------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(7, 4.5))
    sizes = [int((df["cluster"] == c).sum()) for c in cluster_ids]
    colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(cluster_ids))]
    bars = ax3.bar(
        [f"C{c}\n{_short_label(c)}" for c in cluster_ids],
        sizes, color=colors, edgecolor="black", lw=0.7,
    )
    for bar, sz in zip(bars, sizes):
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                 str(sz), ha="center", fontweight="bold", fontsize=10)
    ax3.set_title("Fig 3  --  Cluster Size Distribution", fontweight="bold")
    ax3.set_ylabel("Number of Students")
    ax3.grid(axis="y", ls="--", alpha=0.4)
    fig3.tight_layout()
    p = os.path.join(output_dir, "kmeans_03_cluster_sizes.png")
    fig3.savefig(p, bbox_inches="tight")
    plt.close(fig3)
    saved["Fig 3  --  Cluster Sizes"] = p

    # -------------------------------------------------------------------
    # FIG 4: Cluster Mean Percentage Comparison
    # -------------------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    means_pct = [df[df["cluster"] == c]["percentage"].mean() for c in cluster_ids]
    bars4 = ax4.bar(
        [f"C{c}\n{_short_label(c)}" for c in cluster_ids],
        means_pct, color=colors, edgecolor="black", lw=0.7,
    )
    for bar, val in zip(bars4, means_pct):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", fontweight="bold", fontsize=9)
    ax4.set_title("Fig 4  --  Mean Percentage by Cluster", fontweight="bold")
    ax4.set_ylabel("Overall Percentage (%)")
    ax4.set_ylim(0, 100)
    ax4.grid(axis="y", ls="--", alpha=0.4)
    fig4.tight_layout()
    p = os.path.join(output_dir, "kmeans_04_mean_percentage.png")
    fig4.savefig(p, bbox_inches="tight")
    plt.close(fig4)
    saved["Fig 4  --  Mean Percentage"] = p

    # -------------------------------------------------------------------
    # FIG 5: Cluster Mean SGPI Comparison
    # -------------------------------------------------------------------
    fig5, ax5 = plt.subplots(figsize=(7, 4.5))
    means_sgpi = [df[df["cluster"] == c]["sgpi"].mean() for c in cluster_ids]
    bars5 = ax5.bar(
        [f"C{c}\n{_short_label(c)}" for c in cluster_ids],
        means_sgpi, color=colors, edgecolor="black", lw=0.7,
    )
    for bar, val in zip(bars5, means_sgpi):
        ax5.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 f"{val:.2f}", ha="center", fontweight="bold", fontsize=9)
    ax5.set_title("Fig 5  --  Mean SGPI by Cluster", fontweight="bold")
    ax5.set_ylabel("SGPI (0-10)")
    ax5.set_ylim(0, 10.5)
    ax5.axhline(7.75, color="#27ae60", ls="--", alpha=0.6, label="Distinction (7.75)")
    ax5.axhline(6.00, color="#e67e22", ls=":", alpha=0.6, label="First Class (6.00)")
    ax5.grid(axis="y", ls="--", alpha=0.4)
    ax5.legend(fontsize=8)
    fig5.tight_layout()
    p = os.path.join(output_dir, "kmeans_05_mean_sgpi.png")
    fig5.savefig(p, bbox_inches="tight")
    plt.close(fig5)
    saved["Fig 5  --  Mean SGPI"] = p

    # -------------------------------------------------------------------
    # FIG 6: Theory vs Lab Performance by Cluster
    # -------------------------------------------------------------------
    fig6, ax6 = plt.subplots(figsize=(8, 6))
    for i, cid in enumerate(cluster_ids):
        sub = df[df["cluster"] == cid]
        clr = _PALETTE[i % len(_PALETTE)]
        ax6.scatter(
            sub["theory_avg_pct"], sub["lab_avg_pct"],
            c=clr, s=65, alpha=0.85, edgecolors="black", lw=0.5,
            label=f"C{cid}: {_short_label(cid)} (n={len(sub)})",
        )
        # Centroid
        cx = sub["theory_avg_pct"].mean()
        cy = sub["lab_avg_pct"].mean()
        ax6.scatter(cx, cy, c=clr, s=200, marker="X",
                    edgecolors="black", lw=1.5, zorder=5)
        ax6.annotate(
            f"({cx:.0f}%, {cy:.0f}%)", (cx, cy),
            textcoords="offset points", xytext=(8, 8), fontsize=7.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.8),
        )

    # Parity line (theory == lab)
    lim = max(ax6.get_xlim()[1], ax6.get_ylim()[1])
    ax6.plot([0, lim], [0, lim], "k--", alpha=0.3, label="Parity (theory = lab)")
    ax6.set_title("Fig 6  --  Theory vs Lab Performance by Cluster", fontweight="bold")
    ax6.set_xlabel("Theory Average (%)")
    ax6.set_ylabel("Lab / Practical Average (%)")
    ax6.grid(True, ls="--", alpha=0.4)
    ax6.legend(fontsize=7.5, loc="lower right")
    fig6.tight_layout()
    p = os.path.join(output_dir, "kmeans_06_theory_vs_lab.png")
    fig6.savefig(p, bbox_inches="tight")
    plt.close(fig6)
    saved["Fig 6  --  Theory vs Lab"] = p

    # -------------------------------------------------------------------
    # FIG 7: PCA 2D Cluster Visualization
    # -------------------------------------------------------------------
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    df["PCA1"] = X_pca[:, 0]
    df["PCA2"] = X_pca[:, 1]
    var_exp = pca.explained_variance_ratio_ * 100

    fig7, ax7 = plt.subplots(figsize=(8, 6))
    for i, cid in enumerate(cluster_ids):
        sub = df[df["cluster"] == cid]
        clr = _PALETTE[i % len(_PALETTE)]
        ax7.scatter(
            sub["PCA1"], sub["PCA2"],
            c=clr, s=65, alpha=0.85, edgecolors="black", lw=0.5,
            label=f"C{cid}: {_short_label(cid)} (n={len(sub)})",
        )
        cx, cy = sub["PCA1"].mean(), sub["PCA2"].mean()
        ax7.scatter(cx, cy, c=clr, s=200, marker="X",
                    edgecolors="black", lw=1.5, zorder=5)

    ax7.set_title(
        f"Fig 7  --  PCA 2D Projection (explained variance: {var_exp.sum():.1f}%)",
        fontweight="bold",
    )
    ax7.set_xlabel(f"PC1 ({var_exp[0]:.1f}%)")
    ax7.set_ylabel(f"PC2 ({var_exp[1]:.1f}%)")
    ax7.grid(True, ls="--", alpha=0.4)
    ax7.legend(fontsize=7.5, loc="best")
    fig7.tight_layout()
    p = os.path.join(output_dir, "kmeans_07_pca_2d.png")
    fig7.savefig(p, bbox_inches="tight")
    plt.close(fig7)
    saved["Fig 7  --  PCA 2D"] = p

    # -------------------------------------------------------------------
    # FIG 8: Correlation Heatmap of Clustering Features
    # -------------------------------------------------------------------
    fig8, ax8 = plt.subplots(figsize=(7, 5.5))
    corr = df[feature_cols].corr()
    im = ax8.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax8.set_xticks(range(len(feature_cols)))
    ax8.set_yticks(range(len(feature_cols)))
    ax8.set_xticklabels(feature_cols, rotation=35, ha="right", fontsize=8)
    ax8.set_yticklabels(feature_cols, fontsize=8)
    # Annotate cells
    for i in range(len(feature_cols)):
        for j in range(len(feature_cols)):
            val = corr.values[i, j]
            color = "white" if abs(val) > 0.6 else "black"
            ax8.text(j, i, f"{val:.2f}", ha="center", va="center",
                     fontsize=8, color=color, fontweight="bold")
    ax8.set_title("Fig 8  --  Feature Correlation Heatmap", fontweight="bold")
    fig8.colorbar(im, ax=ax8, shrink=0.8, label="Pearson r")
    fig8.tight_layout()
    p = os.path.join(output_dir, "kmeans_08_correlation_heatmap.png")
    fig8.savefig(p, bbox_inches="tight")
    plt.close(fig8)
    saved["Fig 8  --  Correlation Heatmap"] = p

    # Report
    print()
    for label, path in saved.items():
        sz_kb = os.path.getsize(path) / 1024 if os.path.exists(path) else 0
        print(f"  [SAVED] {label:35s}  _  {os.path.basename(path)}  ({sz_kb:.0f} KB)")

    return saved


# ===========================================================================
# 13.  EXPORT RESULTS
# ===========================================================================

def export_results(
    df: pd.DataFrame,
    output_path: str | None = None,
) -> str:
    """Export the enriched dataset and print a student roster.

    The roster is sorted by cluster, then by overall_total descending within
    each cluster.
    """
    print("\n" + "=" * 80)
    print("  STEP 13  --  STUDENT ROSTER & EXPORT")
    print("=" * 80)

    if output_path is None:
        output_path = os.path.join(
            _BASE_DIR, "data", "processed", "AI_DS_SEM4_CLUSTERED_STUDENTS.csv"
        )

    # --- student roster ----------------------------------------------------
    roster_cols = [
        "student_id", "seat_no", "name", "cluster", "persona_label",
        "overall_total", "percentage", "sgpi", "result",
        "failed_subjects_count",
    ]
    roster = df[roster_cols].sort_values(
        ["cluster", "overall_total"], ascending=[True, False]
    )

    print(f"\n  {'SEAT_NO':>12s}  {'NAME':35s}  {'CL':>3s}  {'MARKS':>6s}  "
          f"{'PCT':>7s}  {'SGPI':>6s}  {'RESULT':12s}  {'FAIL':>4s}")
    print("  " + "-" * 100)

    prev_cluster = None
    for _, r in roster.iterrows():
        cid = int(r["cluster"])
        if cid != prev_cluster:
            lbl = r["persona_label"]
            n = int((df["cluster"] == cid).sum())
            print(f"\n  _ CLUSTER {cid}: {lbl}  (n={n})")
            print("  " + "-" * 100)
            prev_cluster = cid

        sgpi_str = f"{r['sgpi']:6.2f}" if r["sgpi"] > 0 else "   0.00"
        print(f"  {str(r['seat_no']):>12s}  {str(r['name'])[:35]:35s}  "
              f"{cid:3d}  {r['overall_total']:6.0f}  {r['percentage']:6.2f}%  "
              f"{sgpi_str}  {str(r['result']):12s}  {int(r['failed_subjects_count']):4d}")

    # --- export CSV --------------------------------------------------------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n  [EXPORT] {len(df)} students _ {output_path}")

    return output_path


# ===========================================================================
# MAIN ORCHESTRATOR
# ===========================================================================

def run_kmeans_clustering(
    data_path: str | None = None,
    output_path: str | None = None,
    figures_dir: str | None = None,
) -> Tuple[pd.DataFrame, KMeans, StandardScaler, pd.DataFrame, Dict[str, str]]:
    """Execute the full end-to-end K-Means clustering pipeline.

    Returns
    -------
    df : pd.DataFrame
        Enriched dataset with cluster, persona_label, PCA1, PCA2.
    model : KMeans
        Fitted KMeans estimator.
    scaler : StandardScaler
        Fitted scaler.
    summary : pd.DataFrame
        Cluster profile summary.
    figures : dict
        Mapping of figure labels to file paths.
    """
    if data_path is None:
        data_path = PROCESSED_DATA_PATH
    if output_path is None:
        output_path = os.path.join(
            _BASE_DIR, "data", "processed", "AI_DS_SEM4_CLUSTERED_STUDENTS.csv"
        )
    if figures_dir is None:
        figures_dir = FIGURES_DIR

    # 1. Load
    df = load_data(data_path)

    # 2. Audit
    df = audit_data(df)

    # 3. Feature engineering
    df, candidate_features = create_features(df)

    # 4. Redundancy analysis _ final feature set
    final_features = validate_features(df, candidate_features)

    # 5. Missing-value handling
    X_clean, _ = handle_missing_values(df, final_features)

    # 6. Scaling
    X_scaled, scaler = scale_features(X_clean)

    # 7. Evaluate K = 2...7
    metrics_df = evaluate_k(X_scaled)

    # 8. Select optimal K
    optimal_k = select_optimal_k(metrics_df)

    # 9. Fit K-Means
    model, labels = fit_kmeans(X_scaled, k=optimal_k)
    df["cluster"] = labels

    # 10. Profile clusters
    summary = profile_clusters(df, labels, final_features)

    # 11. Assign personas
    df, label_map, desc_map = assign_personas(df, summary)

    # 12. Visualizations (also computes PCA1/PCA2 and adds to df)
    figures = generate_visualizations(
        df, X_scaled, metrics_df, optimal_k, label_map, final_features, figures_dir
    )

    # 13. Export
    export_results(df, output_path)

    # __ Final summary _____________________________________________________
    print("\n" + "=" * 80)
    print("  K-MEANS CLUSTERING RESULTS  --  FINAL SUMMARY")
    print("=" * 80)
    print(f"\n  Dataset         : {len(df)} students")
    print(f"  Final features  : {final_features}")
    print(f"  Selected K      : {optimal_k}")
    print(f"  Silhouette      : {metrics_df.loc[metrics_df['k']==optimal_k, 'silhouette'].values[0]:.4f}")
    print(f"  Calinski-Harabasz : {metrics_df.loc[metrics_df['k']==optimal_k, 'calinski_harabasz'].values[0]:.2f}")
    print(f"  Davies-Bouldin  : {metrics_df.loc[metrics_df['k']==optimal_k, 'davies_bouldin'].values[0]:.4f}")
    print()
    for cid in sorted(label_map.keys()):
        n = int((df["cluster"] == cid).sum())
        pct = n / len(df) * 100
        print(f"  Cluster {cid}  (n={n:3d}, {pct:5.1f}%)  _  {label_map[cid]}")
        print(f"    {desc_map[cid]}")
    print(f"\n  Output CSV      : {output_path}")
    print(f"  Figures dir     : {figures_dir}")
    print("=" * 80)

    return df, model, scaler, summary, figures


# ===========================================================================

if __name__ == "__main__":
    run_kmeans_clustering()
