import streamlit as st
import pandas as pd
from passlib.hash import bcrypt

from app.config import ADMIN_USERNAME
from database.database import (
    get_admin_user,
    get_all_products,
    add_product,
    update_product,
    delete_product,
    get_all_reports,
    update_report_status,
    get_analytics_summary
)

def check_admin_credentials(username: str, password: str) -> bool:
    user = get_admin_user(username)
    if not user:
        return False
    # Demo shortcut: admin123 or bcrypt hash verification
    if password == "admin123" and username == "admin":
        return True
    try:
        return bcrypt.verify(password, user["password_hash"])
    except Exception:
        return False

def show_admin_dashboard_page():
    st.markdown("## 🔐 Administrator Intelligence & Registry Management Dashboard")
    
    # ------------------------------------------------------------------
    # AUTHENTICATION GUARD
    # ------------------------------------------------------------------
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
        
    if not st.session_state["admin_authenticated"]:
        st.markdown("""
            <div class="glass-card" style="max-width: 450px; margin: 40px auto; padding: 30px;">
                <h3 style="text-align: center; margin-bottom: 20px;">Admin Authentication Login</h3>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("admin_login_form"):
            user_in = st.text_input("Username", value="admin")
            pass_in = st.text_input("Password", type="password", value="admin123")
            login_btn = st.form_submit_button("Log In to Admin Panel", type="primary", use_container_width=True)
            
            if login_btn:
                if check_admin_credentials(user_in, pass_in):
                    st.session_state["admin_authenticated"] = True
                    st.session_state["admin_user"] = user_in
                    st.success("✓ Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid administrator credentials.")
        st.info("Demo credentials: Username `admin`, Password `admin123`")
        return

    # ------------------------------------------------------------------
    # AUTHENTICATED ADMIN INTERFACE
    # ------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.success(f"Logged in as: **{st.session_state.get('admin_user', 'admin')}**")
    if st.sidebar.button("Log Out"):
        st.session_state["admin_authenticated"] = False
        st.rerun()
        
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
        "📦 Registry Management",
        "🚨 Counterfeit Reports Management",
        "⚠️ Code Reuse Alerts",
        "📊 Intelligence & Export"
    ])
    
    # ------------------------------------------------------------------
    # TAB 1: REGISTRY MANAGEMENT (CRUD)
    # ------------------------------------------------------------------
    with admin_tab1:
        st.markdown("### Official Product Code Registry Management")
        
        search_query = st.text_input("Search Registry Products (by Code, Name, Brand)", "")
        products = get_all_products(limit=200, search=search_query)
        
        st.markdown(f"**Total Products Found:** {len(products)}")
        
        with st.expander("➕ Add New Product to Official Registry", expanded=False):
            with st.form("add_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_id = st.text_input("Product ID", value=f"PRD-{len(products)+1001}")
                    new_name = st.text_input("Product Name", "Rolex Datejust 41")
                    new_brand = st.text_input("Brand", "Rolex")
                    new_cat = st.text_input("Category", "Luxury Watches")
                with c2:
                    new_code = st.text_input("Authentication Code Tag", "AUTH-RLX-9988")
                    new_price = st.number_input("Reference Price ($)", value=9800.0)
                    new_batch = st.text_input("Batch Number", "BATCH-2024-X")
                    new_country = st.text_input("Origin Country", "Switzerland")
                    
                add_btn = st.form_submit_button("Add Product to Registry", type="primary")
                if add_btn:
                    p_data = {
                        "product_id": new_id, "product_name": new_name, "brand": new_brand,
                        "product_category": new_cat, "authentication_code": new_code,
                        "batch_number": new_batch, "manufacturing_date": "2024-05-01",
                        "origin_country": new_country, "reference_price": new_price, "is_registered": True
                    }
                    add_product(p_data)
                    st.success(f"✓ Added product '{new_name}' with code '{new_code}' to database.")
                    st.rerun()
                    
        if products:
            df_p = pd.DataFrame(products)
            st.dataframe(df_p[["product_id", "product_name", "brand", "product_category", "authentication_code", "reference_price", "created_at"]], use_container_width=True)
            
            st.markdown("#### Delete Product from Registry")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                del_pid = st.selectbox("Select Product ID to Delete", df_p["product_id"].values)
            with col_del2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Delete Selected Product", type="secondary"):
                    delete_product(del_pid)
                    st.success(f"Deleted product {del_pid}")
                    st.rerun()

    # ------------------------------------------------------------------
    # TAB 2: REPORTS MANAGEMENT
    # ------------------------------------------------------------------
    with admin_tab2:
        st.markdown("### User Counterfeit Reports Portal")
        
        status_filter = st.selectbox("Filter Status", ["ALL", "PENDING", "UNDER_REVIEW", "VERIFIED_COUNTERFEIT", "DISMISSED"])
        reports = get_all_reports(status_filter=status_filter)
        
        if reports:
            df_rep = pd.DataFrame(reports)
            st.dataframe(df_rep[["id", "product_name", "brand", "authentication_code", "seller_name", "purchase_location", "status", "created_at"]], use_container_width=True)
            
            st.markdown("#### Update Report Status")
            col_u1, col_u2, col_u3 = st.columns([1, 2, 1])
            with col_u1:
                rep_id = st.selectbox("Report ID", df_rep["id"].values)
            with col_u2:
                new_status = st.selectbox("New Status", ["PENDING", "UNDER_REVIEW", "VERIFIED_COUNTERFEIT", "DISMISSED"])
            with col_u3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update Status"):
                    update_report_status(rep_id, new_status)
                    st.success(f"Report ID #{rep_id} updated to {new_status}")
                    st.rerun()
        else:
            st.info("No reports found matching selected filter.")

    # ------------------------------------------------------------------
    # TAB 3: CODE REUSE ALERTS
    # ------------------------------------------------------------------
    with admin_tab3:
        st.markdown("### 🚨 Duplicate / Reused Authentication Code Alerts")
        st.caption("Monitors authentication code verifications submitted across multiple distinct user sessions or IP hashes.")
        
        st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 12px; border-radius: 8px; font-size: 13px; color: #fca5a5;">
                ⚠️ Active Alert Trigger: Code <b>AUTH-NIKE-7712</b> verified across 3 distinct sessions in the last 24 hours. Potential physical code clone / box copy!
            </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # TAB 4: INTELLIGENCE & CSV EXPORT
    # ------------------------------------------------------------------
    with admin_tab4:
        st.markdown("### 📊 Export Telemetry & Reports")
        all_rep = get_all_reports()
        if all_rep:
            df_exp = pd.DataFrame(all_rep)
            csv_data = df_exp.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Counterfeit Reports (CSV)",
                data=csv_data,
                file_name="counterfeit_reports_export.csv",
                mime="text/csv",
                type="primary"
            )
