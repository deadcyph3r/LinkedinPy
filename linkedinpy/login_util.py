"""Module only used for the login part of the script"""
# import built-in & third-party modules
import time
from selenium.webdriver.common.action_chains import ActionChains

from socialcommons.time_util import sleep
from .util import update_activity
from .util import web_address_navigator
from .util import get_current_url
from .util import explicit_wait
from .settings import Settings

def login_user(browser,
               username,
               userid,
               password,
               logger,
               logfolder,
               switch_language=True,
               bypass_suspicious_attempt=False,
               bypass_with_mobile=False):
    """Logins the user with the given username and password"""
    assert username, 'Username not provided'
    assert password, 'Password not provided'

    print(username, password)
    ig_homepage = "https://www.linkedin.com/login/"
    web_address_navigator(Settings, browser, ig_homepage)
    time.sleep(1)

    input_username_XP = '//*[@id="username"]'
    input_username = browser.find_element_by_xpath(input_username_XP)

    print('Entering username')
    (ActionChains(browser)
     .move_to_element(input_username)
     .click()
     .send_keys(username)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    input_password = browser.find_elements_by_xpath('//*[@id="password"]')
    if not isinstance(password, str):
        password = str(password)

    print('Entering password')
    (ActionChains(browser)
     .move_to_element(input_password[0])
     .click()
     .send_keys(password)
     .perform())

    # update server calls for both 'click' and 'send_keys' actions
    for i in range(2):
        update_activity(Settings)

    sleep(1)

    print('Submitting login_button')
    login_button = browser.find_element_by_xpath('//*[@type="submit"]')

    (ActionChains(browser)
     .move_to_element(login_button)
     .click()
     .perform())

    # update server calls
    update_activity(Settings)

    sleep(10)

    current_url = get_current_url(browser)
    if current_url !=  "https://www.linkedin.com/feed/":
        explicit_wait(browser, "PFL", [], logger, 5)

    current_url = get_current_url(browser)
    if current_url == "https://www.linkedin.com/feed/":
        return True
    else:
        return False

