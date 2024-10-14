### JamfCommander

***JamfCommander*** is a Python-based GUI tool designed to replicate some of the key functionalities of the deprecated Jamf Remote app. The tool enables IT administrators to remotely manage devices, send MDM commands, create one-off policies, and run scripts on demand using the Jamf Pro API.

### ⚠️ Disclaimer

This is a work in progress and is not fully functional yet. The current version of the tool includes limited functionality and is still under development. It is advised to not rely on this tool in production environments until it reaches a stable version.

### Features

- ***Authenticate with Jamf Pro:*** Log in securely using the Jamf Pro API.
- ***Send MDM Commands:*** Directly send MDM commands like device lock, restart, or wipe to managed devices.
- ***Run Scripts on Demand:*** Execute custom scripts on remote devices.
- ***Create One-Off Policies:*** Create temporary policies that will run on devices during the next check-in.
- ***Clear Stuck Commands:*** Monitor and clear stuck or pending commands.
- ***Dashboard:*** Displays Jamf Pro version, number of managed computers, mobile devices, computer/mobile device groups, policies, and configuration profiles.

### Requirements

1. Python 3.x

Ensure that you have Python 3 installed on your system. You can check by running:
```bash
python3 --version
```

2. Required Python Libraries
```bash
Install the following dependencies using pip:
```
```bash
pip3 install requests python-dotenv
```

- ***requests:*** Used for interacting with the Jamf Pro API.
- ***tkinter:*** Pre-installed with Python for creating the GUI interface.
- ***python-dotenv:*** Used to manage environment variables (such as the Jamf Pro URL).

3. Tkinter Installation (if not pre-installed)

If Tkinter is not pre-installed, you can install it using:
```bash
brew install tcl-tk
```
Setup Instructions

Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/JamfCommander.git
```
```bash
cd JamfCommander
```
Step 2: (Optional) Create a Python Virtual Environment

It is recommended to use a virtual environment for isolating dependencies.
```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
Step 3: Install the Required Python Packages
```bash
pip3 install -r requirements.txt
```
Step 4: Run the Application

To run the application:
```bash
python3 main.py
```
### Directory Structure
```bash
JamfCommander/
│
├── main.py                     # Main Python script for the application
├── src/                        # Source folder containing various modules
│   ├── auth.py                 # Handles authentication with Jamf Pro
│   ├── api.py                  # API calls to Jamf Pro and Classic API
│   ├── gui.py                  # GUI components and layout
│   ├── utils.py                # Helper functions, environment variable handling, and token management
├── requirements.txt            # Python dependencies (requests, dotenv, etc.)
├── .env                        # Environment variables (Jamf Pro URL)
├── .gitignore                  # Git ignore file
└── README.md                   # Project documentation
```
### Example Usage

1.	Launch the GUI: The application starts with a login page.
2.	Authenticate: Enter your Jamf Pro URL and click login. The credentials are loaded from the .jcinf.json file.
3.	Use Dashboard: After authentication, view the dashboard that displays the Jamf Pro version, managed computers, groups, policies, and profiles.
4.	Additional Tabs: Use the Computers and Devices tabs to fetch relevant groups and other data.

### Troubleshooting

***Common Errors:***

1. ModuleNotFoundError: No module named ‘requests’

Ensure that requests is installed by running:
```bash
pip3 install requests
```
2. Tkinter Deprecation Warning

You may see warnings related to the version of Tkinter. These warnings can be ignored, or you can suppress them by setting the environment variable:
```bash
export TK_SILENCE_DEPRECATION=1
```

### Notes on Environment Setup

- When setting up the environment, we downloaded the Python installer directly and did not use Homebrew for Python installation.
- The application uses the Jamf Pro Classic API for some data, so be sure your Jamf Pro instance supports both the Classic and Jamf Pro APIs.

### Contributing

If you would like to contribute to the project or report an issue, feel free to create an issue or pull request in the GitHub repository.

### License

This project is licensed under the MIT License. See the LICENSE file for more details.

### Acknowledgments

- Thanks to the Jamf Pro API documentation for providing the necessary information to interact with the API.
- Shoutout to the Python community for creating and maintaining the requests library.