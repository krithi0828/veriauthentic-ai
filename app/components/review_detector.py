import streamlit as st
from typing import Dict, Any

def render_review_detector_card(features: Dict[str, Any]):
    count = int(features.get("review_count", 0))
    avg_rating = float(features.get("average_rating", 0.0))
    var = float(features.get("rating_variance", 0.0))
    extreme_ratio = float(features.get("extreme_rating_ratio", 0.0))
    one_star = float(features.get("one_star_pct", 0.0))
    five_star = float(features.get("five_star_pct", 0.0))
    signal = float(features.get("review_authenticity_signal", 0.0))
    
    status_label = "Unusual pattern detected" if signal >= 45.0 else "Normal rating distribution"
    status_color = "#ef4444" if signal >= 45.0 else "#10b981"
    
    st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">⭐ Review Anomaly Detector</div>
                <span style="background: {status_color}22; color: {status_color}; border: 1px solid {status_color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                    {status_label}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; text-align: center; margin-top: 10px;">
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Total Reviews</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">{count}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Avg Rating</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">{avg_rating:.1f}/5.0</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">Variance</div>
                    <div style="font-size: 16px; font-weight: 700; color: {'#ef4444' if var > 1.8 else '#f8fafc'};">{var:.2f}</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">5-Star Ratio</div>
                    <div style="font-size: 16px; font-weight: 700; color: #f8fafc;">{five_star:.1f}%</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.5); padding: 8px; border-radius: 8px;">
                    <div style="font-size: 11px; color: #94a3b8;">1-Star Ratio</div>
                    <div style="font-size: 16px; font-weight: 700; color: {'#ef4444' if one_star > 25 else '#f8fafc'};">{one_star:.1f}%</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
