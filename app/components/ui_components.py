import streamlit as st
from typing import Dict, Any, Optional

def render_glass_card_start(title: Optional[str] = None, subtitle: Optional[str] = None):
    header_html = ""
    if title:
        sub_html = f"<div style='color: #94a3b8; font-size: 14px; margin-top: 4px;'>{subtitle}</div>" if subtitle else ""
        header_html = f"<div style='font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 12px;'>{title}{sub_html}</div>"
    
    st.markdown(f"""
        <div class="glass-card">
            {header_html}
    """, unsafe_allow_html=True)

def render_glass_card_end():
    st.markdown("</div>", unsafe_allow_html=True)

def render_risk_badge(risk_score: float) -> str:
    from app.config import get_risk_level_info
    info = get_risk_level_info(risk_score)
    label = info["label"]
    badge_cls = info["badge"]
    return f"""<span class="risk-badge {badge_cls}">{label} ({risk_score:.1f}%)</span>"""

def render_metric_card(label: str, value: Any, delta: Optional[str] = None, icon: str = "📊"):
    delta_html = f"<div style='font-size: 12px; color: #10b981; margin-top: 4px;'>{delta}</div>" if delta else ""
    st.markdown(f"""
        <div class="glass-card" style="padding: 16px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 6px;">{icon}</div>
            <div style="font-size: 13px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            <div style="font-size: 26px; font-weight: 800; color: #f8fafc; margin-top: 4px;">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

def render_custom_progress_bar(label: str, value_pct: float, color: str = "#6366f1", sub_text: str = ""):
    val = max(0.0, min(100.0, float(value_pct)))
    st.markdown(f"""
        <div style="margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; font-weight: 600; color: #cbd5e1;">
                <span>{label}</span>
                <span>{val:.1f}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {val}%; background: {color};"></div>
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">{sub_text}</div>
        </div>
    """, unsafe_allow_html=True)
