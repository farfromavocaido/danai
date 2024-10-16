import os
import json
import requests
from datetime import datetime, timedelta
import base64

# Define paths for the cache, JSON, and metadata
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PRICING_FILE = os.path.join(PACKAGE_DIR, 'pricing.json')
CACHE_DIR = os.path.expanduser("~/.danai_cache")
CACHE_FILE = os.path.join(CACHE_DIR, "cached_pricing.json")
METADATA_FILE = os.path.join(CACHE_DIR, "metadata.json")

# Ensure the cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# URL to fetch the JSON dynamically (if hosted elsewhere)
JSON_URL = "https://raw.githubusercontent.com/farfromavocaido/ai_utils/refs/heads/main/danai/pricing.json"

def fetch_json():
    """Fetch the JSON from the external source (e.g., GitHub)."""
    response = requests.get(JSON_URL)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch JSON: {response.status_code}")

def load_local_json():
    """Load the locally cached JSON file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    else:
        return load_default_pricing()

def save_local_json(data):
    """Save the fetched JSON data and update metadata."""
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)
    # Update the metadata with the current time
    with open(METADATA_FILE, 'w') as f:
        json.dump({"last_updated": datetime.now().isoformat()}, f)

def load_metadata():
    """Load the metadata for the last update time."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"last_updated": None}

def load_default_pricing():
    """Load the default pricing JSON from the package directory."""
    with open(PRICING_FILE, 'r') as pricing_file:
        return json.load(pricing_file)

def check_for_update():
    """Check if the pricing data is outdated and prompt the user to update."""
    metadata = load_metadata()
    last_updated_str = metadata.get("last_updated")
    
    if last_updated_str:
        last_updated = datetime.fromisoformat(last_updated_str)
        if datetime.now() - last_updated > timedelta(days=1):
            # Prompt user to update
            prompt_user_to_update(last_updated)
        else:
            return load_local_json()
    else:
        # No metadata found, use default
        return load_default_pricing()

def prompt_user_to_update(last_updated):
    """Prompt the user to update the pricing data."""
    print(f"Your pricing data was last updated on {last_updated}.")
    user_input = input("Would you like to update the pricing data? (y/n): ").strip().lower()

    if user_input == 'y':
        try:
            data = fetch_json()
            save_local_json(data)
            print("Pricing data updated successfully.")
            return data
        except Exception as e:
            print(f"Failed to update pricing data: {e}")
            return load_local_json()
    else:
        print("Using cached or default pricing data.")
        return load_local_json()
    