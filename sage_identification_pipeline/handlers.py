import os
from typing import Any

from h2o_wave import Q
from h2o_wave.core import expando_to_dict
from .wave_utils import clear_cards, handler
from .components import make_candidate_dialog, make_example_image_dialog, get_target_image_display, get_target_image
from .sage import fetch_db_numbers, post_target_image


@handler()
async def user_files(q: Q):
    print(q.args.user_files)
    print('here')
    links = q.args.user_files
    if links:
        q.app.target_image = await q.site.download(links[0], '.')
        q.page['target_image'] = get_target_image_display(q)
        
    await q.page.save()


@handler()
async def run(q: Q):
    model_tag = q.args.model_tag
    nms = q.args.nms
    sensitivity = q.args.sensitivity
    post_target_image()
    print(f'model tag: {model_tag}, nms: {nms}, sensitivity: {sensitivity}')
    await q.page.save()

@handler()
async def example_image_chosen(q: Q):
    q.page['meta'].dialog = None
    q.app.target_image = q.args.example_image_selected
    q.page['target_image'] = get_target_image_display(q)
    await q.page.save()

@handler()
async def reset_target_image(q: Q):
    q.app.target_image = None
    q.page['target_image'] = get_target_image(q)
    await q.page.save()

@handler()
async def open_example_image_dialog(q: Q):
    await make_example_image_dialog(q)
    await q.page.save()

@handler()
async def results_table(q: Q):
    await make_candidate_dialog(q)
    await q.page.save()


@handler()
async def close_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
