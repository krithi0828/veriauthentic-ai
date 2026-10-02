import streamlit as st
from typing import Dict, Any
from app.config import get_risk_level_info
from app.components.ui_components import render_custom_progress_bar

def display_risk_score_card(pred_result: Dict[str, Any]):
    risk_score = pred_result["risk_score"]
    pred_label = pred_result["prediction_label"]
    conf = pred_result["confidence_pct"]
    risk_info = pred_result["risk_level_info"]
    color = risk_info["color"]
    badge_cls = risk_info["badge"]
    
    st.markdown(f"""
        <div class="glass-card" style="border-left: 6px solid {color}; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div style="font-size: 13px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">AI Authenticity Risk Assessment</div>
                    <div style="font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 4px;">{pred_label}</div>
                    <div style="font-size: 14px; color: #cbd5e1; margin-top: 4px;">
                        Confidence Score: <b>{conf:.1f}%</b> | Evaluated Signal: Multi-Layer ML Model
                    </div>
                </div>
                <div style="text-align: right; margin-top: 10px;">
                    <div style="font-size: 42px; font-weight: 900; color: {color}; line-height: 1;">
                        {risk_score:.1f}<span style="font-size: 20px; color: #94a3b8;">/100</span>
                    </div>
                    <div class="risk-badge {badge_cls}" style="margin-top: 6px; display: inline-block;">
                        {risk_info['label']}
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def display_multi_signal_breakdown(breakdown: Dict[str, float]):
    st.markdown("""
        <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;">
            📡 Multi-Signal Risk Decomposition
        </div>
    """, unsafe_allow_html=True)
    
    price_risk = breakdown.get("price_risk", 0.0)
    seller_risk = breakdown.get("seller_risk", 0.0)
    review_risk = breakdown.get("review_risk", 0.0)
    text_risk = breakdown.get("text_risk", 0.0)
    registry_risk = breakdown.get("registry_risk", 0.0)
    
    render_custom_progress_bar("💰 Price Deviation Risk", price_risk, "#ef4444" if price_risk > 40 else "#10b981", "Discrepancy between listed price and MSRP reference")
    render_custom_progress_bar("👤 Seller Credibility Risk", seller_risk, "#ef4444" if seller_risk > 50 else "#10b981", "Seller account age, verification status, and platform rating")
    render_custom_progress_bar("⭐ Review Anomaly Risk", review_risk, "#f59e0b" if review_risk > 40 else "#10b981", "Rating distribution variance and extreme review ratios")
    render_custom_progress_bar("📝 Text Description Risk", text_risk, "#ef4444" if text_risk > 50 else "#10b981", "TF-IDF patterns and promotional / replica phrase indicators")
    render_custom_progress_bar("🏷️ Registry Lookup Risk", registry_risk, "#ef4444" if registry_risk > 50 else "#10b981", "Official manufacturer code registration status in SQLite registry")
