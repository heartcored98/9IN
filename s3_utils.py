import yaml
import s3fs
import pandas as pd
from io import StringIO
import boto3
import json

##############################################################################
######################## Configuration Object   ##############################
##############################################################################


class Objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def load_yml_config(filename='settings.yml'):
    with open(filename, 'r') as stream:
        try:
            return Objdict(yaml.load(stream))
        except yaml.YAMLError as exc:
            return None


##############################################################################
############################ Get AWS Object   ################################
##############################################################################


def get_session():
    settings = load_yml_config()
    session = boto3.Session(
        aws_access_key_id=settings.ACCESS_ID,
        aws_secret_access_key=settings.ACCESS_KEY,
        region_name=settings.REGION_NAME
    )
    return session


def get_client(session, service):
    return session.client(service)


##############################################################################
############################ Get Lambda Client  ##############################
##############################################################################


def get_lambda_client():
    return get_client(get_session(), "lambda")


def invoke_event(func_name, payload):
    lambda_client = get_lambda_client()
    lambda_client.invoke(
        FunctionName=func_name,
        InvocationType='Event',
        Payload=json.dumps(payload),
    )


##############################################################################
######################### Get S3 File System   ###############################
##############################################################################


def get_s3fs():
    settings = load_yml_config()
    aws_access_key_id = settings.ACCESS_ID
    aws_secret_access_key = settings.ACCESS_KEY
    fs = s3fs.S3FileSystem(key=aws_access_key_id, secret=aws_secret_access_key)
    return fs


def upload_df(table, filepath):
    fs = get_s3fs()
    with fs.open(filepath, 'wb') as f:
        bytes_to_write = table.to_csv(None).encode(encoding='ms949')
        f.write(bytes_to_write)


def download_df(filepath):
    # Ref : https://stackoverflow.com/questions/38154040/save-dataframe-to-csv-directly-to-s3-python

    fs = get_s3fs()
    with fs.open(filepath, 'rb') as f:
        table_bytes = f.read()
        table = pd.read_csv(StringIO(table_bytes.decode('ms949')))
        table.index = table['id']
        table = table.drop(columns=['id'])
        return table


if __name__ == '__main__':
    from post_parser import get_ara_table

    settings = load_yml_config()
    filename = settings.FILE_NAME
    bucket = settings.BUCKET_NAME
    filepath = "{}/{}".format(bucket, filename)

    table = get_ara_table()
    print(table)
    upload_df(table, filepath)
    download_df(filepath)



