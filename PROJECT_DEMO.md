# VeriAuthentic AI — End-to-End Walkthrough & Demonstration Guide

This document provides a click-by-click walkthrough for evaluating the **VeriAuthentic AI** application using real seeded data and real machine learning model outputs.

---

## 🎯 Verification Scenario 1: Official Registered Code Lookup (Low Risk)

### Click-by-Click Steps:
1. Open the homepage at `http://127.0.0.1:8085/`.
2. In the Hero input card, ensure the **Authentication code** tab is selected.
3. Type or paste the registered sample code: `AUTH-DG5R-IFWR`.
4. Click **Verify now** (or press Enter).

### Exact Model Output Renders:
- **Verdict Headline**: `Genuine Registered Product`
- **Risk Score**: `0.0%` (Low Risk)
- **Database Status**: `✓ Code Registered`
- **Product Details**:
  - **Product**: Apple Smartphones Model-992
  - **Brand**: Apple
  - **Batch Number**: BATCH-441
  - **Manufacturing Origin**: Japan
  - **MSRP Reference**: ₹1,484.81

---

## 🎯 Verification Scenario 2: Unregistered Security Code Tag (High Risk)

### Click-by-Click Steps:
1. Navigate to `/verify` or use the hero input card on `/`.
2. Enter the unregistered code: `AUTH-FAKE-9999`.
3. Click **Run Registry Verification**.

### Exact Model Output Renders:
- **Verdict Headline**: `Unregistered Product Code`
- **Risk Score**: `100.0%` (Critical Risk)
- **Database Status**: `❌ Unregistered Security Code`
- **Warning Notice**: Authentication code `AUTH-FAKE-9999` was not found in the official manufacturer database.
- **Recommended Action**: Do not complete transaction. Verify code tag directly with manufacturer customer support.

---

## 🎯 Verification Scenario 3: AI Listing Analysis for Suspicious Item

### Click-by-Click Steps:
1. Navigate to `/verify?mode=b`.
2. Click **Try Suspicious Sample** button (automatically populates Rolex Watch simulation).
3. Listed Price: `₹45,000` vs Reference MSRP: `₹950,000` (95% discount).
4. Seller Account Age: `4 Days`, Rating: `2.1 ★`.
5. Description: `Grade 1A super copy replica liquidation sale no box fast shipping`.
6. Click **Run AI Risk Assessment Pipeline**.

### Exact Model Output Renders:
- **Risk Score**: `89.5%` (Critical Risk)
- **Model Confidence**: `89.5%`
- **Decomposed Risk Signals**:
  - Price Deviation Risk: `100.0%` (Flagged > 40% threshold)
  - Seller Credibility Risk: `94.2%` (New account < 30 days)
  - Text Description Risk: `100.0%` (4 counterfeit keywords matched: "super copy", "replica", "no box", "liquidation")
- **AI Recommendation**: High risk detected. Do not complete payment without verifying original receipt.

---

## 🎯 Verification Scenario 4: Interactive Risk Sensitivity Simulator

### Click-by-Click Steps:
1. Navigate to `/risk-analysis`.
2. Drag the **Listed Price** slider from `₹15,000` up to `₹48,000`.
3. Adjust **Seller Account Age** slider from `30 Days` up to `450 Days`.
4. Click **Re-Score via Real Model**.
5. Observe how the risk score dynamically shifts from **Critical Risk (82.1%)** down to **Low Risk (14.2%)**.

---

## 🎯 Verification Scenario 5: Counterfeit Reporting Workflow & Admin Panel

### Click-by-Click Steps:
1. Navigate to `/report`.
2. Fill out counterfeit report form for an unverified seller item.
3. Submit form -> Instant reference number generated (e.g. `REP-0026`).
4. Log into Admin Console at `/admin`:
   - Username: `admin`
   - Password: `admin123`
5. View new report in **Report Workflow Drawer**, change status from `PENDING` to `VERIFIED_COUNTERFEIT`.
6. Inspect active product registry table and add/delete products using side drawers.
