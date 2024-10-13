import requests
from tkinter import *
from tkinter import messagebox

# Function to authenticate with Jamf Pro API
def authenticate():
    url = entry_url.get() + "/JSSResource/computers"
    username = entry_username.get()
    password = entry_password.get()

    response = requests.get(url, auth=(username, password))

    if response.status_code == 200:
        messagebox.showinfo("Success", "Authenticated Successfully!")
    else:
        messagebox.showerror("Error", f"Failed to Authenticate: {response.status_code}")

# Creating the GUI window
root = Tk()
root.title("Jamf Commander")

# Setting the window size
root.geometry('400x200')

# URL input
frame_url = Frame(root)
frame_url.pack(pady=10)
Label(frame_url, text="Jamf Pro URL").pack(side=LEFT, padx=10)
entry_url = Entry(frame_url, width=30)
entry_url.pack(side=LEFT)

# Username input
frame_username = Frame(root)
frame_username.pack(pady=10)
Label(frame_username, text="Username").pack(side=LEFT, padx=10)
entry_username = Entry(frame_username, width=30)
entry_username.pack(side=LEFT)

# Password input
frame_password = Frame(root)
frame_password.pack(pady=10)
Label(frame_password, text="Password").pack(side=LEFT, padx=10)
entry_password = Entry(frame_password, width=30, show="*")
entry_password.pack(side=LEFT)

# Login button
login_button = Button(root, text="Login", command=authenticate)
login_button.pack(pady=20)

root.mainloop()