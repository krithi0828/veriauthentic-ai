import streamlit as st
from typing import Dict, Any
from ml.explain import explain_prediction

def render_explanation_panel(prediction_result: Dict[str, Any]):
    explanation = explain_prediction(prediction_result)
    
    risk_factors = explanation["risk_factors"]
    positive_signals = explanation["positive_signals"]
    ai_recs = explanation["ai_recommendations"]
    
    st.markdown("""
        <div class="glass-card">
            <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 14px;">
                🤖 AI Multi-Signal Explanation Panel
            </div>
    """, unsafe_allow_html=True)
    
    if risk_factors:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #ef4444; margin-bottom: 6px;'>⚠️ Key Risk Signals Identified</div>", unsafe_allow_html=True)
        for rf in risk_factors:
            st.markdown(f"<div style='background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; color: #fca5a5;'>⚠️ {rf}</div>", unsafe_allow_html=True)
            
    if positive_signals:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #10b981; margin-top: 10px; margin-bottom: 6px;'>✓ Positive Verification Signals</div>", unsafe_allow_html=True)
        for ps in positive_signals:
            st.markdown(f"<div style='background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 8px 12px; margin-bottom: 6px; font-size: 13px; color: #6ee7b7;'>✓ {ps}</div>", unsafe_allow_html=True)
            
    if ai_recs:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #6366f1; margin-top: 14px; margin-bottom: 6px;'>📌 AI Advisory Next-Step Guidance</div>", unsafe_allow_html=True)
        for rec in ai_recs:
            st.markdown(f"<div style='font-size: 13px; color: #cbd5e1; margin-bottom: 4px;'>👉 {rec}</div>", unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
