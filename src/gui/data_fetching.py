import os
import requests
import logging
import xml.etree.ElementTree as ET

from src.api import parse_computer_info, parse_mobile_device_info
from src.utils import load_token

def make_classic_api_request(jamf_url, endpoint, token):
    try:
        headers = {"Accept": "application/xml", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/{endpoint}", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making API request to {endpoint}: {e}")
        return None

def fetch_computer_groups(jamf_url, token):
    endpoint = "JSSResource/computergroups"
    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        root = ET.fromstring(response)
        groups = []
        for group in root.findall(".//computer_group"):
            groups.append({
                "name": group.find("name").text,
                "type": group.find("is_smart").text,
                "id": group.find("id").text
            })
        return {"groups": groups}
    return None

def fetch_mobile_device_groups(jamf_url, token):
    endpoint = "JSSResource/mobiledevicegroups"
    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        root = ET.fromstring(response)
        groups = []
        for group in root.findall(".//mobile_device_group"):
            groups.append({
                "name": group.find("name").text,
                "type": group.find("is_smart").text,
                "id": group.find("id").text
            })
        return {"groups": groups}
    return None

def fetch_computer_info(jamf_url, computer_id, token):
    endpoint = f"JSSResource/computers/id/{computer_id}"
    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        return response
    return None

def fetch_mobile_device_info(jamf_url, device_id, token):
    endpoint = f"JSSResource/mobiledevices/id/{device_id}"
    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        return response
    return None

def fetch_jamf_pro_version(jamf_url, token):
    try:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.get(f"{jamf_url}/JSSResource/jssuser", headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("version")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Jamf Pro version: {e}")
        return None

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