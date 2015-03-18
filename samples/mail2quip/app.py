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

"""Inbound email handler that creates Quip messages from emails.

This is a sample app for the Quip API - https://quip.com/api/.
"""

import logging
import jinja2
import os
import quip
import urllib
import webapp2

from google.appengine.api import files
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)

class Home(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template(
            "templates/index.html")
        self.response.write(template.render())


class MailHandler(InboundMailHandler):
    def receive(self, message):
        addresses = message.to.split(',')
        thread_id = ""
        token = ""
        client = None
        for address in addresses:
            try:
                (to, domain) = address.split('@')
                (thread_id, token) = to.split('+', 1)
            except:
                pass
            if len(thread_id) in [11,12] and len(token) > 0:
                client = quip.QuipClient(access_token=token, request_timeout=30)
                try:
                    client.get_thread(thread_id)
                    break
                except Exception as e:
                    client = None
                    logging.exception(e)
            client = quip.QuipClient(access_token=to, request_timeout=30)
            try:
                client.get_authenticated_user()
                thread_id = ""
                break
            except Exception as e:
                client = None
                logging.exception(e)
        if not client:
            logging.error("Could not find token in %r", addresses)
            self.abort(404)
        text = None
        for content_type, body in message.bodies("text/plain"):
            text = body.decode()
            # Strip some common signature patterns
            for pattern in ["\n----", "\nIFTTT"]:
                if pattern in text:
                    text = text[:text.find(pattern)]
            if len(text) > 0:
                break
        html = None
        for content_type, body in message.bodies("text/html"):
            html = body.decode()
            if len(html) > 0:
                break
        attachments = []
        if hasattr(message, "attachments"):
            for filename, attachment in message.attachments:
                try:
                    blob = files.blobstore.create(
                        _blobinfo_uploaded_filename=filename)
                    with files.open(blob, 'a') as f:
                        f.write(attachment.decode())
                    files.finalize(blob)
                    host = self.request.host_url.replace("http:", "https:")
                    attachments.append("%s/attach/%s" % (
                        host, files.blobstore.get_blob_key(blob)))
                except Exception:
                    pass
        message_id = None
        if "message-id" in message.original:
            message_id = message.original["message-id"]
        if thread_id:
            # Post a message
            args = {
                "silent": "silent" in message.subject,
            }
            if attachments:
                args["attachments"] = ",".join(attachments)
            if message_id:
                args["service_id"] = message_id
            client.new_message(thread_id, text, **args)
        else:
            # Create a thread from the message body
            thread = client.new_document(
                html or text, format="html" if html else "markdown",
                title=message.subject)
            if attachments:
                client.new_message(
                    thread["thread"]["id"], attachments=",".join(attachments))


class AttachmentHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


application = webapp2.WSGIApplication([
    ('/', Home),
    ('/attach/([^/]+)?', AttachmentHandler),
    MailHandler.mapping(),
], debug=True)
