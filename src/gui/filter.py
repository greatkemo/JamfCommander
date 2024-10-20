import tkinter as tk
from tkinter import ttk

def create_filter_section(parent, search_callback):
    # Create a frame for the filter section
    filter_frame = tk.Frame(parent)
    filter_frame.pack(fill='x', padx=10, pady=5)

    # Dropdown menu for selecting filter type
    tk.Label(filter_frame, text="Filter by:", font=("Arial", 12)).pack(side='left', padx=5)
    filter_var = tk.StringVar()
    filter_dropdown = ttk.Combobox(filter_frame, textvariable=filter_var, values=["Computers", "Devices", "Groups"], state="readonly")
    filter_dropdown.pack(side='left', padx=5)

    # Search box
    search_var = tk.StringVar()
    search_entry = tk.Entry(filter_frame, textvariable=search_var, width=30)
    search_entry.pack(side='left', padx=5)

    # Search button
    search_button = tk.Button(filter_frame, text="Search", command=lambda: search_callback(filter_var.get(), search_var.get()))
    search_button.pack(side='left', padx=5)

    return filter_var, search_var