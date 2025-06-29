import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.api import get_items
import pandas as pd
from datetime import datetime, timedelta
import requests

SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')
if not SPOONACULAR_API_KEY:
    st.error("SPOONACULAR_API_KEY not set. Please check your .env file.")
    st.stop()

st.title("⏰ Items Expiring Soon + Recipes")

st.markdown("See which items are about to expire and get recipe suggestions.")

user_id = st.text_input("👤 User ID", value="testuser")

if user_id:
    response = get_items(user_id)

    if isinstance(response, list) and response:
        today = datetime.now().date()
        threshold = today + timedelta(days=2)

        expiring_items = [
            item for item in response
            if datetime.strptime(item["expiry_date"], "%Y-%m-%d").date() <= threshold
        ]

        if expiring_items:
            st.subheader("⚠️ Expiring Soon")
            for item in expiring_items:
                st.markdown(f"- **{item['item_name']}** (expires on `{item['expiry_date']}`)")

            # Combine ingredients for recipe search
            ingredients = ",".join(i["item_name"] for i in expiring_items)

            st.subheader("🍽 Suggested Recipes")

            # Call Spoonacular API (or Forkify fallback)
            try:
                url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=3&apiKey={SPOONACULAR_API_KEY}"
                recipe_res = requests.get(url).json()

                if isinstance(recipe_res, list) and recipe_res:
                    for recipe in recipe_res:
                        st.markdown(f"### {recipe['title']}")
                        st.image(recipe['image'], width=300)
                        st.markdown(f"[View Recipe](https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']})")
                else:
                    st.warning("No recipes found for these items.")
            except Exception as e:
                st.error(f"Failed to fetch recipes: {e}")
        else:
            st.info("No items are expiring soon.")
    else:
        st.error("Failed to fetch items or no data found.")
