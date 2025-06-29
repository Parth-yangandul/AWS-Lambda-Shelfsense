import streamlit as st
import sys
import os
from datetime import date
sys.path.append(os.path.dirname(__file__))  # ✅ Add this only here

st.set_page_config(
    page_title="ShelfSense",
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ ShelfSense - Smart Food Inventory & Expiry Tracker")

st.markdown("""
Welcome to **ShelfSense** – your intelligent kitchen companion!

📦 Track your groceries  
⏰ Get notified before they expire  
🥘 Discover recipes to reduce waste  
📊 Gain insights from food analytics

---  

🔍 Use the sidebar to:
- ➕ Add Items  
- 👀 View / Update / Delete  
- ⏰ See Expiring Items + Recipes  
- 📈 Explore Inventory Analytics  
""")

st.info(f"Today’s date: **{date.today()}**")

st.success("Ready to explore? Use the sidebar ➡️")
