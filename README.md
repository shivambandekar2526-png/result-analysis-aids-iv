# 🎓 AI & DS Semester-IV Academic Result Analysis & Machine Learning Workspace

This repository contains the end-to-end extracted dataset, structured pipelines, exploratory analytics, and machine learning models for the University of Mumbai Semester-IV **Artificial Intelligence and Data Science (AI & DS)** Examination.

---

## 📁 Repository Structure

```text
result-analysis-aids/
├── .vscode/                                    # VS Code IDE & Pylance configuration
│   └── settings.json                           # Source root extraPaths for clean imports
│
├── data/
│   ├── raw/
│   │   └── AI&DS_SEM4_RESULTS.pdf              # Raw 47-page university result PDF gazette
│   └── processed/
│       ├── AI_DS_SEM4_MASTER_RESULTS.csv       # Clean master dataset (88 students × 113 columns)
│       └── AI_DS_SEM4_CLUSTERED_STUDENTS.csv   # Clustered dataset with personas & PCA coordinates
│
├── notebooks/                                  # Interactive Jupyter Notebook Workspaces
│   ├── 01_eda_and_academic_analytics.ipynb     # Grade distribution, SGPI trends & descriptive statistics
│   ├── 02_grade_distribution_and_correlations.ipynb # Course-by-course performance & correlation heatmaps
│   ├── 03_predictive_modeling_and_ml.ipynb     # Regression, At-Risk Classification & K-Means Clustering
│   └── complete_data-analysis.ipynb            # Full consolidated academic analytics notebook
│
├── src/                                        # Modular Python Package
│   ├── config.py                               # Subject codes, evaluation schemes, credits & file paths
│   ├── analytics/
│   │   └── eda.py                              # Visualizations, distributions & descriptive statistics
│   └── ml/
│       ├── feature_engineering.py              # Automated feature derivation (Theory/Lab ratios, health indices)
│       ├── clustering.py                       # K-Means clustering (4 metrics, diagnostics, dashboard)
│       ├── regression.py                       # Predictive SGPI & total marks regression pipelines
│       └── models.py                           # Central runner for all ML models
│
├── reports/                                    # Output Artifacts & Documentation
│   ├── figures/                                # High-resolution analytical charts & plots (200 DPI)
│   │   ├── kmeans_01_k_selection_diagnostics.png
│   │   ├── kmeans_02_silhouette_analysis.png
│   │   ├── kmeans_03_pca_2d_projection.png
│   │   ├── kmeans_04_theory_vs_lab_scatter.png
│   │   ├── kmeans_05_cluster_feature_profiles.png
│   │   ├── kmeans_06_sgpi_distribution_boxplot.png
│   │   ├── kmeans_student_personas_dashboard.png
│   │   ├── sgpa_distribution.png
│   │   ├── result_breakdown.png
│   │   └── subject_performance_comparison.png
│   └── documentation/                          # Detailed Word (.docx) analytical reports
│       ├── Academic_Result_Analysis_Report.docx
│       ├── data_analysis_report.docx
│       └── QNA.docx
│
└── scripts/                                    # Standalone analytical tools
    ├── generate_word_report.py                 # Generates executive Word reports
    ├── top_rankers_compare.py                  # Comparative ranker analysis
    ├── weakest_subject_analysis.py             # Subject difficulty & failure metrics
    ├── compare_shivam_stats.py                 # Topper academic case study profile
    ├── compare_arya_stats.py                   # Mid-tier student profile comparison
    └── archive/                                # Archived OCR parsing & debug utilities
```

---

## 📊 Dataset Schema Overview

The primary dataset [`data/processed/AI_DS_SEM4_MASTER_RESULTS.csv`](data/processed/AI_DS_SEM4_MASTER_RESULTS.csv) contains **88 students** and **113 features**:

1. **Student Identifiers**: `student_id`, `seat_no`, `name`, `gender`, `status`, `ern`, `college`, `page`
2. **Subject Assessments** (11 Courses):
   - **`OE_`** (Administrative Policy of Chhatrapati Shivaji Maharaja): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`MINIPROJ_`** (Mini Project): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`CT_`** (Computational Theory): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DBMS_`** (Database Management System): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`OS_`** (Operating System): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DBMS_LAB_`** (DBMS Lab): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`OS_LAB_`** (OS Lab): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`FTS_`** (Fundamentals of Telecommunication Systems): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`TC_LAB_`** (Basic Telecommunication Experiments): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`BMD_`** (Business Model Development): `term_work`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DT_`** (Design Thinking): `term_work`, `total`, `grade`, `gp`, `credits`, `gc`
3. **Academic Summary**: `overall_total`, `maximum_total`, `percentage`, `result`, `remark`, `aC`, `aCG`, `sgpi`

---

## 🚀 Quickstart

### 1. Run K-Means Student Segmentation & Visual Analytics
```bash
python src/ml/clustering.py
```

### 2. Run Coursework-to-SGPI Regression Models
```bash
python src/ml/regression.py
```

### 3. Run All Machine Learning Pipelines
```bash
python src/ml/models.py
```

### 4. Run Exploratory Data Analysis (EDA)
```bash
python src/analytics/eda.py
```

### 5. Launch Interactive Jupyter Notebooks
```bash
jupyter notebook notebooks/
```
