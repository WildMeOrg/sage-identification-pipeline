from datetime import datetime

from h2o_wave import Q, app, main, ui  # noqa: F401

from sage_identification_pipeline import GLOBAL_HANDLERS

from . import handlers  # noqa: F401 Need to import to register the handlers
from .initializers import initialize_app, initialize_client, initialize_user
from .wave_utils import (
    print_q_args,
    ui_crash_card,
)


@app('/', mode='multicast')
async def serve(q: Q):
    print('Enter serve')
    before = datetime.now()

    print_q_args(q.args)

    try:
        del q.page['crash_card']

        await initialize_app(q)
        await initialize_user(q)
        await initialize_client(q)

        for h in GLOBAL_HANDLERS:
            await h(q)
        else:
            await q.page.save()

    except Exception as unknown_exception:
        q.page.drop()
        await ui_crash_card(
            q,
            app_name='WBIA Identification Pipeline',
            card_name='crash_card',
            box='1 1 -1 -1',
            label='wildme/sage_identification_pipeline',
            path='https://github.com/WildMeOrg/sage-identification-pipeline',
        )

    print(f'Time in serve(ms): {int((datetime.now() - before).microseconds/1000.0)}')
