import random
import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from database.database import (
    get_all_products,
    get_product_by_id,
    get_product_by_auth_code,
    add_product,
    update_product as db_update_product,
    delete_product as db_delete_product
)

def generate_random_code(prefix: str = "AUTH") -> str:
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    return f"{prefix}-{part1}-{part2}"

class RegistryService:
    @staticmethod
    def get_products(limit: int = 100, offset: int = 0, search: str = "") -> List[Dict[str, Any]]:
        return get_all_products(limit=limit, offset=offset, search=search)

    @staticmethod
    def get_product(product_id: str) -> Optional[Dict[str, Any]]:
        return get_product_by_id(product_id)

    @staticmethod
    def get_by_code(auth_code: str) -> Optional[Dict[str, Any]]:
        return get_product_by_auth_code(auth_code)

    @staticmethod
    def create_product(data: Dict[str, Any]) -> int:
        return add_product(data)

    @staticmethod
    def update_product(product_id: str, data: Dict[str, Any]) -> bool:
        return db_update_product(product_id, data)

    @staticmethod
    def delete_product(product_id: str) -> bool:
        return db_delete_product(product_id)

    @staticmethod
    def generate_batch_auth_codes(count: int = 10, prefix: str = "AUTH") -> List[str]:
        generated = []
        attempts = 0
        max_attempts = count * 10
        while len(generated) < count and attempts < max_attempts:
            attempts += 1
            code = generate_random_code(prefix=prefix)
            if not get_product_by_auth_code(code) and code not in generated:
                generated.append(code)
        return generated

    @staticmethod
    def bulk_import_csv(csv_text: str) -> Tuple[int, int, List[str]]:
        success_count = 0
        error_count = 0
        errors = []
        
        reader = csv.DictReader(io.StringIO(csv_text))
        required_cols = {"product_id", "product_name", "brand", "authentication_code"}
        
        if not required_cols.issubset(set(reader.fieldnames or [])):
            missing = required_cols - set(reader.fieldnames or [])
            return 0, 1, [f"Missing required CSV columns: {', '.join(missing)}"]
            
        for idx, row in enumerate(reader, start=1):
            auth_code = str(row.get("authentication_code", "")).strip().upper()
            prod_id = str(row.get("product_id", "")).strip()
            
            if not auth_code or not prod_id:
                error_count += 1
                errors.append(f"Row {idx}: Missing product_id or authentication_code")
                continue
                
            if get_product_by_auth_code(auth_code):
                error_count += 1
                errors.append(f"Row {idx}: Code '{auth_code}' already exists in registry")
                continue
                
            p_data = {
                "product_id": prod_id,
                "product_name": row.get("product_name", "Imported Item"),
                "brand": row.get("brand", "Generic Brand"),
                "product_category": row.get("product_category", "General"),
                "authentication_code": auth_code,
                "batch_number": row.get("batch_number", "BATCH-IMP-01"),
                "manufacturing_date": row.get("manufacturing_date", "2024-01-01"),
                "origin_country": row.get("origin_country", "USA"),
                "reference_price": float(row.get("reference_price", 100.0)),
                "is_registered": True
            }
            try:
                add_product(p_data)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Row {idx}: DB Insertion Error ({e})")
                
        return success_count, error_count, errors
