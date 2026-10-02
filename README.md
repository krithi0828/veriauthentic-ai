# VeriAuthentic AI — Product Authenticity & Risk Verification Platform 🛡️

**Know what you're buying.**  
VeriAuthentic AI is a multi-signal product authenticity verification engine built with **Python, FastAPI, Jinja2, Vanilla CSS/JS, Scikit-Learn, and SQLite**. It combines official brand code registry verification with machine learning risk assessment for online marketplace listings.

---

## 🌟 Key Features

1. **AI Authenticity Risk Assessment**: 0–100 risk score calculated directly from Random Forest model classification probabilities.
2. **Multi-Signal Risk Decomposition**: Evaluates Price Risk, Seller Credibility Risk, Review Anomaly Risk, Text Description Risk, and Registry Status independently.
3. **Plain-Language Explainable AI**: Explains why a product was flagged with clear risk indicators (⚠️) and positive signals (✓).
4. **Brand Registry Code Lookup**: Instant validation of 12-character security code tags (`AUTH-XXXX-XXXX`) against official database tables.
5. **Duplicate / Reused Code Detection**: Telemetry tracking that flags authentication codes verified across multiple distinct user sessions.
6. **Smart Price Analyzer**: Live calculation comparing listed marketplace prices against official MSRP reference values.
7. **Seller Credibility Profile**: Composite trust metric based on seller account age, platform rating, and verification status.
8. **Natural Language Processing**: TF-IDF text vectorizer detecting suspicious counterfeit keyword phrases ("1:1 super copy", "liquidation fast ship", "mirror quality").
9. **Guided 3-Step Verification Wizard**: Task-first flow allowing shoppers to check code tags, listing details, or combined signals.
10. **Interactive Risk Sensitivity Simulator**: What-if simulation tool allowing users to tweak price, seller, and review parameters to re-score live via the model.
11. **Side-by-Side Listing Comparison**: Compare two marketplace listings simultaneously to identify lower risk purchasing options.
12. **Counterfeit Reporting Portal**: Multi-section user submission system generating unique reference tracking numbers (`REP-XXXX`).
13. **Administrator Management Console**: Protected admin dashboard with bcrypt authentication, product registry CRUD drawers, report workflow status management, and telemetry.
14. **Session-Scoped Verification History**: Searchable, filterable activity log with CSV export capability.
15. **100% Progressive Enhancement & WCAG 2.2 AA Accessibility**: Full functionality without JavaScript, visible focus rings, ARIA landmarks, and dark/light system theme support.

---

## 🏗️ Architecture Overview

```
product-authenticity-system/
├── app/
│   ├── main.py                     # FastAPI application routes & REST endpoints
│   ├── config.py                   # App settings, directory paths, and risk thresholds
│   ├── templates/                  # Jinja2 HTML templates (layout, index, verify, result, etc.)
│   ├── assets/                     # Design system CSS (tokens, base, components) & JS bundles
│   └── services/                   # Business logic (verification, registry, report, admin)
├── ml/                             # Machine Learning Pipeline
│   ├── feature_engineering.py      # Feature extraction & multi-signal rules
│   ├── train.py                    # Random Forest training pipeline
│   ├── evaluate.py                 # Evaluation metrics & confusion matrix generation
│   ├── predict.py                  # Real-time risk score prediction
│   └── explain.py                  # Explainability & feature importance breakdown
├── database/                       # SQLite Database
│   ├── database.py                 # Parameterized query helper functions
│   ├── schema.sql                  # Database table definitions
│   └── seed.py                     # Demo data generator & seed script
├── docs/                           # Documentation
│   ├── BLANK_PAGE_RCA.md           # Root Cause Analysis for Jinja layout bug
│   └── DESIGN_SYSTEM.md            # Visual design tokens & component guide
└── tests/                          # Automated Pytest & UI Regression Test Suite
```

---

## ⚡ Quick Start & Run Commands

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed Database
```bash
python database/seed.py
```

### 3. Train ML Pipeline (Optional - Pre-trained model provided)
```bash
python ml/train.py
python ml/evaluate.py
```

### 4. Run Application Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8085 --reload
```
Open **http://127.0.0.1:8085** in your browser.

### 5. Run Full Automated Test Suite
```bash
python -m pytest tests/
```

---

## 🔐 Admin Credentials (Demo)
- **URL**: `/admin`
- **Username**: `admin`
- **Password**: `admin123`

---

## 📜 Seeded Sample Authentication Codes for Testing
- **Genuine Registered Code**: `AUTH-NIKE-7712` (Nike Air Max 270 Sneakers)
- **Reused Duplicate Alert Code**: `AUTH-ROLEX-1001` (Checked across multiple user sessions)
- **Unregistered Code**: `AUTH-FAKE-9999` (Triggers registration alert)
