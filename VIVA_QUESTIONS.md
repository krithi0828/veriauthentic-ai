# VeriAuthentic AI — Viva Voce Questions & Answers

This document contains comprehensive answers for oral examinations, technical reviews, and architecture defense based on the **actual implementation** of VeriAuthentic AI.

---

## Q1: How does the AI authenticity risk score calculation work?
**Answer:**  
The risk score is calculated as a rounded percentage from the classification probability of a Random Forest Classifier trained on synthetic product listing data:
$$\text{Risk Score} = \text{Round}(100 \times P(\text{Counterfeit}))$$
The engine assigns scores into four discrete risk bands:
- **Low Risk (0–25%)**: Strong genuine signals, matching registry code.
- **Moderate Risk (26–50%)**: Slight price deviation or unverified seller history.
- **High Risk (51–75%)**: Multiple warning flags (e.g. 40%+ discount, low seller rating).
- **Critical Risk (76–100%)**: Extreme discount, suspicious TF-IDF keywords ("1:1 super copy"), or code reuse.

---

## Q2: How does the system handle progressive enhancement and offline JavaScript resiliency?
**Answer:**  
We enforce a strict **Progressive Enhancement Guarantee**:
1. All core HTML elements and text are rendered server-side via Jinja2 templates and are 100% visible and interactive with JavaScript disabled.
2. Initial hidden animation states (e.g. `opacity: 0` or `transform: translateY(24px)`) are applied **only** when JavaScript dynamically attaches the `.js` class to the `<html>` root element (`html.js .reveal-on-scroll`).
3. If JavaScript fails or throws an exception, content remains completely visible, and a non-blocking error boundary banner (`#js-error-banner`) informs the user without disrupting the page layout.

---

## Q3: What was the root cause of the blank home page rendering bug, and how was it fixed?
**Answer:**  
The root cause was a **Jinja2 structural layout block misplacement** in `app/templates/layout.html`.  
When `is_public_page=True` was passed to the render function (on public marketing routes like `/`, `/help`, `/privacy`), Jinja evaluated the `{% if is_public_page %}` branch. However, `{% block content %}` had been accidentally placed exclusively inside the `{% else %}` block (which was reserved for the internal app shell). As a result, Jinja rendered the header, skipped `{% else %}`, and jumped directly to `<footer>`, leaving 0 bytes of content in the main body.

**Fix:** Re-architected `layout.html` so that `<main id="main-content">` and `{% block content %}` exist in a unified container rendered for both public layout and app shell layout, while ensuring `{% block content %}` is compiled exactly once per template.

---

## Q4: Why are Brand Registry Verification and ML Risk Assessment displayed in separate cards?
**Answer:**  
To prevent misleading users with a single merged score. A product code existing in a manufacturer database does not prove that a physical item shipped by an unverified third-party seller is authentic. Conversely, an unregistered code tag indicates database absence, even if the listing details appear normal. Presenting **Registry Status** (rule-based database lookup) and **ML Risk Assessment** (statistical pattern prediction) in distinct cards ensures clear, transparent decision support.

---

## Q5: How is code reuse / duplicate tag cloning detected?
**Answer:**  
Every code verification event logs the authentication code tag, session ID, and timestamp into the `code_verification_events` database table. The function `check_code_reuse_alert()` queries the count of total verifications and distinct session IDs. If a code is checked across multiple distinct user sessions (`total_events > 1 and distinct_sessions > 1`), the system triggers a **Potential Code Reuse Alert** to warn buyers of tag cloning.

---

## Q6: What automated regression tests were added to prevent rendering regressions?
**Answer:**  
We implemented an automated UI regression test suite in `tests/test_ui_regression.py`. Using FastAPI `TestClient`, it executes across every application route (`/`, `/verify`, `/dashboard`, `/risk-analysis`, `/compare`, `/analytics`, `/model-card`, `/history`, `/report`, `/admin`, `/help`, `/privacy`, `/terms`, `/styleguide`) and asserts that:
1. `<main id="main-content">` exists and contains at least 300 characters of non-empty content.
2. The H1 heading is present and visible.
3. No unscoped `opacity: 0` rules exist in CSS.
4. Dark and light themes render clean HTTP 200 responses.
