import tkinter as tk
from tkinter import ttk
import logging
import os
from src.utils import load_token, make_classic_api_request, save_to_cache
from src.api import fetch_general_info, parse_computer_info, parse_mobile_device_info
import xml.etree.ElementTree as ET

def setup_gui(root, authenticate_callback):
    root.title("Jamf Commander")
    root.geometry("1200x800")

    # Create a frame for the URL input, Login button, and status message
    top_frame = tk.Frame(root)
    top_frame.pack(pady=20)

    # URL Entry
    tk.Label(top_frame, text="Jamf Pro URL:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
    entry_url = tk.Entry(top_frame, width=50)
    entry_url.grid(row=0, column=1, padx=5)

    # Login Button
    tk.Button(top_frame, text="Login", command=lambda: authenticate_callback(entry_url.get())).grid(row=0, column=2, padx=5)

    # Status Label
    status_label = tk.Label(top_frame, text="NOT AUTHENTICATED", fg="red", font=("Arial", 12, "bold"))
    status_label.grid(row=0, column=3, padx=5)

    # Create a notebook (tabbed layout)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', pady=20)

    # Create tabs
    tab_dashboard = ttk.Frame(notebook)
    tab_computers = ttk.Frame(notebook)
    tab_devices = ttk.Frame(notebook)
    notebook.add(tab_dashboard, text='Dashboard')
    notebook.add(tab_computers, text='Computers')
    notebook.add(tab_devices, text='Devices')

    # Version Label
    tk.Label(tab_dashboard, text="Jamf Pro Version:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    version_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    version_value.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Managed Computers:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    managed_computers_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    managed_computers_value.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Smart Computer Groups:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    smart_computer_groups_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    smart_computer_groups_value.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Static Computer Groups:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    static_computer_groups_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    static_computer_groups_value.grid(row=3, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Computer Policies:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    computer_policies_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    computer_policies_value.grid(row=4, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Computer Profiles:", font=("Arial", 12, "bold")).grid(row=5, column=0, sticky="w", padx=10, pady=5)
    computer_profiles_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    computer_profiles_value.grid(row=5, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Managed Mobile Devices:", font=("Arial", 12, "bold")).grid(row=6, column=0, sticky="w", padx=10, pady=5)
    managed_mobile_devices_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    managed_mobile_devices_value.grid(row=6, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Smart Mobile Device Groups:", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky="w", padx=10, pady=5)
    smart_mobile_groups_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    smart_mobile_groups_value.grid(row=7, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Static Mobile Device Groups:", font=("Arial", 12, "bold")).grid(row=8, column=0, sticky="w", padx=10, pady=5)
    static_mobile_groups_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    static_mobile_groups_value.grid(row=8, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_dashboard, text="Mobile Device Profiles:", font=("Arial", 12, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=5)
    mobile_profiles_value = tk.Label(tab_dashboard, text="N/A", font=("Arial", 12))
    mobile_profiles_value.grid(row=9, column=1, sticky="w", padx=10, pady=5)

    # Create frames for computer groups and members
    computer_groups_frame = tk.Frame(tab_computers)
    computer_groups_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    computer_members_frame = tk.Frame(tab_computers)
    computer_members_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Create frames for device groups and members
    device_groups_frame = tk.Frame(tab_devices)
    device_groups_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    device_members_frame = tk.Frame(tab_devices)
    device_members_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Computer Groups Treeview
    tree_computers = ttk.Treeview(computer_groups_frame, columns=("group_name", "group_type", "group_id"), show="headings")
    tree_computers.heading("group_name", text="Group Name")
    tree_computers.heading("group_type", text="Group Type")
    tree_computers.heading("group_id", text="Group ID")
    tree_computers.column("group_name", width=200)
    tree_computers.column("group_type", width=100)
    tree_computers.column("group_id", width=100)
    tree_computers.pack(fill="both", expand=True)
    
    # Mobile Device Groups Treeview
    tree_devices = ttk.Treeview(device_groups_frame, columns=("group_name", "group_type", "group_id"), show="headings")
    tree_devices.heading("group_name", text="Group Name")
    tree_devices.heading("group_type", text="Group Type")
    tree_devices.heading("group_id", text="Group ID")
    tree_devices.column("group_name", width=200)
    tree_devices.column("group_type", width=100)
    tree_devices.column("group_id", width=100)
    tree_devices.pack(fill="both", expand=True)
    
    # Computer Members Treeview
    tree_computer_members = ttk.Treeview(computer_members_frame, columns=("member_name", "member_id"), show="headings")
    tree_computer_members.heading("member_name", text="Member Name")
    tree_computer_members.heading("member_id", text="Member ID")
    tree_computer_members.column("member_name", width=150)
    tree_computer_members.column("member_id", width=100)
    tree_computer_members.pack(fill="both", expand=True)
    
    # Device Members Treeview
    tree_device_members = ttk.Treeview(device_members_frame, columns=("member_name", "member_id"), show="headings")
    tree_device_members.heading("member_name", text="Member Name")
    tree_device_members.heading("member_id", text="Member ID")
    tree_device_members.column("member_name", width=150)
    tree_device_members.column("member_id", width=100)
    tree_device_members.pack(fill="both", expand=True)

    # General Information Frame for Computers
    general_info_frame_computers = ttk.LabelFrame(tab_computers, text="Computer Information")
    general_info_frame_computers.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    # General Information Textbox for Computers
    general_info_text_computers = tk.Text(general_info_frame_computers, wrap="word", height=10)
    general_info_text_computers.pack(fill="both", expand=True)

    # General Information Frame for Devices
    general_info_frame_devices = ttk.LabelFrame(tab_devices, text="Device Information")
    general_info_frame_devices.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    # General Information Textbox for Devices
    general_info_text_devices = tk.Text(general_info_frame_devices, wrap="word", height=10)
    general_info_text_devices.pack(fill="both", expand=True)

    # Add click event handlers to the group names
    def on_computer_group_click(event):
        selected_item = tree_computers.selection()[0]
        group_id = tree_computers.item(selected_item, "values")[2]  # Assuming the group ID is in the third column
        fetch_and_display_group_members(group_id, "computers", tree_computer_members)
    
    def on_device_group_click(event):
        selected_item = tree_devices.selection()[0]
        group_id = tree_devices.item(selected_item, "values")[2]  # Assuming the group ID is in the third column
        fetch_and_display_group_members(group_id, "devices", tree_device_members)

    def display_general_info(info, text_widget):
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, info)
    
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
    
        general_info = fetch_general_info(jamf_url, member_id, "computers", token)
        if general_info:
            formatted_info = parse_computer_info(general_info)
            display_general_info(formatted_info, general_info_text_computers)
    
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
    
        general_info = fetch_general_info(jamf_url, member_id, "mobiledevices", token)
        if general_info:
            formatted_info = parse_mobile_device_info(general_info)
            display_general_info(formatted_info, general_info_text_devices)

    tree_computers.bind("<Double-1>", on_computer_group_click)
    tree_devices.bind("<Double-1>", on_device_group_click)
    tree_computer_members.bind("<ButtonRelease-1>", on_computer_member_click)
    tree_device_members.bind("<ButtonRelease-1>", on_device_member_click)

    return (entry_url, status_label, version_value, smart_computer_groups_value, static_computer_groups_value,
            computer_policies_value, computer_profiles_value, smart_mobile_groups_value,
            static_mobile_groups_value, mobile_profiles_value, managed_computers_value,
            managed_mobile_devices_value, tree_computers, tree_devices, tree_computer_members, tree_device_members, 
            general_info_text_computers, general_info_text_devices)

def fetch_and_display_group_members(group_id, group_type, tree_members):
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

def fetch_general_info(jamf_url, member_id, member_type, token):
    if member_type == "computers":
        endpoint = f"JSSResource/computers/id/{member_id}"
    else:
        endpoint = f"JSSResource/mobiledevices/id/{member_id}"

    response = make_classic_api_request(jamf_url, endpoint, token)
    if response:
        # Parse the XML response to extract general information
        root = ET.fromstring(response)
        general_info = ET.tostring(root, encoding='unicode', method='text')
        return general_info
    return None