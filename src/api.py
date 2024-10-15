import requests
import logging
import xml.etree.ElementTree as ET
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
def fetch_mobile_device_groups(jamf_url, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/mobiledevicegroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        mobile_groups = response.json()

        logging.debug(f"Fetched mobile device groups: {mobile_groups}")

        groups = []
        smart_count = 0
        static_count = 0

        for group in mobile_groups['mobile_device_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            group_id = group['id']
            groups.append({
                'name': group_name,
                'type': group_type,
                'id': group_id
            })

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {
            "groups": groups,
            "smart_count": smart_count,
            "static_count": static_count
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching mobile device groups: {e}")
        return None

# Function to fetch computer groups using the Classic API
def fetch_computer_groups(jamf_url, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/computergroups", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        computer_groups = response.json()

        logging.debug(f"Fetched computer groups: {computer_groups}")

        groups = []
        smart_count = 0
        static_count = 0

        for group in computer_groups['computer_groups']:
            group_name = group['name']
            group_type = "Smart" if group['is_smart'] else "Static"
            group_id = group['id']
            groups.append({
                'name': group_name,
                'type': group_type,
                'id': group_id
            })

            if group['is_smart']:
                smart_count += 1
            else:
                static_count += 1

        return {
            "groups": groups,
            "smart_count": smart_count,
            "static_count": static_count
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching computer groups: {e}")
        return None

# Function to fetch detailed information for a computer
def fetch_computer_info(jamf_url, computer_id, token):
    try:
        headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/computers/id/{computer_id}", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching computer info: {e}")
        return None

# Function to fetch detailed information for a mobile device
def fetch_mobile_device_info(jamf_url, device_id, token):
    try:
        headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/mobiledevices/id/{device_id}", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching mobile device info: {e}")
        return None

# Function to parse and format computer information
def parse_computer_info(xml_data):
    root = ET.fromstring(xml_data)
    computer_info = {
        "Computer Name": root.findtext(".//name"),
        "Model": root.findtext(".//model"),
        "Model Identifier": root.findtext(".//model_identifier"),
        "Architecture Type": root.findtext(".//processor_architecture"),
        "Serial Number": root.findtext(".//serial_number"),
        "Primary MAC Address": root.findtext(".//mac_address"),
        "IP Address": root.findtext(".//ip_address"),
        "OS Version": root.findtext(".//os_version"),
        "OS Build": root.findtext(".//os_build"),
        "Jamf Pro Computer ID": root.findtext(".//id"),
        "Last Inventory Update": root.findtext(".//report_date_utc"),
        "Managed": root.findtext(".//managed"),
        "Supervised": root.findtext(".//supervised")
    }
    formatted_info = "\n".join([f"{key}: {value}" for key, value in computer_info.items() if value])
    return formatted_info

# Function to parse and format mobile device information
def parse_mobile_device_info(xml_data):
    root = ET.fromstring(xml_data)
    device_info = {
        "Mobile Device Name": root.findtext(".//name"),
        "Model": root.findtext(".//model"),
        "Model Identifier": root.findtext(".//model_identifier"),
        "Model Number": root.findtext(".//model_number"),
        "Serial Number": root.findtext(".//serial_number"),
        "Wi-Fi MAC Address": root.findtext(".//wifi_mac_address"),
        "IP Address": root.findtext(".//ip_address"),
        "OS Version": root.findtext(".//os_version"),
        "OS Build": root.findtext(".//os_build"),
        "Jamf Pro Mobile Device ID": root.findtext(".//id"),
        "Last Inventory Update": root.findtext(".//last_inventory_update_utc"),
        "Managed": root.findtext(".//managed"),
        "Supervised": root.findtext(".//supervised")
    }
    formatted_info = "\n".join([f"{key}: {value}" for key, value in device_info.items() if value])
    return formatted_info

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

# Function to fetch and display group members
def fetch_and_display_group_members(jamf_url, group_id, group_type, token):
    if group_type == "computers":
        endpoint = f"JSSResource/computergroups/id/{group_id}"
    else:
        endpoint = f"JSSResource/mobiledevicegroups/id/{group_id}"

    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        members = parse_group_members(response)
        return members
    return None

# Function to parse group members from XML data
def parse_group_members(xml_data):
    root = ET.fromstring(xml_data)
    members = []
    for computer in root.findall(".//computer"):
        members.append((computer.find("name").text, computer.find("id").text))
    for device in root.findall(".//mobile_device"):
        members.append((device.find("name").text, device.find("id").text))
    return members

# Function to display group members in a treeview
def display_group_members(members, tree_members):
    # Clear the existing items in the treeview
    for item in tree_members.get_children():
        tree_members.delete(item)
    # Add the new members to the treeview
    for member in members:
        tree_members.insert("", "end", values=member)