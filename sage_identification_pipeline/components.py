import os

from h2o_wave import Q, ui

from .layouts import get_layouts
from .wave_utils import WaveColors
from .constants import detection_model_tags, classification_model_tags


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
        subtitle='Created by Wild Me for the H2O.AI Hybrid Cloud Appstore',
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
            ui.dropdown(
                name='detection_model_tag',
                label='Detection model tag',
                choices=[ui.choice(name=x, label=x) for x in detection_model_tags],
            ),
            ui.dropdown(
                name='classification_model_tag',
                label='Classification model tag',
                choices=[ui.choice(name=x, label=x) for x in classification_model_tags],
            ),
            ui.slider(
                name='sensitivity',
                label='Sensitivity',
                min=0,
                max=1,
                value=0.5,
                step=0.01,
            ),
            ui.slider(
                name='nms',
                label='Non-maximal suppression (NMS)',
                min=0,
                max=1,
                value=0.5,
                step=0.01,
            ),
            ui.button(name='run', label='Run identification pipeline'),
        ],
    )


def get_stepper(q: Q):
    return ui.form_card(
        box='footer',
        items=[
            ui.stepper(
                name='pipeline-stepper',
                items=[
                    ui.step(label='Upload', icon='CloudUpload'),
                    ui.step(label='Detection', icon='BuildQueueNew'),
                    ui.step(label='Classification', icon='Compare'),
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
            sortable=True,
            link=True,
        ),
        ui.table_column(
            name='avg',
            label='Avg. score',
            sortable=True,
        ),
        ui.table_column(
            name='curvrank',
            label='Curvrank score',
            sortable=True,
        ),
        ui.table_column(
            name='finfindr',
            label='finFindR score',
            sortable=True,
        ),
    ]
    return columns


def get_results_table():
    fake_row_data = [
        ['abc', '232', '123', '42'],
        ['def', '232', '123', '42'],
        ['ghi', '232', '123', '42'],
    ]
    return ui.form_card(
        title='Identification results',
        box=ui.box('footer'),  # height='100%'),
        items=[
            ui.table(
                name='results_table',
                columns=get_results_columns(),
                rows=[ui.table_row(name=x[0], cells=x) for x in fake_row_data],
                # height='400px',  # Need this so that table occupies a fixed space regardless of number of rows  # noqa: E501
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
        items=[],
    )
    await q.page.save()


def generate_evidence_url(
    extern_reference, query_annot_uuid, database_annot_uuid, version
):
    api_prefix = 'https://demo.dyn.wildme.io'
    return f'{api_prefix}/api/query/graph/match/thumb/?extern_reference={extern_reference}&query_annot_uuid={query_annot_uuid}&database_annot_uuid={database_annot_uuid}&version={version}'


async def make_candidate_dialog(q: Q):
    extern_reference = 'angmvnjtzxbhuhta'
    query_annot_uuid = 'df1fde83-ff93-468b-be52-e7a94b48ef9a'
    database_annot_uuid = '5e494777-bf4d-485e-8c29-1026111b48b0'

    cleanUrl = generate_evidence_url(
        extern_reference, query_annot_uuid, database_annot_uuid, 'clean'
    )
    matchesUrl = generate_evidence_url(
        extern_reference, query_annot_uuid, database_annot_uuid, 'matches'
    )
    heatmaskUrl = generate_evidence_url(
        extern_reference, query_annot_uuid, database_annot_uuid, 'heatmask'
    )

    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Identification candidate',
        closable=True,
        items=[
            ui.text(content='Target image with candidate match'),
            ui.text(content=f'![target image with candidate image]({cleanUrl})'),
            ui.text(content='Hotspotter markup'),
            ui.text(
                content=f'![target image with candidate image and hotspotter markup]({matchesUrl})'
            ),
            ui.text(content='Hotspotter heatmap'),
            ui.text(
                content=f'![target image with candidate image and heatmap]({heatmaskUrl})'
            ),
            ui.button(name='close_dialog', label='Close', primary=True),
            ui.button(name='close_dialog', label='Close', primary=True),
            # Note: wave seems to be ignoring the last item in this list, hence the duplicate item.
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
