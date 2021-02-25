from h2o_wave import ui

'''
-------------------------------------------------------------------------------
Header
-------------------------------------------------------------------------------
Title_Path -----------
Title      20|80 Path
-------------------------------------------------------------------------------
                                    Commands
-------------------------------------------------------------------------------
Content --------
Side                  30|70 Main
                        ---------
                        |    Main_Top
                        |______________________________________________________
                        |    Main Center
                        |
                        |
-------------------------------------------------------------------------------
Footer
-------------------------------------------------------------------------------
'''


def get_layouts(side_panel=False):
    layouts = [
        ui.layout(
            breakpoint='xl',
            width='1200px',
            zones=[
                ui.zone('header'),
                ui.zone(
                    'title_path',
                    direction=ui.ZoneDirection.ROW,
                    zones=[
                        ui.zone('title', size='20%'),
                        ui.zone('path', size='80%'),
                    ],
                ),
                ui.zone(
                    'commands',
                    direction=ui.ZoneDirection.ROW,
                    justify='between',
                    align='center',
                ),
                ui.zone(
                    'content',
                    direction=ui.ZoneDirection.ROW,
                    justify='start',
                    zones=[
                        ui.zone('side', size='100%' if side_panel else '0%'),
                        ui.zone(
                            'main',
                            direction=ui.ZoneDirection.COLUMN,
                            size='0%' if side_panel else '100%',
                            justify='start',
                            # align='stretch',
                            # wrap='stretch',
                            zones=[
                                ui.zone(
                                    'main_top',
                                    direction=ui.ZoneDirection.ROW,
                                    # size='100%',
                                    # align='stretch',
                                ),
                                ui.zone(
                                    'main_center',
                                    direction=ui.ZoneDirection.ROW,
                                    # size='100%',
                                    # align='stretch',
                                    # wrap='stretch',
                                ),
                            ],
                        ),
                    ],
                ),
                ui.zone('footer', direction=ui.ZoneDirection.ROW, justify='center'),
            ],
        )
    ]
    return layouts
