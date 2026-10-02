import streamlit as st
from database.database import add_report

def show_report_counterfeit_page():
    st.markdown("## 📢 Report Counterfeit Product / Listing")
    st.caption("Submit suspicious listings or counterfeit purchases to our brand protection and intelligence database.")
    
    with st.form("counterfeit_report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name *", placeholder="e.g. Nike Air Jordan 1 Retro")
            brand = st.text_input("Brand / Manufacturer", placeholder="e.g. Nike")
            auth_code = st.text_input("Authentication Code Tag (if available)", placeholder="e.g. AUTH-XXXX-XXXX")
            seller_name = st.text_input("Seller Name / Store Account", placeholder="e.g. DiscountOutletStore99")
            
        with col2:
            purchase_loc = st.text_input("Purchase Location / Marketplace URL *", placeholder="e.g. eBay / Instagram Ad / Unauthorized Website")
            reporter_name = st.text_input("Your Name *", placeholder="e.g. John Doe")
            reporter_email = st.text_input("Your Contact Email *", placeholder="e.g. john@example.com")
            
        reason = st.text_area("Detailed Reason for Counterfeit Suspicion *", placeholder="Describe why you suspect this item is counterfeit (e.g. fake materials, blurred logo, missing warranty card, 70% price discount below retail, invalid code).")
        
        submitted = st.form_submit_button("Submit Counterfeit Report", type="primary", use_container_width=True)
        
        if submitted:
            if not product_name or not purchase_loc or not reporter_name or not reporter_email or not reason:
                st.error("Please fill in all required fields marked with *.")
            else:
                report_data = {
                    "product_name": product_name,
                    "brand": brand,
                    "authentication_code": auth_code,
                    "seller_name": seller_name,
                    "purchase_location": purchase_loc,
                    "reason": reason,
                    "reporter_name": reporter_name,
                    "reporter_email": reporter_email,
                    "risk_score": 85.0,
                    "prediction": 1,
                    "status": "PENDING"
                }
                report_id = add_report(report_data)
                st.success(f"✓ Counterfeit report submitted successfully! Reference ID: `REP-{report_id:04d}`. Our intelligence team will review this report.")
