# JamfCommander

**JamfCommander** is a Python-based GUI tool designed to replicate some of the key functionalities of the deprecated Jamf Remote app. The tool enables IT administrators to remotely manage devices, send MDM commands, create one-off policies, and run scripts on demand using the Jamf Pro API.

## Features
- **Authenticate with Jamf Pro**: Log in securely using the Jamf Pro API.
- **Send MDM Commands**: Directly send MDM commands like device lock, restart, or wipe to managed devices.
- **Run Scripts on Demand**: Execute custom scripts on remote devices.
- **Create One-Off Policies**: Create temporary policies that will run on devices during the next check-in.
- **Clear Stuck Commands**: Monitor and clear stuck or pending commands.

## Requirements

### 1. Python 3.x
Ensure that you have Python 3 installed on your system. You can check by running:
```bash
python3 --version
```

2. Required Python Libraries

Install the following dependencies using pip:
```bash
pip3 install requests
```
	•	requests: Used for interacting with the Jamf Pro API.
	•	tkinter: Pre-installed with Python for creating the GUI interface.

3. Tkinter Installation (if not pre-installed)

If Tkinter is not pre-installed, you can install it using Homebrew:
```bash
brew install tcl-tk
```
Setup Instructions

	1.	Clone this repository:
```bash
git clone https://github.com/your-username/JamfCommander.git
cd JamfCommander
```
	2.	Create a Python virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate
```
	3.	Install the required Python packages:
```bash
pip3 install -r requirements.txt
```
	4.	Run the application:
```bash
python3 main.py
```
Directory Structure
```bash
JamfCommander/
│
├── main.py               # Main Python script for the application
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies (requests, etc.)
└── .gitignore            # Git ignore file
```
Example Usage

	1.	Launch the GUI.
	2.	Enter your Jamf Pro URL, username, and password.
	3.	Send MDM commands or create policies using the provided options.

Troubleshooting

Common Errors:

	1.	ModuleNotFoundError: No module named ‘requests’
Ensure requests is installed by running:
```bash
pip3 install requests
```

	2.	Tkinter Deprecation Warning
You may see warnings related to the version of Tkinter. These warnings can be ignored, or you can suppress them by setting the environment variable:
```bash
export TK_SILENCE_DEPRECATION=1
```

```bash
Contributing

If you would like to contribute to the project or report an issue, feel free to create an issue or pull request in the GitHub repository.

License

This project is licensed under the MIT License. See the LICENSE file for more details.

Acknowledgments

    •	Thanks to the Jamf Pro API documentation for providing the necessary information to interact with the API.
    •	Shoutout to the Python community for creating and maintaining the requests library.
```