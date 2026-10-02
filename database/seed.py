import sys
import os
import random
import sqlite3
from pathlib import Path
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import DB_PATH, DATA_DIR, ADMIN_USERNAME, ADMIN_PASSWORD_HASH
# pyrefly: ignore [missing-import]
from database.database import init_db, get_connection, create_admin_user



def generate_auth_code() -> str:
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    return f"AUTH-{part1}-{part2}"

BRANDS_CATEGORIES = [
    ("Nike", "Footwear", 120.0, 300.0, "Premium athletic footwear with air cushion technology."),
    ("Rolex", "Luxury Watches", 8500.0, 25000.0, "Swiss precision mechanical timepiece with sapphire crystal."),
    ("Apple", "Smartphones", 999.0, 1599.0, "Flagship smartphone with titanium enclosure and A17 chip."),
    ("Sony", "Electronics", 349.0, 499.0, "Industry-leading noise cancelling wireless headphones."),
    ("Samsung", "Smartphones", 899.0, 1399.0, "Dynamic AMOLED display smartphone with integrated S-Pen."),
    ("Gucci", "Accessories", 450.0, 1200.0, "Italian leather luxury belt with interlocking GG buckle."),
    ("Dyson", "Appliances", 499.0, 699.0, "Multi-styler hair wrap tool with Coanda air styling technology."),
    ("Chanel", "Cosmetics", 160.0, 350.0, "Classic eau de parfum fragrance with floral aldehydes."),
    ("Ray-Ban", "Eyewear", 150.0, 250.0, "Classic aviator sunglasses with polarized UV-protection glass lenses."),
    ("Levi's", "Apparel", 69.0, 120.0, "Original fit denim jeans crafted from heavy cotton denim."),
    ("Adidas", "Footwear", 100.0, 220.0, "Boost foam responsive cushioning running shoes."),
    ("Bose", "Audio", 299.0, 429.0, "QuietComfort premium acoustic noise cancelling headphones."),
    ("Prada", "Luxury Goods", 1500.0, 3500.0, "Saffiano leather luxury tote handbag with metal logo plaque."),
    ("Louis Vuitton", "Luxury Goods", 1800.0, 4200.0, "Monogram canvas travel bag with natural cowhide trim."),
    ("Canon", "Cameras", 1200.0, 2800.0, "Full-frame mirrorless digital camera body with 4K video recording.")
]

GENUINE_DESCRIPTIONS = [
    "Official manufacturer product. Comes with full warranty, authentic serial code tag, and original packaging.",
    "Authorized distributor stock. Certified genuine product with standard brand guarantee and complete accessories.",
    "100% genuine retail package. Inspected and verified by official distribution center before shipment.",
    "Brand new sealed in original box with anti-tamper security sticker and serial number validation card."
]

COUNTERFEIT_DESCRIPTIONS = [
    "High quality replica 1:1 super copy! Direct factory liquidation clearance sale. Fast shipping no box.",
    "Grade 1A mirror quality original copy! Same factory OEM materials, unverified serial code clearance discount.",
    "Cheap 100% original copy high quality fast ship. Parallel import without factory box warranty card.",
    "Factory overstock liquidation! Direct import copy product, minor cosmetic flaw no box discount price."
]

def generate_demo_dataset(num_records: int = 650, output_csv: Path = None) -> pd.DataFrame:
    random.seed(42)
    records = []
    
    if output_csv is None:
        output_csv = DATA_DIR / "raw" / "products_demo.csv"
        
    os.makedirs(output_csv.parent, exist_ok=True)
    
    for i in range(1, num_records + 1):
        product_id = f"PRD-{1000 + i}"
        brand, category, min_ref, max_ref, base_desc = random.choice(BRANDS_CATEGORIES)
        ref_price = round(random.uniform(min_ref, max_ref), 2)
        
        # 70% genuine (label 0), 30% counterfeit (label 1)
        is_counterfeit = 1 if random.random() < 0.30 else 0
        
        auth_code = generate_auth_code()
        
        if is_counterfeit:
            # Suspicious metrics
            discount_pct = random.uniform(0.35, 0.75) # 35% to 75% off reference price
            listed_price = round(ref_price * (1.0 - discount_pct), 2)
            seller_age = random.randint(1, 75) # New account
            seller_rating = round(random.uniform(1.5, 3.8), 1)
            seller_verified = False if random.random() < 0.85 else True
            review_count = random.randint(3, 40)
            avg_rating = round(random.uniform(1.8, 4.9), 1)
            variance = round(random.uniform(1.4, 2.8), 2)
            extreme_ratio = round(random.uniform(0.65, 0.95), 2)
            one_star_pct = round(random.uniform(20.0, 50.0), 1)
            five_star_pct = round(100.0 - one_star_pct - random.uniform(5.0, 20.0), 1)
            desc = f"{brand} {category} item. " + random.choice(COUNTERFEIT_DESCRIPTIONS)
        else:
            # Genuine metrics
            discount_pct = random.uniform(-0.05, 0.15) # Small discount or full MSRP
            listed_price = round(ref_price * (1.0 - discount_pct), 2)
            seller_age = random.randint(150, 1800) # Established/trusted account
            seller_rating = round(random.uniform(4.3, 5.0), 1)
            seller_verified = True if random.random() < 0.90 else False
            review_count = random.randint(45, 850)
            avg_rating = round(random.uniform(4.2, 4.9), 1)
            variance = round(random.uniform(0.2, 0.8), 2)
            extreme_ratio = round(random.uniform(0.15, 0.45), 2)
            one_star_pct = round(random.uniform(1.0, 6.0), 1)
            five_star_pct = round(random.uniform(65.0, 85.0), 1)
            desc = f"{brand} {base_desc} " + random.choice(GENUINE_DESCRIPTIONS)
            
        prod_name = f"{brand} {category} Model-{random.randint(100, 999)}"
        
        records.append({
            "product_id": product_id,
            "product_name": prod_name,
            "brand": brand,
            "product_category": category,
            "listed_price": listed_price,
            "reference_price": ref_price,
            "seller_account_age_days": seller_age,
            "seller_rating": seller_rating,
            "seller_verified": seller_verified,
            "review_count": review_count,
            "average_rating": avg_rating,
            "rating_variance": variance,
            "extreme_rating_ratio": extreme_ratio,
            "one_star_pct": one_star_pct,
            "five_star_pct": five_star_pct,
            "product_description": desc,
            "authentication_code": auth_code,
            "label": is_counterfeit
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_csv, index=False)
    print(f"Generated {len(df)} synthetic records in {output_csv}")
    return df

def seed_database(db_path: str = DB_PATH, csv_path: Path = None) -> None:
    init_db(db_path)
    
    if csv_path is None or not csv_path.exists():
        csv_path = DATA_DIR / "raw" / "products_demo.csv"
        if not csv_path.exists():
            generate_demo_dataset(num_records=650, output_csv=csv_path)
            
    df = pd.read_csv(csv_path)
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Clear existing tables for seed reset
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM reports")
        cursor.execute("DELETE FROM verification_history")
        cursor.execute("DELETE FROM code_verification_events")
        cursor.execute("DELETE FROM admin_users")
        
        # 1. Insert products table
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO products (
                    product_id, product_name, brand, product_category,
                    authentication_code, batch_number, manufacturing_date,
                    origin_country, reference_price, is_registered
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row["product_id"]),
                str(row["product_name"]),
                str(row["brand"]),
                str(row["product_category"]),
                str(row["authentication_code"]),
                f"BATCH-{random.randint(100, 999)}",
                f"202{random.randint(2, 4)}-0{random.randint(1, 9)}-{random.randint(10, 28)}",
                random.choice(["USA", "Germany", "Japan", "Switzerland", "Italy", "France", "Vietnam", "China"]),
                float(row["reference_price"]),
                True
            ))
            
        # 2. Insert default admin user
        # admin credentials: username=admin, password=admin123
        create_admin_user(ADMIN_USERNAME, ADMIN_PASSWORD_HASH, db_path=db_path, conn=conn)
        
        # 3. Create 25 sample counterfeit reports
        sample_reasons = [
            "Serial number label looks blurred and misaligned on the box.",
            "Price was 70% below retail store price. Packaging smelled strongly of chemical glue.",
            "Authentication code failed lookup on the official website.",
            "Hardware stitching unraveled within 2 days of arrival. Material is fake plastic.",
            "Seller account deleted after payment. Received plastic fake item instead of metal original."
        ]
        
        product_rows = cursor.execute("SELECT product_name, brand, authentication_code FROM products LIMIT 50").fetchall()
        for i in range(25):
            prod = random.choice(product_rows)
            cursor.execute("""
                INSERT INTO reports (
                    product_name, brand, authentication_code, seller_name,
                    purchase_location, reason, reporter_name, reporter_email,
                    risk_score, prediction, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prod[0],
                prod[1],
                prod[2],
                f"Seller_{random.randint(100, 999)}",
                random.choice(["eBay Marketplace", "Social Media Ad", "Unauthorized Discount Site", "Third-party Store"]),
                random.choice(sample_reasons),
                f"User_{random.randint(10, 99)}",
                f"reporter{i}@example.com",
                round(random.uniform(55.0, 95.0), 1),
                1,
                random.choice(["PENDING", "UNDER_REVIEW", "VERIFIED_COUNTERFEIT", "DISMISSED"])
            ))
            
        # 4. Create 50+ verification history entries
        for i in range(55):
            prod = random.choice(product_rows)
            score = round(random.uniform(5.0, 90.0), 1)
            pred = 1 if score > 50.0 else 0
            cursor.execute("""
                INSERT INTO verification_history (
                    session_id, product_name, authentication_code, prediction, risk_score, verification_type
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"session_demo_{random.randint(1, 5)}",
                prod[0],
                prod[2],
                pred,
                score,
                random.choice(["CODE_LOOKUP", "AI_LISTING_ANALYSIS", "COMBINED_VERIFICATION"])
            ))
            
        # 5. Create 10 code verification events (including duplicate detection tests)
        reused_code = product_rows[0][2] # Code used in multiple distinct sessions
        cursor.execute("INSERT INTO code_verification_events (authentication_code, session_id, ip_hash, listing_details_hash) VALUES (?, ?, ?, ?)",
                       (reused_code, "session_user_A", "ip_hash_111", "hash_details_1"))
        cursor.execute("INSERT INTO code_verification_events (authentication_code, session_id, ip_hash, listing_details_hash) VALUES (?, ?, ?, ?)",
                       (reused_code, "session_user_B", "ip_hash_222", "hash_details_2"))
        cursor.execute("INSERT INTO code_verification_events (authentication_code, session_id, ip_hash, listing_details_hash) VALUES (?, ?, ?, ?)",
                       (reused_code, "session_user_C", "ip_hash_333", "hash_details_3"))
                       
        for i in range(7):
            prod = random.choice(product_rows[1:])
            cursor.execute("INSERT INTO code_verification_events (authentication_code, session_id, ip_hash, listing_details_hash) VALUES (?, ?, ?, ?)",
                           (prod[2], f"session_{i}", f"ip_hash_{i}", f"hash_details_{i}"))
                           
        conn.commit()
        print(f"Database seeded successfully at {db_path}!")

if __name__ == "__main__":
    generate_demo_dataset()
    seed_database()
