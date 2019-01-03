import logging
from post_parser import *
from pusher import *
from os import listdir
from os.path import isfile, join
from s3_utils import *

def generate_content(new_posts, base_url):
    list_contents = []
    for id, value in new_posts.to_dict('index').items():
        url = base_url.format(id)
        title = value['제목']
        body = value.get('body', '')
        content = "*{}*\n{} \n[바로가기>]({})".format(title, body, url)
        list_contents.append(content)
    return list_contents


def generate_payload(new_posts, base_url):
    list_posts = []
    for id, value in new_posts.to_dict('index').items():
        url = base_url.format(id)
        title = value['제목']
        list_posts.append({'url':url, 'title':title})
    return list_posts


def ara_wanted_handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

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
    last_max_id = max(list(prev_table.index))
    new_ids = [post_id for post_id in new_ids if post_id > last_max_id]
    if len(new_ids) > 0:
        logger.info("Find new post ids : {}. {} posts.".format(str(new_ids), len(new_ids)))
    else:
        logger.info("No post is found")

    new_posts = new_table.loc[new_ids, :]
    payload = generate_payload(new_posts, base_url)
    logger.info("Generate payload done!")

    # ===== Invoke Article Parsing Lambda Fuction ===== #
    invoke_event('test_sele', payload)

    # ===== Upload current posts ====== #
    logger.info("Uploading current posts...")
    upload_df(new_table, filepath)
    logger.info("Uploading current posts done! {} posts.".format(len(new_table)))



if __name__ == '__main__':
    ara_wanted_handler({}, {})
    # selenium_handler({}, {})