# 🎓 AI & DS Semester-IV Academic Result Analysis & Machine Learning Workspace

This repository contains the end-to-end extracted dataset, structured pipelines, exploratory analytics, and machine learning models for the University of Mumbai Semester-IV **Artificial Intelligence and Data Science (AI & DS)** Examination.

---

## 📁 Repository Structure

```text
result-analysis-aids/
├── .gitignore                                  # Git exclusion rules (caches, temporary builds, scratch)
├── README.md                                   # Workspace documentation & quickstart guide
├── requirements.txt                            # Pinned Python package dependencies
│
├── data/
│   ├── raw/
│   │   └── AI&DS_SEM4_RESULTS.pdf              # Raw 47-page university result PDF gazette
│   ├── processed/
│   │   ├── AI_DS_SEM4_MASTER_RESULTS.csv       # Clean master dataset (88 students × 113 columns)
│   │   ├── AI_DS_SEM4_STUDENT_CLUSTERS_V2.csv  # Primary competency-based clustered dataset (K=4)
│   │   └── AI_DS_SEM4_CLUSTERED_STUDENTS.csv   # Baseline diagnostic clustered dataset (K=3)
│   ├── backups/                                # Checkpoint backups of pre-audit datasets
│   └── cache/
│       └── ocr_cache/                          # 47 raw OCR page extraction caches (gitignored)
│
├── deliverables/                               # Centralized stakeholder presentations & executive reports
│   ├── AI_DS_Sem4_Academic_Result_Analysis_Final.pptx       # 12-slide executive presentation
│   ├── AI_DS_SEM4_Academic_Result_Analysis_Presentation.pptx # 20-slide analytical deep-dive presentation
│   └── Academic_Result_Analysis_Report.docx                 # Formal executive Word analysis report
│
├── notebooks/                                  # Interactive Jupyter Notebook Workspaces
│   ├── eda_complete.ipynb                      # Comprehensive 100-cell EDA & visual analytics workspace
│   └── complete_data-analysis.ipynb            # Initial data ingestion & extraction audit workspace
│
├── src/                                        # Modular Python Package
│   ├── config.py                               # Subject codes, evaluation schemes, credits & file paths
│   ├── analytics/
│   │   └── eda.py                              # Visualizations, distributions & descriptive statistics
│   └── ml/
│       ├── feature_engineering.py              # Automated feature derivation (Theory/Lab ratios, health indices)
│       ├── clustering.py                       # Baseline K-Means clustering (3 clusters, 4 metrics, diagnostics)
│       ├── clustering_v2.py                    # Competency-based K-Means clustering (4 clusters, 17 features)
│       ├── regression.py                       # Predictive SGPI & total marks regression pipelines
│       └── models.py                           # Central runner for all ML models
│
├── reports/                                    # Analytical Artifacts & Ground-Truth Documentation
│   ├── AUDIT_AND_CORRECTION_REPORT.md          # Comprehensive PDF ground-truth audit & verification signoff
│   ├── clustering_v2_summary.txt               # Statistical profiles & personas for V2 clusters
│   ├── documentation/                          # Supporting Word documentation (QNA, technical reports)
│   │   ├── Academic_Result_Analysis_Report.docx
│   │   ├── data_analysis_report.docx
│   │   └── QNA.docx
│   └── figures/                                # High-resolution analytical charts & plots (>= 150 DPI)
│       ├── clustering_v2_*.png                 # V2 radar, elbow, silhouette, PCA, boxplots
│       ├── kmeans_*.png                        # Baseline V1 diagnostic & persona plots
│       └── extracted_eda/                      # Notebook-rendered exploratory charts
│
└── scripts/                                    # Standalone analytical tools & generators
    ├── generators/                             # Document & presentation generation pipelines
    │   ├── generate_powerpoint_presentation.py # Builds 20-slide analytical presentation
    │   ├── generate_word_report.py             # Generates executive Word report
    │   └── build_deck.mjs                      # MJS presentation compiler
    ├── analytics/                              # Student profiles & comparative queries
    │   ├── compare_shivam_stats.py             # Class topper academic profile comparison
    │   ├── compare_arya_stats.py               # Mid-tier student profile comparison
    │   ├── top_rankers_compare.py              # Comparative ranker analysis
    │   └── weakest_subject_analysis.py         # Subject difficulty & failure metrics
    ├── audit/                                  # Data integrity & PDF verification scripts
    │   ├── audit_step1_inspect.py              # Schema inspection & legend sanity
    │   ├── audit_step3_comprehensive.py        # 5-invariant ground-truth audit validator
    │   ├── audit_legend.py                     # OCR bounding-box legend inspection
    │   └── crop_discrepant_students.py         # Visual PDF crop extraction for auditing
    └── archive/                                # Archived OCR parsing & debug utilities (48 prototypes)
```

---

## 📊 Dataset Schema Overview

The primary dataset [`data/processed/AI_DS_SEM4_MASTER_RESULTS.csv`](data/processed/AI_DS_SEM4_MASTER_RESULTS.csv) contains **88 students** and **113 features**:

1. **Student Identifiers**: `student_id`, `seat_no`, `name`, `gender`, `status`, `ern`, `college`, `page`
2. **Subject Assessments** (11 Courses):
   - **`OE_`** (Administrative Policy of Chhatrapati Shivaji Maharaj): `external`, `internal`, `total`, `grade`, `gp`, `credits`, `gc`
   - **`MINIPROJ_`** (Mini Project 2A): `term_work`, `oral`, `total`, `grade`, `gp`, `credits`, `gc`
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

### 1. Run Master Machine Learning Pipelines (Regression & Both K-Means Models)
```bash
python src/ml/models.py
```

### 2. Run Competency-Based Student Clustering (V2)
```bash
python src/ml/clustering_v2.py
```

### 3. Run Coursework-to-SGPI Regression
```bash
python src/ml/regression.py
```

### 4. Run Exploratory Data Analysis (EDA)
```bash
python src/analytics/eda.py
```

### 5. Generate Presentations and Reports
```bash
python scripts/generators/generate_powerpoint_presentation.py
python scripts/generators/generate_word_report.py
```

### 6. Run Student Spotlight & Subject Difficulty Analysis
```bash
python scripts/analytics/compare_shivam_stats.py
python scripts/analytics/weakest_subject_analysis.py
python scripts/analytics/top_rankers_compare.py
```

### 7. Run Comprehensive Ground-Truth Audit
```bash
python scripts/audit/audit_step3_comprehensive.py
```

### 8. Launch Interactive Jupyter Notebooks
```bash
jupyter notebook notebooks/eda_complete.ipynb
```
