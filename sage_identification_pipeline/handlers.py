import os
from typing import Any
import asyncio

from h2o_wave import Q
from h2o_wave.core import expando_to_dict
from .wave_utils import clear_cards, handler
from .components import make_candidate_dialog, make_example_image_dialog, make_upload_image_dialog
from .common import make_base_ui
from .sage import post_target_image, fetch_image_uuid, fetch_image_size, run_pipeline


@handler()
async def target_image_upload(q: Q):
    links = q.args.target_image_upload
    if links:
        q.app.target_image = links[0]
        q.page['meta'].dialog = None
        await make_base_ui(q)


@handler()
async def run(q: Q):
    model_tag = q.args.model_tag
    nms = q.args.nms
    sensitivity = q.args.sensitivity
    local_image_path = await q.site.download(q.app.target_image, '.')

    await run_pipeline(q, local_image_path)

    # q.run(run_pipeline, q, image_uuid) # await it? https://h2oai.github.io/wave/docs/api/server/#h2o_wave.server.Query.run
    # loop = asyncio.get_event_loop()
    # loop.create_task(run_pipeline(q, image_uuid)) 
    # I expect that the print and q.page.save happen immediately after this is called, but 
    # that the wave program still shows a loading spinner because the main process is busy.
    # loop.run_in_executor(run_pipeline(q, image_uuid))
    
    print(f'model tag: {model_tag}, nms: {nms}, sensitivity: {sensitivity}')
    await q.page.save()

@handler()
async def example_image_chosen(q: Q):
    q.page['meta'].dialog = None
    q.app.target_image = q.args.example_image_selected
    await make_base_ui(q)

@handler()
async def reset_target_image(q: Q):
    await q.site.unload(q.app.target_image)
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
