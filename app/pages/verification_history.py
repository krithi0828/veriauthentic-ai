import streamlit as st
import uuid
import pandas as pd
from database.database import get_verification_history

def show_verification_history_page():
    st.markdown("## 📜 Session Verification History")
    st.caption("Tracks your product authenticity queries for this session. (Privacy note: session-based tracking, cleared when browser is reset).")
    
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())[:8]
        
    session_id = st.session_state["session_id"]
    st.info(f"🔑 Active Session Identifier: `{session_id}`")
    
    history_records = get_verification_history(session_id=session_id, limit=50)
    
    if not history_records:
        st.warning("No verification history recorded in this current session yet. Run a verification query under 'Verify Product' to see history log.")
    else:
        df_hist = pd.DataFrame(history_records)
        df_hist["Risk Badge"] = df_hist["risk_score"].apply(lambda s: f"🔴 Critical ({s:.1f}%)" if s >= 76 else f"🟠 High ({s:.1f}%)" if s >= 51 else f"🟡 Moderate ({s:.1f}%)" if s >= 26 else f"🟢 Low ({s:.1f}%)")
        
        st.markdown(f"### Recorded Session Verification Logs ({len(history_records)} items)")
        
        display_df = df_hist[["created_at", "product_name", "authentication_code", "verification_type", "Risk Badge"]]
        display_df.columns = ["Timestamp", "Product Name", "Auth Code Tag", "Workflow Mode", "Risk Tier Score"]
        
        st.dataframe(display_df, use_container_width=True)
