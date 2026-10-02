-- SQL Schema for AI-Driven Product Authenticity Verification System

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    brand TEXT NOT NULL,
    product_category TEXT,
    authentication_code TEXT UNIQUE NOT NULL,
    batch_number TEXT,
    manufacturing_date DATE,
    origin_country TEXT,
    reference_price REAL,
    is_registered BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    brand TEXT,
    authentication_code TEXT,
    seller_name TEXT,
    purchase_location TEXT,
    reason TEXT,
    reporter_name TEXT,
    reporter_email TEXT,
    risk_score REAL,
    prediction INTEGER,
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verification_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    product_name TEXT,
    authentication_code TEXT,
    prediction INTEGER,
    risk_score REAL,
    verification_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS code_verification_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    authentication_code TEXT NOT NULL,
    session_id TEXT,
    ip_hash TEXT,
    listing_details_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimized querying
CREATE INDEX IF NOT EXISTS idx_products_auth_code ON products(authentication_code);
CREATE INDEX IF NOT EXISTS idx_products_product_id ON products(product_id);
CREATE INDEX IF NOT EXISTS idx_events_auth_code ON code_verification_events(authentication_code);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
