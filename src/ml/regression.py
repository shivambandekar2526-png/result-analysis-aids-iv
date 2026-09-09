import os, sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import clone

sys.stdout.reconfigure(encoding='utf-8')

# Resolve repo root and data path
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(_BASE_DIR, "src"))

def run_regression_pipeline():
    # Load dataset from processed data directory
    data_path = os.path.join(_BASE_DIR, "data", "processed", "AI_DS_SEM4_MASTER_RESULTS.csv")
    df = pd.read_csv(data_path)
    
    # Internal Continuous Assessment Features (Available before External University Exams)
    coursework_features = [
        "OE_internal", "CT_internal", "DBMS_internal", "OS_internal", "FTS_internal",
        "MINIPROJ_term_work", "MINIPROJ_oral", "DBMS_LAB_term_work", "DBMS_LAB_oral",
        "OS_LAB_term_work", "OS_LAB_oral", "TC_LAB_term_work", "TC_LAB_oral",
        "BMD_term_work", "DT_term_work"
    ]
    
    X = df[coursework_features].fillna(0)
    
    print("=" * 80)
    print("      ACADEMIC PERFORMANCE PREDICTIVE REGRESSION BENCHMARK")
    print("=" * 80)
    print(f"Total Dataset Samples: {len(df)} Students | Input Features: {len(coursework_features)} Continuous Assessment Marks")
    print("Input Features:", ", ".join(coursework_features))
    
    # =========================================================================
    # EXPERIMENT 1: PREDICTING FINAL SGPI FROM INTERNAL COURSEWORK
    # =========================================================================
    print("\n" + "#" * 80)
    print(" EXPERIMENT 1: FORECASTING FINAL SEMESTER SGPI (SCALE: 0.0 - 10.0)")
    print("#" * 80)
    
    # Filter passed students or all students
    # Using all students with SGPI
    y_sgpi = df["sgpi"].fillna(0)
    
    # Train-Test Split (80% Train, 20% Test)
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_sgpi, test_size=0.20, random_state=42)
    
    base_models = {
        "Support Vector Regressor (SVR)": Pipeline([('scaler', StandardScaler()), ('reg', SVR(C=3.0, epsilon=0.1))]),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        "Ridge Regression (L2)": Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=2.0))]),
        "ElasticNet Regression": Pipeline([('scaler', StandardScaler()), ('reg', ElasticNet(alpha=0.05, l1_ratio=0.5))]),
        "Lasso Regression (L1)": Pipeline([('scaler', StandardScaler()), ('reg', Lasso(alpha=0.05))]),
        "Linear Regression": Pipeline([('scaler', StandardScaler()), ('reg', LinearRegression())])
    }
    
    results_sgpi = []
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    fitted_sgpi_models = {}
    
    for name, model_tmpl in base_models.items():
        model = clone(model_tmpl)
        cv_r2 = cross_val_score(model, X, y_sgpi, cv=kf, scoring='r2').mean()
        cv_mae = -cross_val_score(model, X, y_sgpi, cv=kf, scoring='neg_mean_absolute_error').mean()
        
        model.fit(X_train_s, y_train_s)
        y_pred_s = model.predict(X_test_s)
        
        r2 = r2_score(y_test_s, y_pred_s)
        mae = mean_absolute_error(y_test_s, y_pred_s)
        rmse = np.sqrt(mean_squared_error(y_test_s, y_pred_s))
        
        fitted_sgpi_models[name] = model
        
        results_sgpi.append({
            "Model": name,
            "Test R² Score": r2,
            "Test MAE (SGPI)": mae,
            "Test RMSE (SGPI)": rmse,
            "5-Fold CV R²": cv_r2,
            "5-Fold CV MAE": cv_mae
        })
        
    res_sgpi_df = pd.DataFrame(results_sgpi).sort_values(by="Test R² Score", ascending=False)
    print(res_sgpi_df.to_string(index=False))
    
    # Best Model Feature Importance
    best_rf = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    best_rf.fit(X, y_sgpi)
    importances = pd.Series(best_rf.feature_importances_, index=coursework_features).sort_values(ascending=False)
    
    print("\n--- Feature Importance: Key Coursework Drivers for SGPI ---")
    for rank, (feat, imp) in enumerate(importances.items(), start=1):
        bar = "█" * int(imp * 50)
        print(f" {rank:2d}. {feat:20s} : {imp*100:5.2f}% {bar}")
        
    # =========================================================================
    # EXPERIMENT 2: PREDICTING TOTAL MARKS (OUT OF 775)
    # =========================================================================
    print("\n" + "#" * 80)
    print(" EXPERIMENT 2: PREDICTING OVERALL MARKS (MAX: 775 MARKS)")
    print("#" * 80)
    
    y_marks = df["overall_total"].fillna(0)
    X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(X, y_marks, test_size=0.20, random_state=42)
    
    results_marks = []
    fitted_marks_models = {}
    
    for name, model_tmpl in base_models.items():
        model_m = clone(model_tmpl)
        model_m.fit(X_train_m, y_train_m)
        y_pred_m = model_m.predict(X_test_m)
        
        r2_m = r2_score(y_test_m, y_pred_m)
        mae_m = mean_absolute_error(y_test_m, y_pred_m)
        rmse_m = np.sqrt(mean_squared_error(y_test_m, y_pred_m))
        
        fitted_marks_models[name] = model_m
        
        results_marks.append({
            "Model": name,
            "Test R² Score": r2_m,
            "Test MAE (Marks)": mae_m,
            "Test RMSE (Marks)": rmse_m,
            "Error (% of Max 775)": (mae_m / 775.0) * 100
        })
        
    res_marks_df = pd.DataFrame(results_marks).sort_values(by="Test R² Score", ascending=False)
    print(res_marks_df.to_string(index=False))
    
    # =========================================================================
    # EXPERIMENT 3: SAMPLE PREDICTION INFERENCE ON SAMPLE PROFILES
    # =========================================================================
    print("\n" + "#" * 80)
    print(" EXPERIMENT 3: LIVE PREDICTION INFERENCE ON KEY STUDENT PROFILES")
    print("#" * 80)
    
    test_indices = [
        ("Shivam Bandekar (Class Topper)", df[df['name'].str.contains('SHIVAM', case=False)].index[0]),
        ("Arya Padwal (Mid-Tier Student)", df[df['name'].str.contains('PADWAL', case=False)].index[0]),
        ("Random Cohort Student", 10)
    ]
    
    # Train full model for inference
    sgpi_infer_model = Pipeline([('scaler', StandardScaler()), ('reg', SVR(C=3.0, epsilon=0.1))])
    sgpi_infer_model.fit(X, y_sgpi)
    
    marks_infer_model = Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=2.0))])
    marks_infer_model.fit(X, y_marks)
    
    for label, idx in test_indices:
        student_row = df.iloc[idx]
        student_x = X.iloc[[idx]]
        
        actual_sgpi = student_row['sgpi']
        pred_sgpi = sgpi_infer_model.predict(student_x)[0]
        
        actual_marks = student_row['overall_total']
        pred_marks = marks_infer_model.predict(student_x)[0]
        
        print(f"\nProfile: {label} ({student_row['name']})")
        print(f"  * Actual SGPI:  {actual_sgpi:5.2f}  |  Predicted SGPI:  {pred_sgpi:5.2f}  |  Diff: {pred_sgpi - actual_sgpi:+5.2f}")
        print(f"  * Actual Marks: {actual_marks:5.1f}  |  Predicted Marks: {pred_marks:5.1f}  |  Diff: {pred_marks - actual_marks:+5.1f} marks")

if __name__ == "__main__":
    run_regression_pipeline()
