import logging
from s3_utils import *
from post_parser import get_ara_table


settings = load_yml_config()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == '__main__':

    logger.info("###########################################")
    logger.info("########## Start POST Monitoring ##########")
    logger.info("###########################################")

    settings = load_yml_config()
    filename = settings.FILE_NAME
    bucket = settings.BUCKET_NAME
    filepath = "{}/{}".format(bucket, filename)

    prev_table = download_df(filepath)
    new_table = get_ara_table()

    new_ids = list(set(new_table.index) - set(prev_table.index))

    titles = new_table.loc[new_ids, '제목']
    print(titles)


    # print(prev_table)


