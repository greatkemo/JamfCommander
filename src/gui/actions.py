import os
import yaml
import tkinter as tk
from tkinter import ttk

def create_actions_section(tab, directory):
    # Create a notebook (tabbed layout) for Actions
    actions_notebook = ttk.Notebook(tab)
    actions_notebook.pack(expand=True, fill='both', pady=10)

    # Create Commands tab for Actions
    tab_commands = ttk.Frame(actions_notebook)
    actions_notebook.add(tab_commands, text='Commands')

    # Load YAML files and create dynamic form
    load_yaml_and_create_form(tab_commands, directory)

def load_yaml_and_create_form(tab, directory):
    for widget in tab.winfo_children():
        widget.destroy()

    row = 0
    command_files = [f for f in os.listdir(directory) if f.endswith(".yaml")]
    if not command_files:
        tk.Label(tab, text="No commands available", font=("Arial", 12)).grid(row=row, column=0, padx=10, pady=5)
        return

    # Dropdown for command selection
    tk.Label(tab, text="Select Command:", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=10, pady=5)
    command_var = tk.StringVar()
    command_dropdown = ttk.Combobox(tab, textvariable=command_var, values=command_files, state="readonly")
    command_dropdown.grid(row=row, column=1, padx=10, pady=5, sticky="w")

    # Run button
    run_button = tk.Button(tab, text="Run", font=("Arial", 12))
    run_button.grid(row=row, column=2, padx=10, pady=5, sticky="e")

    row += 1

    # Frame for dynamic form
    form_frame = ttk.Frame(tab)
    form_frame.grid(row=row, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
    row += 1

    def on_command_select(event):
        selected_command = command_var.get()
        if selected_command:
            create_dynamic_form(form_frame, os.path.join(directory, selected_command))

    command_dropdown.bind("<<ComboboxSelected>>", on_command_select)

def create_dynamic_form(frame, yaml_file):
    for widget in frame.winfo_children():
        widget.destroy()

    with open(yaml_file, 'r') as file:
        command_data = yaml.safe_load(file)

    row = 0
    for key, value in command_data.items():
        if key not in ['title', 'description', 'payload', 'payloadkeys']:
            tk.Label(frame, text=f"{key}:", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            tk.Entry(frame, width=50).grid(row=row, column=1, padx=10, pady=5)
            row += 1

    # Display command description
    if 'description' in command_data:
        tk.Label(frame, text=command_data['description'], font=("Arial", 10, "italic")).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        row += 1

    # Display supported OSs
    if 'payload' in command_data and 'supportedOS' in command_data['payload']:
        supported_os_text = "Supported OSs: " + ", ".join([f"{os}: {details['introduced']}" for os, details in command_data['payload']['supportedOS'].items()])
        tk.Label(frame, text=supported_os_text, font=("Arial", 10, "italic")).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=5)