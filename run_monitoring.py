import logging
from post_parser import *
from pusher import *


def generate_content(new_posts, base_url):
    list_contents = []
    for id, value in new_posts.to_dict('index').items():
        url = base_url.format(id)
        title = value['제목']
        body = value.get('body', '')
        content = "*{}*\n{} \n[바로가기>]({})".format(title, body, url)
        list_contents.append(content)
    return list_contents


def ara_wanted_handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    TEST_MODE = event.get('TEST_MODE', True)

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
    logger.info("Generate content message done!")

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

    # ===== Upload current posts ====== #
    logger.info("Uploading current posts...")
    upload_df(new_table, filepath)
    logger.info("Uploading current posts done! {} posts.".format(len(new_table)))



if __name__ == '__main__':
    ara_wanted_handler({}, {})
