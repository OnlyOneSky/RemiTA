"""Custom wait helpers wrapping Selenium WebDriverWait."""

from __future__ import annotations

from typing import Tuple

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = Tuple[str, str]

DEFAULT_TIMEOUT = 15


def wait_for_element_visible(
    driver: WebDriver, locator: Locator, timeout: int = DEFAULT_TIMEOUT
) -> WebElement:
    """Wait until an element is visible on screen."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_for_element_clickable(
    driver: WebDriver, locator: Locator, timeout: int = DEFAULT_TIMEOUT
) -> WebElement:
    """Wait until an element is clickable."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


def wait_for_text_present(
    driver: WebDriver, locator: Locator, text: str, timeout: int = DEFAULT_TIMEOUT
) -> bool:
    """Wait until specific text appears in an element."""
    return WebDriverWait(driver, timeout).until(
        EC.text_to_be_present_in_element(locator, text)
    )


def wait_for_element_gone(
    driver: WebDriver, locator: Locator, timeout: int = DEFAULT_TIMEOUT
) -> bool:
    """Wait until an element disappears from the DOM."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )
        return True
    except TimeoutException:
        return False
