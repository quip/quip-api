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
import datetime
import logging
import os.path
import re
import shutil
import sys
import urllib2
import xml.etree.cElementTree
import xml.sax.saxutils

reload(sys)
sys.setdefaultencoding('utf8')

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
        access_token=args.access_token, base_url=args.quip_api_base_url,
        retry_rate_limit=True, request_timeout=120)
    output_directory = os.path.join(
        _normalize_path(args.output_directory), "baqup")
    _ensure_path_exists(output_directory)
    shutil.rmtree(output_directory, ignore_errors=True)
    output_static_diretory = os.path.join(
        output_directory, _OUTPUT_STATIC_DIRECTORY_NAME)
    shutil.copytree(_STATIC_DIRECTORY, output_static_diretory)
    _run_backup(client, output_directory, args.root_folder_id)

def _run_backup(client, output_directory, root_folder_id):
    user = client.get_authenticated_user()
    processed_folder_ids = set()
    if root_folder_id:
        _descend_into_folder(root_folder_id, processed_folder_ids,
            client, output_directory, 0)
    else:
        _descend_into_folder(user["private_folder_id"], processed_folder_ids,
            client, output_directory, 0)
        _descend_into_folder(user["starred_folder_id"], processed_folder_ids,
            client, output_directory, 0)
    logging.info("Looking for conversations")
    conversation_threads = _get_conversation_threads(client)
    if conversation_threads:
        conversations_directory = os.path.join(output_directory, "Conversations")
        _ensure_path_exists(conversations_directory)
        for thread in conversation_threads:
            _backup_thread(thread, client, conversations_directory, 1)

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
            thread = client.get_thread(child["thread_id"])
            _backup_thread(thread, client, folder_output_path, depth + 1)

def _backup_thread(thread, client, output_directory, depth):
    thread_id = thread["thread"]["id"]
    title = thread["thread"]["title"]
    logging.info("%sBacking up thread %s (%s)...",
        "  " * depth, title, thread_id)
    sanitized_title = _sanitize_title(title)
    if "html" in thread:
        # Parse the document
        tree = client.parse_document_html(thread["html"])
        # Download each image and replace with the new URL
        for img in tree.iter("img"):
            src = img.get("src")
            if not src.startswith("/blob"):
                continue
            _, _, thread_id, blob_id = src.split("/")
            blob_response = client.get_blob(thread_id, blob_id)
            image_filename = blob_response.info().get(
                "Content-Disposition").split('"')[-2]
            image_output_path = os.path.join(output_directory, image_filename)
            with open(image_output_path, "w") as image_file:
                image_file.write(blob_response.read())
            img.set("src", image_filename)
        html = unicode(xml.etree.cElementTree.tostring(tree))
        # Strip the <html> tags that were introduced in parse_document_html
        html = html[6:-7]

        document_file_name = sanitized_title + ".html"
        document_output_path = os.path.join(
            output_directory, document_file_name)
        document_html = _DOCUMENT_TEMPLATE % {
            "title": _escape(title),
            "stylesheet_path": ("../" * depth) +
                _OUTPUT_STATIC_DIRECTORY_NAME + "/main.css",
            "body": html,
        }
        with open(document_output_path, "w") as document_file:
            document_file.write(document_html.encode("utf-8"))
    messages = _get_thread_messages(thread_id, client)
    if messages:
        title_suffix = "messages" if "html" in thread else thread_id
        message_file_name = "%s (%s).html" % (sanitized_title, title_suffix)
        messages_output_path = os.path.join(output_directory, message_file_name)
        messages_html = _MESSAGES_TEMPLATE % {
            "title": _escape(title),
            "stylesheet_path": ("../" * depth) +
                _OUTPUT_STATIC_DIRECTORY_NAME + "/main.css",
            "body": "".join([_MESSAGE_TEMPLATE % {
                "author_name":
                    _escape(_get_user(client, message["author_id"])["name"]),
                "timestamp": _escape(_format_usec(message["created_usec"])),
                "message_text": _escape(message["text"]),
            } for message in messages])
        }
        with open(messages_output_path, "w") as messages_file:
            messages_file.write(messages_html.encode("utf-8"))

def _get_thread_messages(thread_id, client):
    max_created_usec = None
    messages = []
    while True:
        chunk = client.get_messages(
            thread_id, max_created_usec=max_created_usec, count=100)
        messages.extend(chunk)
        if chunk:
            max_created_usec = chunk[-1]["created_usec"] - 1
        else:
            break
    messages.reverse()
    return messages

def _get_conversation_threads(client):
    max_updated_usec = None
    threads = []
    thread_ids = set()
    while True:
        chunk = client.get_recent_threads(
            max_updated_usec=max_updated_usec, count=50).values()
        chunk.sort(key=lambda t:t["thread"]["updated_usec"], reverse=True)
        threads.extend([t for t in chunk
            if "html" not in t and t["thread"]["id"] not in thread_ids])
        thread_ids.update([t["thread"]["id"] for t in chunk])
        if chunk:
            chunk_max_updated_usec = chunk[-1]["thread"]["updated_usec"] - 1
            if chunk_max_updated_usec == max_updated_usec:
                logging.warning("New chunk had the same max_updated_usec (%d) "
                    "as the last one, can't get any older threads",
                    max_updated_usec)
                break
            max_updated_usec = chunk_max_updated_usec
        else:
            break
        logging.info("  Got %d threads, paged back to %s",
            len(threads), _format_usec(max_updated_usec))
    threads.reverse()
    return threads

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

_user_cache = {}
def _get_user(client, id):
    if id not in _user_cache:
        try:
            _user_cache[id] = client.get_user(id)
        except quip.QuipError:
            _user_cache[id] = {"id": id, "name": "Unknown user %s" % id}
    return _user_cache[id]

def _read_template(template_file_name):
    template_path = os.path.join(_TEMPLATE_DIRECTORY, template_file_name)
    with open(template_path, "r") as template_file:
        return "".join(template_file.readlines())

def _escape(s):
    return xml.sax.saxutils.escape(s, {'"': "&quot;"})

def _format_usec(usec):
    return datetime.datetime.utcfromtimestamp(usec / 1000000.0).isoformat()

_DOCUMENT_TEMPLATE = _read_template("document.html")
_MESSAGE_TEMPLATE = _read_template("message.html")
_MESSAGES_TEMPLATE = _read_template("messages.html")

if __name__ == '__main__':
    main()
