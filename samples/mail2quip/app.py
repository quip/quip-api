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

import logging
import jinja2
import os
import quip
import webapp2

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
        for address in addresses:
            try:
                (to, domain) = address.split('@')
                (thread_id, token) = to.split('+', 1)
                if len(thread_id) == 11 and len(token) > 0:
                    break
            except:
                pass
        text = ""
        for content_type, body in message.bodies('text/plain'):
            text = body.decode()
            # Strip some common signature patterns
            for pattern in ["\n----", "\nIFTTT"]:
                if pattern in text:
                    text = text[:text.find(pattern)]
            if len(text) > 0:
                break
        # TODO: Attachments
        if len(text) > 0 and len(thread_id) == 11 and len(token) > 0:
            client = quip.QuipClient(access_token=token)
            client.new_message(
                thread_id, text, silent="silent" in message.subject)


application = webapp2.WSGIApplication([
    ('/', Home),
    MailHandler.mapping(),
], debug=True)
