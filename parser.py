#!/home/ubuntu/anaconda3/bin/python3

# from pytz import timezone
from datetime import date, datetime
from multiprocessing import Pool
import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Manager
from functools import partial
import time
import json
import pprint
import os, signal
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui


FLAG_DEBUG = False
CHROMEDRIVER_PATH = '/home/ubuntu/chromedriver'


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
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            if not bool(kwargs):
                self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)
            else:
                self.driver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=options)
            """
            options = webdriver.ChromeOptions()
            options.add_argument("headless")  # remove this line if you want to see the browser popup
            self.driver = webdriver.Chrome(chrome_options=options, executable_path='/usr/bin/chromedriver')
            """
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


    # @_retry
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
