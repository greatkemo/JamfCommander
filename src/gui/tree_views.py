import xml.etree.ElementTree as ET
import logging
import os

def fetch_and_display_group_members(group_id, group_type, tree_members, make_classic_api_request, load_token, save_to_cache):
    # Fetch the list of computers or devices in the selected group
    if group_type == "computers":
        endpoint = f"JSSResource/computergroups/id/{group_id}"
    else:
        endpoint = f"JSSResource/mobiledevicegroups/id/{group_id}"

    token = load_token()
    if not token:
        logging.error("No token found!")
        return

    jamf_url = os.getenv("JAMF_PRO_URL", "")
    if not jamf_url:
        logging.error("No Jamf URL found!")
        return

    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        # Parse the XML response and display the group members
        members = parse_group_members(response)
        display_group_members(members, tree_members)
        # Cache the response
        cache_filename = f"{group_type}_{group_id}.xml"
        save_to_cache(cache_filename, response)

def parse_group_members(xml_data):
    root = ET.fromstring(xml_data)
    members = []
    for computer in root.findall(".//computer"):
        members.append((computer.find("name").text, computer.find("id").text))
    for device in root.findall(".//mobile_device"):
        members.append((device.find("name").text, device.find("id").text))
    return members

def display_group_members(members, tree_members):
    # Clear the existing items in the treeview
    for item in tree_members.get_children():
        tree_members.delete(item)
    # Add the new members to the treeview
    for member in members:
        tree_members.insert("", "end", values=member)

def update_tree_view(tree_view, data):
    # Clear the existing items in the treeview
    for item in tree_view.get_children():
        tree_view.delete(item)

    # Insert the filtered data into the treeview
    for entry in data:
        tree_view.insert("", "end", values=(entry['name'], entry['type'], entry['id']))