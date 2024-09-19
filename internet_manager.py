"""
This module contains a function that checks for an active internet connection.
"""
import time

import requests


def wait_for_internet() -> None:
    """
    Check for an active internet connection by sending a request to Google.
    If the connection is not available, wait for 30 seconds before trying again.
    """
    while True:
        try:
            requests.get(url='https://www.google.com/', timeout=5)
            print("Connected to the internet")
            return
        except requests.ConnectionError:
            print("Waiting for internet connection...")
            time.sleep(30)  # Wait for 30 seconds before trying again
