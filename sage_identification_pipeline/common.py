import os
import shutil
import subprocess
from datetime import timedelta
from typing import List, Tuple

from h2o_wave import Q, site

from .components import (
    get_meta,
    get_logo,
    get_title,
    get_stepper,
    get_target_image,
    get_target_image_display,
    get_action_card,
    get_detection_progress_card,
    get_detection_card,
    get_classification_progress_card,
    get_classification_card,
    get_identification_in_progress,
    get_identification_results,
    get_footer,
)

from .utils import (
    download_file,
    now,
    size_human_readable,
    time_human_readable,
)


async def make_base_ui(q: Q):
    q.page['meta'] = get_meta()
    q.page['logo'] = get_logo(q)
    q.page['title'] = get_title(q)

    if (q.app.target_image):
        q.page['target_image'] = get_target_image_display(q)
    else:
        q.page['target_image'] = get_target_image(q)
    
    q.page['action_card'] = get_action_card(q)
    q.page['stepper'] = get_stepper(q)

    if q.app.detection_in_progress:
        q.page['detection_card'] = get_detection_progress_card(q)
    elif q.app. detection_complete:
        q.page['detection_card'] = get_detection_card(q)
    else:
        del q.page['detection_card']

    if q.app.classification_in_progress:
        q.page['classification_card'] = get_classification_progress_card(q)
    elif q.app.classification_complete:
        q.page['classification_card'] = get_classification_card(q)
    else:
        del q.page['classification_card']

    if q.app.identification_in_progress:
        q.page['results_table'] = get_identification_in_progress(q)
    elif q.app.identification_complete:
        q.page['results_table'] = get_identification_results(q)
    else:
        del q.page['results_table']
    
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
