"""
This module contains the function to share newsletters on LinkedIn by reposting them to the feed.
"""
import time
from typing import List

from selenium.common import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, \
    WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from internet_manager import wait_for_internet


def share_newsletters(driver: WebDriver, newsletter_urls: List[str]) -> List[str]:
    """
    Share newsletters on LinkedIn by reposting them to the feed.

    :param driver: WebDriver instance
    :param newsletter_urls: List of newsletter URLs to share
    :return: List of URLs that failed to share
    """
    erroneous_urls: List[str] = []
    for idx, url in enumerate(newsletter_urls):
        # Pause for 10 minutes when visiting every 100 posts
        if idx != 0 and idx % 100 == 0:
            time.sleep(600)
        driver.execute_script(script=f"window.open('{url}', '_blank');")
        driver.switch_to.window(window_name=driver.window_handles[-1])
        time.sleep(6)

        # Wait for the dropdown with "Repost to Feed" to appear
        wait = WebDriverWait(driver, timeout=10)

        try:
            share_button: WebElement = driver.find_element(by=By.ID, value="publishing-entity-share-dropdown-trigger")
            share_button.click()
            time.sleep(6)
            repost_list_item: WebElement = wait.until(
                ec.element_to_be_clickable((By.XPATH, "//*[text()='Repost to Feed']")))
            repost_list_item.click()
            time.sleep(6)

            post_button = driver.find_element(by=By.XPATH, value="//*[text()='Post']//ancestor::button")
            post_button.click()
            time.sleep(6)
            print(f"Reposted newsletter: {url}")
        except (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException,
                WebDriverException) as e:
            print(f"Error occurred for {url}: {e}")
            erroneous_urls.append(url)
            wait_for_internet()  # Wait for internet connectivity
        except Exception as e:
            print(f"Failed to share newsletter {url}: {e}")
            erroneous_urls.append(url)
        finally:
            driver.close()
            driver.switch_to.window(window_name=driver.window_handles[0])

        time.sleep(5)  # Pause to avoid rate limiting
    return erroneous_urls
