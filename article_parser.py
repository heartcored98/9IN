
import os
import time
import logging

from bs4 import BeautifulSoup

from utils import load_yml_config
from pusher import *
from webmonitor import WebDriver


def generate_content(title, body, url):
    content = "*[{}]*\n{} \n[자세히보기>]({})".format(title, body, url)
    return content


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
        html = html[start_idx+23:end_idx].replace('<br />', ' ').replace('\n', ' ')
        html = ' '.join(html.split())
        html = html.strip()
        article = BeautifulSoup(html, 'lxml')
        return article.text


def article_handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    TEST_MODE = event.get('TEST_MODE', True)
    posts = event.get('posts', [])

    settings = load_yml_config()
    ara_id = settings.ARA_ID
    ara_key = settings.ARA_KEY
    MAX_LEN = settings.MAX_LEN

    ara = ParserARA()
    ara.login(ara_id, ara_key)

    # ===== Construct Telegram Bot ====== #
    telegram_pusher = get_telegram_pusher(test_mode=TEST_MODE)
    logger.info("Construct telegram pusher done!")

    message_ids = []
    for post in posts:
        url = post['url']
        title = post['title']
        body = ara.get_article(url)
        if isinstance(body, str):
            if len(body) > 0:
                if len(body) > MAX_LEN:
                    body = body[:MAX_LEN] + '...'
                content = generate_content(title, body, url)
                resp = telegram_pusher.send_message(content)
                try:
                    message_ids.append(resp.message_id)
                    logger.info("Post url={}. title={} pushed successfully".format(url, title))
                except:
                    logger.error("Post url={}. title={} failed to parse article".format(url, title))
            else:
                logger.error("Post url={}. title={} got zero length".format(url, title))
        else:
            logger.error("Post url={}. title={} failed to parse article".format(url, title))

    logger.info("Message ids : {}".format(str(message_ids)))
    logger.info("Pushed {}/{} successfully!".format(len(message_ids), len(posts)))

if __name__ == '__main__':
    payload = {"posts":[{"url": "https://ara.kaist.ac.kr/board/Wanted/568845/", "title": "aaa"}]}
    article_handler(payload, None)
