import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

from app.config import MODELS_DIR, OUTPUTS_DIR

def evaluate_models():
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    rf_model = joblib.load(MODELS_DIR / "random_forest_model.pkl")
    lr_model = joblib.load(MODELS_DIR / "logistic_regression_model.pkl")
    
    test_data = np.load(MODELS_DIR / "test_data.npz")
    X_test = test_data["X_test_trans"]
    y_test = test_data["y_test"]
    
    # 1. Random Forest Predictions
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)[:, 1]
    
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_prec = precision_score(y_test, rf_preds, zero_division=0)
    rf_rec = recall_score(y_test, rf_preds, zero_division=0)
    rf_f1 = f1_score(y_test, rf_preds, zero_division=0)
    rf_auc = roc_auc_score(y_test, rf_probs)
    
    # 2. Logistic Regression Predictions
    lr_preds = lr_model.predict(X_test)
    lr_probs = lr_model.predict_proba(X_test)[:, 1]
    
    lr_acc = accuracy_score(y_test, lr_preds)
    lr_prec = precision_score(y_test, lr_preds, zero_division=0)
    lr_rec = recall_score(y_test, lr_preds, zero_division=0)
    lr_f1 = f1_score(y_test, lr_preds, zero_division=0)
    lr_auc = roc_auc_score(y_test, lr_probs)
    
    # Generate & Save Confusion Matrix Plot
    cm = confusion_matrix(y_test, rf_preds)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
                xticklabels=["Genuine (0)", "Counterfeit (1)"],
                yticklabels=["Genuine (0)", "Counterfeit (1)"])
    plt.title("Random Forest Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.tight_layout()
    cm_path = OUTPUTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    
    # Generate & Save Evaluation Report Markdown
    rf_report_str = classification_report(y_test, rf_preds, target_names=["Genuine", "Counterfeit"])
    lr_report_str = classification_report(y_test, lr_preds, target_names=["Genuine", "Counterfeit"])
    
    report_md = f"""# Model Evaluation Report

## Executive Summary
This report presents the empirical performance evaluation of the trained Machine Learning models for the **AI-Driven Product Authenticity Verification System**.

All metrics are calculated on an unseen 20% stratified test set ({len(y_test)} samples).

## Primary Model Performance: Random Forest Classifier

| Metric | Score |
| :--- | :--- |
| **Accuracy** | `{rf_acc:.4f}` ({rf_acc*100:.2f}%) |
| **Precision** | `{rf_prec:.4f}` ({rf_prec*100:.2f}%) |
| **Recall** | `{rf_rec:.4f}` ({rf_rec*100:.2f}%) |
| **F1-Score** | `{rf_f1:.4f}` ({rf_f1*100:.2f}%) |
| **ROC-AUC** | `{rf_auc:.4f}` ({rf_auc*100:.2f}%) |

### Detailed Classification Report (Random Forest)
```
{rf_report_str}
```

---

## Baseline Model Performance: Logistic Regression

| Metric | Score |
| :--- | :--- |
| **Accuracy** | `{lr_acc:.4f}` ({lr_acc*100:.2f}%) |
| **Precision** | `{lr_prec:.4f}` ({lr_prec*100:.2f}%) |
| **Recall** | `{lr_rec:.4f}` ({lr_rec*100:.2f}%) |
| **F1-Score** | `{lr_f1:.4f}` ({lr_f1*100:.2f}%) |
| **ROC-AUC** | `{lr_auc:.4f}` ({lr_auc*100:.2f}%) |

### Detailed Classification Report (Logistic Regression)
```
{lr_report_str}
```

---

## Confusion Matrix Visualization
Confusion Matrix saved at: `outputs/confusion_matrix.png`
"""
    
    report_path = OUTPUTS_DIR / "evaluation_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"Evaluation report generated at {report_path}")
    print(f"Random Forest Accuracy: {rf_acc*100:.2f}%, F1: {rf_f1*100:.2f}%, ROC-AUC: {rf_auc*100:.2f}%")
    return {
        "rf_accuracy": rf_acc,
        "rf_f1": rf_f1,
        "rf_auc": rf_auc,
        "lr_accuracy": lr_acc,
        "lr_f1": lr_f1
    }

if __name__ == "__main__":
    evaluate_models()
