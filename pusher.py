import logging
import time
import telegram
from s3_utils import *

settings = load_yml_config()
logger = logging.getLogger(__name__)

NEW = 0
UPDATE = 1
FINISHED = 2

################################################################################
######################### TELEGRAM Push Notification ###########################
################################################################################

def get_telegram_pusher(test_mode=True):
    if test_mode:
        token = settings.TEST_BOT_TOKEN
        channel_id = settings.TEST_CHANNEL_URL
    else:
        token = settings.DEPLOY_BOT_TOKEN
        channel_id = settings.DEPLOY_CHANNEL_URL
    telegram_pusher = TelegramPusher(token, channel_id)
    return telegram_pusher

class TelegramPusher():
    def __init__(self, token, channel_id):
        self.bot = telegram.Bot(token=token)
        self.channel_id = channel_id

    def _retry(func):
        def retried_func(*args, **kwargs):
            MAX_TRIES = 2
            tries = 1
            while True:
                try:
                    resp = func(*args, **kwargs)
                    return resp

                except:
                    logger = logging.getLogger(__name__)
                    error = "error is occured {} times @{}".format(str(tries), func.__name__)
                    logger.error(error, exc_info=True)
                    tries += 1
                    time.sleep(0.5)
                    if tries > MAX_TRIES:
                        raise
                    continue

        return retried_func

    @_retry
    def send_message(self, content):
        resp = self.bot.sendMessage(
            chat_id=self.channel_id,
            text=content,
            parse_mode='MARKDOWN',
            disable_web_page_preview=True
        )
        return resp


if __name__ == '__main__':
    request = {'title':'한글 모십니다', 'body':'일본어 가리쳐주실 분 구합니다..', 'link':'http://ara.kaist.ac.kr/board/Wanted/563979/?page_no=1'}
    content = "*{}*\n{} \n[inline URL]({})".format(request['title'], request['body'], request['link'])
    print(content)

    token = settings.TEST_BOT_TOKEN
    channel_id = settings.TEST_CHANNEL_URL
    telegram_pusher = TelegramPusher(token, channel_id)
    # print(telegram_pusher.bot.get_me())
    telegram_pusher.bot.sendMessage(chat_id='@kaist9in_test', text=content, parse_mode='MARKDOWN', disable_web_page_preview=True)
