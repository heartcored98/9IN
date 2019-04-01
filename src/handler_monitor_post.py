import logging
import os
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
    ARTICLE_PARSER_LAMBDA = os.environ['ARTICLE_PARSER_LAMBDA'] #settings.ARTICLE_PARSER_LAMBDA
    TEST_MODE = bool(os.environ['TEST_MODE']) #settings.TEST_MODE
    STOP_WORDS = os.environ['STOP_WORDS'].split('/')


    settings = load_yml_config()
    base_url = settings.ARA_WANTED_BASE_URL
    bucket = settings.BUCKET_NAME

    if TEST_MODE:
        filename = settings.TEST_ARA_WANTED_FILE_NAME
    else:
        filename = settings.DEPLOY_ARA_WANTED_FILE_NAME

    filepath = "{}/{}".format(bucket, filename)
    logger.info("ARTICLE_PARSER : {}".format(ARTICLE_PARSER_LAMBDA))
    logger.info("TEST_MODE : {}".format(TEST_MODE))
    logger.info("STOP_WORDS : {}".format(str(STOP_WORDS)))

    # ===== Download previous posts ====== #
    logger.info("Downloading previous posts...")
    flag_prev_table = True
    try:
        prev_table = download_df(filepath)
        if prev_table is None: # If empty dataframe downloaded then mark as flag_prev_table False
            flag_prev_table = False
            logger.error("Empty DataFrame Detected! DataFrame would be updated!")
            raise ValueError("Break current process")
        last_id = prev_table.index[0]
        logger.info("Downloading previous posts done! {} posts. Last id={}".format(len(prev_table), last_id))
    except FileNotFoundError:
        flag_prev_table = False
        logger.error("File not found. Maybe first time to launch?")
    except Exception as e:
        flag_prev_table = False
        logger.error("Unknown error occurred while downloading previous table! + \n" + str(e), exc_info=True)

    # ===== Fetching current posts ====== #
    logger.info("Fetching current posts...")
    new_table = get_ara_table(STOP_WORDS=STOP_WORDS, url='https://ara.kaist.ac.kr/board/Wanted/', test_mode=TEST_MODE)
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