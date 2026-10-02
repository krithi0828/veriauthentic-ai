import streamlit as st
from database.database import get_analytics_summary, get_all_reports, get_verification_history
from app.components.ui_components import render_metric_card

def show_dashboard_page():
    st.markdown("""
        <div class="glass-card" style="padding: 32px; background: linear-gradient(135deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.95) 100%); text-align: center;">
            <div style="display: inline-block; padding: 6px 16px; background: rgba(99, 102, 241, 0.2); color: #818cf8; border-radius: 20px; font-weight: 700; font-size: 12px; letter-spacing: 1px; margin-bottom: 12px;">
                🚀 COLLEGE PROJECT DEMO • VERIAUTHENTIC AI
            </div>
            <h1 style="font-size: 36px; font-weight: 900; background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
                AI-Driven Product Authenticity Verification System
            </h1>
            <p style="font-size: 16px; color: #94a3b8; max-width: 700px; margin: 0 auto 24px auto; line-height: 1.6;">
                Multi-signal machine learning platform evaluating price discrepancy, seller credibility, review anomalies, TF-IDF descriptions, and official code registry databases to detect counterfeit risk.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("🔍 Verify Product Code (Mode A)", type="primary", use_container_width=True):
            st.session_state["current_page"] = "Verify Product"
            st.session_state["verify_mode"] = "Mode A: Code Verification"
            st.rerun()
    with col_btn2:
        if st.button("🤖 AI Listing Risk Analysis (Mode B)", use_container_width=True):
            st.session_state["current_page"] = "Verify Product"
            st.session_state["verify_mode"] = "Mode B: AI Listing Risk Analysis"
            st.rerun()
    with col_btn3:
        if st.button("⚔️ Side-by-Side Comparison", use_container_width=True):
            st.session_state["current_page"] = "Verify Product"
            st.session_state["verify_mode"] = "Mode D: Product Comparison"
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Stats
    summary = get_analytics_summary()
    st.markdown("### 📊 System Quick Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Registered Products", f"{summary['total_products']:,}", "Official Registry", "📦")
    with col2:
        render_metric_card("Total Verifications", f"{summary['total_verifications']:,}", "Session Tracking", "🔎")
    with col3:
        render_metric_card("High-Risk Flagged", f"{summary['high_risk_verifications']:,}", "ML Risk Signal", "⚠️")
    with col4:
        render_metric_card("Counterfeit Reports", f"{summary['total_reports']:,}", "User Submitted", "📋")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### ⚡ Recent Verification Activity Feed")
        history = get_verification_history(limit=5)
        if history:
            for item in history:
                risk = item["risk_score"]
                color = "#ef4444" if risk >= 51 else "#f59e0b" if risk >= 26 else "#10b981"
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid {color}; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; font-size: 13px;">
                        <div style="display: flex; justify-content: space-between; font-weight: 700; color: #f8fafc;">
                            <span>{item['product_name'] or 'Unnamed Listing'}</span>
                            <span style="color: {color};">{risk:.1f}% Risk</span>
                        </div>
                        <div style="color: #94a3b8; font-size: 11px; margin-top: 2px;">
                            Code: {item['authentication_code'] or 'N/A'} | Type: {item['verification_type']} | {item['created_at']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent verification activity recorded.")
            
    with col_right:
        st.markdown("### 💡 Core System Highlights")
        st.markdown("""
            <div class="glass-card" style="padding: 18px;">
                <div style="margin-bottom: 12px;">
                    <b style="color: #6366f1;">• 15 Unique Innovation Features:</b> Multi-signal ML, duplicate code detection, seller credibility, review anomaly score, side-by-side comparison, and admin analytics.
                </div>
                <div style="margin-bottom: 12px;">
                    <b style="color: #10b981;">• Machine Learning Pipeline:</b> Random Forest Classifier with 5-fold cross-validation + TF-IDF text features & ColumnTransformer preprocessor.
                </div>
                <div>
                    <b style="color: #f59e0b;">• Technically Responsible:</b> Outputs probability-based risk scores (0-100%) and advisory signals — never claiming 100% guarantee.
                </div>
            </div>
        """, unsafe_allow_html=True)
