import requests
from tkinter import *
from tkinter import messagebox
import json

# Add your client ID and secret from the generated JSON
client_id = "your_client_id"
client_secret = "your_client_secret"

# Function to obtain an OAuth 2.0 token
def get_token(jamf_url):
    token_url = f"{jamf_url}/api/v1/auth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        # Make the request to get the token
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response and extract the token
        token_info = response.json()
        return token_info["token"]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get token: {e}")
        return None

# Function to handle the login and test API call
def login():
    # Get the values entered by the user
    jamf_url = entry_url.get()

    # Show a loading message
    messagebox.showinfo("Loading", "Attempting to log in...")

    # Get the OAuth token
    token = get_token(jamf_url)

    if token:
        # Now we will use the token to make an API request to list computers
        api_url = f"{jamf_url}/JSSResource/computers"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        try:
            # Make the API request using the token
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            # Show success message and output the result
            messagebox.showinfo("Success", "Successfully authenticated and fetched computers!")
            print(f"Response: {response.json()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch computers: {e}")
    else:
        messagebox.showerror("Error", "Failed to authenticate. No token was received.")

# Creating the GUI window
root = Tk()
root.title("JamfCommander")
root.geometry('400x300')

# Jamf Pro URL input
Label(root, text="Jamf Pro URL").pack(pady=10)
entry_url = Entry(root, width=40)
entry_url.pack(pady=5)

# Login button
Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()