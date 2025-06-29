import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.api import add_item
from datetime import date

st.title("📝 Add Food Item")

st.markdown("Use the form below to add a new food item to your ShelfSense tracker.")

with st.form("add_form"):
    user_id = st.text_input("👤 User ID", value="testuser")
    item_name = st.text_input("🍎 Item Name")
    expiry_date = st.date_input("📅 Expiry Date", min_value=date.today())
    quantity = st.text_input("🔢 Quantity", placeholder="e.g., 1 pack, 500g")

    submitted = st.form_submit_button("➕ Add Item")

    if submitted:
        try:
            result = add_item(user_id, item_name, expiry_date.strftime("%Y-%m-%d"), quantity)
            st.success(f"✅ Item added! ID: {result.get('item_id', 'N/A')}")
        except Exception as e:
            st.error(f"❌ Failed to add item: {e}")
