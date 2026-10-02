import streamlit as st
from typing import Dict, Any
from ml.predict import predict_authenticity
from app.components.risk_visualizations import display_risk_score_card, display_multi_signal_breakdown

def render_product_comparison_ui(get_product_func=None):
    st.markdown("""
        <div style="font-size: 20px; font-weight: 800; color: #f8fafc; margin-bottom: 12px;">
            ⚔️ Side-by-Side Product Comparison Mode
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Listing A")
        name_a = st.text_input("Product Name A", "Rolex Submariner Watch", key="name_a")
        brand_a = st.text_input("Brand A", "Rolex", key="brand_a")
        ref_price_a = st.number_input("Reference Price MSRP A ($)", value=12500.0, key="ref_a")
        list_price_a = st.number_input("Listed Marketplace Price A ($)", value=11900.0, key="list_a")
        seller_age_a = st.number_input("Seller Account Age A (Days)", value=450, key="age_a")
        seller_rating_a = st.slider("Seller Rating A", 1.0, 5.0, 4.8, key="rating_a")
        seller_ver_a = st.checkbox("Seller Verified A", value=True, key="ver_a")
        code_a = st.text_input("Authentication Code A", "AUTH-ROLEX-9901", key="code_a")
        desc_a = st.text_area("Description A", "Official manufacturer Rolex watch with box and warranty tag.", key="desc_a")
        
    with col2:
        st.subheader("Listing B")
        name_b = st.text_input("Product Name B", "Rolex Submariner Luxury Copy", key="name_b")
        brand_b = st.text_input("Brand B", "Rolex", key="brand_b")
        ref_price_b = st.number_input("Reference Price MSRP B ($)", value=12500.0, key="ref_b")
        list_price_b = st.number_input("Listed Marketplace Price B ($)", value=2500.0, key="list_b")
        seller_age_b = st.number_input("Seller Account Age B (Days)", value=15, key="age_b")
        seller_rating_b = st.slider("Seller Rating B", 1.0, 5.0, 2.3, key="rating_b")
        seller_ver_b = st.checkbox("Seller Verified B", value=False, key="ver_b")
        code_b = st.text_input("Authentication Code B", "AUTH-FAKE-0000", key="code_b")
        desc_b = st.text_area("Description B", "Direct factory liquidation 1:1 super copy mirror quality fast ship no box.", key="desc_b")
        
    if st.button("Evaluate & Compare Both Listings with AI", type="primary", use_container_width=True):
        input_a = {
            "product_name": name_a, "brand": brand_a, "reference_price": ref_price_a, "listed_price": list_price_a,
            "seller_account_age_days": seller_age_a, "seller_rating": seller_rating_a, "seller_verified": seller_ver_a,
            "review_count": 120, "average_rating": 4.8, "rating_variance": 0.4, "extreme_rating_ratio": 0.3,
            "one_star_pct": 3.0, "five_star_pct": 80.0, "product_description": desc_a, "authentication_code": code_a
        }
        input_b = {
            "product_name": name_b, "brand": brand_b, "reference_price": ref_price_b, "listed_price": list_price_b,
            "seller_account_age_days": seller_age_b, "seller_rating": seller_rating_b, "seller_verified": seller_ver_b,
            "review_count": 8, "average_rating": 2.3, "rating_variance": 2.2, "extreme_rating_ratio": 0.9,
            "one_star_pct": 40.0, "five_star_pct": 50.0, "product_description": desc_b, "authentication_code": code_b
        }
        
        res_a = predict_authenticity(input_a, db_check_func=get_product_func)
        res_b = predict_authenticity(input_b, db_check_func=get_product_func)
        
        st.markdown("---")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown("### Evaluation Result: Listing A")
            display_risk_score_card(res_a)
            display_multi_signal_breakdown(res_a["multi_signal_breakdown"])
            
        with res_col2:
            st.markdown("### Evaluation Result: Listing B")
            display_risk_score_card(res_b)
            display_multi_signal_breakdown(res_b["multi_signal_breakdown"])
