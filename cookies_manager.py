"""
This module provides functions to load and save cookies from/to a file.
"""
import os
import pickle
import time

from selenium.webdriver.chrome.webdriver import WebDriver


def load_cookies(driver: WebDriver) -> None:
    """
    Load cookies from a file and add them to the WebDriver instance.

    :param driver: WebDriver instance
    """
    if os.path.exists("linkedin_cookies.pkl"):
        with open(file="linkedin_cookies.pkl", mode="rb") as cookies_file:
            cookies = pickle.load(file=cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie_dict=cookie)
        time.sleep(5)
        driver.refresh()

        if "feed" not in driver.current_url:
            print("Cookies expired, manual login required.")
            driver.get(url="https://www.linkedin.com/login")
    else:
        print("No cookies found, manual login required.")
        driver.get(url="https://www.linkedin.com/login")


def save_cookies(driver: WebDriver) -> None:
    """
    Save cookies to a pickle file.

    :param driver: WebDriver instance
    """
    with open(file="linkedin_cookies.pkl", mode="wb") as cookies_file:
        pickle.dump(obj=driver.get_cookies(), file=cookies_file)
