from typing import Any

from h2o_wave import Q
from h2o_wave.core import expando_to_dict

from .common import (
    clear_connector_config,
    clear_dialog,
    clear_import_wizard,
    clear_preview,
    clear_selections,
    clear_settings,
    clear_upload_box,
    delete_selected,
    download_to_local_storage,
    enable_multi_select,
    get_expiration_time,
    get_minio_share_link,
    make_base_ui,
    make_connector_config_card,
    make_connector_table,
    make_import_wizard_card,
    make_upload_box,
    minio_to_waved,
    multi_select_disabled,
    prep_empty_folder,
    prep_for_download,
    preview_csv,
    save_odbc_data,
    set_path_pointer,
    step_into_folder,
    update_favorite,
    update_object_actions,
    update_object_table,
    update_path,
    upload_to_minio,
    waved_to_minio,
)
from .components import (
    get_search_bar,
    get_secondary_commands,
    make_can_not_download_dialog,
    make_can_not_share_dialog,
    make_create_folder_dialog,
    make_delete_confirm_dialog,
    make_delete_failed_dialog,
    make_download_links_dialog,
    make_import_completed_dialog,
    make_import_failed_dialog,
    make_import_from_url_dialog,
    make_ingest_completed_dialog,
    make_invalid_expiration_time_dialog,
    make_invalid_import_link_dialog,
    make_share_link_dialog,
    make_share_object_dialog,
    make_wait_for_download_dialog,
    make_wait_for_import_dialog,
)
from .wave_utils import clear_cards, handler


@handler()
async def user_files(q: Q):
    await waved_to_minio(q, q.args.user_files)
    await clear_upload_box(q)
    await update_object_table(q)


@handler()
async def error_report(q: Q):
    clear_cards(q)
    await make_base_ui(q)
    await update_object_table(q)


@handler()
async def refresh(q: Q):
    await clear_selections(q)
    await update_path(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def path_tabs(q: Q):
    set_path_pointer(q)
    await clear_selections(q)
    await update_path(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def nav_forward(q: Q):
    q.client.path_pointer = min(len(q.client.path) - 1, q.client.path_pointer + 1)
    await clear_selections(q)
    await update_path(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def nav_back(q: Q):
    q.client.path_pointer = max(0, q.client.path_pointer - 1)
    await clear_selections(q)
    await update_path(q)
    await update_object_table(q)
    await update_object_actions(q)


def not_in_multi_select_mode(q: Q, *args: Any, **kwargs: Any) -> bool:
    return (
        q.args.object_table
        and not q.args.multi_select
        and multi_select_disabled(q)
        and len(q.args.object_table) == 1
        and not q.args.refresh
        and not q.args.path_tabs
        and not q.args.nav_forward
        and not q.args.nav_back
        and not q.args.share
        and not q.args.download
        and not q.args.delete
        and not q.args.delete_now
        and not q.args.preview_imported
    )


@handler(not_in_multi_select_mode)
async def object_table(q: Q):
    if q.args.object_table[0].endswith('/'):
        step_into_folder(q)
    else:
        enable_multi_select(q)
        q.client.selected_objects = q.args.object_table
    await q.page.save()
    await update_path(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def multi_select(q: Q):
    if multi_select_disabled(q):
        enable_multi_select(q)
    else:
        await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def create_folder(q: Q):
    await clear_selections(q)
    await update_object_table(q)
    await make_create_folder_dialog(q)


def is_folder_name_valid(q: Q, *args: Any, **kwargs: Any) -> bool:
    return q.args.folder_name is not None


@handler(is_folder_name_valid)
async def create_now(q: Q):
    q.page['meta'].dialog = None
    await clear_selections(q)
    prep_empty_folder(q)
    await update_object_table(q)


@handler()
async def cancel_create_now(q: Q):
    await clear_dialog(q)


@handler()
async def file_upload(q: Q):
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)
    await make_upload_box(q)


@handler()
async def file_upload_cancel(q: Q):
    await clear_upload_box(q)


@handler()
async def import_from_url(q: Q):
    await clear_selections(q)
    await update_object_table(q)
    await make_import_from_url_dialog(q)


@handler()
async def import_from_url_now(q: Q):
    await make_wait_for_import_dialog(q)
    is_import_url_valid = q.args.object_url is not None and len(q.args.object_url) > 1
    if is_import_url_valid:
        try:
            file_path = download_to_local_storage(q, q.args.object_url)
        except Exception as e:
            print(e)
            await make_import_failed_dialog(q)
        else:
            upload_to_minio(q, file_path)
            await update_object_table(q)
            await make_import_completed_dialog(q, file_path)
    else:
        await make_invalid_import_link_dialog(q)


@handler()
async def cancel_import_from_url_now(q: Q):
    await clear_dialog(q)


@handler()
async def delete(q: Q):
    # TODO: Check if q.args.object_table can be directly passed to update_object_table
    q.client.selected_objects = q.args.object_table
    await update_object_table(q)

    await make_delete_confirm_dialog(q)


@handler()
async def delete_now(q: Q):
    await clear_dialog(q)
    errors = delete_selected(q)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)
    if errors:
        await make_delete_failed_dialog(q, errors)


@handler()
async def cancel_delete_now(q: Q):
    await clear_dialog(q)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def download(q: Q):
    q.client.selected_objects = q.args.object_table
    await update_object_table(q)

    if not q.args.object_table:
        await make_can_not_download_dialog(q, 'Please select an object to download')
        return

    await make_wait_for_download_dialog(q)
    object_names, file_paths, download_dir, use_zip = prep_for_download(q)
    # TODO: If object_names is empty, show warning
    wave_file_paths = minio_to_waved(q, object_names, file_paths, download_dir, use_zip)
    await make_download_links_dialog(q, wave_file_paths)


@handler()
async def close_download_dialog(q: Q):
    await clear_dialog(q)
    if q.client.wave_file_paths is not None:
        for x in q.client.wave_file_paths:
            await q.site.unload(x)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def share(q: Q):
    q.client.selected_objects = q.args.object_table
    await update_object_table(q)

    if not q.args.object_table:
        await make_can_not_share_dialog(q, 'Please select an object to share')
    elif len(q.args.object_table) > 1:
        await make_can_not_share_dialog(
            q, 'Can not share more than one object at a time'
        )
    elif q.args.object_table[0].endswith('/'):
        await make_can_not_share_dialog(q, 'Can not share a folder')
    else:
        await make_share_object_dialog(q)


@handler()
async def get_share_link(q: Q):
    # await make_wait_for_share_link_dialog(q)
    expiration_time = get_expiration_time(
        days=q.args.expire_days,
        hours=q.args.expire_hours,
        minutes=q.args.expire_minutes,
    )
    if not expiration_time:
        await make_invalid_expiration_time_dialog(q)
    else:
        object_name, share_link = get_minio_share_link(q, expiration_time)
        await make_share_link_dialog(q, object_name, share_link)


@handler()
async def cancel_share_link(q: Q):
    await clear_dialog(q)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def configure_connectors(q: Q):
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)
    await make_connector_table(q)


@handler()
async def close_settings(q: Q):
    await clear_settings(q)


@handler()
async def driver_table(q: Q):
    connector_name = q.args.driver_table[0]
    q.client.selected_connector = connector_name
    await make_connector_config_card(q, connector_name)


def is_close_connector_config(q: Q, *args: Any, **kwargs: Any) -> bool:
    return q.args.close_connector_config or (
        q.args.show_first_step
        and q.client.selected_connector
        and not q.client.import_from
    )


@handler(is_close_connector_config)
async def close_connector_config(q: Q):
    q.client.selected_connector = None
    await clear_connector_config(q)


@handler()
async def favorite_connector(q: Q):
    await update_favorite(q)


@handler()
async def save_configuration(q: Q):
    pass


def is_import_from(q: Q, *args: Any, **kwargs: Any) -> bool:
    for k, v in expando_to_dict(q.args).items():
        if v and k.startswith('import_from_') and 'url' not in k:
            q.client.import_from = k.split('import_from_')[-1]
            return True
    return False


@handler(is_import_from)
async def import_wizard(q: Q):
    await make_import_wizard_card(q)


@handler()
async def ingest_from_odbc(q: Q):
    file_path = await save_odbc_data(q)
    if file_path is not None:
        upload_to_minio(q, file_path)
    q.client.import_from = None
    await clear_import_wizard(q)
    if file_path is not None:
        await make_ingest_completed_dialog(q, file_path)


@handler()
async def cancel_import_from_qdb(q: Q):
    await clear_dialog(q)


@handler()
async def preview_imported(q: Q):
    await clear_dialog(q)
    if not q.client.selected_objects and q.args.object_table:
        q.client.selected_objects = q.args.object_table
        await update_object_table(q)

    if q.client.selected_objects and q.client.selected_objects[0].endswith('.csv'):
        object_names, file_paths, *_ = prep_for_download(q)
        await preview_csv(q, object_names, file_paths)
    else:
        await clear_selections(q)
        await update_object_table(q)
        await update_object_actions(q)


def is_close_import_wizard(q: Q, *args: Any, **kwargs: Any) -> bool:
    return q.args.close_import_wizard or (
        q.args.show_first_step
        and q.client.import_from
        and not q.client.selected_connector
    )


@handler(is_close_import_wizard)
async def close_import_wizard(q: Q):
    q.client.import_from = None
    await clear_import_wizard(q)


@handler()
async def close_preview(q: Q):
    q.client.selected_objects = None
    await clear_preview(q)


@handler()
async def search(q: Q):
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)
    # q.page['objects'].items[0].table.columns[0].searchable = True
    q.page['search_bar'] = get_search_bar()
    await q.page.save()


@handler()
async def relative_timestamps(q: Q):
    q.user.user.relative_timestamps = True
    q.page['commands'].secondary_items = get_secondary_commands(q)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)


@handler()
async def absolute_timestamps(q: Q):
    q.user.user.relative_timestamps = False
    q.page['commands'].secondary_items = get_secondary_commands(q)
    await clear_selections(q)
    await update_object_table(q)
    await update_object_actions(q)
