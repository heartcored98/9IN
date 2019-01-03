from selenium import webdriver
import os
import time
from webmonitor import WebDriver
from s3_utils import load_yml_config
from bs4 import BeautifulSoup




class ParserARA(WebDriver):
    def __init__(self):
        self.target_url = 'https://ara.kaist.ac.kr/board/Wanted/'
        WebDriver.__init__(self, target_url=self.target_url)

    def login(self, id, key):
        path_id = '//*[@id="miniLoginID"]'
        path_pw = '//*[@id="miniLoginPassword"]'
        path_btn = '//*[@id="loginBox"]/dd/form/ul/li[3]/a[1]'

        input_id = self.driver.find_element_by_xpath(path_id)
        input_id.send_keys(id)

        input_pw = self.driver.find_element_by_xpath(path_pw)
        input_pw.send_keys(key)

        # Login to the site
        self.click_btn(path_btn)

    def get_article(self, url):
        self.get_url(url)
        html = self.get_source()
        start_idx = html.find('<div class="article "')
        end_idx = html.find('</div>', start_idx)
        html = html[start_idx+23:end_idx].replace('<br />', '').replace('\n', ' ')
        html = ' '.join(html.split())
        html = html.strip()
        article = BeautifulSoup(html, 'lxml')
        return article.text




def article_handler(event, context):
    settings = load_yml_config()
    ara_id = settings.ARA_ID
    ara_key = settings.ARA_KEY
    posts = event.get('posts', [])

    ara = ParserARA()
    ara.login(ara_id, ara_key)

    for post in posts:
        url = post['url']
        title = post['title']
        body = ara.get_article('https://ara.kaist.ac.kr/board/Wanted/568788')
    print(body)
    # print(ara.get_source())


    # ===== Construct Telegram Bot ====== #
    telegram_pusher = get_telegram_pusher(test_mode=TEST_MODE)
    logger.info("Construct telegram pusher done!")

    message_ids = []
    for content in contents:
        resp = telegram_pusher.send_message(content)
        try:
            message_ids.append(resp.message_id)
        except:
            pass
    logger.info("Message ids : {}".format(str(message_ids)))
    logger.info("Pushed {}/{} successfully!".format(len(message_ids), len(contents)))



if __name__ == '__main__':
    article_handler(None, None)
