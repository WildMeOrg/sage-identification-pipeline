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
        box='title',
        title='hey',
        subtitle='sblibbl',
        items=[],
    )


def make_tabs(tab_data):
    return [ui.tab(**x) for x in tab_data]


def get_path_tabs(items=None, value=None):
    return ui.tab_card(
        box='path',
        name='path_tabs',
        items=items or make_tabs([dict(name='/', label='', icon='Home')]),
        value=value or '/',
        link=False,
    )


def get_secondary_commands(q: Q):
    # return [
    #     ui.command(
    #         name='settings',
    #         label='',
    #         icon='Settings',
    #         caption='Settings',
    #         items=[
    #             ui.command(
    #                 name='configure_connectors',
    #                 label='Connectors',
    #                 icon='Plug',
    #                 caption='Configure Data Connectors',
    #             ),
    #         ],
    #     ),
    # ]
    return [
        ui.command(
            name='relative_timestamps',
            label='Use Relative Time',
            icon='Timeline',
            caption='Switch to relative timestamps',
        ),
        ui.command(
            name='configure_connectors',
            label='Connectors',
            icon='Plug',
            caption='Configure Data Connectors',
        ),
    ]


def get_connector_config_commands(q: Q, favorite=None):
    items = [
        ui.command(
            name='close_connector_config',
            label='Back',
            icon='Back',
            caption='Back',
        ),
    ]
    if favorite is not None:
        items.append(
            ui.command(
                name='favorite_connector',
                label='Add to Favorites',
                icon='HeartFill' if favorite else 'Heart',
                caption='Add Connector to Favorites',
            )
        )
    return items


def get_primary_commands(q: Q):
    favorite_connectors = [
    ]
    more_items = [
    ]
    if more_items:
        more_connectors = [
            ui.command(
                name='more_connectors',
                label='More',
                icon='More',
                items=more_items,
            )
        ]
    else:
        more_connectors = []
    items = [
        ui.command(name='nav_back', label='', icon='Back', caption='Back'),
        ui.command(name='nav_forward', label='', icon='Forward', caption='Forward'),
        ui.command(name='refresh', label='', icon='Refresh', caption='Refresh'),
        ui.command(
            name='import_from',
            label='Add',
            icon='Add',
            caption='Add to Ocean',
            items=[
                ui.command(
                    name='file_upload',
                    label='Upload',
                    icon='CloudUpload',
                    caption='Upload files from your computer to Ocean',  # noqa: E501
                ),
                ui.command(
                    name='import_from_url',
                    label='Import from a URL',
                    icon='AddLink',
                    caption='Import from a URL into your Ocean',  # noqa: E501
                ),
            ]
            + favorite_connectors
            + more_connectors,
        ),
        ui.command(
            name='create_folder',
            label='Create Folder',
            icon='FabricNewFolder',
            caption='Create Folder',
        ),
        ui.command(
            name='multi_select',
            label='Select',
            icon=q.client.multi_select_icon,
            caption='Select multiple',
        ),
        # ui.command(name='search', label='Search', icon='Search'),
    ]
    return items


def get_toolbar(q: Q):
    return ui.toolbar_card(
        box=ui.box('commands', order=1, width='100%'),
        items=get_primary_commands(q),
        secondary_items=get_secondary_commands(q),
    )


def get_object_actions_bar(q: Q):
    return ui.toolbar_card(
        box=ui.box('commands', order=2),  # , width='320px'),
        items=[
            ui.command(name='preview_imported', label='Preview', icon='SeeDo'),
            ui.command(name='share', label='Share', icon='Share'),
            ui.command(name='download', label='Download', icon='Download'),
            ui.command(name='delete', label='Delete', icon='Delete'),
        ],
    )


def get_connector_table_commands():
    return [
        ui.command(
            name='close_settings',
            label='Back',
            icon='Back',
            caption='Close Settings',
        ),
    ]


def get_import_wizard_commands():
    return [
        ui.command(
            name='close_import_wizard',
            label='Back',
            icon='Back',
            caption='Cancel Import',
        ),
    ]


def get_preview_commands():
    return [
        ui.command(
            name='close_preview',
            label='Back',
            icon='Back',
            caption='Close Preview',
        ),
    ]


def get_object_table_columns():
    columns = [
        ui.table_column(
            name='name',
            label='Name',
            max_width='230px',
            searchable=True,
            sortable=False,
        ),
        ui.table_column(name='type', label='Type', max_width='80px', filterable=True),
        ui.table_column(
            name='modified',
            max_width='200px',
            label='Modified',
        ),
        ui.table_column(
            name='size',
            max_width='110px',
            label='Size',
        ),
        ui.table_column(
            name='access', max_width='100px', label='Access', filterable=True
        ),
    ]
    return columns


def get_object_table_form():
    return ui.form_card(
        box=ui.box('main_center', order=1),  # height='100%'),
        items=[
            ui.table(
                name='object_table',
                columns=get_object_table_columns(),
                rows=[],
                height='800px',  # Need this so that table occupies a fixed space regardless of number of rows  # noqa: E501
                # height='100%',  # Will make table disappear
                multiple=False,
                values=None,
            )
        ],
    )


def get_upload_box_form():
    return ui.form_card(
        # box=ui.box('main_top', order=1, height='400px', width='100%'),
        box=ui.box('main_top', order=1),
        items=[
            ui.buttons(
                items=[
                    ui.button(
                        name='file_upload_cancel',
                        label='Close',
                        primary=True,
                    )
                ],
                justify='end',
            ),
            ui.file_upload(name='user_files', label='Upload', multiple=True),
        ],
    )


def get_footer():
    return ui.footer_card(
        box=ui.box('footer', order=1),
        caption='Made with 💛️ using [Wave](https://h2oai.github.io/wave/). (c) 2021 H2O.ai. All rights reserved.',  # noqa: E501
    )


def list_to_table_rows(rows, name_col_index=0):
    table_rows = [ui.table_row(name=x[name_col_index], cells=x) for x in rows]
    return table_rows


async def make_create_folder_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Create Folder',
        items=[
            ui.textbox(name='folder_name', label='Folder Name'),
            ui.buttons(
                items=[
                    ui.button(name='create_now', label='Create', primary=True),
                    ui.button(name='cancel_create_now', label='Cancel', primary=False),
                ],
                justify='start',
            ),
        ],
    )
    await q.page.save()


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


def get_driver_table_columns():
    return [
        ui.table_column(
            name='name',
            label='Name',
            max_width='200px',
            searchable=True,
            sortable=True,
            link=True,
        ),
        ui.table_column(
            name='tested',
            label='Tested',
            max_width='100px',
            filterable=True,
        ),
        ui.table_column(
            name='configured',
            label='Configured',
            max_width='100px',
            filterable=True,
        ),
        ui.table_column(
            name='favorite',
            label='Favorite',
            max_width='100px',
            filterable=True,
        ),
    ]


def get_connector_table_form():
    return ui.form_card(
        box=ui.box('main_center', order=1),
        title='Configure Data Connectors',
        items=[
            ui.table(
                name='driver_table',
                columns=get_driver_table_columns(),
                rows=[],
                height='800px',
                multiple=False,
                groupable=False,
                resettable=True,
                tooltip='A table of all the available Data Connectors',
            ),
        ],
    )


def get_connector_config_form(driver_name):
    connector_form = ui.form_card(
        box=ui.box('main_center', order=1, height=f'{800}px', width='100%'),
        title=driver_name,
        items=[],
    )
    return connector_form


def get_search_bar():
    return ui.form_card(
        box=ui.box('main_top', order=1),
        items=[
            ui.textbox(name='search_objects', label='', icon='Search'),
        ],
    )


async def make_ingest_completed_dialog(q: Q, file_path):
    q.page['meta'].dialog = None
    await q.page.save()
    q.client.selected_objects = [os.path.basename(file_path)]
    q.page['meta'].dialog = ui.dialog(
        title='Import from QDB Connector',
        items=[
            ui.message_bar(
                type='success',
                text=(f'Successfully imported {os.path.basename(file_path)}'),
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='preview_imported',
                        label='Show Preview',
                        primary=False,
                    ),
                    ui.button(
                        name='cancel_import_from_qdb',
                        label='Close',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


async def make_ingest_failed_dialog(q: Q, connector_name, table_name):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Import from QDB Connector',
        items=[
            ui.message_bar(
                type='danger',
                text=(f'Importing {table_name} from {connector_name} Failed!'),
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='cancel_import_from_qdb',
                        label='Close',
                        primary=True,
                    ),
                ],
                justify='center',
            ),
        ],
    )
    await q.page.save()


def df_to_table(df):
    row_data = df.values.tolist()
    row_data_str = [[str(x) for x in row] for row in row_data]
    return ui.table(
        name='object_table',
        columns=[
            ui.table_column(
                name=x,
                label=x,
            )
            for x in df.columns
        ],
        rows=list_to_table_rows(row_data_str),
        height='800px',
        multiple=False,
        values=None,
    )


def get_df_preview_form(filename, df):
    return ui.form_card(
        box=ui.box('main_center', order=1, height=f'{800}px', width='100%'),
        title=filename,
        items=[df_to_table(df)],
    )
