
import logging
import os

from parser_content import ParserARA
from utils import load_yml_config
from pusher_telegram import *


def generate_content(title, body, url):
    if '[' in title or ']' in title:
        content = "*{}*\n{} \n[자세히보기>]({})".format(title, body, url)
    else:
        content = "*[{}]*\n{} \n[자세히보기>]({})".format(title, body, url)
    return content


def article_handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    MAX_LEN = int(os.environ['MAX_LEN'])
    TEST_MODE = True if os.environ['TEST_MODE'] == 'true' else False

    logger.info("TEST_MODE : {}".format(TEST_MODE))
    logger.info("MAX_LEN : {}".format(MAX_LEN))


    posts = event.get('posts', [])

    settings = load_yml_config()
    ara_id = settings.ARA_ID
    ara_key = settings.ARA_KEY

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
