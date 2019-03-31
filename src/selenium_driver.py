###############################################################################
# Chromedriver download url : https://chromedriver.storage.googleapis.com/index.html?path=2.45/
# Selenium Get Started Page : http://chromedriver.chromium.org/getting-started

import os, signal
from os.path import join
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui


class WebDriver:
    """Wrapper Class of webdriver which has useful functionality
    This class handle all the web browsing process with connecting to url,
    clicking button on website, extracting text on websites. Also it has
    its own retry decorator feature which enable auto-reconnection when
    initial attempt get failed.
    """

    def __init__(self, target_url, window=False):
        self.logger = logging.getLogger(__name__)

        self.count_reset = 0
        self.MAX_COUNT = 5

        self.target_url = target_url
        self.PATH_SCREENSHOT_DIR = './screenshot'
        self.window = window
        self.driver = None
        self.start_driver()

    def _retry(func):
        def retried_func(*args, **kwargs):
            MAX_TRIES = 2
            tries = 1
            while True:
                try:
                    resp = func(*args, **kwargs)
                    return resp
                except NoSuchElementException:
                    raise NoSuchElementException
                except:
                    logger = logging.getLogger(__name__)
                    error = "error is occured {} times @{}".format(str(tries), func.__name__)
                    logger.error(error, exc_info=True)
                    tries += 1
                    # time.sleep(0.5)
                    if tries > MAX_TRIES:
                        raise
                    continue

        return retried_func

    def set_counter(self, MAX_COUNT=5):
        self.MAX_COUNT = MAX_COUNT

    def reset_driver(self):
        self.logger.info("start resetting driver")
        if self.count_reset >= self.MAX_COUNT:
            self.quit_driver()
            # time.sleep(1)
            self.start_driver()
            self.count_reset = 0
        else:
            self.count_reset += 1
        self.logger.info("end resetting driver")

    @_retry
    def start_driver(self, **kwargs):
        self.logger.info("driver warming up")

        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1280x1696')
            chrome_options.add_argument('--user-data-dir=/tmp/user-data')
            chrome_options.add_argument('--hide-scrollbars')
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=99')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--data-path=/tmp/data-path')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--homedir=/tmp')
            chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
            chrome_options.binary_location = os.getcwd() + "/headless-chromium"

            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        except:
            self.logger.critical("some error", exc_info=True)
        self.driver.get(self.target_url)
        self.logger.info("new driver generated")

    def quit_driver(self):
        try:
            if self.driver is not None:
                self.driver.service.process.send_signal(signal.SIGTERM)
                self.driver.quit()
                self.logger.info("driver terminated")

        except:
            self.logger.error('error in quit_driver', exc_info=True)

    @_retry
    def get_url(self, url):
        self.driver.get(url)

    def get_source(self):
        return self.driver.page_source

    def screenshot(self, name="shoot.png"):
        filename = "{}/{}".format(self.PATH_SCREENSHOT_DIR, name)
        self.driver.save_screenshot(filename)


    def get_pid(self):
        try:
            if self.driver is not None:
                return self.driver.service.process.pid
        except:
            return -1

    def is_visible(self, locator, timeout=1.0):
        try:
            ui.WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return True
        except TimeoutException:
            return False
        except:
            self.logger.error("error in is_visible", exc_info=True)
            return False

    @_retry
    def get_text(self, path):
        try:
            if self.is_visible(path):
                context = self.driver.find_element_by_xpath(path)
                return context.text
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            raise NoSuchElementException

        except Exception:
            self.logger.error("error in get text", exc_info=True)
            raise

    @_retry
    def click_btn(self, path, id=False, selector=False):
        try:
            if self.is_visible(path):
                if id:
                    btn = self.driver.find_element_by_id(path)
                elif selector:
                    btn = self.driver.find_element_by_selector(path)
                else:
                    btn = self.driver.find_element_by_xpath(path)
                btn.click()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            print("No element")

        except Exception:
            self.logger.error("error in click_btn", exc_info=True)
            raise

if __name__ == '__main__':

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    driver = webdriver.Chrome('./headless-chromium', chrome_options=chrome_options)
    driver.get('https://ara.kaist.ac.kr/board/Wanted/')
    time.sleep(1)
    print(driver.page_source)
    driver.quit()
