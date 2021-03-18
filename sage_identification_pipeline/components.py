import os

from h2o_wave import Q, ui, graphics as g

from .layouts import get_layouts
from .wave_utils import WaveColors
from .constants import detection_model_tags, classification_model_tags

def get_meta(side_panel=False):
    return ui.meta_card(
        box='',
        title='WBIA Identification Pipeline',
        layouts=get_layouts(side_panel=side_panel),
    )

def get_logo(q: Q):
    return ui.footer_card(
        box='header',
        caption=f'![wild me logo]({q.app.logo_path})'
    )

def get_title(q: Q):
    return ui.section_card(
        box='header',
        title='WBIA Identification Pipeline',
        subtitle='Created by Wild Me for the H2O.AI Hybrid Cloud Appstore',
        items=[],
    )

def get_target_image(q: Q):
    return ui.form_card(
        box='left',
        title='Target image',
        items=[
            ui.text(''), # margin top hack
            ui.text('WBIA will process the target image using pre-trained image analysis models. The detection model attempts to draw a box around each individual in the target image. The classification model vets the boxes (annotations) for quality. The identification model compares each annotation to our database of individuals to try to find matches.'),
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
    sliderNms = q.args.nms if 'nms' in q.args else 0.4
    sliderSensitivity = q.args.sensitivity if 'sensitivity' in q.args else 0.4

    return ui.form_card(
        box='right',
        title='Parameters',
        items=[
            ui.dropdown(
                name='detection_model_tag',
                label='Detection model tag',
                choices=[ui.choice(name=x, label=x) for x in detection_model_tags],
                value='ggr2',
                tooltip='The detection model is used to identify annotations in the target image (draw boxes around animals).',
            ),
            ui.dropdown(
                name='classification_model_tag',
                label='Classification model tag',
                choices=[ui.choice(name=x, label=x) for x in classification_model_tags],
                value='zebra_v1',
                tooltip='The classification model is used to label the annotations with species, viewpoint, and confidence score.',
            ),
            ui.slider(
                name='sensitivity',
                label='Sensitivity',
                min=0.2,
                max=1,
                value=sliderSensitivity,
                step=0.01,
                tooltip='Lower sensitivity scores result in more annotations.',
            ),
            ui.slider(
                name='nms',
                label='Non-maximal suppression (NMS)',
                min=0.2,
                max=1,
                value=sliderNms,
                step=0.01,
                tooltip='Non-maximal suppression attempts to de-duplicate overlapping annotations of the same animal.',
            ),
            ui.button(name='run', label='Run identification pipeline', primary=True, disabled=not q.app.target_image or q.app.running_pipeline),
        ],
    )


def get_stepper(q: Q):
    return ui.form_card(
        box='results',
        items=[
            ui.stepper(
                name='pipeline-stepper',
                items=[
                    ui.step(label='Upload', icon='CloudUpload', done=bool(q.app.upload_complete)),
                    ui.step(label='Detection', icon='BuildQueueNew', done=bool(q.app.detection_complete)),
                    ui.step(label='Classification', icon='Compare', done=bool(q.app.classification_complete)),
                    ui.step(label='Identification', icon='BranchCompare', done=bool(q.app.identification_complete)),
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

def get_rect(annotation):
    return g.rect(
        x=annotation['top'],
        y=annotation['left'],
        width=annotation['width'],
        height=annotation['height'],
        fill='rgba(0, 0, 255, 0.2)',
        stroke='rgb(0, 0, 255)',
        stroke_width='2px'
    )

def get_detection_card(q: Q):
    if 'annotations' in q.app and bool(q.app.annotations):
        card_padding = 30 # inferred from DOM
        card_width = 386 # inferred from DOM
        svg_width = card_width - card_padding
        svg_height = svg_width * q.app.image_size[1] / q.app.image_size[0] 
        card_height = svg_height + card_padding

        return ui.graphics_card(
            box= ui.box(zone='detection',
            height=f'{card_height}px'),
            view_box=f'0 0 {q.app.image_size[0]} {q.app.image_size[1]}', height=f'{svg_height}px', width=f'{svg_width}px',
            stage=g.stage(
                target = g.image(x='0', y='0', width=f'{q.app.image_size[0]}', height=f'{q.app.image_size[1]}', href=q.app.target_image),
                **{a['uuid']: get_rect(a) for a in q.app.annotations},
            )
        )
    else:
        return ui.form_card(
            box='detection',
            items=[
                ui.label(label='Detection results'),
                ui.text_s('No results to display'),
            ]
        )


def get_classification_progress_card(q: Q):
    return ui.form_card(
        box='classification',
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


def get_identification_in_progress(q: Q):
    return ui.form_card(
        box='identification',
        items=[
            ui.progress(label='Identification in progress', caption='This step can take a long time...')
        ]
    )

def get_identification_results(q: Q):
    if 'identification_results' in q.app and bool(q.app.identification_results):
        clean_identification_results = [r for r in q.app.identification_results if r]
        items = [ui.label(label='Identification results')]
        i = 1
        for result in clean_identification_results:
            cleanUrl = generate_evidence_url(
                result['reference'], result['qannot_uuid'], result['dannot_uuid'], 'clean'
            )
            matchesUrl = generate_evidence_url(
                result['reference'], result['qannot_uuid'], result['dannot_uuid'], 'matches'
            )
            heatmaskUrl = generate_evidence_url(
                result['reference'], result['qannot_uuid'], result['dannot_uuid'], 'heatmask'
            )

            items.append(ui.separator(label=f'Annotation {i}'))
            items.append(ui.text_s(f'Best match with no evidence'))
            items.append(ui.text(
                content=f'![target image with candidate image and heatmap]({cleanUrl})'
            ))
            items.append(ui.text_s(f'Best match with heatmask evidence'))
            items.append(ui.text(
                content=f'![target image with candidate image and heatmap]({heatmaskUrl})'
            ))
            items.append(ui.text_s(f'Best match with detailed evidence'))
            items.append(ui.text(
                content=f'![target image with candidate image and heatmap]({matchesUrl})'
            ))
            i += 1

        items.append(ui.text(
            content='Using your own wildlife images? Researchers would appreciate it if you would report them to the appropriate [Wildbook](https://wildme.org/#/platforms)!'
        ))
        return ui.form_card(
            box='identification',
            items=items
        )
    else:
        return ui.form_card(
            box='identification',
            items=[
                ui.label(label='Identification results'),
                ui.text_s('No results to display'),
            ]
        )

def get_results_table(q: Q):
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

    if 'example_images' in q.app:
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
    else:
        q.page['meta'].dialog = ui.dialog(
            title='Loading example images',
            closable=True,
            items=[
                ui.text('Example images have not loaded yet. Check back in a few seconds.'),
                ui.text('Example images have not loaded yet. Check back in a few seconds.'),
                # Note: wave seems to be ignoring the last item in this list, hence the duplicate item.
            ],
        )

    await q.page.save()
