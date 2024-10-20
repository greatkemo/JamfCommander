import logging
import os
import tkinter as tk
from src.gui.data_fetching import fetch_computer_info, fetch_mobile_device_info, fetch_computer_groups, fetch_mobile_device_groups
from src.utils import save_url_to_env, load_token, make_classic_api_request
from src.auth import authenticate
from src.api import parse_computer_info, parse_mobile_device_info
from src.gui.tree_views import fetch_and_display_group_members  # Correct import

# Function to handle authentication and update the GUI accordingly
def authenticate_callback(jamf_url, status_label, update_dashboard, clone_or_update_repo, tree_computers, tree_devices, smart_computer_groups_value, static_computer_groups_value, smart_mobile_groups_value, static_mobile_groups_value):
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

# Function to handle computer group click event
def on_computer_group_click(event, tree_computers, tree_computer_members):
    selected_item = tree_computers.selection()[0]
    group_id = tree_computers.item(selected_item, "values")[2]  # Assuming the group ID is in the third column
    fetch_and_display_group_members(group_id, "computers", tree_computer_members)

# Function to handle device group click event
def on_device_group_click(event, tree_devices, tree_device_members):
    selected_item = tree_devices.selection()[0]
    group_id = tree_devices.item(selected_item, "values")[2]  # Assuming the group ID is in the third column
    fetch_and_display_group_members(group_id, "devices", tree_device_members)

# Function to handle computer member click event
def on_computer_member_click(event, tree_computer_members, general_info_text_computers):
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
def on_device_member_click(event, tree_device_members, general_info_text_devices):
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

# Function to display general information in the text widget
def display_general_info(info, text_widget):
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, info)

# Function to fetch general information for computers or devices
def fetch_general_info(member_id, member_type):
    token = load_token()
    if not token:
        logging.error("No token found!")
        return "No token found!"

    jamf_url = os.getenv("JAMF_PRO_URL", "")
    if not jamf_url:
        logging.error("No Jamf URL found!")
        return "No Jamf URL found!"

    if member_type == "computers":
        endpoint = f"JSSResource/computers/id/{member_id}"
        response = make_classic_api_request(jamf_url, endpoint, token)
        if response:
            return parse_computer_info(response)
    elif member_type == "devices":
        endpoint = f"JSSResource/mobiledevices/id/{member_id}"
        response = make_classic_api_request(jamf_url, endpoint, token)
        if response:
            return parse_mobile_device_info(response)

    return "No information found."