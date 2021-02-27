import os

from h2o_wave import Q, ui

from .layouts import get_layouts
from .wave_utils import WaveColors


def get_meta(side_panel=False):
    return ui.meta_card(
        box='',
        title='Sage Identification Pipeline',
        layouts=get_layouts(side_panel=side_panel),
    )


def get_header():
    return ui.header_card(
        box='header',
        title='Sage Identification Pipeline',
        subtitle='Object storage for H2O-AI-Cloud',
        icon='Lifesaver',
        icon_color=WaveColors.tangerine,
    )


def get_title(q: Q):
    return ui.section_card(
        box='header',
        title='Sage Identification Pipeline',
        subtitle='Created by Wild Me for the Wave App Store',
        items=[],
    )


def get_target_image(q: Q):
    return ui.form_card(
        box='left',
        title='Target image',
        items=[
            ui.file_upload(
                name='Target image upload',
                label='Upload target image',
                file_extensions=['jpg', 'png'],
                height='180px',
            )
        ],
    )


def get_action_card(q: Q):
    return ui.form_card(
        box='right',
        title='Parameters',
        items=[
            ui.toggle(name='hyperspeed', label='Use hyperspeed'),
            ui.toggle(name='warp', label='Attend warp tour'),
            ui.toggle(name='dogs', label='Pet dogs'),
            ui.button(name='run', label='Run identification pipeline'),
        ],
    )


def get_stepper(q: Q):
    return ui.form_card(
        box='footer',
        items=[
            ui.stepper(
                name='almost-done-stepper',
                items=[
                    ui.step(label='Upload', icon='CloudUpload'),
                    ui.step(label='Detection', icon='BuildQueueNew'),
                    ui.step(label='Identification', icon='BranchCompare'),
                ],
            )
        ],
    )


def get_results_columns():
    columns = [
        ui.table_column(
            name='individual',
            label='Individual',
            max_width='160px',
            searchable=True,
            sortable=True,
        ),
        ui.table_column(
            name='avg',
            label='Avg. score',
            max_width='100px',
            sortable=True,
        ),
        ui.table_column(
            name='curvrank',
            label='Curvrank score',
            max_width='100px',
            sortable=True,
        ),
        ui.table_column(
            name='finfindr',
            label='finFindR score',
            max_width='100px',
            sortable=True,
        ),
    ]
    return columns


def get_results_table():
    return ui.form_card(
        box=ui.box('footer'),  # height='100%'),
        items=[
            ui.table(
                name='results_table',
                columns=get_results_columns(),
                rows=[],
                height='400px',  # Need this so that table occupies a fixed space regardless of number of rows  # noqa: E501
                # height='100%',  # Will make table disappear
                multiple=False,
                values=None,
            )
        ],
    )


def get_footer():
    return ui.footer_card(
        box=ui.box('footer', order=1),
        caption='Made with 💛️ using [Wave](https://h2oai.github.io/wave/). (c) 2021 [Wild Me](https://www.wildme.org/). All rights reserved.',  # noqa: E501
    )


async def make_import_from_url_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import From a URL',
        items=[
            ui.textbox(name='object_url', label='URL'),
            ui.buttons(
                items=[
                    ui.button(name='import_from_url_now', label='Import', primary=True),
                    ui.button(
                        name='cancel_import_from_url_now', label='Cancel', primary=False
                    ),
                ],
                justify='start',
            ),
        ],
    )
    await q.page.save()


async def make_wait_for_import_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import From a URL',
        items=[
            ui.text('Please wait while your file is being imported ...'),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_import_from_url_now',
                        label='Close',
                        primary=True,
                        disabled=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_import_failed_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import From a URL',
        items=[
            ui.message_bar(
                type='danger',
                text=(
                    'Error while importing file.'
                    'Please check the import link or try again later.'
                ),
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_import_from_url_now',
                        label='Close',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_invalid_import_link_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import From a URL',
        items=[
            ui.message_bar(type='danger', text='Invalid import link'),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_import_from_url_now', label='Close', primary=True
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_import_completed_dialog(q: Q, file_path):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import From a URL',
        items=[
            ui.message_bar(
                type='success',
                text=(
                    f'Successfully imported {os.path.basename(file_path)}'
                    f' as {q.client.path[q.client.path_pointer]}'
                ),
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_import_from_url_now',
                        label='Close',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_delete_confirm_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Delete Objects',
        items=[
            ui.message_bar(
                type='danger',
                text='Are you sure you want to delete? This cannot be undone!',
            ),
            ui.buttons(
                items=[
                    ui.button(name='delete_now', label='Yes! Delete.', primary=True),
                    ui.button(name='cancel_delete_now', label='No', primary=False),
                ],
                justify='start',
            ),
        ],
    )
    await q.page.save()


async def make_delete_failed_dialog(q: Q, errors):
    q.page['meta'].dialog = None
    await q.page.save()
    error_messages = [ui.message_bar(type='danger', text=x) for x in errors]

    q.page['meta'].dialog = ui.dialog(
        title='Deleting Objects Failed!',
        items=error_messages
        + [
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_delete_now',
                        label='Close',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_can_not_download_dialog(q: Q, error_msg):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Download',
        items=[
            ui.message_bar(
                type='danger',
                text=error_msg,
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='close_download_dialog', label='Close', primary=True
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_wait_for_download_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Download',
        items=[
            ui.text('Please wait while your Download is being prepared ...'),
            ui.buttons(
                items=[
                    ui.button(
                        name='close_download_dialog',
                        label='Close',
                        primary=True,
                        disabled=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_download_links_dialog(q: Q, wave_file_paths):
    q.page['meta'].dialog = None
    await q.page.save()
    # print(wave_file_paths)
    if wave_file_paths:
        download_links = [
            ui.link(label=os.path.basename(x), path=x, download=True)
            for x in wave_file_paths
        ]
    else:
        download_links = [
            ui.message_bar(type='danger', text='Did not find any objects to download.')
        ]
    dialog_items = download_links + [
        ui.buttons(
            items=[
                ui.button(name='close_download_dialog', label='Close', primary=True),
            ],
            justify='center',
        ),
    ]
    q.page['meta'].dialog = ui.dialog(
        title='Download',
        items=dialog_items,
    )
    await q.page.save()


async def make_can_not_share_dialog(q: Q, error_msg):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Share Object',
        items=[
            ui.message_bar(
                type='danger',
                text=error_msg,
            ),
            ui.buttons(
                items=[
                    ui.button(name='cancel_share_link', label='Close', primary=True),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_share_object_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Share Object',
        items=[
            ui.text('Expires in (Max 7 days)'),
            ui.inline(
                items=[
                    ui.spinbox(
                        name='expire_days', label='Days', min=0, max=7, step=1, value=5
                    ),
                    ui.spinbox(
                        name='expire_hours',
                        label='Hours',
                        min=0,
                        max=23,
                        step=1,
                    ),
                    ui.spinbox(
                        name='expire_minutes',
                        label='Minutes',
                        min=0,
                        max=59,
                        step=1,
                    ),
                ]
            ),
            ui.buttons(
                items=[
                    ui.button(name='get_share_link', label='Share', primary=True),
                    ui.button(name='cancel_share_link', label='Cancel', primary=False),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_wait_for_share_link_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Share Object',
        items=[
            ui.text('Please wait while your Share Link is being created ...'),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_share_link',
                        label='Close',
                        primary=True,
                        disabled=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_invalid_expiration_time_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Share Object',
        items=[
            ui.message_bar(type='danger', text='Please select a valid Expiration Time'),
            ui.buttons(
                items=[
                    ui.button(name='cancel_share_link', label='Close', primary=True),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_share_link_dialog(q: Q, object_name, share_link):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Share Object',
        items=[
            ui.textbox(
                name='object_share_link_textbox',
                label=object_name,
                value=share_link,
                multiline=True,
                height='180px',
            ),
            ui.buttons(
                items=[
                    ui.button(name='cancel_share_link', label='Close', primary=True),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()
