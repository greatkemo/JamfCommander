import json
import os
import logging
import requests
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

TOKEN_FILE = ".jamf_token"
TMP_DIR = "tmp"

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env
def load_env_variables():
    load_dotenv()

# Save the Jamf Pro URL to the environment
def save_url_to_env(jamf_url):
    with open(".env", "w") as env_file:
        env_file.write(f"JAMF_PRO_URL={jamf_url}\n")
    logging.debug(f"Saved Jamf Pro URL to .env file: {jamf_url}")

# Load credentials from .jcinf.json
def load_credentials():
    try:
        logging.debug("Attempting to load credentials from .jcinf.json")
        with open('.jcinf.json') as file:
            credentials = json.load(file)
            logging.debug(f"Credentials loaded successfully: {credentials}")
            return credentials.get('client_id'), credentials.get('client_secret'), credentials.get('grant_type')
    except FileNotFoundError:
        logging.error("The credentials file (.jcinf.json) is missing.")
        return None, None, None
    except KeyError as e:
        logging.error(f"Error loading credentials: Missing key {e}")
        return None, None, None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return None, None, None

# Save the token to a file
def save_token(token, expiry_time):
    token_data = {
        "token": token,
        "expiry": expiry_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    with open(TOKEN_FILE, "w") as token_file:
        json.dump(token_data, token_file)
    logging.debug(f"Token saved to {TOKEN_FILE}")

# Clear the token file
def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        logging.debug("Token file cleared")

# Load the token from the file
def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token_file:
            token_data = json.load(token_file)
            token = token_data.get("token")
            expiry = token_data.get("expiry")

            if not token or not expiry:
                return None

            # Check if the token is expired
            expiry_time = datetime.strptime(expiry, "%Y-%m-%dT%H:%M:%S.%fZ")
            if datetime.utcnow() >= expiry_time:
                logging.debug("Token expired, renewing token")
                return renew_token()

            logging.debug("Token loaded from file")
            return token
    logging.error("Token file not found, please authenticate")
    return None

# Load the token from the file (alternative name for compatibility)
def load_token_from_file():
    return load_token()

# Ensure the tmp directory exists
def ensure_tmp_directory():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)
        logging.debug(f"Created tmp directory: {TMP_DIR}")

# Save data to cache
def save_to_cache(filename, data):
    ensure_tmp_directory()
    filepath = os.path.join(TMP_DIR, filename)
    with open(filepath, "w") as cache_file:
        if isinstance(data, dict):
            json.dump(data, cache_file)
        elif isinstance(data, bytes):
            cache_file.write(data.decode('utf-8'))  # Decode bytes to string
        else:
            cache_file.write(data)  # Write string data directly
    logging.debug(f"Saved data to cache: {filepath}")

# Function to make an authenticated Classic API request (XML response)
def make_classic_api_request(jamf_url, endpoint, token=None):
    if not token:
        token = load_token()
        if not token:
            logging.error("No valid token available")
            return None

    # Construct the API URL
    api_url = f"{jamf_url}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/xml"
    }
    # Make the API request
    try:
        logging.debug(f"Making Classic API request to {api_url}")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.content  # Return XML content
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# Function to make an authenticated Jamf Pro API request (JSON response)
def make_api_request(jamf_url, endpoint):
    token = load_token()
    if not token:
        logging.error("No token found!")
        return None

    api_url = f"{jamf_url}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    try:
        logging.debug(f"Making Jamf Pro API request to {api_url}")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()  # Return JSON content
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# Function to parse XML and extract the <size> element value (count)
def get_size_from_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
        size_element = root.find('size')
        if size_element is not None:
            return size_element.text
        else:
            return "N/A"
    except ET.ParseError as e:
        logging.error(f"Error parsing XML: {e}")
        return "N/A"

# Renew the token if expired
def renew_token():
    jamf_url = os.getenv("JAMF_PRO_URL")
    client_id, client_secret, grant_type = load_credentials()

    if not jamf_url or not client_id or not client_secret or not grant_type:
        logging.error("Jamf URL, client ID, client secret, or grant type not set in environment variables.")
        return None

    token, expires_in = get_token(jamf_url, client_id, client_secret, grant_type)
    if token:
        # Calculate the expiry time
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        save_token(token, expiry_time)  # Save token and expiry time for future API requests
        logging.debug("Token renewed and saved to file")
        return token
    else:
        logging.error("Token renewal failed")
        return None

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