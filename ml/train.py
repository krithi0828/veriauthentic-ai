import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from app.config import DATA_DIR, MODELS_DIR
from ml.model_config import RANDOM_SEED, PARAM_GRID_RF
from ml.preprocessing import prepare_dataset, get_preprocessor

def train_models():
    raw_path = DATA_DIR / "raw" / "products_demo.csv"
    processed_path = DATA_DIR / "processed" / "products_processed.csv"
    
    if not processed_path.exists():
        df = prepare_dataset(raw_path, processed_path)
    else:
        df = pd.read_csv(processed_path)
        
    X = df.drop(columns=["label", "product_id", "product_name", "brand", "product_category", "price_deviation_category", "account_age_category", "authentication_code"], errors="ignore")
    y = df["label"].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )
    
    # Preprocessing
    preprocessor = get_preprocessor()
    X_train_trans = preprocessor.fit_transform(X_train)
    X_test_trans = preprocessor.transform(X_test)
    
    print(f"Transformed training feature shape: {X_train_trans.shape}")
    
    # 1. Primary Model: Random Forest Classifier with GridSearchCV
    rf_base = RandomForestClassifier(class_weight="balanced", random_state=RANDOM_SEED)
    grid_search = GridSearchCV(
        estimator=rf_base,
        param_grid=PARAM_GRID_RF,
        cv=5,
        scoring="f1",
        n_jobs=-1
    )
    grid_search.fit(X_train_trans, y_train)
    best_rf = grid_search.best_estimator_
    print(f"Best Random Forest Params: {grid_search.best_params_}")
    
    # 2. Baseline Model: Logistic Regression
    lr_model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=RANDOM_SEED)
    lr_model.fit(X_train_trans, y_train)
    
    # Save artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_rf, MODELS_DIR / "random_forest_model.pkl")
    joblib.dump(lr_model, MODELS_DIR / "logistic_regression_model.pkl")
    joblib.dump(preprocessor, MODELS_DIR / "preprocessor.pkl")
    
    # Save train/test split arrays for evaluation
    np.savez(
        MODELS_DIR / "test_data.npz",
        X_test_trans=X_test_trans,
        y_test=y_test
    )
    
    print(f"Models successfully trained and saved to {MODELS_DIR}!")
    return best_rf, lr_model, preprocessor

if __name__ == "__main__":
    train_models()
