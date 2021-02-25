import os

from h2o_wave import Q

from .common import get_user_bucket


class AppUser:
    def __init__(self, user_id, email, users_dir):
        self.user_id = user_id
        self.email = email
        self.connectors = {}
        self.relative_timestamps = False
        self._set_name()
        self._create_user_dirs(users_dir)
        self._set_storage_prefix()

    def _set_name(self):
        names = self.email.split('@')[0].split('.')
        if len(names) > 1:
            self.first, *_, self.last = names
        elif names:
            self.first = names[0]
            self.last = ''
        self.name = f'{self.first} {self.last}'.strip().title()

    def _create_user_dirs(self, users_dir):
        self.user_dir = os.path.join(users_dir, self.user_id)
        os.makedirs(self.user_dir, exist_ok=True)

    def _set_storage_prefix(self):
        self.storage_prefix = f'ai/h2o/ocean/user/{self.user_id}'

    def assign_storage(self, q: Q):
        self.bucket = get_user_bucket(self.storage_prefix)
        local_path = '.ignoreme'
        with open(local_path, mode='w') as fp:
            fp.write(self.storage_prefix + '/')
        self.bucket.upload_file(
            object_name='.ignoreme',
            file_path=local_path,
        )
        os.remove(local_path)
