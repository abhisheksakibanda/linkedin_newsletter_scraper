"""
This module contains functions to scrape newsletters from LinkedIn and subscribe to them.
"""
import time
from typing import List, Dict

from selenium.common import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, \
    WebDriverException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from internet_manager import wait_for_internet


def click_element(driver: WebDriver, element: WebElement) -> None:
    """
    Clicks an element using JavaScript to avoid any overlay issues.

    :param driver: WebDriver instance
    :param element: WebElement to click
    """
    driver.execute_script("arguments[0].click();", element)
    time.sleep(6)  # Slight delay to avoid overwhelming the page


def find_subscribe_button(newsletter_card: WebElement) -> WebElement:
    """
    Finds the "Subscribe" button within a newsletter card.

    :param newsletter_card: WebElement of the newsletter card
    :return: WebElement of the "Subscribe" button
    """
    return newsletter_card.find_element(by=By.XPATH, value=".//div[@class='p3']//button")


def scroll_to_bottom(driver: WebDriver) -> None:
    """
    Scroll to the bottom of the page to load all the content.

    :param driver: WebDriver instance
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for content to load

        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    print("Scrolled to the bottom of the page.")


def handle_subscription(driver: WebDriver, newsletter_card: WebElement, existing_urls: List[str],
                        subscribed_newsletters: List[str], failed_attempts: Dict[str, WebElement]) -> None:
    """
    Handles the subscription process for a single newsletter card.

    :param driver: WebDriver instance
    :param newsletter_card: WebElement of the newsletter card
    :param existing_urls: List of existing newsletter URLs
    :param subscribed_newsletters: List of subscribed newsletter URLs
    :param failed_attempts: Dictionary of failed attempts with URLs and WebElements
    """
    newsletter_url: str | None = None
    subscribe_button: WebElement | None = None
    try:
        # Get the address of the newsletter and check if it has already been subscribed to
        newsletter_url = newsletter_card.find_element(by=By.TAG_NAME, value="a").get_attribute("href")
        if newsletter_url and (newsletter_url in existing_urls or newsletter_url in subscribed_newsletters):
            print(f"Already subscribed to: {newsletter_url}")
            return

        # Click the "Subscribe" button
        subscribe_button = find_subscribe_button(newsletter_card)
        if subscribe_button.text == "Subscribe":
            click_element(driver, subscribe_button)

            # Check if the subscription was successful
            subscribed_button = find_subscribe_button(newsletter_card)
            if subscribed_button.text == "Subscribed":
                subscribed_newsletters.append(newsletter_url)
                print(f"Subscribed and scraped: {newsletter_url}")
            else:
                # Subscription failed, retry later (could be due to network issues)
                print(f"Failed to subscribe to newsletter: {newsletter_url}")
                wait_for_internet()
                failed_attempts[newsletter_url] = subscribe_button
    except (
            NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException,
            WebDriverException) as e:
        print(f"Error occurred for {newsletter_url}: {e}")
        wait_for_internet()
        failed_attempts[newsletter_url] = subscribe_button
    except Exception as e:
        print(f"Failed to subscribe to newsletter: {e}")


def subscribe_to_newsletters(driver: WebDriver, existing_urls: List[str]) -> List[str]:
    """
    Subscribe to newsletters on LinkedIn and scrape their URLs.

    :param driver: WebDriver instance
    :param existing_urls: List of existing newsletter URLs
    :return: List of subscribed newsletter URLs
    """
    driver.get(url="https://www.linkedin.com/mynetwork/grow/")

    # Wait for the page to load
    wait = WebDriverWait(driver, timeout=10)

    # Scroll to the bottom of the page to load all the sections
    scroll_to_bottom(driver)

    try:
        # Locate all divs with the class 'discover-sections-list__item'
        sections = wait.until(
            ec.visibility_of_all_elements_located((By.CLASS_NAME, "discover-sections-list__item"))
        )

        for section in sections:
            # Check if the section contains a "Subscribe" button
            try:
                if section.find_element(by=By.XPATH, value=".//*[contains(@aria-label, 'Subscribe to')]"):
                    # Scroll to the section and locate the "See all" button (usually the first button in the section)
                    see_all_button = section.find_element(by=By.TAG_NAME, value="button")

                    # Click the "See all" button using JS to avoid any overlay issues
                    click_element(driver, see_all_button)
                    print("Clicked 'See all' button for the section containing 'Subscribe'")
                    break  # Found the section, no need to check further
            except NoSuchElementException:
                print("No 'Subscribe' button found in this section")

    except Exception as e:
        print(f"Error: {e}")

    subscribed_newsletters: List[str] = []
    failed_attempts: Dict[str, WebElement] = {}

    # Wait for the modal to appear
    modal = wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "artdeco-modal")))

    # Scroll to the bottom of the modal to load all newsletters
    scroll_to_bottom_of_modal(driver, modal)

    # Once all newsletters are loaded, find all the newsletter cards in the modal
    newsletter_cards = modal.find_elements(by=By.CLASS_NAME, value="discover-fluid-entity-list--item")

    for newsletter_card in newsletter_cards:
        handle_subscription(driver, newsletter_card, existing_urls, subscribed_newsletters, failed_attempts)

    # Verify if failed newsletters were subscribed to
    if failed_attempts:
        print(f"Failed to subscribe to {len(failed_attempts)} newsletters. Retrying up to 3 times...")
        retry_count: int = 3
        for _ in range(retry_count):
            if not failed_attempts:
                break
            current_failed_attempts: Dict[str, WebElement] = failed_attempts.copy()
            failed_attempts.clear()
            for newsletter_url, subscribe_button in current_failed_attempts.items():
                try:
                    click_element(driver, subscribe_button)

                    # Check if the subscription was successful
                    subscribed_button = find_subscribe_button(subscribe_button.find_element(By.XPATH, ".."))
                    if subscribed_button.text == "Subscribed":
                        subscribed_newsletters.append(newsletter_url)
                        print(f"Subscribed and scraped on retry: {newsletter_url}")
                    else:
                        print(f"Failed to subscribe to newsletter: {newsletter_url}")
                        wait_for_internet()
                        failed_attempts[newsletter_url] = subscribe_button
                except StaleElementReferenceException:
                    print("Already subscribed to newsletter...")
                    subscribed_newsletters.append(
                        newsletter_url) if newsletter_url not in subscribed_newsletters else None
                except (NoSuchElementException, ElementClickInterceptedException, WebDriverException) as e:
                    print(f"Retry failed for {newsletter_url}: {e}")
                    wait_for_internet()  # Wait for internet connectivity
                    failed_attempts[newsletter_url] = subscribe_button
                except Exception as e:
                    print(f"Failed to subscribe to newsletter: {newsletter_url}, on retry: {e}")
                    failed_attempts[newsletter_url] = subscribe_button

        if failed_attempts:
            print(f"Failed to subscribe to the following newsletters after {retry_count} attempts:")
            for newsletter_url in failed_attempts.keys():
                print(newsletter_url)

    return subscribed_newsletters


def scroll_to_bottom_of_modal(driver: WebDriver, modal: WebElement) -> None:
    """
    Scroll to the bottom of the modal to load all the content.

    :param driver: WebDriver instance
    :param modal: WebElement of the modal
    """
    # Get the initial scroll height
    last_height = driver.execute_script("return arguments[0].scrollHeight", modal)

    while True:
        # Scroll to the bottom of the modal
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        time.sleep(6)  # Wait for content to load

        # Calculate new scroll height
        new_height = driver.execute_script("return arguments[0].scrollHeight", modal)
        time.sleep(4)
        if new_height == last_height:
            break
        last_height = new_height
    print("Scrolled to the bottom of the modal.")
