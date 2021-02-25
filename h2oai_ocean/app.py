from datetime import datetime

from h2o_wave import Q, app, main, ui  # noqa: F401

from h2oai_ocean import GLOBAL_HANDLERS

from . import handlers  # noqa: F401 Need to import to register the handlers
from .initializers import initialize_app, initialize_client, initialize_user
from .wave_utils import (
    make_access_denied_card,
    print_q_args,
    ui_crash_card,
    verify_access,
)


@app('/', mode='multicast')
async def serve(q: Q):
    print('Enter serve')
    before = datetime.now()

    if not verify_access(q):
        await make_access_denied_card(q, 'access_denied', '1 1 -1 -1')
        return

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
            app_name='H2OAI Ocean',
            card_name='crash_card',
            box='1 1 -1 -1',
            label='h2oai/ocean',
            path='https://github.com/h2oai/ocean',
        )

    print(f'Time in serve(ms): {int((datetime.now() - before).microseconds/1000.0)}')
