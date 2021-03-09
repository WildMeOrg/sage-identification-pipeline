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
    get_stepper,
    get_target_image,
    get_target_image_display,
    get_action_card,
    get_results_table,
    get_footer,
    get_detection_card,
    get_classification_card,
)

from .utils import (
    download_file,
    now,
    size_human_readable,
    time_human_readable,
)


async def make_base_ui(q: Q):
    q.page['meta'] = get_meta()
    # q.page['header'] = get_header()
    q.page['title'] = get_title(q)

    print('making base ui')
    print(q.args)
    if (q.app.target_image):
        q.page['target_image'] = get_target_image_display(q)
    else:
        q.page['target_image'] = get_target_image(q)
    
    q.page['action_card'] = get_action_card(q)
    q.page['stepper'] = get_stepper(q)
    q.page['detection_card'] = get_detection_card(q)
    q.page['classification_card'] = get_classification_card(q)
    q.page['results_table'] = get_results_table()
    q.page['footer'] = get_footer()
    await q.page.save()


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
