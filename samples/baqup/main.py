#!/usr/bin/python
#
# Copyright 2014 Quip
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Backs up a Quip account to a local folder.

This is a sample app for the Quip API - https://quip.com/api/.
"""

import argparse
import logging
import os.path
import re
import shutil
import urllib2

import quip

_BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIRECTORY = os.path.abspath(os.path.join(_BASE_DIRECTORY, 'static'))
_TEMPLATE_DIRECTORY = os.path.abspath(
    os.path.join(_BASE_DIRECTORY, 'templates'))
_OUTPUT_STATIC_DIRECTORY_NAME = '_static'
_MAXIMUM_TITLE_LENGTH = 64

def main():
    logging.getLogger().setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description="Backup of a Quip account")

    parser.add_argument("--access_token", required=True,
        help="Access token for the user whose account should be backed up")
    parser.add_argument("--root_folder_id", default=None,
        help="If provided, only the documents in the given folder will be "
             "backed up. Otherwise all folder and documents will be backed up.")
    parser.add_argument("--quip_api_base_url", default=None,
        help="Alternative base URL for the Quip API. If none is provided, "
             "https://platform.quip.com will be used")
    parser.add_argument("--output_directory", default="./",
        help="Directory where to place backup data.")

    args = parser.parse_args()

    client = quip.QuipClient(
        access_token=args.access_token, base_url=args.quip_api_base_url)
    output_directory = _normalize_path(args.output_directory)
    shutil.rmtree(output_directory, ignore_errors=True)
    output_static_diretory = os.path.join(
        output_directory, _OUTPUT_STATIC_DIRECTORY_NAME)
    shutil.copytree(_STATIC_DIRECTORY, output_static_diretory)
    _ensure_path_exists(output_directory)
    _run_backup(client, output_directory, args.root_folder_id)

def _run_backup(client, output_directory, root_folder_id):
    user = client.get_authenticated_user()
    processed_folder_ids = set()
    if root_folder_id:
        _descend_into_folder(root_folder_id, processed_folder_ids,
            client, output_directory, 0)
    else:
        _descend_into_folder(user["archive_folder_id"], processed_folder_ids,
            client, output_directory, 0)
        _descend_into_folder(user["desktop_folder_id"], processed_folder_ids,
            client, output_directory, 0)

def _descend_into_folder(folder_id, processed_folder_ids, client,
        output_directory, depth):
    if folder_id in processed_folder_ids:
        return
    processed_folder_ids.add(folder_id)
    try:
        folder = client.get_folder(folder_id)
    except quip.QuipError, e:
        if e.code == 403:
            logging.warning("%sSkipped over restricted folder %s.",
                "  " * depth, folder_id)
        else:
            logging.warning("%sSkipped over folder %s due to unknown error %d.",
                "  " * depth, folder_id, e.code)
        return
    except urllib2.HTTPError, e:
        logging.warning("%sSkipped over folder %s due to HTTP error %d.",
            "  " * depth, folder_id, e.code)
        return
    title = folder["folder"]["title"]
    logging.info("%sBacking up folder %s...", "  " * depth, title)
    folder_output_path = os.path.join(output_directory, _sanitize_title(title))
    _ensure_path_exists(folder_output_path)
    for child in folder["children"]:
        if "folder_id" in child:
            _descend_into_folder(child["folder_id"], processed_folder_ids,
                client, folder_output_path, depth + 1)
        elif "thread_id" in child:
            _backup_thread(child["thread_id"], client, folder_output_path,
                depth + 1)

def _backup_thread(thread_id, client, output_directory, depth):
    thread = client.get_thread(thread_id)
    title = thread["thread"]["title"]
    logging.info("%sBacking up thread %s...", "  " * depth, title)
    sanitized_title = _sanitize_title(title)
    if "html" in thread:
        file_name = sanitized_title + ".html"
        thread_output_path = os.path.join(output_directory, file_name)
        with open(thread_output_path, "w") as thread_file:
            document_html = _DOCUMENT_TEMPLATE % {
                "title": title,
                "stylesheet_path": ("../" * depth) +
                    _OUTPUT_STATIC_DIRECTORY_NAME + "/main.css",
                "body": thread["html"],
            }
            thread_file.write(document_html.encode("utf-8"))

def _ensure_path_exists(directory_path):
    if os.path.exists(directory_path):
        return
    os.makedirs(directory_path)

def _normalize_path(path):
    return os.path.abspath(os.path.expanduser(path))

def _sanitize_title(title):
    sanitized_title = re.sub(r"\s", " ", title)
    sanitized_title = re.sub(r"(?u)[^- \w.]", "", sanitized_title)
    if len(sanitized_title) > _MAXIMUM_TITLE_LENGTH:
        sanitized_title = sanitized_title[:_MAXIMUM_TITLE_LENGTH]
    return sanitized_title

def _read_template(template_file_name):
    template_path = os.path.join(_TEMPLATE_DIRECTORY, template_file_name)
    with open(template_path, "r") as template_file:
        return "".join(template_file.readlines())

_DOCUMENT_TEMPLATE = _read_template("document.html")

if __name__ == '__main__':
    main()
