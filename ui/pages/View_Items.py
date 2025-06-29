import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.api import get_items, update_item, delete_item
from datetime import datetime, timedelta, timezone
import pandas as pd

st.set_page_config(page_title="View Items", page_icon="📦")

st.title("📋 View & Manage Your Food Inventory")

st.markdown("Enter your User ID to view, update, or delete your items. We’ll also highlight if something is expiring soon!")

user_id = st.text_input("👤 User ID", value="testuser")
refresh = st.button("🔄 Refresh Items")

def get_expiry_status(expiry_date):
    today = datetime.now(timezone.utc).date()
    expiry = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    if expiry < today:
        return "❌ Expired", "red"
    elif expiry <= today + timedelta(days=2):
        return "⚠️ Expiring Soon", "orange"
    else:
        return "✅ Fresh", "green"

if user_id or refresh:
    response = get_items(user_id)

    if isinstance(response, list):
        if response:
            for item in response:
                status_text, color = get_expiry_status(item['expiry_date'])
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: black; border-left: 5px solid {color}; padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                            <h4>🧾 {item['item_name']}</h4>
                            <p><strong>📦 Quantity:</strong> {item['quantity']}</p>
                            <p><strong>📅 Expiry Date:</strong> {item['expiry_date']} <span style="color:{color}; font-weight:bold;">({status_text})</span></p>
                            <p><strong>📥 Added On:</strong> {item['added_on']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        with st.expander("📝 Update Item"):
                            new_expiry = st.date_input("📅 New Expiry Date", value=datetime.strptime(item['expiry_date'], "%Y-%m-%d").date(), key=f"exp_{item['item_id']}")
                            new_quantity = st.text_input("✏️ New Quantity", value=item['quantity'], key=f"qty_{item['item_id']}")
                            if st.button("✔ Confirm Update", key=f"submit_{item['item_id']}"):
                                update_resp = update_item(
                                    user_id,
                                    item_id=item["item_id"],
                                    expiry_date=new_expiry.strftime("%Y-%m-%d"),
                                    quantity=new_quantity
                                )
                                if "message" in update_resp:
                                    st.success("✅ Item updated! Click Refresh.")
                                else:
                                    st.error(f"❌ Update failed: {update_resp}")

                    with col2:
                        if st.button("🗑 Delete", key=f"delete_{item['item_id']}"):
                            delete_resp = delete_item(user_id, item["item_id"])
                            if "message" in delete_resp:
                                st.success("🧹 Item deleted! Click Refresh.")
                            else:
                                st.error(f"❌ Delete failed: {delete_resp}")
        else:
            st.info("🤷 No items found for this user.")
    else:
        st.error(f"Failed to fetch items. Response: {response}")
