import os
import shutil
import subprocess
from datetime import timedelta
from typing import List, Tuple

import pandas as pd

from h2o_wave import Q, site

from .components import (
    get_connector_config_commands,
    get_connector_config_form,
    get_connector_table_commands,
    get_connector_table_form,
    get_df_preview_form,
    get_footer,
    get_header,
    get_import_wizard_commands,
    get_meta,
    get_object_actions_bar,
    get_object_table_form,
    get_path_tabs,
    get_preview_commands,
    get_primary_commands,
    get_secondary_commands,
    get_title,
    get_toolbar,
    get_upload_box_form,
    list_to_table_rows,
    make_ingest_failed_dialog,
    make_tabs,
)
from .drivers import DataConnector, make_valid_name
from .minio_helper import MinioBucket
from .utils import (
    download_file,
    download_from_presigned_url,
    is_presigned_url,
    now,
    size_human_readable,
    time_human_readable,
    zip_dir,
)


def create_app_dirs(q: Q):
    # A directory for all users data
    q.app.users_dir = os.path.abspath('./app-data/users')
    os.makedirs(q.app.users_dir, exist_ok=True)


def initialize_minio():
    process = subprocess.Popen(['bash', './install_minio.sh'])


def get_minio_credentials():
    access_key = os.getenv('MINIO_ROOT_USER')
    secret_key = os.getenv('MINIO_ROOT_PASSWORD')
    endpoint = os.getenv('MINIO_ENDPOINT')
    bucket_name = os.getenv('MINIO_ROOT_BUCKET')

    # print(f'Minio Access Key: {access_key}')
    # print(f'Minio Secret Key: {secret_key}')
    # print(f'Minio Endpoint: {endpoint}')
    # print(f'Minio Bucket: {bucket_name}')

    if (
        access_key is None
        or secret_key is None
        or endpoint is None
        or bucket_name is None
    ):
        print('Minio: Credentials Unavailable')
        raise RuntimeError('Minio: Credentials Unavailable')

    return dict(
        endpoint=endpoint,
        bucket_name=bucket_name,
        access_key=access_key,
        secret_key=secret_key,
    )


def get_root_bucket():
    return MinioBucket(**get_minio_credentials())


def get_user_bucket(prefix):
    return MinioBucket(**get_minio_credentials(), default_prefix=prefix)


async def make_base_ui(q: Q):
    q.page['meta'] = get_meta()
    q.page['header'] = get_header()
    q.page['title'] = get_title(q)
    q.page['path_tabs'] = get_path_tabs()
    q.page['commands'] = get_toolbar(q)
    q.page['objects'] = get_object_table_form()
    # q.page['config_connectors'] = get_config_connector_form()
    q.page['footer'] = get_footer()
    await q.page.save()


async def make_upload_box(q: Q):
    q.page['upload_box'] = get_upload_box_form()
    q.page['objects'].items[0].table.height = f'{400}px'
    await q.page.save()


async def clear_upload_box(q: Q):
    del q.page['upload_box']
    q.page['objects'].items[0].table.height = f'{800}px'
    await q.page.save()


def get_object_row_data(object_iterator, relative_timestamps):
    folders = []
    files = []
    for obj in object_iterator:
        if obj.object_name.endswith('.ignoreme'):
            continue
        obj_name = obj.object_name
        name = os.path.basename(obj_name.rstrip('/'))
        if obj.object_name.endswith('/'):
            name += '/'
            obj_type = 'folder'
            obj_size = ''
            modified = ''
            access = 'private'
            folders.append([name, obj_type, modified, obj_size, access])
        else:
            _, obj_type = os.path.splitext(obj.object_name)
            obj_type = obj_type.strip('.')
            obj_size = size_human_readable(obj.size)
            modified = time_human_readable(obj.last_modified, relative_timestamps)
            access = 'private'
            files.append([name, obj_type, modified, obj_size, access])
    rows = sorted(folders) + sorted(files)
    return rows


async def update_object_table(q: Q):
    obj_list = q.user.user.bucket.list(prefix=q.client.path[q.client.path_pointer])
    obj_row_data = get_object_row_data(obj_list, q.user.user.relative_timestamps)
    q.page['objects'].items[0].table.rows = list_to_table_rows(obj_row_data)
    q.page['objects'].items[0].table.multiple = (
        q.client.multi_select_icon == 'CheckboxCompositeReversed'
    )
    q.page['objects'].items[0].table.values = q.client.selected_objects
    await q.page.save()


async def waved_to_minio(q: Q, user_files):
    for link in user_files:
        local_path = await q.site.download(link, '.')
        q.user.user.bucket.upload_file(
            object_name=os.path.join(
                q.client.path[q.client.path_pointer], os.path.basename(local_path)
            ),
            file_path=local_path,
        )
        os.remove(local_path)
        await q.site.unload(link)


async def update_path(q: Q):
    path_tabs = q.client.path[: q.client.path_pointer + 1]
    visible_path = '/'.join([x.strip('/').split('/')[-1] for x in path_tabs])
    last_removed = ''
    if len(visible_path) > q.app.max_path_length:
        while len(visible_path) > q.app.max_path_length - 5:
            last_removed = path_tabs.pop(0)
            visible_path = '/'.join([x.strip('/').split('/')[-1] for x in path_tabs])
        path_tabs.insert(0, '...')
    path_tabs_data = [dict(name='/', icon='Home', label='')] + [
        dict(
            name=last_removed if x == '...' else x,
            label=x.strip('/').split('/')[-1],
        )
        for x in path_tabs
        if x != ''
    ]

    path_items = make_tabs(path_tabs_data)
    path_value = q.client.path[q.client.path_pointer] or '/'
    q.page['path_tabs'] = get_path_tabs(items=path_items, value=path_value)

    await q.page.save()


async def update_object_actions(q: Q):
    if q.client.multi_select_icon == 'CheckboxComposite':
        del q.page['actions']
    else:
        q.page['actions'] = get_object_actions_bar(q)
    await q.page.save()


async def clear_selections(q: Q):
    '''Clear selected_objects and disable multi_select'''

    q.client.multi_select_icon = 'CheckboxComposite'
    q.client.selected_objects = None
    q.page['commands'].items[q.app.multi_select_index].icon = q.client.multi_select_icon
    # TODO: Check if saving the page is required
    await q.page.save()


def set_path_pointer(q: Q):
    if q.args.path_tabs == '/':
        q.client.path_pointer = 0
    else:
        q.client.path_pointer = q.client.path.index(q.args.path_tabs)


def enable_multi_select(q: Q):
    q.client.multi_select_icon = 'CheckboxCompositeReversed'
    q.page['commands'].items[q.app.multi_select_index].icon = q.client.multi_select_icon


def step_into_folder(q: Q):
    q.client.path = q.client.path[: q.client.path_pointer + 1]
    q.client.path.append(os.path.join(q.client.path[-1], q.args.object_table[0]))
    q.client.path_pointer = len(q.client.path) - 1


def prep_empty_folder(q: Q):
    if q.args.folder_name != '':
        local_path = '.ignoreme'
        path_to_new_folder = os.path.join(
            q.client.path[q.client.path_pointer], q.args.folder_name + '/'
        )
        with open(local_path, mode='w') as fp:
            fp.write(path_to_new_folder)
        q.user.user.bucket.upload_file(
            object_name=os.path.join(path_to_new_folder, '.ignoreme'),
            file_path=local_path,
        )
        os.remove(local_path)


def multi_select_disabled(q: Q):
    return q.client.multi_select_icon == 'CheckboxComposite'


async def clear_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()


def upload_to_minio(q: Q, file_path):
    q.user.user.bucket.upload_file(
        object_name=os.path.join(
            q.client.path[q.client.path_pointer],
            os.path.basename(file_path),
        ),
        file_path=file_path,
    )
    os.remove(file_path)


def download_to_local_storage(q: Q, object_url):
    if is_presigned_url(object_url):
        file_path = download_from_presigned_url(object_url, q.user.user.user_dir)
    else:
        file_path = download_file(
            q.args.object_url,
            os.path.join('.', os.path.basename(q.args.object_url)),
        )
    return file_path


def get_names_prefixes_in_selected(q: Q) -> Tuple[List[str], List[str]]:
    current_path = q.client.path[q.client.path_pointer]
    names = []
    prefixes = []
    for x in q.client.selected_objects:
        full_path = os.path.join(current_path, x)
        if full_path.endswith('/'):
            prefixes.append(full_path)
        else:
            names.append(full_path)
    return names, prefixes


def delete_selected(q: Q):
    names, prefixes = get_names_prefixes_in_selected(q)
    all_errors = []
    for x in prefixes:
        prefix_errors = q.user.user.bucket.delete_recursive(prefix=x)
        if prefix_errors:
            all_errors.extend(prefix_errors)
    object_errors = q.user.user.bucket.delete_multiple(names)
    if object_errors:
        all_errors.extend(object_errors)
    return all_errors


def minio_to_waved(q: Q, object_names, file_paths, download_dir, use_zip):
    # Download objects from minio
    for object_name, file_path in zip(object_names, file_paths):
        obj_info = q.user.user.bucket.download(object_name, file_path)
    # Upload them to Wave server
    if use_zip:  # len(file_paths) > 1:
        zip_path = zip_dir(download_dir)
        wave_file_paths = site.upload([zip_path])
        os.remove(zip_path)
    else:  # len(file_paths) == 1:
        wave_file_paths = site.upload(file_paths)

    shutil.rmtree(download_dir)
    q.client.wave_file_paths = wave_file_paths
    return wave_file_paths


def prep_for_download(q: Q):
    # Get Current Directory
    current_path = q.client.path[q.client.path_pointer]
    current_dir = os.path.dirname(current_path)
    current_dir_name = os.path.basename(current_dir)
    # TODO: This if statement is probably unnecessary
    if current_dir_name == '':
        current_dir_name = 'ocean'
    download_dir = os.path.join(q.user.user.user_dir, f'{current_dir_name}_{now()}')
    os.makedirs(download_dir, exist_ok=False)

    # Get a list of files and directories
    selected_names, selected_prefixes = get_names_prefixes_in_selected(q)

    use_zip = True
    dir_to_zip = download_dir

    # If downloading a single file, don't zip
    if not selected_prefixes and len(selected_names) == 1:
        use_zip = False

    # Work with all the individual files in the selection
    file_paths = []
    names = []
    for name in selected_names:
        file_paths.append(os.path.join(download_dir, os.path.basename(name)))
        names.append(name)

    # Work with all the directories in the selection
    for prefix in selected_prefixes:
        selected_dir_path = os.path.dirname(prefix)
        selected_dir_name = os.path.basename(selected_dir_path)

        # If downloading a single directory, create the zip with the same name
        if not selected_names and len(selected_prefixes) == 1:
            prefix_dir = os.path.join(download_dir, f'{selected_dir_name}_{now()}')
            dir_to_zip = prefix_dir
        else:
            prefix_dir = os.path.join(download_dir, selected_dir_name)

        os.makedirs(prefix_dir, exist_ok=False)

        # Get the list of all objects inside the selected dir
        object_list = q.user.user.bucket.list(prefix=prefix, recursive=True)
        for object in object_list:
            # Get name of this object
            object_name = object.object_name
            # print(f'object_name: {object_name}')

            # Get the parent directory path of this object
            object_dirname = os.path.dirname(object_name)
            # Get its parent directory path relative to the selected dir
            object_dirname_relative = os.path.relpath(
                object_dirname, start=selected_dir_path
            )
            # Join the relative path to the download dir path
            download_dir_relpath = os.path.join(prefix_dir, object_dirname_relative)
            # Normalize it to get the final path inside the download dir
            new_path_normalized = os.path.normpath(download_dir_relpath)
            # Create the dir inside the download dir if it does not exist
            os.makedirs(new_path_normalized, exist_ok=True)
            # Skip all the .ignoreme files
            if not object_name.endswith('/.ignoreme'):
                names.append(object_name)
                file_paths.append(
                    os.path.join(new_path_normalized, os.path.basename(object_name))
                )

    return names, file_paths, dir_to_zip, use_zip


def get_expiration_time(days, hours, minutes, max_days=7):
    expiration_time = timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
    )
    if 0 < expiration_time.total_seconds() <= timedelta(days=max_days).total_seconds():
        return expiration_time


def get_minio_share_link(q: Q, expiration_time):
    current_path = q.client.path[q.client.path_pointer]
    object_name = os.path.join(current_path, q.client.selected_objects[0])
    share_link = q.user.user.bucket.share(object_name, expiration_time)
    return object_name, share_link


def get_connector_table_rows(q: Q):
    connector_row_data = []
    for k, v in q.app.connectors.items():
        if k in q.user.user.connectors:
            row = [
                str(y)
                for y in q.user.user.connectors[k].to_list(
                    keys=['_name', '_tested', '_configured', '_favorite']
                )
            ]
        else:
            row = [
                str(y)
                for y in v.to_list(
                    keys=['_name', '_tested', '_configured', '_favorite']
                )
            ]
        connector_row_data.append(row)
    return list_to_table_rows(connector_row_data)


async def make_connector_table(q: Q):
    # q.page['objects'].box = ''
    # await q.page.save()
    # q.page['config_connectors'].box = 'main_center'
    # await q.page.save()

    # Clear existing objects table
    del q.page['objects']
    del q.page['path_tabs']
    # Create Connector table
    q.page['connectors'] = get_connector_table_form()
    q.page['connectors'].items[0].table.rows = get_connector_table_rows(q)
    # Update commands
    q.page['commands'].items = get_connector_table_commands()
    # q.page['commands'].secondary_items = get_secondary_commands(settings=False)
    q.page['commands'].secondary_items = []
    await q.page.save()


async def clear_settings(q: Q):
    # q.page['config_connectors'].box = ''
    # q.page['objects'].box = 'main_center'
    # await q.page.save()

    # Remove Connectors table
    del q.page['connectors']
    # Create Objects table
    q.page['objects'] = get_object_table_form()
    # Update commands
    q.page['commands'].items = get_primary_commands(q)
    q.page['commands'].secondary_items = get_secondary_commands(q)
    # Update Objects table and actions
    await update_object_table(q)
    await update_object_actions(q)
    await update_path(q)
    # await q.page.save()


async def make_connector_config_card(q: Q, connector_name):
    del q.page['connectors']
    q.page['connector_config'] = get_connector_config_form(connector_name)

    favorite = None
    if connector_name in q.user.user.connectors:
        favorite = q.user.user.connectors[connector_name].favorite
    q.page['commands'].items = get_connector_config_commands(q, favorite)

    driver_params = dict(connector_name={})

    # QDB: skip first_step
    q.args.handle_selected_source = True
    q.args.dropdown = connector_name

    # TODO: Confirm how this is working without save
    # await q.page.save()


async def update_favorite(q: Q):
    connector_name = q.client.selected_connector
    if connector_name in q.user.user.connectors:
        q.user.user.connectors[connector_name].favorite = not q.user.user.connectors[
            connector_name
        ].favorite
        favorite = q.user.user.connectors[connector_name].favorite
        q.page['commands'].items = get_connector_config_commands(q, favorite)
    await q.page.save()


async def clear_connector_config(q: Q):
    del q.page['connector_config']
    q.page['connectors'] = get_connector_table_form()
    q.page['connectors'].items[0].table.rows = get_connector_table_rows(q)
    q.page['commands'].items = get_connector_table_commands()
    q.page['commands'].secondary_items = []
    await q.page.save()


async def save_connector_config(q: Q):
    pass


async def make_import_wizard_card(q: Q):

    # Clear existing objects table
    del q.page['objects']

    connector_name = q.client.import_from

    q.page['commands'].items = get_import_wizard_commands()
    q.page['commands'].secondary_items = []

    # Create import wizard
    q.page['import_wizard'] = get_connector_config_form(connector_name)
    await q.page.save()

    driver_params = q.user.user.connectors[connector_name].configuration
    print(driver_params)


async def clear_import_wizard(q: Q):
    # Remove Connectors table
    del q.page['import_wizard']
    # Create Objects table
    q.page['objects'] = get_object_table_form()
    # Update commands
    q.page['commands'].items = get_primary_commands(q)
    q.page['commands'].secondary_items = get_secondary_commands(q)
    # Update Objects table and actions
    await update_object_table(q)
    await update_object_actions(q)
    await q.page.save()


async def save_odbc_data(q: Q):
    connector_name = q.client.import_from
    table_name = q.args.table_id

    driver_params = q.user.user.connectors[connector_name].configuration
    df = None
    if df is None:
        await make_ingest_failed_dialog(q, connector_name, table_name)
        return

    if table_name:
        filename = f'{make_valid_name(connector_name)}_{table_name}_{now()}.csv'
    else:
        filename = f'{make_valid_name(connector_name)}_{now()}.csv'

    file_path = os.path.join(q.user.user.user_dir, filename)
    df.to_csv(file_path, index=False)
    return file_path


async def preview_csv(q: Q, object_names, file_paths):
    obj_info = q.user.user.bucket.download(object_names[0], file_paths[0])
    df = pd.read_csv(file_paths[0])

    # Clear existing objects table
    del q.page['objects']
    del q.page['path_tabs']

    q.page['commands'].items = get_preview_commands()
    q.page['commands'].secondary_items = []

    # Create import wizard
    q.page['preview'] = get_df_preview_form(
        os.path.basename(file_paths[0]), df.head(15)
    )
    await clear_selections(q)
    await update_object_actions(q)
    # await q.page.save()


async def clear_preview(q: Q):
    # Remove Connectors table
    del q.page['preview']
    # Create Objects table
    q.page['objects'] = get_object_table_form()
    # Update commands
    q.page['commands'].items = get_primary_commands(q)
    q.page['commands'].secondary_items = get_secondary_commands(q)
    # Update Objects table and actions
    await update_object_table(q)
    await update_path(q)
    # await update_object_actions(q)
    # await q.page.save()
