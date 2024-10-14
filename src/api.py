import json
import xml.etree.ElementTree as ET
from src.utils import make_classic_api_request, make_api_request

# Function to fetch the Jamf Pro version using the Jamf Pro API
def fetch_jamf_pro_version(jamf_url):
    version_data = make_api_request(jamf_url, 'api/v1/jamf-pro-version')
    if version_data and 'version' in version_data:
        return version_data['version']
    return None

# Function to fetch computer groups using the Classic API and correctly calculate Smart and Static groups
def fetch_computer_groups(jamf_url):
    computer_groups_data = make_classic_api_request(jamf_url, 'JSSResource/computergroups')
    if computer_groups_data:
        root = ET.fromstring(computer_groups_data)
        smart_count = 0
        static_count = 0
        for group in root.findall("computer_group"):
            is_smart = group.find("is_smart").text == "true"
            if is_smart:
                smart_count += 1
            else:
                static_count += 1
        return {"smart_count": smart_count, "static_count": static_count}
    return None

# Function to fetch mobile device groups using the Classic API
def fetch_mobile_device_groups(jamf_url):
    mobile_groups_data = make_classic_api_request(jamf_url, 'JSSResource/mobiledevicegroups')
    if mobile_groups_data:
        root = ET.fromstring(mobile_groups_data)
        smart_count = 0
        static_count = 0
        for group in root.findall("mobile_device_group"):
            is_smart = group.find("is_smart").text == "true"
            if is_smart:
                smart_count += 1
            else:
                static_count += 1
        return {"smart_count": smart_count, "static_count": static_count}
    return None