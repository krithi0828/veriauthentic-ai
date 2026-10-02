import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIRoutes(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app_name"], "VeriAuthentic AI")

    def test_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("VeriAuthentic AI", res.text)

    def test_dashboard_page(self):
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)

    def test_verify_page(self):
        res = self.client.get("/verify")
        self.assertEqual(res.status_code, 200)

    def test_code_verification_api(self):
        res = self.client.post("/api/v1/verify/code", data={"auth_code": "AUTH-NIKE-7712"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn("Verification Result", res.text)

    def test_history_csv_export(self):
        res = self.client.get("/api/v1/history/export")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers["content-type"], "text/csv; charset=utf-8")

if __name__ == "__main__":
    unittest.main()
