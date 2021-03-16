import os
from typing import Any
import asyncio
import concurrent.futures

from h2o_wave import Q
from h2o_wave.core import expando_to_dict
from .wave_utils import clear_cards, handler
from .components import make_candidate_dialog, make_example_image_dialog, make_upload_image_dialog
from .common import make_base_ui
from .sage import post_target_image, fetch_image_uuid, fetch_image_size, run_pipeline
from .initializers import reset_pipeline_variables


@handler()
async def target_image_upload(q: Q):
    links = q.args.target_image_upload
    if links:
        q.app.target_image = links[0]
        q.page['meta'].dialog = None
        await make_base_ui(q)


@handler()
async def run(q: Q):
    local_image_path = await q.site.download(q.app.target_image, '.')
    q.app.running_pipeline = True
    await make_base_ui(q)

    await run_pipeline(q, local_image_path)

    # await q.run(run_pipeline, q, local_image_path)

    # with concurrent.futures.ThreadPoolExecutor() as pool:
    #     await q.exec(pool, run_pipeline, q, local_image_path)
    
    await q.page.save()

@handler()
async def example_image_chosen(q: Q):
    q.page['meta'].dialog = None
    q.app.target_image = q.args.example_image_selected
    await make_base_ui(q)

@handler()
async def reset_target_image(q: Q):
    # await q.site.unload(q.app.target_image)
    reset_pipeline_variables(q)
    q.app.target_image = None
    await make_base_ui(q)


@handler()
async def open_example_image_dialog(q: Q):
    await make_example_image_dialog(q)
    await q.page.save()

@handler()
async def open_upload_image_dialog(q: Q):
    await make_upload_image_dialog(q)
    await q.page.save()

@handler()
async def results_table(q: Q):
    await make_candidate_dialog(q)
    await q.page.save()


@handler()
async def close_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
