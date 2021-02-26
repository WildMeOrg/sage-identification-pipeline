import os

from h2o_wave import Q

class AppUser:
    def __init__(self, user_id, email, users_dir):
        self.user_id = user_id
        self.email = email
