import time

import requests


def wait_for_internet() -> None:
    while True:
        try:
            requests.get(url='https://www.google.com/', timeout=5)
            print("Connected to the internet")
            return
        except requests.ConnectionError:
            print("Waiting for internet connection...")
            time.sleep(30)  # Wait for 30 seconds before trying again
