import requests
from dotenv import load_dotenv
import os
load_dotenv()

# 🔧 Replace this with your actual deployed API Gateway base URL
BASE_URL = os.getenv("API_GATEWAY_BASE_URL")

def add_item(user_id, item_name, expiry_date, quantity):
    url = f"{BASE_URL}/add-item"
    payload = {
        "user_id": user_id,
        "item_name": item_name,
        "expiry_date": expiry_date,
        "quantity": quantity
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Will throw error if response is not 2xx
    return response.json()       # Should contain 'message' or 'item_id'


def get_items(user_id):
    url = f"{BASE_URL}/get-items"
    params = {"user_id": user_id}
    response = requests.get(url, params=params)
    return response.json()

def update_item(user_id, item_id, expiry_date=None, quantity=None):
    url = f"{BASE_URL}/update-item"
    payload = {
        "user_id": user_id,
        "item_id": item_id
    }
    if expiry_date:
        payload["expiry_date"] = expiry_date
    if quantity:
        payload["quantity"] = quantity
    response = requests.post(url, json=payload)
    return response.json()

def delete_item(user_id, item_id):
    url = f"{BASE_URL}/delete-item"
    payload = {
        "user_id": user_id,
        "item_id": item_id
    }
    response = requests.post(url, json=payload)
    return response.json()
