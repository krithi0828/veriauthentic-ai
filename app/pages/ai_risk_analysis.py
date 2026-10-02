import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px

from app.config import MODELS_DIR
from ml.predict import predict_authenticity
from app.components.risk_visualizations import display_risk_score_card, display_multi_signal_breakdown
from app.components.explanation_panel import render_explanation_panel

def show_ai_risk_analysis_page():
    st.markdown("## 🧠 Detailed AI Risk Analysis & Model Explainability Engine")
    st.caption("Inspect underlying Machine Learning feature importances and test signal sensitivity interactively.")
    
    tab1, tab2 = st.tabs(["🔬 Interactive Risk Simulator", "📊 Global Feature Importance"])
    
    with tab1:
        st.markdown("### Interactive Multi-Signal Risk Simulator")
        st.markdown("Tweak listing parameters below to observe how the Random Forest model and risk breakdown react dynamically.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("💰 Price Signals")
            ref_p = st.number_input("MSRP Reference Price ($)", value=500.0, key="sim_ref")
            list_p = st.number_input("Listed Price ($)", value=150.0, key="sim_list")
            
        with col2:
            st.subheader("👤 Seller Signals")
            age = st.slider("Seller Account Age (Days)", 1, 1000, 30, key="sim_age")
            rating = st.slider("Seller Rating", 1.0, 5.0, 2.8, key="sim_rating")
            ver = st.checkbox("Seller Verified", value=False, key="sim_ver")
            
        with col3:
            st.subheader("⭐ Review & Code Signals")
            rev_cnt = st.number_input("Review Count", value=15, key="sim_rev")
            extreme_r = st.slider("Extreme Rating Ratio", 0.0, 1.0, 0.9, key="sim_ext")
            code_reg = st.checkbox("Code Registered in Database", value=False, key="sim_reg")
            
        kw_desc = st.selectbox("Text Description Quality Strategy", [
            "Suspicious Promotional (Contains '100% original copy, grade 1A replica, fast ship no box')",
            "Standard Genuine Manufacturer Description (Clean, technical specification)",
            "Heavy UPPERCASE Promotional Spammers"
        ])
        
        desc_text = "Grade 1A replica 100% original copy super copy fast ship no box direct factory liquidation."
        if "Standard Genuine" in kw_desc:
            desc_text = "Official manufacturer product with full warranty card and anti-tamper security seal."
        elif "UPPERCASE" in kw_desc:
            desc_text = "CHEAP DISCOUNT CLEARANCE LIQUIDATION SALE FAST SHIP BUY NOW SPECIAL DEAL."
            
        sim_input = {
            "product_name": "Simulated Product Item",
            "brand": "Generic Brand",
            "reference_price": ref_p,
            "listed_price": list_p,
            "seller_account_age_days": age,
            "seller_rating": rating,
            "seller_verified": ver,
            "review_count": rev_cnt,
            "average_rating": rating,
            "rating_variance": 2.1,
            "extreme_rating_ratio": extreme_r,
            "one_star_pct": 30.0,
            "five_star_pct": 60.0,
            "product_description": desc_text,
            "authentication_code": "AUTH-SIM-1234",
            "code_registered": code_reg
        }
        
        res = predict_authenticity(sim_input)
        
        st.markdown("---")
        display_risk_score_card(res)
        display_multi_signal_breakdown(res["multi_signal_breakdown"])
        render_explanation_panel(res)
        
    with tab2:
        st.markdown("### Global Machine Learning Feature Importance Breakdown")
        st.markdown("Relative influence of top numerical, binary, and text features extracted from the trained **Random Forest Classifier**.")
        
        try:
            rf_model = joblib.load(MODELS_DIR / "random_forest_model.pkl")
            preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
            
            # Extract feature names from preprocessor transformers
            num_names = preprocessor.transformers_[0][2]
            text_vectorizer = preprocessor.transformers_[1][1]
            text_names = [f"text_tfidf: {f}" for f in text_vectorizer.get_feature_names_out()]
            bin_names = preprocessor.transformers_[2][2]
            
            feature_names = list(num_names) + list(text_names) + list(bin_names)
            importances = rf_model.feature_importances_
            
            df_imp = pd.DataFrame({
                "Feature": feature_names[:len(importances)],
                "Importance": importances
            }).sort_values(by="Importance", ascending=False).head(15)
            
            fig = px.bar(
                df_imp,
                x="Importance",
                y="Feature",
                orientation="h",
                title="Top 15 Most Important Counterfeit Detection Features",
                color="Importance",
                color_continuous_scale="Viridis",
                template="plotly_dark"
            )
            fig.update_layout(yaxis=dict(autorange="reversed"), height=500)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Could not load model feature importances: {e}")
