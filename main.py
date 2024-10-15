import os
import subprocess
import logging
import tkinter as tk
from tkinter import Tk
from src.auth import authenticate
from src.api import fetch_computer_groups, fetch_mobile_device_groups, fetch_jamf_pro_version, fetch_computer_info, fetch_mobile_device_info, parse_computer_info, parse_mobile_device_info, make_classic_api_request
from src.gui import setup_gui
from src.utils import load_env_variables, save_url_to_env, get_size_from_xml, load_token

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

        # Clone or update the GitHub repository
        clone_or_update_repo()

        # Fetch computer groups
        computer_groups = fetch_computer_groups(global_jamf_url, token)
        if computer_groups:
            for group in computer_groups['groups']:
                tree_computers.insert("", "end", values=(group['name'], group['type'], group['id']))
            smart_computer_groups_value.config(text=f"{computer_groups['smart_count']}")
            static_computer_groups_value.config(text=f"{computer_groups['static_count']}")
        else:
            smart_computer_groups_value.config(text="N/A")
            static_computer_groups_value.config(text="N/A")

        # Fetch mobile device groups
        mobile_groups = fetch_mobile_device_groups(global_jamf_url, token)
        if mobile_groups:
            for group in mobile_groups['groups']:
                tree_devices.insert("", "end", values=(group['name'], group['type'], group['id']))
            smart_mobile_groups_value.config(text=f"{mobile_groups['smart_count']}")
            static_mobile_groups_value.config(text=f"{mobile_groups['static_count']}")
        else:
            smart_mobile_groups_value.config(text="N/A")
            static_mobile_groups_value.config(text="N/A")
    else:
        status_label.config(text="AUTH FAILED", fg="red")

# Function to display general information in the text widget
def display_general_info(info, text_widget):
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, info)

# Function to handle computer member click event
def on_computer_member_click(event):
    selected_item = tree_computer_members.selection()[0]
    member_id = tree_computer_members.item(selected_item, "values")[1]  # Assuming the member ID is in the second column
    token = load_token()
    if not token:
        logging.error("No token found!")
        return

    jamf_url = os.getenv("JAMF_PRO_URL", "")
    if not jamf_url:
        logging.error("No Jamf URL found!")
        return

    general_info = fetch_computer_info(jamf_url, member_id, token)
    if general_info:
        formatted_info = parse_computer_info(general_info)
        display_general_info(formatted_info, general_info_text_computers)

# Function to handle device member click event
def on_device_member_click(event):
    selected_item = tree_device_members.selection()[0]
    member_id = tree_device_members.item(selected_item, "values")[1]  # Assuming the member ID is in the second column
    token = load_token()
    if not token:
        logging.error("No token found!")
        return

    jamf_url = os.getenv("JAMF_PRO_URL", "")
    if not jamf_url:
        logging.error("No Jamf URL found!")
        return

    general_info = fetch_mobile_device_info(jamf_url, member_id, token)
    if general_info:
        formatted_info = parse_mobile_device_info(general_info)
        display_general_info(formatted_info, general_info_text_devices)

# Initialize the Tkinter root window
root = Tk()

# Set up the GUI and get references to the key UI elements
entry_url, status_label, version_value, smart_computer_groups_value, static_computer_groups_value, \
computer_policies_value, computer_profiles_value, smart_mobile_groups_value, \
static_mobile_groups_value, mobile_profiles_value, managed_computers_value, \
managed_mobile_devices_value, tree_computers, tree_devices, tree_computer_members, tree_device_members, \
general_info_text_computers, general_info_text_devices = setup_gui(
    root, 
    authenticate_callback  # Correctly pass the authenticate callback here
)

# Bind the click events to the tree views
tree_computer_members.bind("<ButtonRelease-1>", on_computer_member_click)
tree_device_members.bind("<ButtonRelease-1>", on_device_member_click)

# Load the URL from the environment variable and pre-fill the entry field if available
saved_url = os.getenv("JAMF_PRO_URL", "")
if saved_url:
    entry_url.insert(0, saved_url)

# Start the GUI event loop
root.mainloop()