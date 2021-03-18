import os
import sys
import traceback
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Optional

from h2o_wave import Q, ui
from h2o_wave.core import expando_to_dict

from .utils import get_hostname
from sage_identification_pipeline import GLOBAL_HANDLERS


@dataclass
class WaveColors:
    # Colors from Wave default Theme.
    # https://github.com/h2oai/wave/blob/4ec0f6a6a2b8f43f11cdb557ba35a540ad23c13c/ui/src/theme.ts#L86
    red: str = '#F44336'
    pink: str = '#E91E63'
    purple: str = '#9C27B0'
    violet: str = '#673AB7'
    indigo: str = '#3F51B5'
    blue: str = '#2196F3'
    azure: str = '#03A9F4'
    cyan: str = '#00BCD4'
    teal: str = '#009688'
    mint: str = '#4CAF50'
    green: str = '#8BC34A'
    lime: str = '#CDDC39'
    yellow: str = '#FFEB3B'
    amber: str = '#FFC107'
    orange: str = '#FF9800'
    tangerine: str = '#FF5722'
    brown: str = '#795548'
    gray: str = '#9E9E9E'


@dataclass
class WhiteSpace:
    # https://qwerty.dev/whitespace/
    zero_width: str = '​'
    hair: str = ' '
    six_per_em: str = ' '
    thin: str = ' '
    punctuation: str = ' '
    four_per_em: str = ' '
    three_per_em: str = ' '
    figure: str = ' '
    en: str = ' '
    em: str = ' '
    braille: str = '⠀'


def clear_cards(q: Q):
    for x in q.app.cards:
        del q.page[x]


async def ui_crash_card(q: Q, app_name, card_name, box, label, path):
    error_msg_items = [
        ui.text_xl('Error!'),
        ui.text_l(
            'Sorry for the Inconvenience. '
            f'Please refresh your browser to restart {app_name}. '
        ),
        ui.buttons(
            items=[ui.button(name='show_autodoc_reports', label='Close', primary=True)],
            justify='start',
        ),
        ui.text_xs('⠀'),
    ]
    error_report_items = [
        ui.text('To report this crash, please go to'),
        ui.link(label=label, path=path, target='_blank'),
        ui.text_xs('⠀'),
    ]
    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)
    stack_trace_items = [ui.text('**Stack Trace**')] + [
        ui.text(f'`{x}`') for x in stack_trace
    ]
    q_args = [f'{k}: {v}' for k, v in expando_to_dict(q.args).items()]
    q_args_str = '**q.args**\n```\n' + '\n'.join(q_args) + '\n```'
    q_args_items = [ui.text_m(q_args_str)] + [ui.text_xs('⠀')]
    error_report_items.extend(q_args_items + stack_trace_items)
    error_report = [
        ui.expander(
            name='error_report',
            label='Report this error',
            expanded=False,
            items=error_report_items,
        )
    ]
    error_items = error_msg_items + error_report + [ui.text_xs('⠀')] * 2
    q.page[card_name] = ui.form_card(box=box, items=error_items)
    await q.page.save()


def default_qualifier(q: Q, arg_name: str) -> bool:
    return getattr(q.args, arg_name)


def handler(qualifier: Optional[Callable[[Q, Any], bool]] = default_qualifier):
    def handler_decorator(func):
        @wraps(func)
        async def handle_func(q: Q, *args, **kwargs):
            if qualifier(q, func.__name__):
                print(f'Calling {func.__name__} ...')
                await func(q, *args, **kwargs)

        GLOBAL_HANDLERS.append(handle_func)
        return handle_func

    return handler_decorator

def print_q_args(q_args):
    print('>>>> q.args >>>>')
    q_args_dict = expando_to_dict(q_args)
    for k, v in q_args_dict.items():
        print(f'{k}: {v}')
    print('<<<< q.args <<<<')

async def make_access_denied_card(q: Q, card_name, box):
    items = [
        ui.text_l(
            f'```\nUser {q.auth.username} Does Not have access privileges to use this app.\n```'  # noqa: E501
        )
    ]
    q.page[card_name] = ui.form_card(box=box, items=items)
    await q.page.save()


def in_cloud():
    return os.getenv('KUBERNETES_PORT') is not None


def get_hac_host_ip():
    if not in_cloud():
        return
    hostname = get_hostname()
    host_name_id = '_'.join(hostname.split('-')[:6]).upper() + '_SERVICE_HOST'
    host_ip = os.getenv(host_name_id)
    return host_ip


def get_service_port():
    if not in_cloud():
        return
    hostname = get_hostname()
    host_port_env = '_'.join(hostname.split('-')[:6]).upper() + '_SERVICE_PORT'
    host_port = os.getenv(host_port_env)
    return host_port


def get_resource_share_link(resource_id):
    host_ip = get_hac_host_ip()
    if host_ip is None:
        return ''
    return f'http://{host_ip}/resources/{resource_id}'


def get_static_share_link(file_name):
    host_ip = get_hac_host_ip()
    if host_ip is None:
        return ''
    return f'http://{host_ip}/static/{file_name}'


def get_waved_share_link(waved_link):
    host_ip = get_hac_host_ip()
    if host_ip is None:
        return ''
    # Replace the domain name with host ip address in the following link
    # https://6d0b39c5-be0c-410b-862e-070f5d5402ea.wave-dev.h2o.ai/_f/0befcbce-0937-4ed8-a2d6-1b6c9de3d449/walmart_train.csv
    service_port = get_service_port()
    object_url = waved_link.split('/_f/')[-1]
    return f'http://{host_ip}:{service_port}/_f/{object_url}'
