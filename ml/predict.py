import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any

from app.config import MODELS_DIR, get_risk_level_info
from ml.feature_engineering import extract_features_single


_rf_model = None
_preprocessor = None

def load_ml_pipeline():
    global _rf_model, _preprocessor
    if _rf_model is None:
        _rf_model = joblib.load(MODELS_DIR / "random_forest_model.pkl")
    if _preprocessor is None:
        _preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
    return _rf_model, _preprocessor

def predict_authenticity(raw_input: Dict[str, Any], registered_codes: set = None, db_check_func=None) -> Dict[str, Any]:
    rf_model, preprocessor = load_ml_pipeline()
    
    # 1. Feature extraction
    features = extract_features_single(raw_input, registered_codes=registered_codes)
    
    # Check registry status dynamically if callback provided
    auth_code = str(raw_input.get("authentication_code", "")).strip().upper()
    if db_check_func and auth_code:
        db_product = db_check_func(auth_code)
        if db_product:
            features["code_registered"] = 1
        else:
            features["code_registered"] = 0
            
    df_feat = pd.DataFrame([features])
    
    # 2. Transform features
    X_trans = preprocessor.transform(df_feat)
    
    # 3. Model prediction
    pred = int(rf_model.predict(X_trans)[0])
    probs = rf_model.predict_proba(X_trans)[0]
    
    prob_genuine = float(probs[0])
    prob_counterfeit = float(probs[1])
    
    # Authenticity Risk Score (0-100)
    risk_score = round(prob_counterfeit * 100.0, 1)
    confidence_pct = round(float(np.max(probs)) * 100.0, 1)
    risk_info = get_risk_level_info(risk_score)
    
    # 4. Multi-Signal Risk Breakdown
    price_dev = features["price_deviation_pct"]
    price_risk = round(max(0.0, min(100.0, (price_dev / 50.0) * 100.0 if price_dev > 0 else 0.0)), 1)
    
    seller_cred = features["seller_credibility_score"]
    seller_risk = round(max(0.0, min(100.0, 100.0 - seller_cred)), 1)
    
    review_risk = round(float(features["review_authenticity_signal"]), 1)
    
    susp_kw = features["suspicious_keyword_count"]
    text_risk = round(min(100.0, (susp_kw * 35.0) + (features["uppercase_ratio"] * 50.0)), 1)
    
    registry_risk = 0.0 if features["code_registered"] == 1 else 100.0
    
    breakdown = {
        "price_risk": price_risk,
        "seller_risk": seller_risk,
        "review_risk": review_risk,
        "text_risk": text_risk,
        "registry_risk": registry_risk
    }
    
    return {
        "prediction": pred, # 0 = Genuine, 1 = Counterfeit/Suspicious
        "prediction_label": "Counterfeit / Suspicious" if pred == 1 else "Genuine Product",
        "probability_genuine": prob_genuine,
        "probability_counterfeit": prob_counterfeit,
        "risk_score": risk_score,
        "confidence_pct": confidence_pct,
        "risk_level_info": risk_info,
        "multi_signal_breakdown": breakdown,
        "engineered_features": features
    }
