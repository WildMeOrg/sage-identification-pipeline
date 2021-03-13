from h2o_wave import ui

def get_layouts(side_panel=False):
    layouts = [
        ui.layout(
            breakpoint='s',
            width='800px',
            zones=[
                ui.zone('header'),
                ui.zone(
                    'split',
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone('left', size='50%'),
                        ui.zone('right', size='50%'),
                    ],
                ),
                ui.zone('results', size='100%', direction=ui.ZoneDirection.COLUMN),
                ui.zone(
                    'svg',
                    align='start',
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone('detection', size='50%'),
                        ui.zone('classification', size='50%'),
                    ],
                ),
                ui.zone('identification'),
                ui.zone('footer'),
            ],
        )
    ]
    return layouts
