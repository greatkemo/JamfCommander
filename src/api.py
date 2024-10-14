import xml.etree.ElementTree as ET
from src.utils import make_classic_api_request, make_api_request
import requests, logging

# Function to fetch the Jamf Pro version using the Jamf Pro API
def fetch_jamf_pro_version(jamf_url, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/api/v1/jamf-pro-version", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        version_data = response.json()
        return version_data.get('version', 'N/A')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Jamf Pro version: {e}")
        return None

# Function to fetch computer groups using the Classic API
def fetch_computer_groups(jamf_url, tree_computers, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/computergroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        computer_groups = response.json()

        # Clear the tree view
        for item in tree_computers.get_children():
            tree_computers.delete(item)

        smart_count = 0
        static_count = 0

        for group in computer_groups['computer_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            tree_computers.insert("", "end", values=(group_name, group_type))

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {"smart_count": smart_count, "static_count": static_count}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching computer groups: {e}")
        return None

# Function to fetch mobile device groups using the Classic API
def fetch_mobile_device_groups(jamf_url, tree_devices, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/mobiledevicegroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        mobile_groups = response.json()

        # Clear the tree view
        for item in tree_devices.get_children():
            tree_devices.delete(item)

        smart_count = 0
        static_count = 0

        for group in mobile_groups['mobile_device_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            tree_devices.insert("", "end", values=(group_name, group_type))

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {"smart_count": smart_count, "static_count": static_count}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching mobile device groups: {e}")
        return None