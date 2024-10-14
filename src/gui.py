from tkinter import *
from tkinter import ttk

def setup_gui(root, authenticate_callback):
    root.title("JamfCommander")
    root.geometry('1200x600')

    # Tabs for Dashboard, Computers, and Devices
    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill='both', padx=10, pady=60)

    # Dashboard Tab
    tab_dashboard = Frame(tab_control)
    tab_control.add(tab_dashboard, text="Dashboard")

    # Tab for Computers
    tab_computers = Frame(tab_control)
    tab_control.add(tab_computers, text="Computers")

    # Tab for Devices
    tab_devices = Frame(tab_control)
    tab_control.add(tab_devices, text="Devices")

    # Jamf Pro URL input
    Label(root, text="Jamf Pro URL").place(x=20, y=20)
    entry_url = Entry(root, width=80)
    entry_url.place(x=150, y=20)

    # Login button
    Button(root, text="Login", command=lambda: authenticate_callback(entry_url.get())).place(x=900, y=16)

    # Status label to display "AUTHENTICATED" or "AUTH FAILED"
    status_label = Label(root, text="", font=("Arial", 12))
    status_label.place(x=980, y=16)

    # Create a grid layout for the dashboard
    Label(tab_dashboard, text="Jamf Pro Version:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    version_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    version_value.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Managed Computers:", font=("Arial", 14, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
    managed_computers_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    managed_computers_value.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Smart Computer Groups:", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=5)
    smart_computer_groups_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    smart_computer_groups_value.grid(row=2, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Static Computer Groups:", font=("Arial", 14, "bold")).grid(row=3, column=0, sticky="w", padx=10, pady=5)
    static_computer_groups_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    static_computer_groups_value.grid(row=3, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Computer Policies:", font=("Arial", 14, "bold")).grid(row=4, column=0, sticky="w", padx=10, pady=5)
    computer_policies_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    computer_policies_value.grid(row=4, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Computer Profiles:", font=("Arial", 14, "bold")).grid(row=5, column=0, sticky="w", padx=10, pady=5)
    computer_profiles_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    computer_profiles_value.grid(row=5, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Managed Mobile Devices:", font=("Arial", 14, "bold")).grid(row=6, column=0, sticky="w", padx=10, pady=5)
    managed_mobile_devices_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    managed_mobile_devices_value.grid(row=6, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Smart Mobile Device Groups:", font=("Arial", 14, "bold")).grid(row=7, column=0, sticky="w", padx=10, pady=5)
    smart_mobile_groups_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    smart_mobile_groups_value.grid(row=7, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Static Mobile Device Groups:", font=("Arial", 14, "bold")).grid(row=8, column=0, sticky="w", padx=10, pady=5)
    static_mobile_groups_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    static_mobile_groups_value.grid(row=8, column=1, sticky="w", padx=10, pady=5)

    Label(tab_dashboard, text="Mobile Device Profiles:", font=("Arial", 14, "bold")).grid(row=9, column=0, sticky="w", padx=10, pady=5)
    mobile_profiles_value = Label(tab_dashboard, text="N/A", font=("Arial", 14))
    mobile_profiles_value.grid(row=9, column=1, sticky="w", padx=10, pady=5)

    # Treeview for displaying the computer groups
    tree_computers = ttk.Treeview(tab_computers, columns=("Group Name", "Group Type"), show="headings")
    tree_computers.heading("Group Name", text="Group Name")
    tree_computers.heading("Group Type", text="Group Type")
    tree_computers.pack(fill="both", expand=True)

    # Treeview for displaying the mobile device groups
    tree_devices = ttk.Treeview(tab_devices, columns=("Group Name", "Group Type"), show="headings")
    tree_devices.heading("Group Name", text="Group Name")
    tree_devices.heading("Group Type", text="Group Type")
    tree_devices.pack(fill="both", expand=True)

    # Return all necessary elements
    return (entry_url, status_label, version_value, smart_computer_groups_value, static_computer_groups_value, 
            computer_policies_value, computer_profiles_value, smart_mobile_groups_value, 
            static_mobile_groups_value, mobile_profiles_value, managed_computers_value, 
            managed_mobile_devices_value, tree_computers, tree_devices)