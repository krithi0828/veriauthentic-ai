import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Dict, Any, List
import numpy as np

def explain_prediction(prediction_result: Dict[str, Any]) -> Dict[str, Any]:
    features = prediction_result.get("engineered_features", {})
    breakdown = prediction_result.get("multi_signal_breakdown", {})
    risk_score = prediction_result.get("risk_score", 0.0)
    pred = prediction_result.get("prediction", 0)
    
    risk_factors = []
    positive_signals = []
    explanations = []
    
    # 1. Price Signal Analysis
    dev_pct = features.get("price_deviation_pct", 0.0)
    ref_price = features.get("reference_price", 0.0)
    list_price = features.get("listed_price", 0.0)
    
    if dev_pct >= 40.0:
        msg = f"Listed price (${list_price:.2f}) is {dev_pct:.1f}% below manufacturer reference price (${ref_price:.2f})."
        risk_factors.append(msg)
        explanations.append("Price is significantly below reference price")
    elif dev_pct >= 15.0:
        msg = f"Listed price (${list_price:.2f}) shows a moderate discount ({dev_pct:.1f}%) compared to reference MSRP."
        risk_factors.append(msg)
        explanations.append("Price discount exceeds normal retail threshold")
    else:
        msg = f"Listed price (${list_price:.2f}) is consistent with market reference price (${ref_price:.2f})."
        positive_signals.append(msg)
        
    # 2. Seller Credibility Analysis
    cred_score = features.get("seller_credibility_score", 100.0)
    age_days = features.get("seller_account_age_days", 365)
    verified = bool(features.get("seller_verified", False))
    
    if cred_score < 40.0:
        msg = f"Seller account is new ({age_days} days old) with low trust score ({cred_score:.1f}/100)."
        risk_factors.append(msg)
        explanations.append("Seller has low credibility score")
    elif not verified and age_days < 90:
        msg = f"Seller is unverified on the platform and has a recently created account."
        risk_factors.append(msg)
    else:
        status_str = "verified" if verified else "established"
        msg = f"Seller is {status_str} with account age of {age_days} days (Trust score: {cred_score:.1f}/100)."
        positive_signals.append(msg)
        
    # 3. Review Pattern Analysis
    rev_signal = features.get("review_authenticity_signal", 0.0)
    extreme_ratio = features.get("extreme_rating_ratio", 0.0)
    var = features.get("rating_variance", 0.0)
    
    if rev_signal >= 45.0:
        msg = f"Unusual rating concentration detected (Extreme rating ratio: {extreme_ratio*100:.1f}%, Variance: {var:.2f})."
        risk_factors.append(msg)
        explanations.append("Review pattern shows unusual rating concentration")
    else:
        msg = "Review rating distribution follows natural buyer feedback patterns."
        positive_signals.append(msg)
        
    # 4. Text Pattern Analysis
    kw_count = features.get("suspicious_keyword_count", 0)
    if kw_count > 0:
        msg = f"Product description contains {kw_count} suspicious promotional/replica phrase(s)."
        risk_factors.append(msg)
        explanations.append("Product description contains suspicious patterns")
    else:
        msg = "Product text description contains clear, standard manufacturer terminology."
        positive_signals.append(msg)
        
    # 5. Registry Verification Analysis
    code_registered = features.get("code_registered", 0)
    auth_code = features.get("authentication_code", "")
    
    if code_registered == 1:
        msg = f"Authentication code ({auth_code}) is registered in the official manufacturer registry database."
        positive_signals.append(msg)
    else:
        msg = f"Authentication code ({auth_code}) was not found in the official registry database."
        risk_factors.append(msg)
        explanations.append("Authentication code is not registered in official registry")
        
    # 6. AI Next-Step Advisory Recommendations
    recommendations = []
    if risk_score > 75.0:
        recommendations.append("High risk detected: Exercise extreme caution. Contact official brand distributor before purchasing.")
        recommendations.append("Request physical proof of origin, invoice, or authentic batch holographic sticker.")
        recommendations.append("Submit a counterfeit report if seller claims guaranteed authenticity without official proof.")
    elif risk_score > 50.0:
        recommendations.append("Moderate counterfeit risk: Verify seller credentials and check return policy carefully.")
        recommendations.append("Cross-reference listing details with authorized retail prices.")
    else:
        recommendations.append("Low risk detected: Listing signals align with genuine product patterns.")
        recommendations.append("Verify authentication code tag upon receiving the package.")
        
    return {
        "risk_factors": risk_factors,
        "positive_signals": positive_signals,
        "human_readable_explanations": explanations,
        "ai_recommendations": recommendations
    }
