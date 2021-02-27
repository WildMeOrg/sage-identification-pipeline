from h2o_wave import ui


def get_layouts(side_panel=False):
    layouts = [
        ui.layout(
            breakpoint='xl',
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
                ui.zone('main'),
                ui.zone('footer'),
            ],
        )
    ]
    return layouts
