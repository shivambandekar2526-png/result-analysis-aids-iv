# 🎓 AI & DS Semester-IV Academic Result Analysis & Machine Learning Workspace

This repository contains the end-to-end extracted dataset, structured pipelines, exploratory analytics, and machine learning models for the University of Mumbai Semester-IV **Artificial Intelligence and Data Science (AI & DS)** Regular Examination.

---

## 📁 Repository Structure

```text
result-analysis-aids/
├── data/
│   ├── raw/
│   │   └── AI&DS_SEM4_RESULTS.pdf              # Original 47-page university result PDF
│   ├── processed/
│   │   └── AI_DS_SEM4_MASTER_RESULTS.csv       # Complete master dataset (88 students × 113 columns)
│   └── cache/
│       └── ocr_cache/                          # Cached OCR bounding box extractions (Pages 0–46)
│
├── notebooks/                                  # Interactive Jupyter Notebook Workspaces
│   ├── 01_eda_and_academic_analytics.ipynb     # Grade distribution, SGPI trends & descriptive statistics
│   ├── 02_grade_distribution_and_correlations.ipynb # Course-by-course performance & correlation heatmaps
│   └── 03_predictive_modeling_and_ml.ipynb     # Regression, At-Risk Classification & K-Means Clustering
│
├── src/                                        # Modular Python Package
│   ├── config.py                               # Subject codes, schemes, credits & path configurations
│   ├── extraction/                             # Extraction & table reconstruction logic
│   ├── analytics/
│   │   └── eda.py                              # Visualizations, distributions & reporting scripts
│   └── ml/
│       ├── feature_engineering.py              # Automated feature derivation (Theory/Lab ratios, health indices)
│       └── models.py                           # Regression, Classification & Clustering pipelines
│
├── reports/
│   ├── figures/                                # High-resolution analytical charts & plots
│   │   ├── sgpa_distribution.png
│   │   ├── result_breakdown.png
│   │   └── subject_performance_comparison.png
│   └── executive_summary.md                    # Detailed extraction and performance overview
│
└── scripts/
    └── archive/                                # Archived scratch & diagnostic tools
```

---

## 📊 Dataset Schema Overview

The primary dataset [`data/processed/AI_DS_SEM4_MASTER_RESULTS.csv`](data/processed/AI_DS_SEM4_MASTER_RESULTS.csv) contains **88 students** and **113 features**:

1. **Student Identifiers**: `student_id`, `seat_no`, `name`, `gender`, `status`, `ern`, `college`, `page`
2. **Subject Assessments** (11 Subjects):
   - **`OE_`** (Administrative Policy of Chhatrapati Shivaji Maharaja): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`MINIPROJ_`** (Mini Project): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`CT_`** (Computational Theory): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DBMS_`** (Database Management System): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`OS_`** (Operating System): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DBMS_LAB_`** (Database Management System Lab): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`OS_LAB_`** (Operating System Lab): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`FTS_`** (Fundamentals of Telecommunication Systems): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`TC_LAB_`** (Basic Telecommunication Experiments): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`BMD_`** (Business Model Development): `term_work`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`DT_`** (Design Thinking): `term_work`, `total`, `grade`, `gp`, `credits`, `gc`
3. **Academic Summary**: `overall_total`, `maximum_total`, `percentage`, `result`, `remark`, `aC`, `aCG`, `sgpi`

---

## 🚀 Quickstart & Notebook Workspaces

### 1. Run Data Analysis
```bash
python src/analytics/eda.py
```

### 2. Run Machine Learning Models
```bash
python src/ml/models.py
```

### 3. Launch Interactive Jupyter Notebooks
```bash
jupyter notebook notebooks/
```
