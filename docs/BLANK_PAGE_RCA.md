# Root Cause Analysis (RCA): Home Page Blank Body Rendering Bug

**System:** VeriAuthentic AI Web Application  
**Route Affected:** `/` (and all public routes where `is_public_page=True`, such as `/help`, `/privacy`, `/terms`)  
**Date:** October 2, 2026  
**Author:** Autonomous Senior Product Designer & Engineer (Google Antigravity)  

---

## 1. Executive Summary
Upon opening `http://127.0.0.1:8085/`, the web application rendered only the sticky header bar and the footer bar. The entire DOM area between them was 0-pixel height and completely blank. 

This issue was identified as a **structural Jinja2 template logic bug** in `app/templates/layout.html`.

---

## 2. Root Cause Identification

### Primary Root Cause
In `app/templates/layout.html`:
```jinja2
{% if is_public_page %}
  <header class="topbar card-glass no-print"> ... </header>
{% else %}
  <div class="app-shell">
    <aside class="sidebar"> ... </aside>
    <div class="main-content">
      <main>
        {% block content %}{% endblock %}
      </main>
    </div>
  </div>
{% endif %}
<footer> ... </footer>
```

When `is_public_page=True` was set in `render()` (such as on `home_page`, `help_page`, `privacy_page`, `terms_page`), Jinja evaluated the `{% if is_public_page %}` branch. It rendered the `<header>` element, skipped the entire `{% else %}` block (which contained `{% block content %}`), and rendered the `<footer>`.

Because `{% block content %}` was exclusively nested inside the `{% else %}` branch, any page rendered with `is_public_page=True` had its content block omitted entirely from the HTML output stream.

---

## 3. Systematic Diagnosis Checklist

| Diagnostic Check | Finding | Status |
|---|---|---|
| **(a) CSS Opacity / Visibility** | CSS opacity 0 / hidden rules without JS reveal. | **Remediated**: Progressive enhancement added; initial hidden states require `<html class="js">`. |
| **(b) Jinja Block Structural Bug** | `{% block content %}` placed inside `{% else %}` branch in `layout.html`. | **CONFIRMED ROOT CAUSE**: Fixed layout structure. |
| **(c) JS Load Exceptions** | No syntax/runtime exception halted initial paint, but error boundary was missing. | **Remediated**: Global `window.onerror` and unhandled rejection handlers installed. |
| **(d) API Fetch Perpetual Loading** | UI relied on async client fetch for some cards without server fallback. | **Remediated**: All dynamic regions have complete server-rendered default HTML. |
| **(e) CSS Height / Overflow** | `.main-content` height collapse when empty. | **Remediated**: Flexbox structure with `min-height: 100vh` and `flex: 1` on main element. |
| **(f) CSP / Inline Scripts** | No inline script violations blocking load. | **Verified**. |
| **(g) Stale Service Worker** | No active service worker intercepting shell. | **Verified**. |

---

## 4. Remediation & Architecture Fixes

1. **Layout Structure Normalization (`app/templates/layout.html`)**:
   - Re-architected template inheritance so `{% block content %}` resides in a common `<main>` tag accessible to both public marketing layout and internal app shell layout.
   - Ensured header, main body, and footer are always rendered regardless of `is_public_page`.

2. **Progressive Enhancement Guarantee**:
   - Content is 100% visible and functional with JavaScript disabled.
   - Animation reveal classes (e.g., `.fade-up`, `.reveal-on-scroll`) are activated **only when JavaScript attaches the `.js` class to `<html>`**.

3. **Fallback & Resiliency System**:
   - Server-rendered HTML fallback for all dynamic widgets.
   - Skeleton loaders during fetch transitions.
   - User-friendly error banners with "Retry" buttons if network calls fail.
   - Global JS error boundary preventing blank screen crashes.

4. **Automated Regression Prevention**:
   - Added automated test runner in `tests/test_ui_regression.py`.
   - Asserts that every route (`/`, `/verify`, `/dashboard`, `/risk-analysis`, `/compare`, `/analytics`, `/model-card`, `/history`, `/report`, `/admin`, `/help`, `/privacy`, `/terms`, `/styleguide`, `404`) has a non-empty `<main>` element with minimum height >= 600px and visible hero headers.
