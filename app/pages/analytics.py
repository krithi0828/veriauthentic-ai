import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import get_analytics_summary, get_all_products, get_all_reports, get_verification_history
from app.components.ui_components import render_metric_card

def show_analytics_page():
    st.markdown("## 📈 Public Verification Analytics & Brand Intelligence")
    st.caption("Real-time telemetry on brand authentication queries, risk tier distributions, and suspicious product trends.")
    
    summary = get_analytics_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Registered Products", f"{summary['total_products']:,}", "Official Registry", "📦")
    with col2:
        render_metric_card("Total Verifications", f"{summary['total_verifications']:,}", "All Sessions", "🔍")
    with col3:
        render_metric_card("High-Risk Verifications", f"{summary['high_risk_verifications']:,}", "Score >= 51%", "⚠️")
    with col4:
        render_metric_card("Counterfeit Reports", f"{summary['total_reports']:,}", "User Submitted", "📋")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    history = get_verification_history(limit=500)
    reports = get_all_reports()
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### 🎯 Verification Risk Level Distribution")
        if history:
            df_hist = pd.DataFrame(history)
            def get_cat(score):
                if score <= 25: return "Low Risk (0-25%)"
                elif score <= 50: return "Moderate Risk (26-50%)"
                elif score <= 75: return "High Risk (51-75%)"
                else: return "Critical Risk (76-100%)"
            df_hist["Risk Level"] = df_hist["risk_score"].apply(get_cat)
            
            counts = df_hist["Risk Level"].value_counts().reset_index()
            counts.columns = ["Risk Level", "Count"]
            
            fig = px.pie(
                counts,
                names="Risk Level",
                values="Count",
                color="Risk Level",
                color_discrete_map={
                    "Low Risk (0-25%)": "#10b981",
                    "Moderate Risk (26-50%)": "#f59e0b",
                    "High Risk (51-75%)": "#ef4444",
                    "Critical Risk (76-100%)": "#7c3aed"
                },
                hole=0.4,
                template="plotly_dark"
            )
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No verification telemetry data available yet.")
            
    with col_right:
        st.markdown("### 🏷️ Counterfeit Reports by Brand")
        if reports:
            df_rep = pd.DataFrame(reports)
            brand_counts = df_rep["brand"].value_counts().reset_index()
            brand_counts.columns = ["Brand", "Report Count"]
            
            fig_bar = px.bar(
                brand_counts.head(10),
                x="Brand",
                y="Report Count",
                color="Report Count",
                color_continuous_scale="Reds",
                template="plotly_dark"
            )
            fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No counterfeit reports data available.")
