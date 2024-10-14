import requests
import logging
from src.utils import make_classic_api_request, save_to_cache

def make_classic_api_request(jamf_url, endpoint, token):
    try:
        headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/{endpoint}", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making Classic API request to {endpoint}: {e}")
        return None

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

# Function to fetch mobile device groups using the Classic API
def fetch_mobile_device_groups(jamf_url, tree_devices, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/mobiledevicegroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        mobile_groups = response.json()

        logging.debug(f"Fetched mobile device groups: {mobile_groups}")

        # Clear the tree view
        for item in tree_devices.get_children():
            tree_devices.delete(item)

        smart_count = 0
        static_count = 0

        for group in mobile_groups['mobile_device_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            group_id = group['id']
            tree_devices.insert("", "end", values=(group_name, group_type, group_id))

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {
            "smart_count": smart_count,
            "static_count": static_count
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching mobile device groups: {e}")
        return None

# Function to fetch computer groups using the Classic API
def fetch_computer_groups(jamf_url, tree_computers, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/computergroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        computer_groups = response.json()

        logging.debug(f"Fetched computer groups: {computer_groups}")

        # Clear the tree view
        for item in tree_computers.get_children():
            tree_computers.delete(item)

        smart_count = 0
        static_count = 0

        for group in computer_groups['computer_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            group_id = group['id']
            tree_computers.insert("", "end", values=(group_name, group_type, group_id))

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {
            "smart_count": smart_count,
            "static_count": static_count
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching computer groups: {e}")
        return None

# Function to fetch general information of a computer or device
def fetch_general_info(jamf_url, item_id, item_type, token):
    endpoint = f"JSSResource/{item_type}/id/{item_id}"
    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        # Cache the response
        cache_filename = f"{item_type}_{item_id}_general.xml"
        save_to_cache(cache_filename, response)
        return response
    return None