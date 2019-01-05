import logging
from parser_post import get_ara_table
from s3_utils import *
from utils import load_yml_config


def generate_payload(new_posts, base_url):
    list_posts = []
    for id, value in new_posts.to_dict('index').items():
        url = base_url.format(id)
        title = value['제목']
        list_posts.append({'url':url, 'title':title})
    return {'posts':list_posts}


def ara_wanted_handler(event, context):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logger.info("###########################################")
    logger.info("########## Start POST Monitoring ##########")
    logger.info("###########################################")

    # ===== Get Settings Parameters ====== #
    settings = load_yml_config()
    base_url = settings.ARA_WANTED_BASE_URL
    bucket = settings.BUCKET_NAME
    ARTICLE_PARSER_LAMBDA = settings.ARTICLE_PARSER_LAMBDA
    TEST_MODE = settings.TEST_MODE
    if TEST_MODE:
        filename = settings.TEST_ARA_WANTED_FILE_NAME
    else:
        filename = settings.DEPLOY_ARA_WANTED_FILE_NAME

    STOP_WORDS = settings.STOP_WORDS
    MAX_LEN = settings.MAX_LEN
    filepath = "{}/{}".format(bucket, filename)
    logger.info("TEST_MODE : {}".format(TEST_MODE))
    logger.info("STOP_WORDS : {}".format(str(STOP_WORDS)))
    logger.info("MAX_LEM : {}".format(MAX_LEN))

    # ===== Download previous posts ====== #
    logger.info("Downloading previous posts...")
    flag_prev_table = True
    try:
        prev_table = download_df(filepath)
        last_id = prev_table.index[0]
        logger.info("Downloading previous posts done! {} posts. Last id={}".format(len(prev_table), last_id))
    except FileNotFoundError:
        flag_prev_table = False
        logger.error("File not found. Maybe first time to launch?")

    # ===== Fetching current posts ====== #
    logger.info("Fetching current posts...")
    new_table = get_ara_table()
    logger.info("Fetching current posts done! {} posts.".format(len(new_table)))

    # ===== Upload current posts ====== #
    logger.info("Uploading current posts...")
    upload_df(new_table, filepath)
    logger.info("Uploading current posts done! {} posts.".format(len(new_table)))

    if flag_prev_table:
        # ===== Filtering new posts ====== #
        new_ids = list(set(new_table.index) - set(prev_table.index))
        last_max_id = max(list(prev_table.index))
        new_ids = [post_id for post_id in new_ids if post_id > last_max_id]
        if len(new_ids) > 0:
            logger.info("Find new post ids : {}. {} posts.".format(str(new_ids), len(new_ids)))
            new_posts = new_table.loc[new_ids, :]
            payload = generate_payload(new_posts, base_url)
            payload.update({"TEST_MODE":TEST_MODE})
            logger.info("Generate payload done!")

            # ===== Invoke Article Parsing Lambda Fuction ===== #
            invoke_event(ARTICLE_PARSER_LAMBDA, payload)
            logger.info("Invoked lambda_selenium!")
        else:
            logger.info("No post is found")




if __name__ == '__main__':
    ara_wanted_handler({}, {})