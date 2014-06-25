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

"""A Quip API client library.

For full API documentation, visit https://quip.com/api/.

Typical usage:

    client = quip.QuipClient(access_token=...)
    user = client.get_authenticated_user()
    desktop = client.get_folder(user["desktop_folder_id"])
    print "There are", len(desktop["children"]), "items on the desktop"

In addition to standard getters and setters, we provide a few convenience
methods for document editing. For example, you can use `add_to_first_list`
to append items (in Markdown) to the first bulleted or checklist in a
given document, which is useful for automating a task list.
"""

import json
import urllib
import urllib2
import xml.etree.cElementTree


class QuipClient(object):
    """A Quip API client"""
    # Edit operations
    APPEND, \
    PREPEND, \
    AFTER_SECTION, \
    BEFORE_SECTION, \
    REPLACE_SECTION, \
    DELETE_SECTION = range(6)

    # Folder colors
    MANILA, \
    RED, \
    ORANGE, \
    GREEN, \
    BLUE = range(5)

    def __init__(self, access_token=None, client_id=None, client_secret=None,
                 base_url=None, request_timeout=None):
        """Constructs a Quip API client.

        If `access_token` is given, all of the API methods in the client
        will work to read and modify Quip documents.

        Otherwise, only `get_authorization_url` and `get_access_token`
        work, and we assume the client is for a server using the Quip API's
        OAuth endpoint.
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url if base_url else "https://platform.quip.com"
        self.request_timeout = request_timeout if request_timeout else 10

    def get_authorization_url(self, redirect_uri, state=None):
        """Returns the URL the user should be redirected to to sign in."""
        return self._url(
            "oauth/login", redirect_uri=redirect_uri, state=state,
            response_type="code", client_id=self.client_id)

    def get_access_token(self, redirect_uri, code):
        """Exchanges a verification code for an access_token.

        Once the user is redirected back to your server from the URL
        returned by `get_authorization_url`, you can exchange the `code`
        argument with this method.
        """
        return self._fetch_json(
            "oauth/access_token", redirect_uri=redirect_uri, code=code,
            grant_type="authorization_code", client_id=self.client_id,
            client_secret=self.client_secret)

    def get_authenticated_user(self):
        """Returns the user corresponding to our access token."""
        return self._fetch_json("users/current")

    def get_user(self, id):
        """Returns the user with the given ID."""
        return self._fetch_json("users/" + id)

    def get_users(self, ids):
        """Returns a dictionary of users for the given IDs."""
        return self._fetch_json("users/", post_data={"ids": ",".join(ids)})

    def get_contacts(self):
        """Returns a list of the users in the authenticated user's contacts."""
        return self._fetch_json("users/contacts")

    def get_folder(self, id):
        """Returns the folder with the given ID."""
        return self._fetch_json("folders/" + id)

    def get_folders(self, ids):
        """Returns a dictionary of folders for the given IDs."""
        return self._fetch_json("folders/", post_data={"ids": ",".join(ids)})

    def new_folder(self, title, parent_id=None, color=None, member_ids=[]):
        return self._fetch_json("folders/new", post_data={
            "title": title,
            "parent_id": parent_id,
            "color": color,
            "member_ids": ",".join(member_ids),
        })

    def update_folder(self, folder_id, color=None, title=None):
        return self._fetch_json("folders/update", post_data={
            "folder_id": folder_id,
            "color": color,
            "title": title,
        })

    def add_folder_members(self, folder_id, member_ids):
        """Adds the given users to the given folder."""
        return self._fetch_json("folders/add-members", post_data={
            "folder_id": folder_id,
            "member_ids": ",".join(member_ids),
        })

    def remove_folder_members(self, folder_id, member_ids):
        """Removes the given users from the given folder."""
        return self._fetch_json("folders/remove-members", post_data={
            "folder_id": folder_id,
            "member_ids": ",".join(member_ids),
        })

    def get_messages(self, thread_id, max_created_usec=None, count=None):
        """Returns the most recent messages for the given thread.

        To page through the messages, use max_created_usec, which is the
        sort order for the returned messages.

        count should be an integer indicating the number of messages you
        want returned. The maximum is 100.
        """
        return self._fetch_json(
            "messages/" + thread_id, max_created_usec=max_created_usec,
            count=count)

    def new_message(self, thread_id, content, silent=False):
        """Sends a message on the given thread.

        `content` is plain text, not HTML.
        """
        return self._fetch_json("messages/new", post_data={
            "thread_id": thread_id,
            "content": content,
            "silent": silent,
        })

    def get_thread(self, id):
        """Returns the thread with the given ID."""
        return self._fetch_json("threads/" + id)

    def get_threads(self, ids):
        """Returns a dictionary of threads for the given IDs."""
        return self._fetch_json("threads/", post_data={"ids": ",".join(ids)})

    def get_recent_threads(self, max_updated_usec=None, count=None):
        """Returns the recently updated threads for a given user."""
        return self._fetch_json(
            "threads/recent", max_updated_usec=max_updated_usec,
            count=count)

    def add_thread_members(self, thread_id, member_ids):
        """Adds the given folder or user IDs to the given thread."""
        return self._fetch_json("threads/add-members", post_data={
            "thread_id": thread_id,
            "member_ids": ",".join(member_ids),
        })

    def remove_thread_members(self, thread_id, member_ids):
        """Removes the given folder or user IDs from the given thread."""
        return self._fetch_json("threads/remove-members", post_data={
            "thread_id": thread_id,
            "member_ids": ",".join(member_ids),
        })

    def new_document(self, content, format="html", title=None, member_ids=[]):
        """Creates a new document from the given content.

        To create a document in a folder, include the folder ID in the list
        of member_ids, e.g.,

            client = quip.QuipClient(...)
            user = client.get_authenticated_user()
            client.new_document(..., member_ids=[user["archive_folder_id"]])

        """
        return self._fetch_json("threads/new-document", post_data={
            "content": content,
            "format": format,
            "title": title,
            "member_ids": ",".join(member_ids),
        })

    def edit_document(self, thread_id, content, operation=APPEND, format="html",
                      section_id=None):
        """Edits the given document, adding the given content.

        `operation` should be one of the constants described above. If
        `operation` is relative to another section of the document, you must
        also specify the `section_id`.
        """
        return self._fetch_json("threads/edit-document", post_data={
            "thread_id": thread_id,
            "content": content,
            "location": operation,
            "format": format,
            "section_id": section_id,
        })

    def add_to_first_list(self, thread_id, *items):
        """Adds the given items to the first list in the given document.

            client = quip.QuipClient(...)
            client.add_to_first_list(thread_id, "Try the Quip API")

        """
        items = [item.replace("\n", " ") for item in items]
        section_id = self.get_last_list_item_id(self.get_first_list(thread_id))
        self.edit_document(
            thread_id=thread_id,
            content="\n\n".join(items),
            format="markdown",
            section_id=section_id,
            operation=self.AFTER_SECTION)

    def toggle_checkmark(self, thread_id, item, checked=True):
        """Sets the checked state of the given list item to the given state.

            client = quip.QuipClient(...)
            list = client.get_first_list(thread_id)
            client.toggle_checkmark(thread_id, list[0])

        """
        if checked:
            item.attrib["class"] = "checked"
        else:
            item.attrib["class"] = ""
        self.edit_document(thread_id=thread_id,
                           content=xml.etree.cElementTree.tostring(item),
                           section_id=item.attrib["id"],
                           operation=self.REPLACE_SECTION)

    def get_first_list(self, thread_id=None, document_html=None):
        """Returns the `ElementTree` of the first list in the document.

        The list can be any type (bulleted, numbered, or checklist).
        If `thread_id` is given, we download the document. If you have
        already downloaded the document, you can specify `document_html`
        directly.
        """
        return self._get_list(thread_id, document_html, True)

    def get_last_list(self, thread_id=None, document_html=None):
        """Like `get_first_list`, but the last list in the document."""
        return self._get_list(thread_id, document_html, False)

    def _get_list(self, thread_id, document_html, first):
        if not document_html:
            document_html = self.get_thread(thread_id)["html"]
        tree = self.parse_document_html(document_html)
        lists = list(tree.iter("ul"))
        if not lists:
            return None
        return lists[0] if first else lists[-1]

    def get_last_list_item_id(self, list_tree):
        """Returns the first item in the given list `ElementTree`."""
        items = list(list_tree.iter("li"))
        return items[-1].attrib["id"] if items else None

    def get_first_list_item_id(self, list_tree):
        """Like `get_last_list_item_id`, but the first item in the list."""
        for item in list_tree.iter("li"):
            return item.attrib["id"]
        return None

    def parse_document_html(self, document_html):
        """Returns an `ElementTree` for the given Quip document HTML"""
        document_xml = "<html>" + document_html + "</html>"
        return xml.etree.cElementTree.fromstring(document_xml.encode("utf-8"))

    def get_blob(self, thread_id, blob_id):
        """Returns a file-like object with the contents of the given blob from
        the given thread.

        The object is described in detail here:
        https://docs.python.org/2/library/urllib2.html#urllib2.urlopen
        """
        request = urllib2.Request(
            url=self._url("blob/%s/%s" % (thread_id, blob_id)))
        if self.access_token:
            request.add_header("Authorization", "Bearer " + self.access_token)
        try:
            return urllib2.urlopen(request, timeout=self.request_timeout)
        except urllib2.HTTPError, error:
            try:
                # Extract the developer-friendly error message from the response
                message = json.loads(error.read())["error_description"]
            except Exception:
                raise error
            raise QuipError(error.code, message, error)

    def put_blob(self, thread_id, blob):
        """Uploads an image or other blob to the given Quip thread. Returns an
        ID that can be used to add the image to the document of the thread.

        blob can be any file-like object. Requires the 'requests' module.
        """
        import requests
        url = "blob/" + thread_id
        headers = None
        if self.access_token:
            headers = {"Authorization": "Bearer " + self.access_token}
        try:
            response = requests.request(
                "post", self._url(url), timeout=self.request_timeout,
                files={"blob": blob}, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException, error:
            try:
                # Extract the developer-friendly error message from the response
                message = error.response.json()["error_description"]
            except Exception:
                raise error
            raise QuipError(error.response.status_code, message, error)

    def _fetch_json(self, path, post_data=None, **args):
        request = urllib2.Request(url=self._url(path, **args))
        if post_data:
            post_data = dict((k, v) for k, v in post_data.items()
                             if v or isinstance(v, int))
            request.data = urllib.urlencode(post_data)
        if self.access_token:
            request.add_header("Authorization", "Bearer " + self.access_token)
        try:
            return json.loads(
                urllib2.urlopen(request, timeout=self.request_timeout).read())
        except urllib2.HTTPError, error:
            try:
                # Extract the developer-friendly error message from the response
                message = json.loads(error.read())["error_description"]
            except Exception:
                raise error
            raise QuipError(error.code, message, error)

    def _url(self, path, **args):
        url = self.base_url + "/1/" + path
        args = dict((k, v) for k, v in args.items() if v)
        if args:
            url += "?" + urllib.urlencode(args)
        return url


class QuipError(Exception):
    def __init__(self, code, message, http_error):
        Exception.__init__(self, "%d: %s" % (code, message))
        self.code = code
        self.http_error = http_error
