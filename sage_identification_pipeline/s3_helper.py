import os

import boto3
import botocore

from .utils import read_lines


class S3Bucket:
    def __init__(self, bucket_name, access_key, secret_key):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource(
            "s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key
        )
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        self.bucket = self.s3.Bucket(self.bucket_name)

    @staticmethod
    def _get_tag_str(tags):
        return "&".join([f"{k}={v}" for k, v in tags.items()])

    @staticmethod
    def _get_tag_set(tags):
        return [{"Key": k, "Value": v} for k, v in tags.items()]

    def list_objects(self, prefix, pattern=None):
        if not prefix.endswith("/"):
            prefix += "/"
        contents = []
        paginator = self.s3_client.get_paginator("list_objects_v2")
        result = paginator.paginate(
            Bucket=self.bucket_name, Delimiter="/", Prefix=prefix
        )
        for folder in result.search("CommonPrefixes"):
            if folder is not None:
                contents.append(folder.get("Prefix"))
        for obj in result.search("Contents"):
            if obj is not None:
                contents.append(obj.get("Key"))
        if pattern is not None:
            return [x for x in contents if pattern in x]
        return contents

    def list_all_objects(self, prefix):
        for obj in self.bucket.objects.filter(Prefix=prefix):
            print(obj.key)

    def search_objects(self, prefix, pattern):
        for obj in self.bucket.objects.filter(Prefix=prefix):
            if pattern in obj.key:
                print(obj.key)

    def upload_file(self, file_path, key, tags):
        tag_str = self._get_tag_str(tags)
        self.bucket.upload_file(
            file_path,
            key,
            ExtraArgs={"Tagging": tag_str},
        )

    def download_file(self, key, file_path, progress=False):
        self.bucket.download_file(key, file_path)
        # if progress:
        # file_size = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)[
        #     "ContentLength"
        # ]
        # progress_bar = tqdm(
        #     desc=os.path.basename(key),
        #     total=file_size,
        #     ascii=True,
        #     unit="B",
        #     unit_scale=True,
        #     dynamic_ncols=True,
        # )
        # self.bucket.download_file(
        #     key, file_path, Callback=lambda x: progress_bar.update(x)
        # )
        # progress_bar.close()
        # return

    def get_object_tags(self, key):
        response = self.s3_client.get_object_tagging(Bucket=self.bucket_name, Key=key)
        return {x["Key"]: x["Value"] for x in response["TagSet"]}

    def set_object_tags(self, key, tags):
        response = self.s3_client.put_object_tagging(
            Bucket=self.bucket_name,
            Key=key,
            Tagging={"TagSet": self._get_tag_set(tags)},
        )
        return response["HTTPStatusCode"]

    def _delete_object(self, keys):
        delete_list = [{"Key": k} for k in keys]
        response = self.bucket.delete_objects(Delete={"Objects": delete_list})
        return [x["Key"] for x in response["Deleted"]]

    def is_accessible(self):
        try:
            result = self.s3_client.get_bucket_acl(Bucket=self.bucket_name)
            return True
        except botocore.exceptions.ClientError as error:  # type: ignore
            print("Unable to connect to S3!")
            print(error)
            return False


def get_aws_credentials_from_env():
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    return access_key, secret_key


def read_s3cfg():
    home = os.environ.get("HOME")
    if home is None:
        print("$HOME not defined!")
        return
    s3cfg = os.path.join(home, ".s3cfg")
    s3cfg_path = os.path.abspath(s3cfg)
    if not os.path.isfile(s3cfg_path):
        print(f"{s3cfg_path} not found!")
        return
    s3cfg_lines = read_lines(s3cfg_path)
    s3_config = {}
    for line in s3cfg_lines:
        line = line.strip()
        if " = " in line:
            k, v, *rest = line.split(" = ")
            if not rest:
                s3_config[k] = v
    return s3_config


def get_aws_credentials():
    access_key, secret_key = get_aws_credentials_from_env()
    if not all([access_key, secret_key]):
        s3_config = read_s3cfg()
        if s3_config is not None:
            access_key = s3_config.get("access_key")
            secret_key = s3_config.get("secret_key")
    return access_key, secret_key
