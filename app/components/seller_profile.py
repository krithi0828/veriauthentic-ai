import streamlit as st
from typing import Dict, Any
from ml.feature_engineering import calculate_seller_credibility, categorize_account_age

def render_seller_profile_card(features: Dict[str, Any]):
    account_age = int(features.get("seller_account_age_days", 180))
    rating = float(features.get("seller_rating", 4.0))
    verified = bool(features.get("seller_verified", False))
    
    trust_score = calculate_seller_credibility(account_age, rating, verified)
    age_cat = categorize_account_age(account_age)
    
    verified_badge = "<span style='background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;'>✓ Verified Seller</span>" if verified else "<span style='background: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;'>⚠️ Unverified Seller</span>"
    
    st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">👤 Seller Credibility Profile</div>
                {verified_badge}
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; margin-top: 10px; text-align: center;">
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Trust Score</div>
                    <div style="font-size: 20px; font-weight: 800; color: {'#10b981' if trust_score > 60 else '#ef4444'};">{trust_score:.1f}/100</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Account Age</div>
                    <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">{account_age} days</div>
                    <div style="font-size: 10px; color: #64748b;">{age_cat}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 10px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Seller Rating</div>
                    <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">⭐ {rating:.1f}/5.0</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
