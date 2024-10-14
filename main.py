from tkinter import Tk
from src.auth import authenticate
from src.api import fetch_computer_groups, fetch_mobile_device_groups, fetch_jamf_pro_version, make_classic_api_request 
from src.gui import setup_gui
from src.utils import load_env_variables, save_url_to_env, get_size_from_xml, load_token_from_file, load_token
import os
import logging

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

# Create a global variable to store the URL
global_jamf_url = None  # Global variable for storing the authenticated Jamf Pro URL

# Load environment variables from the .env file
load_env_variables()

# Function to update the dashboard with relevant counts
def update_dashboard(token):
    global global_jamf_url

    if not global_jamf_url:
        logging.error("No Jamf URL available to fetch data.")
        return

    # Jamf Pro Version (JSON response)
    version = fetch_jamf_pro_version(global_jamf_url, token)
    if version:
        version_value.config(text=f"{version}")
    else:
        version_value.config(text="N/A")

    # Managed Computers (Classic API)
    computers_data = make_classic_api_request(global_jamf_url, 'JSSResource/computers', token)
    if computers_data:
        managed_computers_value.config(text=get_size_from_xml(computers_data))
    else:
        managed_computers_value.config(text="N/A")

    # Computer Policies (Classic API)
    policies_data = make_classic_api_request(global_jamf_url, 'JSSResource/policies', token)
    if policies_data:
        computer_policies_value.config(text=get_size_from_xml(policies_data))
    else:
        computer_policies_value.config(text="N/A")

    # Computer Profiles (Classic API)
    profiles_data = make_classic_api_request(global_jamf_url, 'JSSResource/osxconfigurationprofiles', token)
    if profiles_data:
        computer_profiles_value.config(text=get_size_from_xml(profiles_data))
    else:
        computer_profiles_value.config(text="N/A")

    # Managed Mobile Devices (Classic API)
    mobile_devices_data = make_classic_api_request(global_jamf_url, 'JSSResource/mobiledevices', token)
    if mobile_devices_data:
        managed_mobile_devices_value.config(text=get_size_from_xml(mobile_devices_data))
    else:
        managed_mobile_devices_value.config(text="N/A")

    # Mobile Device Profiles (Classic API)
    mobile_profiles_data = make_classic_api_request(global_jamf_url, 'JSSResource/mobiledeviceconfigurationprofiles', token)
    if mobile_profiles_data:
        mobile_profiles_value.config(text=get_size_from_xml(mobile_profiles_data))
    else:
        mobile_profiles_value.config(text="N/A")

# Function to handle authentication and update the GUI accordingly
def authenticate_callback(jamf_url):
    global global_jamf_url

    # Ensure the URL has a scheme (https://)
    if not jamf_url.startswith("http://") and not jamf_url.startswith("https://"):
        jamf_url = f"https://{jamf_url}"

    logging.debug(f"Attempting to authenticate with URL: {jamf_url}")

    token = authenticate(jamf_url, status_label)  # Pass only jamf_url and status_label
    if token:
        status_label.config(text="AUTHENTICATED", fg="green")
        global_jamf_url = jamf_url  # Save the authenticated URL globally for future API calls
        save_url_to_env(jamf_url)   # Save the URL to .env after successful login
        update_dashboard(token)  # Call this function to update the dashboard after successful authentication

        # Fetch computer groups
        computer_groups = fetch_computer_groups(global_jamf_url, tree_computers, token)
        if computer_groups:
            smart_computer_groups_value.config(text=f"{computer_groups['smart_count']}")
            static_computer_groups_value.config(text=f"{computer_groups['static_count']}")
        else:
            smart_computer_groups_value.config(text="N/A")
            static_computer_groups_value.config(text="N/A")

        # Fetch mobile device groups
        mobile_groups = fetch_mobile_device_groups(global_jamf_url, tree_devices, token)
        if mobile_groups:
            smart_mobile_groups_value.config(text=f"{mobile_groups['smart_count']}")
            static_mobile_groups_value.config(text=f"{mobile_groups['static_count']}")
        else:
            smart_mobile_groups_value.config(text="N/A")
            static_mobile_groups_value.config(text="N/A")
    else:
        status_label.config(text="AUTH FAILED", fg="red")

# Initialize the Tkinter root window
root = Tk()

# Set up the GUI and get references to the key UI elements
entry_url, status_label, version_value, smart_computer_groups_value, static_computer_groups_value, \
computer_policies_value, computer_profiles_value, smart_mobile_groups_value, \
static_mobile_groups_value, mobile_profiles_value, managed_computers_value, \
managed_mobile_devices_value, tree_computers, tree_devices, tree_computer_members, \
tree_device_members, general_info_text = setup_gui(
    root, 
    authenticate_callback  # Correctly pass the authenticate callback here
)

# Load the URL from the environment variable and pre-fill the entry field if available
saved_url = os.getenv("JAMF_PRO_URL", "")
if saved_url:
    entry_url.insert(0, saved_url)

# Start the GUI event loop
root.mainloop()