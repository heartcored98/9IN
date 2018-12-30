import logging
from s3_utils import *
from post_parser import *
from pusher import *


settings = load_yml_config()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

def generate_content(new_posts, base_url):
    list_contents = []
    for id, value in new_posts.to_dict('index').items():
        url = base_url.format(id)
        title = value['제목']
        body = value.get('body', '')
        content = "*{}*\n{} \n[바로가기>]({})".format(title, body, url)
        list_contents.append(content)
    return list_contents


if __name__ == '__main__':

    logger.info("###########################################")
    logger.info("########## Start POST Monitoring ##########")
    logger.info("###########################################")

    # ===== Get Settings Parameters ====== #
    settings = load_yml_config()
    filename = settings.ARA_WANTED_FILE_NAME
    base_url = settings.ARA_WANTED_BASE_URL
    bucket = settings.BUCKET_NAME
    filepath = "{}/{}".format(bucket, filename)

    # ===== Download previous posts ====== #
    logger.info("Downloading previous posts...")
    prev_table = download_df(filepath)
    logger.info("Downloading previous posts done! {} posts.".format(len(prev_table)))

    # ===== Fetching current posts ====== #
    logger.info("Fetching current posts...")
    new_table = get_ara_table()
    logger.info("Fetching current posts done! {} posts.".format(len(new_table)))

    # ===== Filtering new posts ====== #
    new_ids = list(set(new_table.index) - set(prev_table.index))
    logger.info("Find new post ids : {}. {} posts.".format(str(new_ids), len(new_ids)))

    new_posts = new_table.loc[new_ids, :]
    contents = generate_content(new_posts, base_url)
    logger.info("Generate content message")

    # ===== Construct Telegram Bot ====== #
    token = settings.TEST_BOT_TOKEN
    channel_id = settings.TEST_CHANNEL_URL
    telegram_pusher = TelegramPusher(token, channel_id)

    for content in contents:
        telegram_pusher.bot.sendMessage(chat_id=channel_id,
                                        text=content,
                                        parse_mode='MARKDOWN',
                                        disable_web_page_preview=True)

    # print(prev_table)


