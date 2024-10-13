import requests
import xml.etree.ElementTree as ET
from tkinter import *
from tkinter import ttk  # For Tabs
import json
import logging
import os
from dotenv import load_dotenv

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file (if it exists)
load_dotenv()

# Path to the temporary token file
TOKEN_FILE = ".jamf_token"

# Function to load client credentials from .jcinf.json
def load_credentials():
    try:
        logging.debug("Loading credentials from .jcinf.json")
        with open('.jcinf.json') as file:
            credentials = json.load(file)
            logging.debug(f"Credentials loaded: {credentials}")
            return credentials['client_id'], credentials['client_secret'], credentials['grant_type']
    except FileNotFoundError:
        logging.error("The credentials file (.jcinf.json) is missing.")
        return None, None, None
    except KeyError as e:
        logging.error(f"Error loading credentials: Missing key {e}")
        return None, None, None

# Function to store the URL in the .env file
def save_url_to_env(jamf_url):
    with open(".env", "w") as env_file:
        env_file.write(f"JAMF_PRO_URL={jamf_url}\n")
    logging.debug(f"Saved Jamf Pro URL to .env file: {jamf_url}")

# Function to save the token to a file
def save_token(token):
    with open(TOKEN_FILE, "w") as token_file:
        token_file.write(token)
    logging.debug(f"Token saved to {TOKEN_FILE}")

# Function to load the token from the file
def load_token():
    try:
        with open(TOKEN_FILE, "r") as token_file:
            token = token_file.read().strip()
        logging.debug("Token loaded from file")
        return token
    except FileNotFoundError:
        logging.error("No token found, please authenticate")
        return None

# Function to delete the token (used when re-authenticating)
def clear_token():
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            logging.debug("Token file deleted")
    except Exception as e:
        logging.error(f"Error clearing token: {e}")

# Function to obtain an OAuth 2.0 access token using client_credentials grant type
def get_token(jamf_url, client_id, client_secret, grant_type):
    token_url = f"{jamf_url}/api/oauth/token"  # Correct authentication endpoint
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
        # Make the request to get the token
        response = requests.post(token_url, headers=headers, data=data)
        logging.debug(f"Response status code: {response.status_code}")
        logging.debug(f"Response content: {response.text}")

        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response and extract the access_token
        token_info = response.json()
        logging.debug(f"Token received: {token_info}")

        # Extract and return the access_token
        return token_info.get("access_token")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# Function to handle authentication
def authenticate():
    # Clear the previous token if it exists
    clear_token()

    # Get the values entered by the user or loaded from environment variable
    jamf_url = entry_url.get()

    if not jamf_url:
        status_label.config(text="AUTH FAILED", fg="red")
        return

    # Save the URL to the .env file for future use
    save_url_to_env(jamf_url)

    # Load client credentials from .jcinf.json
    client_id, client_secret, grant_type = load_credentials()

    if not client_id or not client_secret or not grant_type:
        status_label.config(text="AUTH FAILED", fg="red")
        return

    # Get the OAuth access token
    token = get_token(jamf_url, client_id, client_secret, grant_type)

    if token:
        save_token(token)  # Save the token to the file for reuse
        status_label.config(text="AUTHENTICATED", fg="green")
        # Automatically update the dashboard after authentication
        update_dashboard()
    else:
        status_label.config(text="AUTH FAILED", fg="red")

# Function to make an authenticated API request to the Classic API
def make_classic_api_request(endpoint):
    token = load_token()
    if not token:
        status_label.config(text="AUTH FAILED", fg="red")
        return None
    
    jamf_url = entry_url.get()
    api_url = f"{jamf_url}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/xml"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.content  # Return XML content
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

# Function to parse the XML response and get the size (for counts)
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

# Function to update the dashboard
def update_dashboard():
    # Jamf Pro Version (JSON response)
    version_data = make_classic_api_request('api/v1/jamf-pro-version')
    if version_data:
        version_label.config(text=f"Jamf Pro Version: {version_data}")

    # Managed Computers
    computers_data = make_classic_api_request('JSSResource/computers')
    computers_count = get_size_from_xml(computers_data)
    computers_label.config(text=f"Managed Computers: {computers_count}")

    # Smart Computer Groups
    smart_computer_groups_data = make_classic_api_request('JSSResource/computergroups')
    smart_computer_groups_count = get_size_from_xml(smart_computer_groups_data)  # Should handle filtering for smart groups
    smart_computer_groups_label.config(text=f"Smart Computer Groups: {smart_computer_groups_count}")

    # Static Computer Groups
    static_computer_groups_data = make_classic_api_request('JSSResource/computergroups')
    static_computer_groups_count = get_size_from_xml(static_computer_groups_data)  # Should handle filtering for static groups
    static_computer_groups_label.config(text=f"Static Computer Groups: {static_computer_groups_count}")

    # Policies (Computers)
    policies_data = make_classic_api_request('JSSResource/policies')
    policies_count = get_size_from_xml(policies_data)
    policies_label.config(text=f"Computer Policies: {policies_count}")

    # Profiles (Computers)
    profiles_data = make_classic_api_request('JSSResource/osxconfigurationprofiles')
    profiles_count = get_size_from_xml(profiles_data)
    profiles_label.config(text=f"Computer Profiles: {profiles_count}")

    # Managed Mobile Devices
    mobile_devices_data = make_classic_api_request('JSSResource/mobiledevices')
    mobile_devices_count = get_size_from_xml(mobile_devices_data)
    mobile_devices_label.config(text=f"Managed Mobile Devices: {mobile_devices_count}")

    # Smart Mobile Device Groups
    smart_mobile_groups_data = make_classic_api_request('JSSResource/mobiledevicegroups')
    smart_mobile_groups_count = get_size_from_xml(smart_mobile_groups_data)
    smart_mobile_groups_label.config(text=f"Smart Mobile Device Groups: {smart_mobile_groups_count}")

    # Static Mobile Device Groups
    static_mobile_groups_data = make_classic_api_request('JSSResource/mobiledevicegroups')
    static_mobile_groups_count = get_size_from_xml(static_mobile_groups_data)
    static_mobile_groups_label.config(text=f"Static Mobile Device Groups: {static_mobile_groups_count}")

    # Profiles (Mobile Devices)
    mobile_profiles_data = make_classic_api_request('JSSResource/mobiledeviceconfigurationprofiles')
    mobile_profiles_count = get_size_from_xml(mobile_profiles_data)
    mobile_profiles_label.config(text=f"Mobile Device Profiles: {mobile_profiles_count}")

# Function to fetch computer groups using the Classic API
def fetch_computer_groups():
    computer_groups_data = make_classic_api_request('JSSResource/computergroups')
    if computer_groups_data:
        display_computer_groups(computer_groups_data)

# Function to fetch mobile device groups using the Classic API
def fetch_mobile_device_groups():
    mobile_groups_data = make_classic_api_request('JSSResource/mobiledevicegroups')
    if mobile_groups_data:
        display_mobile_device_groups(mobile_groups_data)

# Function to display computer groups in the tab
def display_computer_groups(xml_data):
    tree_computers.delete(*tree_computers.get_children())  # Clear the tree
    root = ET.fromstring(xml_data)
    for group in root.findall("computer_group"):
        group_name = group.find("name").text
        smart_group = group.find("is_smart").text
        group_type = "Smart" if smart_group == "true" else "Static"
        tree_computers.insert("", "end", values=(group_name, group_type))

# Function to display mobile device groups in the tab
def display_mobile_device_groups(xml_data):
    tree_devices.delete(*tree_devices.get_children())  # Clear the tree
    root = ET.fromstring(xml_data)
    for group in root.findall("mobile_device_group"):
        group_name = group.find("name").text
        smart_group = group.find("is_smart").text
        group_type = "Smart" if smart_group == "true" else "Static"
        tree_devices.insert("", "end", values=(group_name, group_type))

# Creating the GUI window
root = Tk()
root.title("JamfCommander")

# Resizing the window
root.geometry('1200x600')

# Tabs for Dashboard, Computers, and Devices
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill='both', padx=10, pady=60)

# Dashboard Tab
tab_dashboard = Frame(tab_control)
tab_control.add(tab_dashboard, text="Dashboard")

# Tab for Computers
tab_computers = Frame(tab_control)
tab_control.add(tab_computers, text="Computers")

# Tab for Devices
tab_devices = Frame(tab_control)
tab_control.add(tab_devices, text="Devices")

# Jamf Pro URL input
Label(root, text="Jamf Pro URL").place(x=20, y=20)
entry_url = Entry(root, width=80)
entry_url.place(x=150, y=20)

# Login button
Button(root, text="Login", command=authenticate).place(x=900, y=16)

# Status label to display "AUTHENTICATED" or "AUTH FAILED"
status_label = Label(root, text="", font=("Arial", 12))
status_label.place(x=980, y=16)

# Treeview for displaying the computer groups
tree_computers = ttk.Treeview(tab_computers, columns=("Group Name", "Group Type"), show="headings")
tree_computers.heading("Group Name", text="Group Name")
tree_computers.heading("Group Type", text="Group Type")
tree_computers.pack(fill="both", expand=True)

# Treeview for displaying the mobile device groups
tree_devices = ttk.Treeview(tab_devices, columns=("Group Name", "Group Type"), show="headings")
tree_devices.heading("Group Name", text="Group Name")
tree_devices.heading("Group Type", text="Group Type")
tree_devices.pack(fill="both", expand=True)

# Adding Labels to Display Dashboard Data, aligned to the left
version_label = Label(tab_dashboard, text="Jamf Pro Version: N/A", font=("Arial", 14), anchor="w")
version_label.pack(pady=10, anchor="w")

computers_label = Label(tab_dashboard, text="Managed Computers: N/A", font=("Arial", 14), anchor="w")
computers_label.pack(pady=10, anchor="w")

smart_computer_groups_label = Label(tab_dashboard, text="Smart Computer Groups: N/A", font=("Arial", 14), anchor="w")
smart_computer_groups_label.pack(pady=10, anchor="w")

static_computer_groups_label = Label(tab_dashboard, text="Static Computer Groups: N/A", font=("Arial", 14), anchor="w")
static_computer_groups_label.pack(pady=10, anchor="w")

policies_label = Label(tab_dashboard, text="Computer Policies: N/A", font=("Arial", 14), anchor="w")
policies_label.pack(pady=10, anchor="w")

profiles_label = Label(tab_dashboard, text="Computer Profiles: N/A", font=("Arial", 14), anchor="w")
profiles_label.pack(pady=10, anchor="w")

mobile_devices_label = Label(tab_dashboard, text="Managed Mobile Devices: N/A", font=("Arial", 14), anchor="w")
mobile_devices_label.pack(pady=10, anchor="w")

smart_mobile_groups_label = Label(tab_dashboard, text="Smart Mobile Device Groups: N/A", font=("Arial", 14), anchor="w")
smart_mobile_groups_label.pack(pady=10, anchor="w")

static_mobile_groups_label = Label(tab_dashboard, text="Static Mobile Device Groups: N/A", font=("Arial", 14), anchor="w")
static_mobile_groups_label.pack(pady=10, anchor="w")

mobile_profiles_label = Label(tab_dashboard, text="Mobile Device Profiles: N/A", font=("Arial", 14), anchor="w")
mobile_profiles_label.pack(pady=10, anchor="w")

# Buttons to fetch computer and mobile device groups
Button(tab_computers, text="Fetch Computer Groups", command=fetch_computer_groups).pack(pady=10)
Button(tab_devices, text="Fetch Mobile Device Groups", command=fetch_mobile_device_groups).pack(pady=10)

# Loading the saved URL from the environment variable (if it exists)
saved_url = os.getenv("JAMF_PRO_URL", "")
if saved_url:
    entry_url.insert(0, saved_url)

root.mainloop()