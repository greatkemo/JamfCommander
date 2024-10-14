import requests
import logging
from datetime import datetime, timedelta
from src.utils import save_token, clear_token, load_credentials

# Function to get an OAuth token from Jamf Pro
def get_token(jamf_url, client_id, client_secret, grant_type):
    token_url = f"{jamf_url}/api/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type
    }

    logging.debug(f"Requesting token from {token_url}")
    logging.debug(f"Request headers: {headers}")
    logging.debug(f"Request payload: {data}")

    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()  # Will raise an exception for any 4XX/5XX responses
        token_info = response.json()
        logging.debug(f"Token received: {token_info}")
        return token_info.get("access_token"), token_info.get("expires_in")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None, None
    except Exception as e:
        logging.error(f"An error occurred while requesting the token: {e}")
        return None, None

# Function to handle authentication process
def authenticate(jamf_url, status_label):
    logging.debug("Starting authentication process...")

    # Clear any existing token
    clear_token()

    # Load credentials from .jcinf.json
    client_id, client_secret, grant_type = load_credentials()

    logging.debug(f"Loaded credentials - Client ID: {client_id}, Grant Type: {grant_type}")

    if not client_id or not client_secret or not grant_type:
        status_label.config(text="AUTH FAILED", fg="red")
        logging.error("Missing credentials, authentication failed.")
        return None

    # Get the OAuth token
    token, expires_in = get_token(jamf_url, client_id, client_secret, grant_type)

    if token:
        # Calculate the expiry time
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        save_token(token, expiry_time)  # Save token and expiry time for future API requests
        status_label.config(text="AUTHENTICATED", fg="green")
        logging.debug("Authentication successful.")
        return token
    else:
        status_label.config(text="AUTH FAILED", fg="red")
        logging.error("Authentication failed.")
        return None