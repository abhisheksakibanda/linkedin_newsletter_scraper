"""
Main script to scrape LinkedIn newsletters, subscribe to them, and share them with connections.
"""
from typing import List

from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver

from cookies_manager import load_cookies, save_cookies
from internet_manager import wait_for_internet
from linkedin_scraper import subscribe_to_newsletters
from newsletter_sharing import share_newsletters
from utils import save_newsletters_to_excel, load_newsletters_from_excel

# Start WebDriver
chrome_driver: WebDriver = webdriver.Chrome()


def login_with_cookies(driver: WebDriver) -> None:
    """
    Log in to LinkedIn using cookies if available, otherwise prompt for manual login.

    :param driver: WebDriver instance
    """
    driver.get(url="https://www.linkedin.com/")
    try:
        load_cookies(driver=driver)
        if "login" in driver.current_url:  # Check if still on the login page
            input("Please log in manually and complete 2FA, then press Enter...")
            save_cookies(driver=driver)
    except FileNotFoundError as ex:  # Handle a missing cookies file
        print(f"Cookies file not found: {ex}")
    except Exception as ex:
        print(f"Login failed: {ex}")
        driver.quit()


if __name__ == "__main__":
    try:
        wait_for_internet()
        login_with_cookies(driver=chrome_driver)

        # Load existing newsletter URLs
        existing_urls = load_newsletters_from_excel()

        # Subscribe and scrape newsletter URLs
        newsletter_urls: List[str] = subscribe_to_newsletters(driver=chrome_driver, existing_urls=existing_urls)

        # Save URLs to Excel
        save_newsletters_to_excel(newsletter_urls=newsletter_urls)

        # Share newsletters and retry on errors
        erroneous_urls = newsletter_urls  # Start with all scraped URLs
        retry_count = 0
        max_retries = 3  # Set a limit to avoid infinite retries

        while erroneous_urls and retry_count < max_retries:
            erroneous_urls = share_newsletters(driver=chrome_driver, newsletter_urls=erroneous_urls)
            if erroneous_urls:
                print(
                    f"\nFailed to share {len(erroneous_urls)} newsletters:\n{erroneous_urls}\nRetrying... (Attempt {retry_count + 1})")
            retry_count += 1

        if erroneous_urls:
            print(
                f"\nFailed to share {len(erroneous_urls)} newsletters after {retry_count} attempts:\n{erroneous_urls}")

    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    except WebDriverException as e:
        print(f"WebDriver error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        chrome_driver.quit()
