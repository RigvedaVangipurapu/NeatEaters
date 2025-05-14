import streamlit as st
import pandas as pd
import numpy as np
import requests
from PIL import Image
import io
import hashlib
import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Maps client with API key from environment variable
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

st.set_page_config(
    page_title="NeatEaters - Snack Finder",
    page_icon="🍎",
    layout="wide"
)

GOOGLE_PLACES_API_KEY = "AIzaSyAzr4bSo8FHHhQvsLnsoGb1ywAytjLWZqI"

# Initialize session state for page navigation and store counter
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_store' not in st.session_state:
    st.session_state.selected_store = None
if 'store_counter' not in st.session_state:
    st.session_state.store_counter = 0

def generate_unique_key(store):
    # Create a unique key using store name and address
    key_string = f"{store['name']}_{store['address']}"
    return hashlib.md5(key_string.encode()).hexdigest()[:10]

# Helper function to get grocery stores near a location
def get_grocery_stores(location, api_key):
    endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"grocery stores near {location}",
        "key": api_key
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        stores = []
        for store in results:
            stores.append({
                "name": store.get("name"),
                "address": store.get("formatted_address"),
                "maps_url": f"https://www.google.com/maps/search/?api=1&query={store.get('geometry', {}).get('location', {}).get('lat','')},{store.get('geometry', {}).get('location', {}).get('lng','')}"
            })
        return stores
    else:
        st.error(f"API Error: {response.status_code} - {response.text}")
        return []

def show_add_snack_page():
    st.title(f"Add Snacks to {st.session_state.selected_store['name']}")
    
    # Back button
    if st.button("← Back to Store List"):
        st.session_state.page = 'main'
        st.rerun()
    
    st.write("Register a new snack you found at this store!")
    
    # Snack registration form
    with st.form("snack_registration"):
        snack_name = st.text_input("Snack Name")
        snack_description = st.text_area("Description")
        snack_price = st.number_input("Price ($)", min_value=0.0, step=0.01)
        
        # Photo upload
        uploaded_file = st.file_uploader("Upload a photo of the snack", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Snack Photo", use_column_width=True)
        
        # Submit button
        submitted = st.form_submit_button("Register Snack")
        if submitted:
            if snack_name and snack_description:
                st.success(f"Successfully registered {snack_name}!")
                # Here you would typically save the data to a database
            else:
                st.error("Please fill in all required fields!")

def main():
    st.title("🍎 NeatEaters - Snack Finder")
    st.write("Find healthy and delicious snacks that match your preferences!")

    # Sidebar for filters
    with st.sidebar:
        st.header("Filters")
        dietary_preferences = st.multiselect(
            "Dietary Preferences",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Nut-Free"]
        )

    # --- Grocery Store Search ---
    st.header("Find Grocery Stores Near You 🛒")
    location = st.text_input("Enter your location:", value="Irvine, CA")
    if st.button("Search Grocery Stores"):
        with st.spinner("Searching for grocery stores..."):
            stores = get_grocery_stores(location, GOOGLE_PLACES_API_KEY)
            if stores:
                # Reset store counter when new search is performed
                st.session_state.store_counter = 0
                
                for store in stores:
                    # Increment counter for each store
                    st.session_state.store_counter += 1
                    current_counter = st.session_state.store_counter
                    
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.markdown(f"**{store['name']}**  ")
                        st.markdown(f"{store['address']}")
                    with col2:
                        st.markdown(f"[View on Google Maps]({store['maps_url']})")
                    with col3:
                        if st.button("Add NeatEats", key=f"add_{current_counter}"):
                            st.session_state.selected_store = store
                            st.session_state.page = 'add_snack'
                            st.rerun()
                    with col4:
                        if st.button("Find NeatEats", key=f"find_{current_counter}"):
                            st.session_state.search_store = store
                            st.info(f"Searching for NeatEats at {store['name']}...")
                    st.markdown("---")
            else:
                st.warning("No grocery stores found for this location.")

    # Main content area
    st.header("Recommended Snacks")
    # Placeholder for snack recommendations
    st.info("Snack recommendations will appear here based on your preferences.")

if __name__ == "__main__":
    if st.session_state.page == 'add_snack':
        show_add_snack_page()
    else:
        main() 