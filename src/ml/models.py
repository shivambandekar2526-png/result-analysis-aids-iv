import os, sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

# Ensure imports work both from root and src/ml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.feature_engineering import load_and_engineer_features
from ml.clustering import run_kmeans_clustering

def run_ml_experiments():
    df = load_and_engineer_features()
    
    # 1. Regression: Predict Grand Total from internal coursework marks
    coursework_features = [
        "OE_internal", "CT_internal", "DBMS_internal", "OS_internal", "FTS_internal",
        "MINIPROJ_term_work", "MINIPROJ_oral", "DBMS_LAB_term_work", "DBMS_LAB_oral",
        "OS_LAB_term_work", "OS_LAB_oral", "TC_LAB_term_work", "TC_LAB_oral",
        "BMD_term_work", "DT_term_work"
    ]
    
    X_reg = df[coursework_features].fillna(0)
    y_reg = df["overall_total"]
    
    X_train, X_test, y_train, y_test = train_test_split(X_reg, y_reg, test_size=0.25, random_state=42)
    
    reg_model = Ridge(alpha=1.0)
    reg_model.fit(X_train, y_train)
    y_pred_reg = reg_model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred_reg)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_reg))
    print("=" * 80)
    print("=== 1. COURSEWORK TO FINAL SCORE REGRESSION ===")
    print("=" * 80)
    print(f"Ridge Regression R² Score: {r2:.4f}")
    print(f"RMSE: {rmse:.2f} marks (out of 775)")
    
    # 2. Classification: Predict At-Risk Students
    y_cls = df["is_at_risk"]
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_reg, y_cls, test_size=0.25, random_state=42, stratify=y_cls)
    
    clf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    clf_model.fit(X_train_c, y_train_c)
    y_pred_cls = clf_model.predict(X_test_c)
    
    acc = accuracy_score(y_test_c, y_pred_cls)
    print("\n" + "=" * 80)
    print("=== 2. EARLY AT-RISK STUDENT PREDICTION CLASSIFIER ===")
    print("=" * 80)
    print(f"Accuracy: {acc*100:.2f}%")
    print("Classification Report:\n", classification_report(y_test_c, y_pred_cls, target_names=["Not At-Risk", "At-Risk"]))
    
    # Feature Importances
    importances = pd.Series(clf_model.feature_importances_, index=coursework_features).sort_values(ascending=False)
    print("Top 5 Indicative Coursework Predictors for At-Risk Status:")
    for feat, imp in importances.head(5).items():
        print(f"  - {feat:20s}: {imp*100:.2f}% importance")
        
    # 3. K-Means Student Segmentation & Visual Analytics
    print("\n")
    run_kmeans_clustering()

if __name__ == "__main__":
    run_ml_experiments()
