import logging
import time
import telegram
from utils import load_yml_config


settings = load_yml_config()
logger = logging.getLogger(__name__)

NEW = 0
UPDATE = 1
FINISHED = 2

################################################################################
######################### TELEGRAM Push Notification ###########################
################################################################################


class TelegramPusher():
    def __init__(self):
        self.bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)
        self.channel_id = settings.TELEGRAM_CHANNEL

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
        self.bot.sendMessage(chat_id='@{}'.format(
            self.channel_id),
            text=content,
            parse_mode='MARKDOWN'
        )

    def generate_content(self, request, mode):
        if mode == NEW:
            template = "*[새글]*  \n[{}]({})"
            content = template.format(
                request['title'],
                request['link']
            )
        elif mode == UPDATE:
            template = "*[변경]*  \n*변경전:* {}  \n*변경후:* [{}]({})"
            content = template.format(
                request['p_title'],
                request['c_title'],
                request['link']
            )
        elif mode == FINISHED:
            template = "*[마감]*  \n[{}]({})"
            content = template.format(
                request['title'],
                request['link']
            )
        return content

if __name__ == '__main__':
    request = {'content':'테스트 메시지2', 'link':'http://ara.kaist.ac.kr/board/Wanted/563979/?page_no=1'}

    content = "[새글]-{} \n -----------------------{}".format(request['content'], request['link'])
    content = "*bold text*  \n_italic text_  \n[inline URL](http://www.example.com/)"

    telegram_pusher = TelegramPusher()
    telegram_pusher.bot.sendMessage(chat_id='@kaist9in', text=content, parse_mode='MARKDOWN')
