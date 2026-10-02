import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
from app.services.verification_service import VerificationService
from app.services.registry_service import RegistryService
from app.services.report_service import ReportService
from app.services.admin_service import AdminService

class TestServices(unittest.TestCase):
    
    def test_verification_code_lookup(self):
        res = VerificationService.verify_code("AUTH-NIKE-7712", session_id="test_sess")
        self.assertIn("result_id", res)
        self.assertIn("registered", res)

    def test_analyze_listing(self):
        listing = {
            "product_name": "Test Headphone",
            "brand": "Sony",
            "reference_price": 300.0,
            "listed_price": 280.0,
            "seller_account_age_days": 400,
            "seller_rating": 4.8,
            "seller_verified": True,
            "product_description": "Official genuine headphones"
        }
        res = VerificationService.analyze_listing(listing, session_id="test_sess")
        self.assertIn("risk_score", res)
        self.assertLess(res["risk_score"], 50.0)

    def test_batch_code_generator(self):
        codes = RegistryService.generate_batch_auth_codes(count=5)
        self.assertEqual(len(codes), 5)
        for c in codes:
            self.assertTrue(c.startswith("AUTH-"))

    def test_admin_authentication_and_lockout(self):
        success, token = AdminService.verify_credentials("admin", "admin123", client_ip="127.0.0.99")
        self.assertTrue(success)
        self.assertTrue(AdminService.validate_session(token))

if __name__ == "__main__":
    unittest.main()
