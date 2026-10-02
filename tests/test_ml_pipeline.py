import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import os
import joblib
import pandas as pd
from app.config import MODELS_DIR
from ml.predict import predict_authenticity
from ml.explain import explain_prediction

class TestMLPipeline(unittest.TestCase):
    
    def test_models_exist(self):
        self.assertTrue((MODELS_DIR / "random_forest_model.pkl").exists(), "Random Forest model file missing")
        self.assertTrue((MODELS_DIR / "logistic_regression_model.pkl").exists(), "Logistic Regression model file missing")
        self.assertTrue((MODELS_DIR / "preprocessor.pkl").exists(), "Preprocessor artifact file missing")

    def test_prediction_genuine_sample(self):
        sample_genuine = {
            "product_name": "Nike Air Max 270 Genuine",
            "brand": "Nike",
            "reference_price": 160.0,
            "listed_price": 150.0,
            "seller_account_age_days": 400,
            "seller_rating": 4.8,
            "seller_verified": True,
            "review_count": 120,
            "average_rating": 4.7,
            "rating_variance": 0.4,
            "extreme_rating_ratio": 0.3,
            "one_star_pct": 3.0,
            "five_star_pct": 75.0,
            "product_description": "Official Nike sneakers with authentic barcode tag.",
            "authentication_code": "AUTH-TEST-GENUINE",
            "code_registered": 1
        }
        res = predict_authenticity(sample_genuine)
        self.assertIn("risk_score", res)
        self.assertIn("prediction", res)
        self.assertLess(res["risk_score"], 50.0, "Genuine sample should receive low risk score")

    def test_prediction_suspicious_sample(self):
        sample_suspicious = {
            "product_name": "Rolex Submariner Copy",
            "brand": "Rolex",
            "reference_price": 10000.0,
            "listed_price": 200.0,
            "seller_account_age_days": 10,
            "seller_rating": 1.8,
            "seller_verified": False,
            "review_count": 5,
            "average_rating": 4.9,
            "rating_variance": 2.5,
            "extreme_rating_ratio": 0.95,
            "one_star_pct": 40.0,
            "five_star_pct": 50.0,
            "product_description": "1:1 super copy replica mirror quality fast ship no box direct factory liquidation.",
            "authentication_code": "AUTH-TEST-FAKE",
            "code_registered": 0
        }
        res = predict_authenticity(sample_suspicious)
        self.assertIn("risk_score", res)
        self.assertGreater(res["risk_score"], 50.0, "Suspicious sample should receive high risk score")

    def test_explainability_output(self):
        sample = {
            "product_name": "Test Item",
            "reference_price": 500.0,
            "listed_price": 100.0,
            "seller_account_age_days": 5,
            "seller_rating": 2.0,
            "seller_verified": False,
            "product_description": "super copy replica"
        }
        res = predict_authenticity(sample)
        exp = explain_prediction(res)
        self.assertIn("risk_factors", exp)
        self.assertIn("positive_signals", exp)
        self.assertIn("ai_recommendations", exp)

if __name__ == "__main__":
    unittest.main()
