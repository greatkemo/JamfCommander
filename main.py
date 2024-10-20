import os
import subprocess
import logging
from tkinter import Tk
from src.auth import authenticate
from src.utils import load_env_variables, save_url_to_env, get_size_from_xml, load_token
from src.gui.gui import setup_gui
from src.gui.data_fetching import fetch_computer_groups, fetch_mobile_device_groups, fetch_jamf_pro_version, fetch_computer_info, fetch_mobile_device_info, make_classic_api_request
from src.gui.event_handlers import authenticate_callback, on_computer_member_click, on_device_member_click, display_general_info

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

# Create a global variable to store the URL
global_jamf_url = None  # Global variable for storing the authenticated Jamf Pro URL

# Load environment variables from the .env file
load_env_variables()

# Function to clone or update the GitHub repository
def clone_or_update_repo():
    repo_url = "https://github.com/apple/device-management.git"
    repo_dir = os.path.join("tmp", "device-management")

    if not os.path.exists(repo_dir):
        logging.info(f"Cloning repository from {repo_url} to {repo_dir}")
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    else:
        logging.info(f"Updating repository in {repo_dir}")
        subprocess.run(["git", "-C", repo_dir, "pull"], check=True)

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

# Initialize the Tkinter root window
root = Tk()

# Set up the GUI and get references to the key UI elements
entry_url, status_label, version_value, smart_computer_groups_value, static_computer_groups_value, \
computer_policies_value, computer_profiles_value, smart_mobile_groups_value, \
static_mobile_groups_value, mobile_profiles_value, managed_computers_value, \
managed_mobile_devices_value, tree_computers, tree_devices, tree_computer_members, tree_device_members, \
general_info_text_computers, general_info_text_devices = setup_gui(
    root, 
    lambda url: authenticate_callback(
        url, status_label, update_dashboard, clone_or_update_repo, 
        tree_computers, tree_devices, smart_computer_groups_value, static_computer_groups_value, 
        smart_mobile_groups_value, static_mobile_groups_value
    )
)

# Bind the click events to the tree views
tree_computer_members.bind("<ButtonRelease-1>", lambda event: on_computer_member_click(event, tree_computer_members, general_info_text_computers))
tree_device_members.bind("<ButtonRelease-1>", lambda event: on_device_member_click(event, tree_device_members, general_info_text_devices))

# Load the URL from the environment variable and pre-fill the entry field if available
saved_url = os.getenv("JAMF_PRO_URL", "")
if saved_url:
    entry_url.insert(0, saved_url)

# Start the GUI event loop
root.mainloop()