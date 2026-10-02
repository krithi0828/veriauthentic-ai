import streamlit as st
from typing import Dict, Any
from ml.feature_engineering import calculate_price_deviation, categorize_price_deviation

def render_price_analyzer_card(features: Dict[str, Any]):
    listed = float(features.get("listed_price", 0.0))
    ref = float(features.get("reference_price", 0.0))
    dev_pct = calculate_price_deviation(ref, listed)
    category = categorize_price_deviation(dev_pct)
    
    cat_color = "#10b981" if category == "Normal" else "#f59e0b" if category == "Suspicious" else "#ef4444"
    
    st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">💡 Smart Price Discrepancy Analyzer</div>
                <span style="background: {cat_color}22; color: {cat_color}; border: 1px solid {cat_color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                    {category} Price Signal
                </span>
            </div>
            
            <div style="display: flex; justify-content: space-around; margin: 14px 0; text-align: center;">
                <div>
                    <div style="font-size: 12px; color: #94a3b8;">Listed Price</div>
                    <div style="font-size: 22px; font-weight: 800; color: #6366f1;">${listed:.2f}</div>
                </div>
                <div style="border-right: 1px solid rgba(255,255,255,0.1);"></div>
                <div>
                    <div style="font-size: 12px; color: #94a3b8;">Manufacturer Reference MSRP</div>
                    <div style="font-size: 22px; font-weight: 800; color: #f8fafc;">${ref:.2f}</div>
                </div>
                <div style="border-right: 1px solid rgba(255,255,255,0.1);"></div>
                <div>
                    <div style="font-size: 12px; color: #94a3b8;">Price Deviation</div>
                    <div style="font-size: 22px; font-weight: 800; color: {cat_color};">{dev_pct:.1f}% off</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
