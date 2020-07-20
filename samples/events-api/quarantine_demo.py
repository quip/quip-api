#!/usr/bin/env python
#
# pip install tornado
#
# Copyright 2019 Quip
# http://www.apache.org/licenses/LICENSE-2.0.html

"""
Examples:

Audit contents of newly created messages.
    -Loop over all company events.
    -Fetch and examine messages' contents, based on `create-message` events.
    -Conditionally quarantine message contents based on admin-specified criteria.

Quarantine sensitive threads if certain events, e.g. sharing, occur.
    -Loop over all company events.
    -Check if ids from `share-thread` events match an admin-specified list.
    -Conditionally quarantine threads' contents.

Examine thread metadata and content.
    -Fetch a thread using its id.

"""

import json
import logging
import os.path
import re
import requests
import tornado.auth
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.httpclient

from tornado.options import define, options

define("port", type=int, default=8080)
define("admin_endpoint_base", default="https://platform.quip.com/1/admin")
define("company_id", default="<11_character_company_id")
# Must be for an admin.
define("access_token",
    default="<see_https://quip.com/dev/automation/documentation#authentication")
define("enable_audit_for_realtime", default=True)


DENYLIST_WORDS = [
    "PII",
    "super_sensitive_info,"
]

DENYLIST_PATTERNS = {
    "social_security_number": r"[0-9]{3}-[0-9]{2}-[0-9]{4}",
}


SHARE_DENYLIST = [
    "<11_character_thread_id>",
]


class Application(tornado.web.Application):
    def __init__(self):
        base_dir = os.path.dirname(__file__)
        settings = {
            "debug": True
        }
        tornado.web.Application.__init__(self, [
            tornado.web.url(r"/events/realtime", RealtimeHandler, name="realtime"),
            tornado.web.url(r"/events/cursor", CursorHandler, name="cursor"),
            tornado.web.url(r"/audit/message/(.*)", AuditMessageHandler, name="message"),
            tornado.web.url(r"/threads/(.*)", GetThread, name="get-thread"),
        ], **settings)


class EventsDemoHandler(tornado.web.RequestHandler):
    def authorized_headers(self):
        return {
            'Authorization': f"Bearer {options.access_token}",
        }

    def fetch_new_cursor_json(self):
        url = f"{options.admin_endpoint_base}/events/1/cursor/realtime/create"
        params = {"company_id": options.company_id}
        response = requests.request("GET", url, headers=self.authorized_headers(), params=params)
        return response.json()

    def next_cursor(self):
        try:
            cursor = self.get_argument("cursor")
        except tornado.web.MissingArgumentError as e:
            cursor = self.fetch_new_cursor_json()["next_cursor"]
        return cursor

    def quarantine_id(self, object_id):
        url = f"{options.admin_endpoint_base}/quarantine"
        params = {
            "company_id": options.company_id,
            "object_id": object_id
        }
        requests.request("POST", url, headers=self.authorized_headers(), params=params)

    def unquarantine_id(self, object_id):
        url = f"{options.admin_endpoint_base}/quarantine"
        params = {
            "company_id": options.company_id,
            "object_id": object_id
        }
        requests.request("DELETE", url, headers=self.authorized_headers(), params=params)


class CursorHandler(EventsDemoHandler):
    @tornado.gen.coroutine
    def get(self):
        response_json = self.fetch_new_cursor_json()
        pretty_response = json.dumps(response_json, sort_keys=True, indent=4)
        self.write(f"<pre>{pretty_response}</pre>")


class RealtimeHandler(EventsDemoHandler):
    @tornado.gen.coroutine
    def get(self):
        url = f"{options.admin_endpoint_base}/events/1/events/realtime/get"
        params = {
            "company_id": options.company_id,
            "cursor": self.next_cursor()
        }
        response = requests.request("GET", url, headers=self.authorized_headers(), params=params)
        raw_html_output = self.pretty_html_formatting(response)
        if options.enable_audit_for_realtime:
            for event in response.json()["events"]:
                audit_event(self, event)
        self.write(raw_html_output)

    def pretty_html_formatting(self, response):
        response_json = response.json()
        next_events_url = f"{self.reverse_url('realtime')}?cursor={response_json['next_cursor']}"
        pretty_response = json.dumps(response_json, sort_keys=True, indent=4).replace(
            '"event"', '<span style="background-color:#00FEFE">"event"</span>')
        return f"""
            <a href={next_events_url}>Fetch Next Events</a>
            </br>
            </br>
            <h3>Raw JSON response:</h3>
            <pre>{pretty_response}</pre>
        """


def audit_event(handler, event):
    if event["event"] == "share-thread":
        if event["thread_id"] in SHARE_DENYLIST:
            handler.quarantine_id(event["thread_id"])
    elif event["event"] == "create-message":
        audit_message(handler, event["message_id"])


def audit_message_summary(handler, message_id):
    url = f"{options.admin_endpoint_base}/message/{message_id}"
    params = {
            "company_id": options.company_id
    }
    response = requests.request("GET", url, headers=handler.authorized_headers(), params=params)
    unredacted_message_text = response.json()[0]["text"]

    denied_words = set()
    for word in  DENYLIST_WORDS:
        if word in unredacted_message_text:
            denied_words.add(word)

    denied_patterns = set()
    for name, pattern in DENYLIST_PATTERNS.items():
        if re.search(pattern, unredacted_message_text):
            denied_patterns.add(name)

    is_disallowed = bool(denied_words or denied_patterns)

    audit_summary = f"Message {message_id}</br></br>Audit: {'FAILED' if is_disallowed else 'PASSED'}."
    if denied_words:
        audit_summary += f"</br></br>Denylist words: {denied_words}"
    if denied_patterns:
        audit_summary += f"</br></br>Denylist patterns: {denied_patterns}"

    return audit_summary


def audit_message(handler, message_id):
    audit_summary = audit_message_summary(handler, message_id)
    # Crude, but hey it's just a demo...
    if "FAILED" in audit_summary:
        handler.quarantine_id(message_id)


class AuditMessageHandler(EventsDemoHandler):
    @tornado.gen.coroutine
    def get(self, message_id):
        audit_summary = audit_message_summary(self, message_id)
        audit_message(self, message_id)
        self.write(audit_summary)


class GetThread(EventsDemoHandler):
    @tornado.gen.coroutine
    def get(self, thread_id):
        url = f"{options.admin_endpoint_base}/threads/{thread_id}"
        params = {
            "company_id": options.company_id
        }
        response = requests.request("GET", url, headers=self.authorized_headers(), params=params)
        response_json = response.json()

        # Field contains raw html that formats oddly.
        thread_html = response_json["html"]
        del response_json["html"]

        pretty_response = json.dumps(response_json, sort_keys=True, indent=4)
        output = f"<pre>{pretty_response}</pre>"
        output += f"</br></br><pre>Thread's HTML (extracted out of above):</pre></br>{thread_html}"
        self.write(output)


def main():
    tornado.options.parse_command_line()
    Application().listen(options.port)
    logging.info("Running at http://localhost:%d", options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
