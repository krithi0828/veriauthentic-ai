import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "VeriAuthentic AI"
    APP_TAGLINE: str = "Know what you're buying."
    APP_SUBLINE: str = "Registry verification and AI risk assessment for product listings."
    
    DATA_MODE: str = "demo" # "demo" or "production"
    
    DATABASE_PATH: str = str(BASE_DIR / "database" / "product_authenticity.db")
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = "$2b$12$eImiTXuWVxfM37uY4JANjOL.81F8kF6J1.O7X5kO0p2N5g.zKqZ9e" # default: admin123
    SESSION_SECRET: str = "super-secret-production-key-change-me"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Directories
APP_DIR = BASE_DIR / "app"
ML_DIR = BASE_DIR / "ml"
DB_DIR = BASE_DIR / "database"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"
ASSETS_DIR = APP_DIR / "assets"
TEMPLATES_DIR = APP_DIR / "templates"

# Create required directories
for d in [DATA_DIR / "raw", DATA_DIR / "processed", MODELS_DIR, OUTPUTS_DIR, ASSETS_DIR / "css", ASSETS_DIR / "js", ASSETS_DIR / "icons", ASSETS_DIR / "fonts", TEMPLATES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = settings.DATABASE_PATH
ADMIN_USERNAME = settings.ADMIN_USERNAME
ADMIN_PASSWORD_HASH = settings.ADMIN_PASSWORD_HASH
DATA_MODE = settings.DATA_MODE

# Risk Thresholds
RISK_CATEGORIES = {
    "LOW": {"min": 0, "max": 25, "label": "Low Risk", "badge": "risk-low", "color": "#10b981"},
    "MODERATE": {"min": 26, "max": 50, "label": "Moderate Risk", "badge": "risk-moderate", "color": "#f59e0b"},
    "HIGH": {"min": 51, "max": 75, "label": "High Risk", "badge": "risk-high", "color": "#f97316"},
    "CRITICAL": {"min": 76, "max": 100, "label": "Critical Risk", "badge": "risk-critical", "color": "#ef4444"}
}

def get_risk_level_info(score: float):
    score = max(0.0, min(100.0, float(score)))
    if score <= 25:
        return RISK_CATEGORIES["LOW"]
    elif score <= 50:
        return RISK_CATEGORIES["MODERATE"]
    elif score <= 75:
        return RISK_CATEGORIES["HIGH"]
    else:
        return RISK_CATEGORIES["CRITICAL"]
