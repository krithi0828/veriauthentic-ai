import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import os
import tempfile
from database.database import (
    init_db,
    get_connection,
    add_product,
    get_product_by_auth_code,
    get_product_by_id,
    delete_product,
    add_report,
    get_all_reports,
    log_verification_event,
    check_code_reuse_alert
)

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)

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


    def test_product_crud(self):
        p_data = {
            "product_id": "PRD-TEST-1",
            "product_name": "Test Product",
            "brand": "TestBrand",
            "product_category": "Testing",
            "authentication_code": "AUTH-TEST-1234",
            "reference_price": 250.0,
            "is_registered": True
        }
        add_product(p_data, db_path=self.db_path)
        
        fetched = get_product_by_auth_code("AUTH-TEST-1234", db_path=self.db_path)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["product_name"], "Test Product")
        
        by_id = get_product_by_id("PRD-TEST-1", db_path=self.db_path)
        self.assertIsNotNone(by_id)
        
        deleted = delete_product("PRD-TEST-1", db_path=self.db_path)
        self.assertTrue(deleted)
        self.assertIsNone(get_product_by_id("PRD-TEST-1", db_path=self.db_path))

    def test_duplicate_code_detection(self):
        code = "AUTH-REUSE-999"
        log_verification_event(code, "session_1", db_path=self.db_path)
        log_verification_event(code, "session_2", db_path=self.db_path)
        
        alert_info = check_code_reuse_alert(code, "session_2", db_path=self.db_path)
        self.assertTrue(alert_info["reuse_alert"])
        self.assertEqual(alert_info["distinct_sessions"], 2)

    def test_reports_operations(self):
        rep = {
            "product_name": "Fake Watch",
            "brand": "Rolex",
            "authentication_code": "AUTH-FAKE",
            "reason": "Cheap plastic feel",
            "reporter_name": "Jane",
            "reporter_email": "jane@example.com"
        }
        add_report(rep, db_path=self.db_path)
        all_reps = get_all_reports(db_path=self.db_path)
        self.assertGreaterEqual(len(all_reps), 1)

if __name__ == "__main__":
    unittest.main()
