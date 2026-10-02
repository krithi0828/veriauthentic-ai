import sqlite3
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.config import DB_PATH, BASE_DIR

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with get_connection(db_path) as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()

def get_product_by_auth_code(code: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE UPPER(authentication_code) = UPPER(?)", (code.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_product_by_id(product_id: str, db_path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_products(limit: int = 100, offset: int = 0, search: str = "", db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if search:
            query = """
                SELECT * FROM products 
                WHERE product_name LIKE ? OR brand LIKE ? OR authentication_code LIKE ? OR product_id LIKE ?
                ORDER BY created_at DESC LIMIT ? OFFSET ?
            """
            s = f"%{search}%"
            cursor.execute(query, (s, s, s, s, limit, offset))
        else:
            query = "SELECT * FROM products ORDER BY created_at DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def add_product(data: Dict[str, Any], db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO products (
                product_id, product_name, brand, product_category, authentication_code,
                batch_number, manufacturing_date, origin_country, reference_price, is_registered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            data.get("product_id"),
            data.get("product_name"),
            data.get("brand"),
            data.get("product_category", "General"),
            data.get("authentication_code"),
            data.get("batch_number", "BATCH-001"),
            data.get("manufacturing_date", "2024-01-01"),
            data.get("origin_country", "USA"),
            float(data.get("reference_price", 0.0)),
            bool(data.get("is_registered", True))
        ))
        conn.commit()
        return cursor.lastrowid

def update_product(product_id: str, data: Dict[str, Any], db_path: str = DB_PATH) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            UPDATE products SET
                product_name = ?, brand = ?, product_category = ?,
                authentication_code = ?, batch_number = ?, manufacturing_date = ?,
                origin_country = ?, reference_price = ?, is_registered = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = ?
        """
        cursor.execute(query, (
            data.get("product_name"),
            data.get("brand"),
            data.get("product_category"),
            data.get("authentication_code"),
            data.get("batch_number"),
            data.get("manufacturing_date"),
            data.get("origin_country"),
            float(data.get("reference_price", 0.0)),
            bool(data.get("is_registered", True)),
            product_id
        ))
        conn.commit()
        return cursor.rowcount > 0

def delete_product(product_id: str, db_path: str = DB_PATH) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount > 0

def log_verification_event(auth_code: str, session_id: str, ip_hash: str = "local_ip", listing_details_hash: str = "default_listing", db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO code_verification_events (authentication_code, session_id, ip_hash, listing_details_hash)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (auth_code.strip(), session_id, ip_hash, listing_details_hash))
        conn.commit()
        return cursor.lastrowid

def get_code_verification_count(auth_code: str, db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM code_verification_events WHERE UPPER(authentication_code) = UPPER(?)", (auth_code.strip(),))
        return cursor.fetchone()[0]

def check_code_reuse_alert(auth_code: str, current_session_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*), COUNT(DISTINCT session_id) FROM code_verification_events WHERE UPPER(authentication_code) = UPPER(?)",
            (auth_code.strip(),)
        )
        total_events, distinct_sessions = cursor.fetchone()
        
        # Check if verified from multiple different sessions
        alert = (total_events > 1 and distinct_sessions > 1)
        return {
            "total_verifications": total_events,
            "distinct_sessions": distinct_sessions,
            "reuse_alert": alert
        }

def add_verification_history(session_id: str, product_name: str, auth_code: str, prediction: int, risk_score: float, verification_type: str, db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO verification_history (session_id, product_name, authentication_code, prediction, risk_score, verification_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (session_id, product_name, auth_code, int(prediction), float(risk_score), verification_type))
        conn.commit()
        return cursor.lastrowid

def get_verification_history(session_id: Optional[str] = None, limit: int = 50, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if session_id:
            query = "SELECT * FROM verification_history WHERE session_id = ? ORDER BY created_at DESC LIMIT ?"
            cursor.execute(query, (session_id, limit))
        else:
            query = "SELECT * FROM verification_history ORDER BY created_at DESC LIMIT ?"
            cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def add_report(report_data: Dict[str, Any], db_path: str = DB_PATH) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO reports (
                product_name, brand, authentication_code, seller_name,
                purchase_location, reason, reporter_name, reporter_email,
                risk_score, prediction, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            report_data.get("product_name"),
            report_data.get("brand", ""),
            report_data.get("authentication_code", ""),
            report_data.get("seller_name", ""),
            report_data.get("purchase_location", ""),
            report_data.get("reason", ""),
            report_data.get("reporter_name", ""),
            report_data.get("reporter_email", ""),
            float(report_data.get("risk_score", 0.0)),
            int(report_data.get("prediction", 0)),
            report_data.get("status", "PENDING")
        ))
        conn.commit()
        return cursor.lastrowid

def get_all_reports(status_filter: Optional[str] = None, search: str = "", db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        params = []
        sql = "SELECT * FROM reports WHERE 1=1"
        if status_filter and status_filter != "ALL":
            sql += " AND status = ?"
            params.append(status_filter)
        if search:
            sql += " AND (product_name LIKE ? OR seller_name LIKE ? OR authentication_code LIKE ?)"
            s = f"%{search}%"
            params.extend([s, s, s])
        sql += " ORDER BY created_at DESC"
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

def update_report_status(report_id: int, status: str, db_path: str = DB_PATH) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
        conn.commit()
        return cursor.rowcount > 0

def get_analytics_summary(db_path: str = DB_PATH) -> Dict[str, Any]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM verification_history")
        total_verifications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM verification_history WHERE risk_score >= 51")
        high_risk_verifications = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM code_verification_events")
        total_verification_events = cursor.fetchone()[0]
        
        return {
            "total_products": total_products,
            "total_verifications": total_verifications,
            "high_risk_verifications": high_risk_verifications,
            "total_reports": total_reports,
            "total_verification_events": total_verification_events
        }

def get_admin_user(username: str, db_path: str = DB_PATH, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    close_at_end = False
    if conn is None:
        conn = get_connection(db_path)
        close_at_end = True
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_users WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        if close_at_end:
            conn.close()

def create_admin_user(username: str, password_hash: str, db_path: str = DB_PATH, conn: Optional[sqlite3.Connection] = None) -> int:
    close_at_end = False
    if conn is None:
        conn = get_connection(db_path)
        close_at_end = True
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO admin_users (username, password_hash) VALUES (?, ?)", (username.strip(), password_hash))
        conn.commit()
        return cursor.lastrowid
    finally:
        if close_at_end:
            conn.close()

