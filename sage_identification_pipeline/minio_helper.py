from logging import exception
import os
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject


class MinioBucket:
    def __init__(
        self, endpoint, bucket_name, access_key, secret_key, default_prefix=''
    ) -> None:
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.default_prefix = default_prefix
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )
        self._create_bucket()

    def _create_bucket(self):
        try:
            found = self.client.bucket_exists(self.bucket_name)
            if not found:
                self.client.make_bucket(self.bucket_name)
                print(f'Bucket {self.bucket_name} created')
            else:
                print(f'Bucket {self.bucket_name} already exists')
        except S3Error as exc:
            print('error occurred.', exc)
            raise

    def upload_file(self, object_name, file_path):
        object_name = os.path.join(self.default_prefix, object_name)
        file_abspath = os.path.abspath(file_path)
        if not os.path.isfile(file_abspath):
            print(f'{file_path} is not a valid file.')
            return
        try:
            self.client.fput_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_abspath,
            )
        except S3Error as exc:
            print('error occurred.', exc)

    def list(self, prefix, recursive=False):
        prefix = os.path.join(self.default_prefix, prefix)
        objects = self.client.list_objects(
            self.bucket_name, prefix=prefix, recursive=recursive
        )
        return objects

    def share(self, object_name, expiration_time):
        object_name = os.path.join(self.default_prefix, object_name)
        try:
            # url = self.client.presigned_get_object(
            #     self.bucket_name,
            #     object_name,
            #     expires=expiration_time,
            # )
            url = self.client.get_presigned_url(
                'GET',
                self.bucket_name,
                object_name,
                expires=expiration_time,
            )
        except exception as e:
            print('Error while generating a share link')
            print(e)
        else:
            return url

    def delete(self, object_name):
        object_name = os.path.join(self.default_prefix, object_name)
        self.client.remove_object(self.bucket_name, object_name)

    def delete_multiple(self, object_list):
        object_list = [os.path.join(self.default_prefix, x) for x in object_list]
        # Remove list of objects.
        errors = self.client.remove_objects(
            self.bucket_name,
            [DeleteObject(x) for x in object_list],
        )
        return list(errors)

    def delete_recursive(self, prefix):
        prefix = os.path.join(self.default_prefix, prefix)
        # Remove a prefix recursively.
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            self.client.list_objects(
                bucket_name=self.bucket_name, prefix=prefix, recursive=True
            ),
        )
        errors = self.client.remove_objects(self.bucket_name, delete_object_list)
        return list(errors)

    def download(self, object_name, file_path, makedirs=True):
        object_name = os.path.join(self.default_prefix, object_name)
        file_abspath = os.path.abspath(file_path)
        parent_dir = os.path.dirname(file_abspath)
        if not os.path.isdir(parent_dir):
            if makedirs:
                os.makedirs(parent_dir)
            else:
                print(f'Error: The directory {parent_dir} does not exist')
                return
        try:
            self.client.fget_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                file_path=file_abspath,
            )
        except S3Error as exc:
            print('error occurred.', exc)
