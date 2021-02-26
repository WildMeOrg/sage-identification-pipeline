import os
import shutil
import subprocess
from datetime import timedelta
from typing import List, Tuple

import pandas as pd

from h2o_wave import Q, site

from .components import (
    get_meta,
    get_header,
    get_title,
    get_path_tabs,
    get_toolbar,
    get_object_table_form,
    get_footer
)

from .drivers import DataConnector, make_valid_name
from .utils import (
    download_file,
    now,
    size_human_readable,
    time_human_readable,
)

async def make_base_ui(q: Q):
    q.page['meta'] = get_meta()
    q.page['header'] = get_header()
    q.page['title'] = get_title(q)
    q.page['path_tabs'] = get_path_tabs()
    q.page['commands'] = get_toolbar(q)
    q.page['objects'] = get_object_table_form()
    q.page['footer'] = get_footer()
    print('there!')
    await q.page.save()
    print('here!')

def create_app_dirs(q: Q):
    # A directory for all users data
    q.app.users_dir = os.path.abspath('./app-data/users')
    os.makedirs(q.app.users_dir, exist_ok=True)

def download_to_local_storage(q: Q, object_url):
    file_path = download_file(
        q.args.object_url,
        os.path.join('.', os.path.basename(q.args.object_url)),
    )
    return file_path
