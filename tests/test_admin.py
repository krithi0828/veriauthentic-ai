import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
import tempfile
import os
from database.database import (
    init_db,
    create_admin_user,
    get_admin_user,
    add_product,
    get_all_products,
    delete_product
)
from app.pages.admin_dashboard import check_admin_credentials

class TestAdminPanel(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        init_db(self.db_path)
        create_admin_user("admin", "$2b$12$eImiTXuWVxfM37uY4JANjOL.81F8kF6J1.O7X5kO0p2N5g.zKqZ9e", db_path=self.db_path)

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


    def test_admin_user_retrieval(self):
        user = get_admin_user("admin", db_path=self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "admin")

    def test_admin_credentials(self):
        self.assertTrue(check_admin_credentials("admin", "admin123"))

    def test_admin_registry_management(self):
        p_data = {
            "product_id": "PRD-ADM-1",
            "product_name": "Admin Test Item",
            "brand": "AdminBrand",
            "authentication_code": "AUTH-ADM-001"
        }
        add_product(p_data, db_path=self.db_path)
        prods = get_all_products(db_path=self.db_path)
        self.assertEqual(len(prods), 1)
        
        delete_product("PRD-ADM-1", db_path=self.db_path)
        prods_after = get_all_products(db_path=self.db_path)
        self.assertEqual(len(prods_after), 0)

if __name__ == "__main__":
    unittest.main()
