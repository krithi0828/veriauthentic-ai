import pandas as pd
import numpy as np
from typing import Dict, Any, Union
from ml.model_config import SUSPICIOUS_KEYWORDS

def calculate_price_deviation(reference_price: float, listed_price: float) -> float:
    if reference_price <= 0:
        return 0.0
    dev = ((reference_price - listed_price) / reference_price) * 100.0
    return float(max(-100.0, min(100.0, dev)))

def categorize_price_deviation(deviation_pct: float) -> str:
    if deviation_pct < 15.0:
        return "Normal"
    elif deviation_pct <= 40.0:
        return "Suspicious"
    else:
        return "Highly Suspicious"

def calculate_seller_credibility(account_age_days: int, rating: float, verified: bool) -> float:
    age_score = min(40.0, (account_age_days / 365.0) * 40.0)
    rating_score = (max(1.0, min(5.0, rating)) / 5.0) * 40.0
    verified_score = 20.0 if verified else 0.0
    return float(min(100.0, max(0.0, age_score + rating_score + verified_score)))

def categorize_account_age(account_age_days: int) -> str:
    if account_age_days < 90:
        return "New"
    elif account_age_days <= 365:
        return "Established"
    else:
        return "Trusted"

def calculate_review_anomaly_signal(
    review_count: int,
    avg_rating: float,
    variance: float,
    extreme_ratio: float,
    one_star_pct: float,
    five_star_pct: float
) -> float:
    signal = 0.0
    # Extreme rating polarity (lots of 1-star and 5-star, few middle ratings)
    if extreme_ratio > 0.7:
        signal += 35.0
    # High variance on high ratings
    if variance > 1.8:
        signal += 25.0
    # Very new / low reviews with 100% 5-star reviews
    if review_count < 10 and five_star_pct > 80.0:
        signal += 20.0
    # High 1-star percentage
    if one_star_pct > 30.0:
        signal += 20.0
    return float(min(100.0, signal))

def extract_features_single(input_data: Dict[str, Any], registered_codes: set = None, verification_counts: dict = None) -> Dict[str, Any]:
    ref_price = float(input_data.get("reference_price", 100.0))
    list_price = float(input_data.get("listed_price", 100.0))
    dev_pct = calculate_price_deviation(ref_price, list_price)
    dev_cat = categorize_price_deviation(dev_pct)

    age_days = int(input_data.get("seller_account_age_days", 180))
    seller_rating = float(input_data.get("seller_rating", 4.0))
    seller_verified = bool(input_data.get("seller_verified", False))
    cred_score = calculate_seller_credibility(age_days, seller_rating, seller_verified)
    age_cat = categorize_account_age(age_days)

    rev_count = int(input_data.get("review_count", 50))
    avg_rat = float(input_data.get("average_rating", 4.0))
    variance = float(input_data.get("rating_variance", 0.5))
    extreme_ratio = float(input_data.get("extreme_rating_ratio", 0.3))
    one_star = float(input_data.get("one_star_pct", 5.0))
    five_star = float(input_data.get("five_star_pct", 70.0))

    rev_signal = calculate_review_anomaly_signal(rev_count, avg_rat, variance, extreme_ratio, one_star, five_star)
    suspicious_rev = 1 if rev_signal >= 45.0 else 0

    desc = str(input_data.get("product_description", ""))
    desc_len = len(desc)
    upper_count = sum(1 for c in desc if c.isupper())
    upper_ratio = upper_count / max(1, desc_len)
    suspicious_kws = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in desc.lower())

    auth_code = str(input_data.get("authentication_code", "")).strip().upper()
    is_reg = 1 if (registered_codes and auth_code in registered_codes) or input_data.get("code_registered", False) else 0
    ver_count = verification_counts.get(auth_code, 1) if verification_counts else int(input_data.get("code_verification_count", 1))

    features = {
        "listed_price": list_price,
        "reference_price": ref_price,
        "price_deviation_pct": dev_pct,
        "price_deviation_category": dev_cat,
        "seller_account_age_days": age_days,
        "seller_rating": seller_rating,
        "seller_verified": 1 if seller_verified else 0,
        "seller_credibility_score": cred_score,
        "account_age_category": age_cat,
        "review_count": rev_count,
        "average_rating": avg_rat,
        "rating_variance": variance,
        "extreme_rating_ratio": extreme_ratio,
        "one_star_pct": one_star,
        "five_star_pct": five_star,
        "review_authenticity_signal": rev_signal,
        "suspicious_review_pattern": suspicious_rev,
        "product_description": desc,
        "desc_length": desc_len,
        "uppercase_ratio": upper_ratio,
        "suspicious_keyword_count": suspicious_kws,
        "authentication_code": auth_code,
        "code_registered": is_reg,
        "code_verification_count": ver_count
    }
    return features

def engineer_features_df(df: pd.DataFrame, registered_codes: set = None, verification_counts: dict = None) -> pd.DataFrame:
    records = df.to_dict(orient="records")
    engineered = [extract_features_single(r, registered_codes, verification_counts) for r in records]
    res_df = pd.DataFrame(engineered)
    if "label" in df.columns:
        res_df["label"] = df["label"].values
    if "product_id" in df.columns:
        res_df["product_id"] = df["product_id"].values
    if "product_name" in df.columns:
        res_df["product_name"] = df["product_name"].values
    if "brand" in df.columns:
        res_df["brand"] = df["brand"].values
    if "product_category" in df.columns:
        res_df["product_category"] = df["product_category"].values
    return res_df
