import os
from typing import Any

from h2o_wave import Q
from h2o_wave.core import expando_to_dict
from .wave_utils import clear_cards, handler
from .components import make_candidate_dialog

@handler()
async def user_files(q: Q):
    print(q.args.user_files)
    links = q.args.user_files
    if links:
      for link in links:
        local_path = await q.site.download(link, '.')
        print(local_path)
        print(os.path.basename(local_path))
    await q.page.save()

@handler()
async def run(q: Q):
   model_tag = q.args.model_tag
   nms = q.args.nms
   sensitivity = q.args.sensitivity
   print(f'model tag: {model_tag}, nms: {nms}, sensitivity: {sensitivity}')
   await q.page.save()

@handler()
async def results_table(q: Q):
   await make_candidate_dialog(q)
   await q.page.save()

@handler()
async def close_dialog(q: Q):
   q.page['meta'].dialog = None
   await q.page.save()

@handler()
async def error_report(q: Q):
    await q.page.save()


@handler()
async def refresh(q: Q):
   await q.page.save() 


@handler()
async def path_tabs(q: Q):
   await q.page.save() 


@handler()
async def nav_forward(q: Q):
   await q.page.save() 


@handler()
async def nav_back(q: Q):
   await q.page.save() 


@handler()
async def object_table(q: Q):
   await q.page.save() 


@handler()
async def multi_select(q: Q):
   await q.page.save() 


@handler()
async def create_folder(q: Q):
   await q.page.save() 


def is_folder_name_valid(q: Q, *args: Any, **kwargs: Any) -> bool:
   return True 


@handler(is_folder_name_valid)
async def create_now(q: Q):
   await q.page.save() 


@handler()
async def cancel_create_now(q: Q):
   await q.page.save() 

@handler()
async def file_upload(q: Q):
   await q.page.save() 


@handler()
async def file_upload_cancel(q: Q):
   await q.page.save() 

@handler()
async def import_from_url(q: Q):
   await q.page.save() 


@handler()
async def import_from_url_now(q: Q):
    await q.page.save()


@handler()
async def cancel_import_from_url_now(q: Q):
   await q.page.save() 

@handler()
async def delete(q: Q):
   await q.page.save() 


@handler()
async def delete_now(q: Q):
   await q.page.save() 


@handler()
async def cancel_delete_now(q: Q):
   await q.page.save() 


@handler()
async def download(q: Q):
    await q.page.save()


@handler()
async def close_download_dialog(q: Q):
   await q.page.save() 


@handler()
async def share(q: Q):
   await q.page.save() 


@handler()
async def get_share_link(q: Q):
    await q.page.save()


@handler()
async def cancel_share_link(q: Q):
   await q.page.save() 


@handler()
async def configure_connectors(q: Q):
   await q.page.save() 


@handler()
async def close_settings(q: Q):
   await q.page.save() 


@handler()
async def driver_table(q: Q):
   await q.page.save() 



def is_close_connector_config(q: Q, *args: Any, **kwargs: Any) -> bool:
   return True 


@handler(is_close_connector_config)
async def close_connector_config(q: Q):
   await q.page.save() 


@handler()
async def favorite_connector(q: Q):
   await q.page.save()


@handler()
async def save_configuration(q: Q):
    await q.page.save()


def is_import_from(q: Q, *args: Any, **kwargs: Any) -> bool:
   return True


@handler(is_import_from)
async def import_wizard(q: Q):
   await q.page.save() 


@handler()
async def ingest_from_odbc(q: Q):
    await q.page.save()


@handler()
async def cancel_import_from_qdb(q: Q):
   await q.page.save() 


@handler()
async def preview_imported(q: Q):
   await q.page.save() 


@handler()
async def close_preview(q: Q):
   await q.page.save() 


@handler()
async def search(q: Q):
   await q.page.save() 


@handler()
async def relative_timestamps(q: Q):
   await q.page.save() 


@handler()
async def absolute_timestamps(q: Q):
   await q.page.save() 
