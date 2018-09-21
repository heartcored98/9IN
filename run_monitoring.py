import logging

from utils import load_yml_config
from webmonitor import *

settings = load_yml_config()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == '__main__':

    monitor = MonitorARA()
    telegram_pusher = TelegramPusher()

    logger.info("###########################################")
    logger.info("########## Start POST Monitoring ##########")
    logger.info("###########################################")


    with pd.option_context('display.max_rows', None, 'display.max_columns', None):


        cnt = 0
        while True:
            time.sleep(0.3)
            new_table = monitor.get_table()
            new_posts, changed_posts, finished_posts = monitor.find_update(monitor.p_table, new_table)
            # monitor.save_table(new_table)

            for id, data in new_posts.items():
                content = telegram_pusher.generate_content(request=data, mode=NEW)
                telegram_pusher.send_message(content)
                logger.info(data)

                # request = KakaoContentMaker.content_new(data['title'], data['link'])
                # KakaoPusher(request)
                # kill_chrome()


            for id, data in changed_posts.items():
                content = telegram_pusher.generate_content(request=data, mode=UPDATE)
                telegram_pusher.send_message(content)
                logger.info(data)

                # request = KakaoContentMaker.content_changed(data['p_title'], data['c_title'], data['link'])
                # KakaoPusher(request)
                # kill_chrome()

            for id, data in finished_posts.items():
                content = telegram_pusher.generate_content(request=data, mode=FINISHED)
                telegram_pusher.send_message(content)
                logger.info(data)

                # request = KakaoContentMaker.content_finished(data['title'], data['link'])
                # KakaoPusher(request)
                # kill_chrome()

            cnt += 1
            if cnt > settings.LOG_INTERVAL:
                logger.info('{} connection tried'.format(settings.LOG_INTERVAL))
                cnt = 0

