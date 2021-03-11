import os

from h2o_wave import Q, ui, graphics as g

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
            ui.text(''), # margin top hack
            ui.text('Sage will process the target image using pre-trained image analysis models. The detection model attempts to draw a box around each individual in the target image. The classification model vets the boxes (annotations) for quality. The identification model compares each annotation to our database of individuals to try to find matches.'),
            ui.button(
                name='open_upload_image_dialog',
                label='Upload target image',
                primary=True,
            ),
            ui.button(
                name='open_example_image_dialog',
                label='Use an example image',
            ),
        ],
    )

def get_target_image_display(q: Q):
    return ui.form_card(
        box='left',
        title='Target image',
        items=[
            ui.text(content=''), # margin top hack
            ui.text(content=f'![target image]({q.app.target_image})'),
            ui.button(name="reset_target_image", label="Reset target image")
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
                value='seadragon_v1',
            ),
            ui.dropdown(
                name='classification_model_tag',
                label='Classification model tag',
                choices=[ui.choice(name=x, label=x) for x in classification_model_tags],
                value='seadragon_v2',
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
            ui.button(name='run', label='Run identification pipeline', primary=True, disabled=not q.app.target_image),
        ],
    )


def get_stepper(q: Q):
    return ui.form_card(
        box='results',
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

def get_detection_progress_card(q: Q):
    return ui.form_card(
        box='detection',
        items=[
            ui.progress(label='Detection in progress', caption='Working...')
        ]
    )

def get_detection_card(q: Q):
    width = 100
    height = 100
    # print(q.app.image_size)
    return ui.graphics_card(
        # box='detection',
        # view_box=f'0 0 100 100',
        # width='100%',
        # height='100%',
        box= ui.box(zone='detection', height='300px'),
        view_box='0 0 70 800', height='100%', width='100%',
        stage=g.stage(
            arc=g.arc(r1=25, r2=50, a1=90, a2=180)
        )
        # stage=g.stage(
        #     # target = g.image(x='0', y='0', width=f'{width}', height=f'{height}'),
        #     annotation = g.rect(x='12', y='12', width='70', height='70', stroke='red', stroke_width='3px')
        # )
    )

def get_classification_progress_card(q: Q):
    return ui.form_card(
        box='svg',
        items=[
            ui.progress(label='Classification in progress', caption='Working...')
        ]
    )

def get_classification_card(q: Q):    
    if 'classification_results' in q.app and bool(q.app.classification_results):
        items = [ui.label(label='Classification results')]
        i = 1
        for a in q.app.classification_results:
            score = a['score']
            species = a['species_nice']
            viewpoint = a['viewpoint_nice']
            items.append(ui.separator(label=f'Annotation {i}'))
            items.append(ui.text_s(f'Score: {score:.3f}'))
            items.append(ui.text_s(f'Species: {species}'))
            items.append(ui.text_s(f'Viewpoint: {viewpoint}'))
            i += 1

        return ui.form_card(
            box='classification',
            items=items
        )
    else:
        return ui.form_card(
            box='classification',
            items=[
                ui.label(label='Classification results'),
                ui.text_s('No results to display'),
            ]
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

async def make_upload_image_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    q.page['meta'].dialog = ui.dialog(
        title='Upload target image',
        closable=True,
        items=[
            ui.file_upload(
                name='target_image_upload',
                label='Upload',
                file_extensions=['jpg', 'png', 'jpeg'],
                height='180px',
            ),
            ui.button(name='gah', label='gahh', primary=True),
            # Note: wave seems to be ignoring the last item in this list, hence the duplicate item.
        ]
    )

async def make_example_image_dialog(q: Q):
    q.page['meta'].dialog = None
    await q.page.save()
    print(q.args.selected_example_image)
    q.page['meta'].dialog = ui.dialog(
        title='Select example image',
        closable=True,
        items=[
            ui.dropdown(
                name='example_image_selected',
                label='Select image',
                value=q.app.example_images[0]['wave_path'],
                choices=[
                    ui.choice(name=img['wave_path'], label=img['label'])
                    for img in q.app.example_images
                ],
            ),
            ui.button(name='example_image_chosen', label='Select', primary=True),
            ui.button(name='example_image_chosen', label='Select', primary=True),
            # Note: wave seems to be ignoring the last item in this list, hence the duplicate item.
        ],
    )
    await q.page.save()
