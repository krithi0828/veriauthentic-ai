import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import tempfile
import os
from database.database import init_db, add_product, get_product_by_auth_code
from ml.predict import predict_authenticity

class TestVerificationWorkflow(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)
        add_product({
            "product_id": "PRD-AUTH-001",
            "product_name": "Authentic Sony Headphones",
            "brand": "Sony",
            "authentication_code": "AUTH-SONY-VALID",
            "reference_price": 399.0
        }, db_path=self.db_path)

    def tearDown(self):
        try:
            os.close(self.db_fd)
        except Exception:
            pass
        try:
            if os.path.exists(self.db_path):
                os.unlink(self.db_path)
        except PermissionError:
            pass


    def test_registered_code_lookup(self):
        prod = get_product_by_auth_code("AUTH-SONY-VALID", db_path=self.db_path)
        self.assertIsNotNone(prod)
        self.assertEqual(prod["product_name"], "Authentic Sony Headphones")

    def test_missing_code_lookup(self):
        prod = get_product_by_auth_code("AUTH-NONEXISTENT", db_path=self.db_path)
        self.assertIsNone(prod)

    def test_combined_verification_flow(self):
        raw_input = {
            "product_name": "Authentic Sony Headphones",
            "brand": "Sony",
            "reference_price": 399.0,
            "listed_price": 380.0,
            "seller_account_age_days": 500,
            "seller_rating": 4.9,
            "seller_verified": True,
            "product_description": "Official Sony noise cancelling headphones with serial number tag.",
            "authentication_code": "AUTH-SONY-VALID"
        }
        res = predict_authenticity(raw_input, registered_codes={"AUTH-SONY-VALID"})
        self.assertEqual(res["engineered_features"]["code_registered"], 1)
        self.assertLess(res["risk_score"], 30.0)

if __name__ == "__main__":
    unittest.main()
