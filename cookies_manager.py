import os
import pickle

from selenium.webdriver.chrome.webdriver import WebDriver


def load_cookies(driver: WebDriver) -> None:
    if os.path.exists("linkedin_cookies.pkl"):
        with open(file="linkedin_cookies.pkl", mode="rb") as cookies_file:
            cookies = pickle.load(file=cookies_file)
            for cookie in cookies:
                driver.add_cookie(cookie_dict=cookie)
        driver.refresh()

        if "feed" not in driver.current_url:
            print("Cookies expired, manual login required.")
            driver.get(url="https://www.linkedin.com/login")
    else:
        print("No cookies found, manual login required.")
        driver.get(url="https://www.linkedin.com/login")


def save_cookies(driver: WebDriver) -> None:
    with open(file="linkedin_cookies.pkl", mode="wb") as cookies_file:
        pickle.dump(obj=driver.get_cookies(), file=cookies_file)
