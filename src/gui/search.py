import logging
import os
from src.gui.data_fetching import fetch_computer_groups, fetch_mobile_device_groups
from src.utils import load_token
from src.gui.tree_views import update_tree_view  # Ensure update_tree_view is imported

def search_callback(tab_type, filter_type, search_term, tree_view):
    logging.info(f"Search for {filter_type} with term: {search_term} in {tab_type}")

    token = load_token()
    if not token:
        logging.error("No token found!")
        return

    jamf_url = os.getenv("JAMF_PRO_URL", "")
    if not jamf_url:
        logging.error("No Jamf URL found!")
        return

    if tab_type == "computers":
        if filter_type == "Groups":
            groups_data = fetch_computer_groups(jamf_url, token)
            if groups_data:
                filtered_groups = [group for group in groups_data['groups'] if search_term.lower() in group['name'].lower()]
                update_tree_view(tree_view, filtered_groups)
        else:
            # Implement search for individual computers if needed
            pass
    elif tab_type == "devices":
        if filter_type == "Groups":
            groups_data = fetch_mobile_device_groups(jamf_url, token)
            if groups_data:
                filtered_groups = [group for group in groups_data['groups'] if search_term.lower() in group['name'].lower()]
                update_tree_view(tree_view, filtered_groups)
        else:
            # Implement search for individual devices if needed
            pass