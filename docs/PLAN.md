# Migration Strategy & Implementation Roadmap

## Overview
This document outlines the step-by-step roadmap to transform **VeriAuthentic AI** into a commercial-grade SaaS web product powered by FastAPI, Jinja2, custom CSS design system, and ES-modules JS.

---

## 🚩 Execution Milestones

### Phase 0: Audit & Architecture Setup
- [x] Create `docs/UI_AUDIT.md` and `docs/PLAN.md`.
- [ ] Refactor business logic into framework-agnostic services (`app/services/`):
  - `verification_service.py`
  - `ml_service.py`
  - `registry_service.py`
  - `report_service.py`
  - `admin_service.py`

### Phase 1: Core FastAPI Backend & REST API
- [ ] Configure `pydantic-settings` in `app/config.py`.
- [ ] Implement versioned REST API (`/api/v1/`):
  - `/api/v1/verify/code`
  - `/api/v1/analyze/listing`
  - `/api/v1/verify/combined`
  - `/api/v1/compare`
  - `/api/v1/reports`
  - `/api/v1/health`
  - `/api/v1/admin/*`
- [ ] Implement CSRF protection, rate limiting, security headers, password hashing (bcrypt), and session security.

### Phase 2: Design System & Assets
- [ ] Local font files (Inter woff2 & JetBrains Mono woff2).
- [ ] CSS Design System (`app/assets/css/tokens.css`, `base.css`, `components.css`).
- [ ] Theme switcher engine (Light / Dark / System with flash prevention).
- [ ] Vendor Chart.js locally in `app/assets/js/chart.min.js`.
- [ ] SVG Icon library (`app/assets/icons/`) & Logo Mark (`logo.svg`, favicon, OG image).
- [ ] Living Styleguide page at `/styleguide`.

### Phase 3: Application Shell & Public Landing Page
- [ ] Base Jinja2 layout template with header, responsive navigation, topbar, Cmd+K search modal, footer, toasts, and modal containers.
- [ ] Public Marketing Home page (`/`) with Hero preview card, 3-step illustrations, Feature grid, Transparency card, and FAQ accordion.

### Phase 4: Product Workspaces & Result View
- [ ] Dashboard (`/dashboard`) with live KPI cards, sparklines, tables, and system metrics.
- [ ] Verify Product (`/verify`) with masked AUTH-XXXX-XXXX input, live price deviation calculator, barcode scanner integration, and file upload.
- [ ] Result View (`/result/{id}`) with SVG semicircular gauge, separate registry status card, multi-signal breakdown bars, explanation panel, print stylesheet (`@media print`), and PDF export layout.
- [ ] Risk Analysis Simulator (`/risk-analysis`) with real-time debounced slider re-scoring.
- [ ] Listing Comparison (`/compare`) with radar chart and side-by-side signal difference highlighter.

### Phase 5: Insights, Admin & Support Pages
- [ ] Analytics (`/analytics`) with model performance metrics, confusion matrix, ROC curve, and dataset overview.
- [ ] Model Card (`/model-card`) detailing model formulas, feature importances, and limitations.
- [ ] History (`/history`) session query log with CSV export.
- [ ] Report Counterfeit (`/report`) form with prefill support.
- [ ] Admin Portal (`/admin`): Login, Registry CRUD, Code generator, Reports workflow, Code reuse alerts, Model retrain & promote/rollback, and Audit log.
- [ ] Help Center (`/help`), Privacy Policy (`/privacy`), Terms of Use (`/terms`), and `docs/LEGAL_REVIEW_NEEDED.md`.

### Phase 6: Production Ops, Testing & Verification
- [ ] Pytest suite covering API endpoints, services, security, and ML models.
- [ ] Dockerfile and `docker-compose.yml`.
- [ ] Database backup scripts & Makefile commands.
- [ ] E2E testing, visual critique, Lighthouse & accessibility verification.
