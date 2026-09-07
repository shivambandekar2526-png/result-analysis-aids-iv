import os, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, calinski_harabasz_score

# Ensure project root and src are on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(SRC_DIR)
sys.path.append(SRC_DIR)
sys.path.append(BASE_DIR)

from config import FIGURES_DIR, PROCESSED_DATA_PATH
from ml.feature_engineering import load_and_engineer_features

# Standard plot aesthetics
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#444444'
plt.rcParams['axes.linewidth'] = 0.9

CLUSTER_PALETTE = ['#1f77b4', '#2ca02c', '#d62728', '#ff7f0e', '#9467bd']

def evaluate_optimal_k(X_scaled, k_range=range(2, 8)):
    """Computes Inertia, Silhouette, Davies-Bouldin, and Calinski-Harabasz metrics across K."""
    metrics = {
        'k': list(k_range),
        'inertia': [],
        'silhouette': [],
        'davies_bouldin': [],
        'calinski_harabasz': []
    }
    
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(X_scaled)
        metrics['inertia'].append(km.inertia_)
        metrics['silhouette'].append(silhouette_score(X_scaled, labels))
        metrics['davies_bouldin'].append(davies_bouldin_score(X_scaled, labels))
        metrics['calinski_harabasz'].append(calinski_harabasz_score(X_scaled, labels))
        
    return pd.DataFrame(metrics)

def plot_optimal_k_metrics(metrics_df, optimal_k, save_path):
    """Generates a 3-panel cluster hyperparameter evaluation visualization."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4.8), dpi=200)
    
    # 1. Elbow Method (Inertia)
    ax1.plot(metrics_df['k'], metrics_df['inertia'], marker='o', linewidth=2.2, color='#1f77b4', markersize=7)
    ax1.axvline(optimal_k, color='#d62728', linestyle='--', linewidth=1.5, label=f'Chosen K = {optimal_k}')
    ax1.set_title('Elbow Method (Inertia / WCSS)', fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel('Number of Clusters (K)', fontsize=11)
    ax1.set_ylabel('Within-Cluster Sum of Squares (WCSS)', fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    # 2. Silhouette Score (Higher is better)
    ax2.plot(metrics_df['k'], metrics_df['silhouette'], marker='s', linewidth=2.2, color='#2ca02c', markersize=7)
    ax2.axvline(optimal_k, color='#d62728', linestyle='--', linewidth=1.5, label=f'Chosen K = {optimal_k}')
    ax2.set_title('Silhouette Coefficient vs K', fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel('Number of Clusters (K)', fontsize=11)
    ax2.set_ylabel('Mean Silhouette Score', fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    # 3. Davies-Bouldin Index (Lower is better)
    ax3.plot(metrics_df['k'], metrics_df['davies_bouldin'], marker='^', linewidth=2.2, color='#9467bd', markersize=7)
    ax3.axvline(optimal_k, color='#d62728', linestyle='--', linewidth=1.5, label=f'Chosen K = {optimal_k}')
    ax3.set_title('Davies-Bouldin Index (Lower = Better)', fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlabel('Number of Clusters (K)', fontsize=11)
    ax3.set_ylabel('Davies-Bouldin Score', fontsize=11)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(frameon=True, facecolor='white', framealpha=0.9)
    
    plt.suptitle('K-Means Hyperparameter Selection: Cluster Validation Diagnostics', fontsize=14, fontweight='bold', y=1.03)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_silhouette_analysis(X_scaled, cluster_labels, optimal_k, persona_mapping, save_path):
    """Generates per-cluster silhouette coefficient analysis."""
    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
    sample_silhouette_values = silhouette_samples(X_scaled, cluster_labels)
    
    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=200)
    y_lower = 10
    
    for i in range(optimal_k):
        ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
        ith_cluster_silhouette_values.sort()
        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]
        ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_silhouette_values,
                         facecolor=color, edgecolor=color, alpha=0.7)
        
        persona_short = persona_mapping[i].split(':')[0]
        ax.text(-0.04, y_lower + 0.5 * size_cluster_i, f"{persona_short}\n(n={size_cluster_i})",
                fontsize=8.5, fontweight='bold', ha='right', va='center')
        y_lower = y_upper + 10
        
    ax.axvline(x=silhouette_avg, color="#c0392b", linestyle="--", linewidth=2,
               label=f'Average Silhouette Score = {silhouette_avg:.3f}')
    ax.set_title(f'Per-Cluster Silhouette Coefficient Profile (K={optimal_k})', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Silhouette Coefficient Values', fontsize=11)
    ax.set_ylabel('Student Records Grouped by Cluster', fontsize=11)
    ax.set_yticks([])
    ax.set_xlim([-0.15, 0.75])
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_clustering_dashboard(df, X_scaled, cluster_features, optimal_k, persona_mapping, save_path):
    """Generates a 4-panel analytical master dashboard."""
    fig = plt.figure(figsize=(18, 14), dpi=200)
    
    # -------------------------------------------------------------
    # Panel 1: PCA 2D Cluster Space
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1)
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_exp = pca.explained_variance_ratio_ * 100
    
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]
    
    for i in range(optimal_k):
        sub = df[df['cluster'] == i]
        color = CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]
        ax1.scatter(sub['pca_1'], sub['pca_2'], color=color,
                    label=f"{persona_mapping[i]} (n={len(sub)})",
                    s=75, alpha=0.85, edgecolors='black', linewidth=0.6)
        
        # Center marker
        center_x = sub['pca_1'].mean()
        center_y = sub['pca_2'].mean()
        ax1.scatter(center_x, center_y, color=color, s=220, marker='X', edgecolors='black', linewidth=1.5, zorder=5)
        
    ax1.set_title(f'PCA 2D Cluster Projection (Variance Explained: {var_exp.sum():.1f}%)', fontsize=12, fontweight='bold')
    ax1.set_xlabel(f'Principal Component 1 ({var_exp[0]:.1f}%)', fontsize=10)
    ax1.set_ylabel(f'Principal Component 2 ({var_exp[1]:.1f}%)', fontsize=10)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)
    
    # -------------------------------------------------------------
    # Panel 2: Theory % vs Lab % Scatter
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2)
    for i in range(optimal_k):
        sub = df[df['cluster'] == i]
        color = CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]
        ax2.scatter(sub['theory_avg_pct'], sub['lab_avg_pct'], color=color,
                    label=persona_mapping[i], s=75, alpha=0.85, edgecolors='black', linewidth=0.6)
        
        c_th = sub['theory_avg_pct'].mean()
        c_lab = sub['lab_avg_pct'].mean()
        ax2.scatter(c_th, c_lab, color=color, s=240, marker='P', edgecolors='black', linewidth=1.5, zorder=6)
        ax2.annotate(f"Centroid {i}\n({c_th:.1f}%, {c_lab:.1f}%)", (c_th, c_lab),
                     textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85))

    ax2.axvline(40, color='#c0392b', linestyle=':', linewidth=1.4, label='Theory Passing Threshold (40%)')
    ax2.set_title('Theory Average vs. Practical & Lab Performance', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Theory Coursework Average (%) [CT, DBMS, OS, FTS, OE]', fontsize=10)
    ax2.set_ylabel('Lab & Project Average (%) [Practicals & Orals]', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='lower right', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)
    
    # -------------------------------------------------------------
    # Panel 3: SGPI Distribution Across Clusters (Boxplot with Jitter)
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3)
    cluster_sgpis = [df[df['cluster'] == i]['sgpi'].dropna().values for i in range(optimal_k)]
    box = ax3.boxplot(cluster_sgpis, patch_artist=True, widths=0.45,
                      medianprops=dict(color='black', linewidth=1.8),
                      showmeans=True, meanprops=dict(marker='D', markeredgecolor='black', markerfacecolor='yellow', markersize=6))
    
    for patch, i in zip(box['boxes'], range(optimal_k)):
        patch.set_facecolor(CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)])
        patch.set_alpha(0.7)
        
    for i in range(optimal_k):
        sub_sgpi = df[df['cluster'] == i]['sgpi'].dropna().values
        if len(sub_sgpi) > 0:
            jitter = np.random.normal(0, 0.04, size=len(sub_sgpi))
            ax3.scatter(np.ones(len(sub_sgpi)) * (i + 1) + jitter, sub_sgpi,
                        color=CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)], edgecolors='black', linewidth=0.5,
                        s=35, alpha=0.8, zorder=4)
        
    ax3.set_title('SGPI Distribution by Student Persona Cluster', fontsize=12, fontweight='bold')
    ax3.set_xticks(range(1, optimal_k + 1))
    ax3.set_xticklabels([f"Cluster {i}\n({persona_mapping[i].split(':')[0]})" for i in range(optimal_k)], fontsize=9, fontweight='bold')
    ax3.set_ylabel('SGPI (Scale 0.0 - 10.0)', fontsize=10)
    ax3.axhline(7.75, color='#27ae60', linestyle='--', alpha=0.7, label='Distinction Benchmark (7.75)')
    ax3.axhline(6.00, color='#ff7f0e', linestyle=':', alpha=0.7, label='First Class Benchmark (6.00)')
    ax3.grid(axis='y', linestyle='--', alpha=0.5)
    ax3.legend(loc='lower right', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)
    
    # -------------------------------------------------------------
    # Panel 4: Radar / Spider Chart of Academic Dimensions
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4, polar=True)
    radar_attributes = [
        'Theory Avg %',
        'Lab Avg %',
        'Internal Marks %',
        'External Exam %',
        'Normalized SGPI %'
    ]
    
    num_vars = len(radar_attributes)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    ax4.set_theta_offset(np.pi / 2)
    ax4.set_theta_direction(-1)
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels(radar_attributes, fontsize=9.5, fontweight='bold')
    ax4.set_ylim(0, 100)
    
    for i in range(optimal_k):
        sub = df[df['cluster'] == i]
        vals = [
            sub['theory_avg_pct'].mean(),
            sub['lab_avg_pct'].mean(),
            (sub['internal_total_score'].mean() / 180.0) * 100.0,
            (sub['external_total_score'].mean() / 270.0) * 100.0,
            (sub['sgpi'].mean() / 10.0) * 100.0 if not pd.isna(sub['sgpi'].mean()) else 0.0
        ]
        vals += vals[:1]
        
        color = CLUSTER_PALETTE[i % len(CLUSTER_PALETTE)]
        ax4.plot(angles, vals, color=color, linewidth=2, label=f"Cluster {i}: {persona_mapping[i].split(':')[0]}")
        ax4.fill(angles, vals, color=color, alpha=0.15)
        
    ax4.set_title('Academic Dimension Radar Profile by Cluster', fontsize=12, fontweight='bold', pad=15)
    ax4.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=8, frameon=True, facecolor='white', framealpha=0.9)
    
    plt.suptitle('Mumbai University AI & DS Semester-IV: K-Means Academic Performance Segmentation',
                 fontsize=15, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def run_kmeans_clustering():
    """Main execution pipeline for K-Means Clustering and visual analytics."""
    print("=" * 80)
    print("         K-MEANS CLUSTERING & STUDENT PERSONA SEGMENTATION")
    print("=" * 80)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # 1. Feature Engineering
    df = load_and_engineer_features()
    print(f"Loaded student cohort dataset: {df.shape[0]} students, {df.shape[1]} attributes.")
    
    # Academic clustering dimensions
    cluster_features = [
        "theory_avg_pct",
        "lab_avg_pct",
        "internal_total_score",
        "external_total_score"
    ]
    
    X = df[cluster_features].fillna(0)
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 2. Optimal K Evaluation
    print("\n--- 1. Evaluating Cluster Validity (K = 2 to 7) ---")
    metrics_df = evaluate_optimal_k(X_scaled, k_range=range(2, 8))
    print(metrics_df.to_string(index=False))
    
    optimal_k = 3
    print(f"\nSelected Optimal K = {optimal_k} (Coherent academic tiering)")
    
    optimal_k_fig_path = os.path.join(FIGURES_DIR, "kmeans_optimal_k_evaluation.png")
    plot_optimal_k_metrics(metrics_df, optimal_k, optimal_k_fig_path)
    print(f"Saved optimal K evaluation figure -> {optimal_k_fig_path}")
    
    # 3. Fit K-Means
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=30, max_iter=500)
    cluster_labels = kmeans.fit_predict(X_scaled)
    df['cluster'] = cluster_labels
    
    # 4. Semantic Persona Labels based on cluster means
    cluster_stats = df.groupby('cluster').agg({
        'sgpi': 'mean',
        'theory_avg_pct': 'mean',
        'lab_avg_pct': 'mean',
        'percentage': 'mean',
        'failed_subjects_count': 'mean',
        'student_id': 'count'
    }).rename(columns={'student_id': 'count'})
    
    # Rank clusters by SGPI/marks
    sorted_clusters = cluster_stats.sort_values(by='theory_avg_pct', ascending=False).index.tolist()
    
    tier_labels = [
        "Tier 1: High Achievers & Academic Leaders",
        "Tier 2: Steady Performers (Practical Strong)",
        "Tier 3: Academic At-Risk (Theory Deficit)"
    ]
    
    persona_mapping = {}
    for rank_idx, orig_cluster_id in enumerate(sorted_clusters):
        label = tier_labels[rank_idx] if rank_idx < len(tier_labels) else f"Tier {rank_idx+1}: Cluster {orig_cluster_id}"
        persona_mapping[orig_cluster_id] = label
        
    df['persona_label'] = df['cluster'].map(persona_mapping)
    
    print("\n--- 2. Student Persona Cluster Profiles ---")
    summary_table = []
    for cid in range(optimal_k):
        sub = df[df['cluster'] == cid]
        summary_table.append({
            "Cluster ID": cid,
            "Persona Label": persona_mapping[cid],
            "Students (N)": len(sub),
            "Share (%)": f"{(len(sub) / len(df)) * 100:.1f}%",
            "Mean SGPI": f"{sub['sgpi'].mean():.2f}" if not pd.isna(sub['sgpi'].mean()) else "N/A",
            "Theory Avg (%)": f"{sub['theory_avg_pct'].mean():.1f}%",
            "Lab Avg (%)": f"{sub['lab_avg_pct'].mean():.1f}%",
            "Mean Total Marks": f"{sub['overall_total'].mean():.1f} / 775",
            "Pass Rate (%)": f"{(sub['result'] == 'SUCCESSFUL').mean() * 100:.1f}%",
            "Avg Failed Subs": f"{sub['failed_subjects_count'].mean():.2f}"
        })
        
    summary_df = pd.DataFrame(summary_table)
    print(summary_df.to_string(index=False))
    
    # 5. Generate Figures
    silhouette_fig_path = os.path.join(FIGURES_DIR, "kmeans_cluster_silhouette_analysis.png")
    plot_silhouette_analysis(X_scaled, cluster_labels, optimal_k, persona_mapping, silhouette_fig_path)
    print(f"Saved silhouette analysis figure -> {silhouette_fig_path}")
    
    dashboard_fig_path = os.path.join(FIGURES_DIR, "kmeans_student_personas_dashboard.png")
    plot_clustering_dashboard(df, X_scaled, cluster_features, optimal_k, persona_mapping, dashboard_fig_path)
    print(f"Saved 4-panel master clustering dashboard -> {dashboard_fig_path}")
    
    # 6. Export Clustered Dataset
    output_csv_path = os.path.join(BASE_DIR, "data", "processed", "AI_DS_SEM4_CLUSTERED_STUDENTS.csv")
    df.to_csv(output_csv_path, index=False)
    print(f"\nExported enriched clustered dataset ({len(df)} rows) -> {output_csv_path}")
    
    # 7. Print Student Tier Roster
    print_student_tier_roster(df)

    print("\n" + "=" * 80)
    print("                K-MEANS CLUSTERING COMPLETED SUCCESSFULLY")
    print("=" * 80)
    return df, kmeans, scaler, summary_df

def print_student_tier_roster(df):
    """Prints a formatted roster of all students grouped by their assigned tier."""
    display_cols = ['seat_no', 'name', 'persona_label', 'sgpi', 'overall_total', 'percentage', 'result', 'failed_subjects_count']
    roster_df = df[display_cols].copy()
    roster_df['sgpi_str'] = roster_df['sgpi'].apply(lambda x: f"{x:5.2f}" if pd.notnull(x) and x > 0 else "  N/A")
    roster_df['marks_str'] = roster_df['overall_total'].apply(lambda x: f"{x:5.1f}")
    roster_df['pct_str'] = roster_df['percentage'].apply(lambda x: f"{x:5.2f}%")
    
    print("\n" + "=" * 110)
    print(f"{'SEAT NO':12s} | {'STUDENT NAME':38s} | {'ASSIGNED TIER':36s} | {'MARKS':7s} | {'SGPI':5s} | {'STATUS':12s}")
    print("-" * 110)
    for _, row in roster_df.sort_values(by=['persona_label', 'overall_total'], ascending=[True, False]).iterrows():
        tier_short = row['persona_label']
        print(f"{str(row['seat_no']):12s} | {str(row['name'])[:38]:38s} | {tier_short:36s} | {row['marks_str']:7s} | {row['sgpi_str']:5s} | {str(row['result']):12s}")
    print("=" * 110)

if __name__ == "__main__":
    run_kmeans_clustering()

