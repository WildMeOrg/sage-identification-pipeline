import json
import os
import re
import socket
import zipfile
from base64 import b64decode
from datetime import datetime, timezone
from hashlib import blake2b
from typing import Dict
from zipfile import ZipFile

import httpx
import requests


def now():
    """Returns current UTC timestamp."""
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def dict2json(data: Dict, file_name: str) -> str:
    out_file_path = os.path.abspath(file_name)
    with open(out_file_path, "w") as json_fp:
        json.dump(data, json_fp)
    return out_file_path


def json2dict(json_file: str) -> dict:
    json_dict = {}
    if not os.path.isfile(os.path.abspath(json_file)):
        print(f"Error: '{json_file}' is not a file.")  # noqa
    else:
        with open(os.path.abspath(json_file), "r") as json_fp:
            json_dict = json.load(json_fp)
    return json_dict


def get_files_in_dir(dir_path, pattern, ext):
    files = []
    with os.scandir(dir_path) as it:
        for entry in it:
            if (
                entry.name.endswith(f".{ext}")
                and pattern in entry.name
                and entry.is_file()
            ):
                files.append(entry.path)
    return files


def get_dirs_in_dir(dir_path, pattern=''):
    dirs = []
    with os.scandir(dir_path) as it:
        for entry in it:
            if entry.is_dir() and pattern in entry.name:
                dirs.append(entry.path)
    return dirs


def unzip(archive_path, out_dir, overwrite=False):
    out_dir_path = os.path.abspath(out_dir)
    if not os.path.isdir(out_dir_path):
        os.makedirs(out_dir_path, exist_ok=True)
    with zipfile.ZipFile(archive_path) as my_zip:
        my_zip.extractall(path=out_dir_path)
    return out_dir_path


def zip_dir(dir_path):
    dir_abspath = os.path.abspath(dir_path)
    zip_name = f"{os.path.basename(dir_abspath)}.zip"
    zip_path = os.path.join(
        os.path.dirname(dir_abspath),
        zip_name,
    )
    cwd = os.getcwd()
    os.chdir(os.path.dirname(dir_abspath))
    with ZipFile(zip_path, "w") as my_zip:
        for root, _dirs, files in os.walk(os.path.basename(dir_abspath)):
            print(f'root: {root}')
            for file in files:
                print(f'file: {file}')
                my_zip.write(os.path.join(root, file))
    os.chdir(cwd)
    return zip_path


def read_lines(file_name):
    with open(os.path.abspath(file_name), "r") as read_file:
        lines = read_file.readlines()
    return lines


def write_lines(file_name, lines):
    with open(os.path.abspath(file_name), "w") as write_file:
        write_file.writelines(lines)


def lines_matching_regex(lines, match_regex, num_after=None):
    p = re.compile(match_regex)
    if num_after is None:
        return [x.strip() for x in lines if p.search(x) is not None]
    start = 0
    for i, line in enumerate(lines):
        m = p.search(line)
        if m is not None:
            start = i
            break
    return [x.strip() for x in lines[start : start + num_after + 1]]


def get_hostname():
    return socket.gethostname()


def safe_request(
    request_job, url, message=None, request_json=None, params=None, options=None
):
    request_args = {"url": url, "params": params}  # "allow_redirects": False
    request_args.update(options)
    if request_json is not None:
        request_args["json"] = request_json
    try:
        response = request_job(**request_args)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        # response.status_code != 200
        print(f"Http Error: {http_error}")
        return None
    except requests.exceptions.ConnectionError as connection_error:
        print(f"Connection Error: {connection_error}")
        return None
    except requests.exceptions.Timeout as timeout_error:
        print(f"Timeout Error: {timeout_error}")
        return None
    except requests.exceptions.RequestException as unknown_error:
        # An unknown error occurred
        print(f"Unknown Error: {unknown_error}")
        return None
    # response.status_code == 200
    if response:
        if message is not None:
            print(message)
        # return response.json()
        return response
    else:
        return None


def download_file(url, file_path):
    file_abspath = os.path.abspath(file_path)
    parent_dir = os.path.dirname(file_abspath)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir, exist_ok=False)
    # r = requests.get(url, allow_redirects=True)
    # r = requests.get(url)
    r = safe_request(
        request_job=requests.get, url=url, options={'allow_redirects': True}
    )
    with open(file_abspath, 'wb') as fp:
        fp.write(r.content)
    return file_abspath


def breakdown_aws_presigned_url(presigned_url):
    """
    Breakdown a presigned AWS URL

    example presigned url:
    http://127.0.0.1:9000/minio-root/ai/h2o/ocean/user/b9bcc9cb-90b9-40bd-8a96-681b5d4f3f87/Iris.csv
    ?X-Amz-Algorithm=AWS4-HMAC-SHA256
    &X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20210217%2Fus-east-1%2Fs3%2Faws4_request
    &X-Amz-Date=20210217T230446Z
    &X-Amz-Expires=86400
    &X-Amz-SignedHeaders=host
    &X-Amz-Signature=9d7abb8e6656a1c87d6ec8e9c11a6db11f5ba906334e47bfce40f4d6b1b06d80

    To be able to use this url in a HTTP GET request, it needs to be broken down in to
    - Actual base URL and it's
    - Parameters
    """
    base_url, params_url = presigned_url.split('?', maxsplit=1)
    *_, file_name = base_url.split('/')
    params_keys = [
        'X-Amz-Algorithm',
        'X-Amz-Credential',
        'X-Amz-Date',
        'X-Amz-Expires',
        'X-Amz-SignedHeaders',
        'X-Amz-Signature',
    ]
    params = {}
    params_url_keys = []
    params_list = params_url.split('&')
    for key in params_keys:
        for x in params_list:
            if key in x:
                k, value = x.split('=', maxsplit=1)
                params_url_keys.append(k)
                params[key] = value
                break

    params['X-Amz-Credential'] = params['X-Amz-Credential'].replace('%2F', '/')

    for k, v in params.items():
        print(f'{k}={v}')

    return base_url, params, file_name


def is_presigned_url(url):
    params_keys = [
        'X-Amz-Algorithm',
        'X-Amz-Credential',
        'X-Amz-Date',
        'X-Amz-Expires',
        'X-Amz-SignedHeaders',
        'X-Amz-Signature',
    ]
    return all([k in url for k in params_keys])


def download_from_presigned_url(presigned_url, download_dir):
    url, params, file_name = breakdown_aws_presigned_url(presigned_url)

    if not os.path.isdir(download_dir):
        os.makedirs(download_dir, exist_ok=False)
    file_abspath = os.path.join(os.path.abspath(download_dir), file_name)

    r = httpx.get(url=url, params=params)
    with open(file_abspath, 'wb') as fp:
        fp.write(r.content)

    return file_abspath


class MyCustomAuth(httpx.Auth):
    requires_response_body = True

    def __init__(self, access_token):
        self.access_token = access_token

    def auth_flow(self, request):
        request.headers["Authentication"] = self.access_token
        response = yield request


def get_file(url, file_path, access_token):
    file_abspath = os.path.abspath(file_path)
    parent_dir = os.path.dirname(file_abspath)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir, exist_ok=False)

    auth = MyCustomAuth(access_token=access_token)
    r = httpx.get(url=url, auth=auth)
    with open(file_abspath, 'wb') as fp:
        fp.write(r.content)
    return file_abspath


def blake2b_hash(message: str, salt: str) -> str:
    h = blake2b(salt=b64decode(salt.encode('utf-8')))
    h.update(message.encode('utf-8'))
    return h.hexdigest()


def size_human_readable(bytes: int) -> str:
    if bytes > 10 ** 9:
        size_str = f'{bytes / 10 ** 9:3.1f} GB'.rjust(8)
    elif bytes > 10 ** 6:
        size_str = f'{bytes / 10 ** 6:3.1f} MB'.rjust(8)
    elif bytes > 10 ** 3:
        size_str = f'{(bytes / 10 ** 3):3.1f} KB'.rjust(8)
    else:
        size_str = f'{bytes:4.0f} B'.rjust(8)
    # print(size_str)
    return size_str


def time_human_readable(timestamp, relative=False) -> str:
    if relative:
        duration = datetime.now(tz=timezone.utc) - timestamp
        days = duration.days
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f'{seconds} Seconds ago'
        if minutes > 0:
            time_str = f'{minutes} Minutes ago'  # + time_str
        if hours > 0:
            time_str = f'{hours} Hours ago'  # + time_str
        if days > 0:
            time_str = f'{days} Days ago'  # + time_str
        return time_str
    else:
        return timestamp.strftime('%b %d, %Y %I:%M:%S %p')
