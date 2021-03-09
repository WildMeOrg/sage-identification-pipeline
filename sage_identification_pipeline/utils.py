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

def json_dump_data(data):
    converted_data = {}
    for key in data:
        converted_data[key] = json.dumps(data[key])
    return converted_data

def safe_request(
    request_job, url, message=None, request_json=None, params=None, data=None, options=None
):
    request_args = {"url": url, "params": params, "data": data}  # "allow_redirects": False
    if options:
        request_args.update(options)
    if request_json is not None:
        request_args["json"] = request_json
    try:
        response = request_job(**request_args)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        # response.status_code != 200
        print(f"Http Error: {http_error}")
        # print('Http Error')
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
