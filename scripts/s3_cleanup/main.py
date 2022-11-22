import argparse
import boto
import boto.s3.connection
import datetime as dt
from dotenv import load_dotenv
import logging
import os
import re

load_dotenv()


def get_s3_bucket(bucketname: str):
    """returns bucket object based

    :param bucketname: name of s3 bucket

    return b: s3 bucket object
    """
    access_key = os.environ.get("access_key")
    secret_key = os.environ.get("secret_key")
    conn = boto.connect_s3(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        host="us-east-1.linodeobjects.com",
    )
    b = conn.get_bucket(bucketname)

    return b


def get_docker_backup_objects(bucket):
    """returns list of objects with docker_backup in the key
    :param bucket: should be s3 bucket object

    :return: list of s3 keys
    """
    docker_backup = [key for key in bucket if "docker_backup" in key.name]

    return docker_backup


def get_key_to_delete(docker_backup: list):
    """returns keys to delete based on regular expression
    :param: docker_backup list of keys with docker_backup in name
    :return

    """
    pattern = r"([\d\-.]{10})"

    # (example output) docker_backups/2023-07-04
    keys_to_delete = []
    for k in docker_backup:
        m = re.search(pattern, k.name)
        if m:
            if m.group(0) <= str(dt.date.today() - dt.timedelta(days=10)):
                keys_to_delete.append(k)

    return keys_to_delete


def delete_keys(keys_to_delete: list, bucket):
    """deletes keys from s3 bucket
    :param keys_to_delete: list of keys to delete
    :param b: s3 bucket

    """

    for k in keys_to_delete:
        logging.info(f"Deleting key {k.name}")
        bucket.delete_key(k)


def parse_arguments():
    """parse commmand-line arguments

    :return parser.parse_args():
    """

    # load cli flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="bucket to parse for docker_backups")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    bucket = get_s3_bucket(args.bucket)
    objects = get_docker_backup_objects(bucket)
    key_to_delete = get_key_to_delete(objects)
    delete_keys(keys_to_delete=key_to_delete, bucket=bucket)
