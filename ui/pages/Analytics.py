import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.api import get_items
import pandas as pd
import plotly.express as px
from datetime import datetime

st.title("📊 ShelfSense Analytics")

st.markdown("Track your food inventory insights in one place.")

user_id = st.text_input("👤 User ID", value="testuser")

if user_id:
    items = get_items(user_id)

    if isinstance(items, list) and items:
        df = pd.DataFrame(items)
        df["expiry_date"] = pd.to_datetime(df["expiry_date"])
        df["added_on"] = pd.to_datetime(df["added_on"])

        st.subheader("📦 Inventory Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Items", len(df))
        col2.metric("Unique Items", df["item_name"].nunique())
        col3.metric("Items Expiring Soon", len(df[df["expiry_date"].dt.date <= datetime.today().date() + pd.Timedelta(days=2)]))

        st.divider()

        st.subheader("🥧 Item Distribution")

        count_df = df["item_name"].value_counts().reset_index()
        count_df.columns = ["Item", "Count"]
        pie_chart = px.pie(count_df, values="Count", names="Item", title="Items by Name")
        st.plotly_chart(pie_chart, use_container_width=True)

        st.subheader("📅 Items Added Over Time")
        added_chart = df.groupby(df["added_on"].dt.date).size().reset_index(name="Items Added")
        line_chart = px.line(added_chart, x="added_on", y="Items Added", markers=True, title="Items Added by Date")
        st.plotly_chart(line_chart, use_container_width=True)

        st.subheader("⏳ Expiry Trend")
        expiry_chart = df.groupby(df["expiry_date"].dt.date).size().reset_index(name="Items Expiring")
        bar_chart = px.bar(expiry_chart, x="expiry_date", y="Items Expiring", title="Upcoming Expiries")
        st.plotly_chart(bar_chart, use_container_width=True)

    elif isinstance(items, list) and not items:
        st.info("No items found for this user.")
    else:
        st.error(f"Failed to fetch data: {items}")
