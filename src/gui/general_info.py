import tkinter as tk
from tkinter import ttk

def create_general_info_frame(parent, title):
    frame = ttk.LabelFrame(parent, text=title)
    frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    text_widget = tk.Text(frame, wrap="word", height=10)
    text_widget.pack(fill="both", expand=True)
    return frame, text_widget

def display_general_info(info, text_widget):
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, info)