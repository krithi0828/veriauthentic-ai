import streamlit as st
import uuid
import hashlib
from typing import Dict, Any

from database.database import (
    get_product_by_auth_code,
    log_verification_event,
    check_code_reuse_alert,
    add_verification_history,
    get_all_products
)
from ml.predict import predict_authenticity
from app.components.risk_visualizations import display_risk_score_card, display_multi_signal_breakdown
from app.components.seller_profile import render_seller_profile_card
from app.components.price_analyzer import render_price_analyzer_card
from app.components.review_detector import render_review_detector_card
from app.components.explanation_panel import render_explanation_panel
from app.components.comparison_mode import render_product_comparison_ui

def show_verify_product_page():
    st.markdown("## 🔍 Product Authenticity Verification & Risk Assessment")
    
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())[:8]
        
    mode = st.radio(
        "Select Verification Workflow Mode:",
        [
            "Mode A: Code Lookup (Registry Database)",
            "Mode B: AI Listing Risk Analysis (ML Pipeline)",
            "Mode C: Combined Verification (Registry + ML)",
            "Mode D: Side-by-Side Product Comparison"
        ],
        index=0 if "verify_mode" not in st.session_state else 
        0 if "Mode A" in st.session_state["verify_mode"] else
        1 if "Mode B" in st.session_state["verify_mode"] else
        2 if "Mode C" in st.session_state["verify_mode"] else 3
    )
    
    st.markdown("---")
    
    # ------------------------------------------------------------------
    # MODE A: Code Lookup (Registry Database)
    # ------------------------------------------------------------------
    if "Mode A" in mode:
        st.markdown("### Mode A: Registry Authentication Code Lookup")
        st.caption("Look up verified product codes directly in the official SQLite registry database.")
        
        col_in, col_sample = st.columns([3, 1])
        with col_in:
            auth_input = st.text_input("Enter Product Authentication Code:", placeholder="e.g. AUTH-XXXX-XXXX").strip().upper()
        with col_sample:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Load Sample Registered Code"):
                prods = get_all_products(limit=1)
                if prods:
                    st.session_state["sample_code"] = prods[0]["authentication_code"]
                    st.rerun()
                    
        if "sample_code" in st.session_state and not auth_input:
            auth_input = st.session_state["sample_code"]
            
        if st.button("Verify Code in Registry", type="primary"):
            if not auth_input:
                st.warning("Please enter a valid authentication code.")
                return
                
            session_id = st.session_state["session_id"]
            log_verification_event(auth_input, session_id)
            
            # Check duplicate / code reuse
            reuse_info = check_code_reuse_alert(auth_input, session_id)
            
            prod = get_product_by_auth_code(auth_input)
            
            if reuse_info["reuse_alert"]:
                st.error(f"⚠️ POTENTIAL CODE REUSE DETECTED! This authentication code ({auth_input}) has been verified in {reuse_info['distinct_sessions']} different user sessions ({reuse_info['total_verifications']} total checks).")
                
            if prod:
                st.success(f"✓ REGISTRY VERIFIED: Product Code `{auth_input}` is REGISTERED in the official brand registry.")
                st.markdown(f"""
                    <div class="glass-card">
                        <div style="font-size: 20px; font-weight: 800; color: #f8fafc; margin-bottom: 8px;">{prod['product_name']}</div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; font-size: 13px;">
                            <div><b>Brand:</b> {prod['brand']}</div>
                            <div><b>Category:</b> {prod['product_category']}</div>
                            <div><b>Batch Number:</b> {prod['batch_number']}</div>
                            <div><b>Manufacturing Date:</b> {prod['manufacturing_date']}</div>
                            <div><b>Country of Origin:</b> {prod['origin_country']}</div>
                            <div><b>Reference MSRP:</b> ${prod['reference_price']:.2f}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                add_verification_history(session_id, prod['product_name'], auth_input, 0, 0.0, "CODE_LOOKUP")
            else:
                st.warning(f"❌ CODE NOT FOUND: Authentication code `{auth_input}` is NOT registered in the official database.")
                add_verification_history(session_id, "Unregistered Product", auth_input, 1, 100.0, "CODE_LOOKUP")

    # ------------------------------------------------------------------
    # MODE B: AI Listing Risk Analysis
    # ------------------------------------------------------------------
    elif "Mode B" in mode:
        st.markdown("### Mode B: AI Listing Multi-Signal Risk Analysis")
        st.caption("Input marketplace listing details to run our Random Forest ML Model & Multi-Signal Risk Engine.")
        
        col1, col2 = st.columns(2)
        with col1:
            prod_name = st.text_input("Product Title", "Sony WH-1000XM5 Wireless Headphones")
            brand = st.selectbox("Brand Name", ["Sony", "Nike", "Rolex", "Apple", "Samsung", "Gucci", "Dyson", "Chanel", "Ray-Ban", "Levi's", "Other"])
            ref_price = st.number_input("Manufacturer Reference Price ($)", value=399.0, min_value=1.0)
            listed_price = st.number_input("Marketplace Listed Price ($)", value=120.0, min_value=1.0)
            seller_age = st.number_input("Seller Account Age (Days)", value=25, min_value=1)
            seller_rating = st.slider("Seller Rating (1.0 to 5.0)", 1.0, 5.0, 3.2, 0.1)
            seller_verified = st.checkbox("Seller Verified on Platform", value=False)
            
        with col2:
            review_count = st.number_input("Total Review Count", value=12, min_value=0)
            avg_rating = st.slider("Average Review Rating", 1.0, 5.0, 4.5, 0.1)
            variance = st.slider("Rating Variance", 0.0, 3.0, 2.1, 0.1)
            extreme_ratio = st.slider("Extreme Rating Ratio (1-star + 5-star)", 0.0, 1.0, 0.85, 0.05)
            one_star_pct = st.number_input("1-Star Reviews (%)", value=35.0, min_value=0.0, max_value=100.0)
            five_star_pct = st.number_input("5-Star Reviews (%)", value=50.0, min_value=0.0, max_value=100.0)
            auth_code = st.text_input("Authentication Code Tag (Optional)", "AUTH-SONY-8841")
            
        desc = st.text_area("Product Listing Description", "Grade 1A super copy replica 100% original copy high quality fast ship no box direct factory liquidation.")
        
        # Image Upload Feature (Feature 15)
        st.markdown("#### 📷 Product Image Preview Attachment (Optional)")
        uploaded_img = st.file_uploader("Upload product photo for report attachment or visual reference", type=["png", "jpg", "jpeg"])
        if uploaded_img:
            st.image(uploaded_img, caption="Listing Image Preview (Note: Image preview is for registry reference, no image-based AI detection claim)", width=300)
            
        if st.button("Run AI Risk Assessment Pipeline", type="primary", use_container_width=True):
            raw_input = {
                "product_name": prod_name,
                "brand": brand,
                "reference_price": ref_price,
                "listed_price": listed_price,
                "seller_account_age_days": seller_age,
                "seller_rating": seller_rating,
                "seller_verified": seller_verified,
                "review_count": review_count,
                "average_rating": avg_rating,
                "rating_variance": variance,
                "extreme_rating_ratio": extreme_ratio,
                "one_star_pct": one_star_pct,
                "five_star_pct": five_star_pct,
                "product_description": desc,
                "authentication_code": auth_code
            }
            
            res = predict_authenticity(raw_input, db_check_func=get_product_by_auth_code)
            
            session_id = st.session_state["session_id"]
            add_verification_history(session_id, prod_name, auth_code, res["prediction"], res["risk_score"], "AI_LISTING_ANALYSIS")
            
            st.markdown("---")
            display_risk_score_card(res)
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_left, col_right = st.columns(2)
            with col_left:
                display_multi_signal_breakdown(res["multi_signal_breakdown"])
                render_price_analyzer_card(res["engineered_features"])
            with col_right:
                render_seller_profile_card(res["engineered_features"])
                render_review_detector_card(res["engineered_features"])
                
            st.markdown("<br>", unsafe_allow_html=True)
            render_explanation_panel(res)

    # ------------------------------------------------------------------
    # MODE C: Combined Verification (Mode A + Mode B)
    # ------------------------------------------------------------------
    elif "Mode C" in mode:
        st.markdown("### Mode C: Combined Verification (Registry + ML Pipeline)")
        st.caption("Combines database authentication code lookup with ML multi-signal risk assessment for maximum verification confidence.")
        
        auth_code_c = st.text_input("Enter Product Authentication Code (Mode A)", "AUTH-NIKE-7712").strip().upper()
        
        col1, col2 = st.columns(2)
        with col1:
            prod_name_c = st.text_input("Listing Title", "Nike Air Max 270 Sneakers", key="c_title")
            brand_c = st.selectbox("Brand", ["Nike", "Rolex", "Apple", "Sony", "Adidas", "Gucci"], key="c_brand")
            ref_c = st.number_input("MSRP Reference Price ($)", value=160.0, key="c_ref")
            list_c = st.number_input("Marketplace Price ($)", value=150.0, key="c_list")
            age_c = st.number_input("Seller Age (Days)", value=320, key="c_age")
            
        with col2:
            rating_c = st.slider("Seller Rating", 1.0, 5.0, 4.7, key="c_rating")
            verified_c = st.checkbox("Seller Verified", value=True, key="c_ver")
            rev_c = st.number_input("Reviews Count", value=145, key="c_rev")
            avg_c = st.slider("Average Rating", 1.0, 5.0, 4.6, key="c_avg")
            
        desc_c = st.text_area("Listing Description", "Official Nike Air Max 270 sneakers with authentic barcode tag in box.", key="c_desc")
        
        if st.button("Run Combined Verification Summary", type="primary", use_container_width=True):
            session_id = st.session_state["session_id"]
            log_verification_event(auth_code_c, session_id)
            
            prod = get_product_by_auth_code(auth_code_c)
            reuse_info = check_code_reuse_alert(auth_code_c, session_id)
            
            raw_input = {
                "product_name": prod_name_c, "brand": brand_c, "reference_price": ref_c, "listed_price": list_c,
                "seller_account_age_days": age_c, "seller_rating": rating_c, "seller_verified": verified_c,
                "review_count": rev_c, "average_rating": avg_c, "rating_variance": 0.4, "extreme_rating_ratio": 0.3,
                "one_star_pct": 3.0, "five_star_pct": 75.0, "product_description": desc_c, "authentication_code": auth_code_c
            }
            res = predict_authenticity(raw_input, db_check_func=get_product_by_auth_code)
            
            st.markdown("---")
            st.markdown("## 📋 Final Combined Verification Summary")
            
            col_reg, col_ml = st.columns(2)
            with col_reg:
                st.markdown("#### Signal 1: Database Registry Verification")
                if prod:
                    st.success(f"✓ REGISTERED CODE (`{auth_code_c}`)\nRegistered to: **{prod['product_name']}**")
                else:
                    st.error(f"❌ UNREGISTERED CODE (`{auth_code_c}`)\nCode was not found in official registry.")
                    
                if reuse_info["reuse_alert"]:
                    st.error(f"⚠️ Code Reuse Alert: Checked in {reuse_info['distinct_sessions']} sessions!")
                    
            with col_ml:
                st.markdown("#### Signal 2: AI Multi-Signal ML Assessment")
                st.info(f"Prediction: **{res['prediction_label']}**\nRisk Score: **{res['risk_score']:.1f}%** | Confidence: **{res['confidence_pct']:.1f}%**")
                
            st.markdown("<br>", unsafe_allow_html=True)
            display_risk_score_card(res)
            render_explanation_panel(res)
            
            add_verification_history(session_id, prod_name_c, auth_code_c, res["prediction"], res["risk_score"], "COMBINED_VERIFICATION")

    # ------------------------------------------------------------------
    # MODE D: Product Comparison Mode
    # ------------------------------------------------------------------
    elif "Mode D" in mode:
        render_product_comparison_ui(get_product_func=get_product_by_auth_code)
