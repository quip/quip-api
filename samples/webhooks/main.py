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

"""Inbound webhook server that posts service activity to a Quip thread.

This is a sample app for the Quip API - https://quip.com/api/.
"""

import json
import logging
import os
import re

import jinja2
import quip
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=["jinja2.ext.autoescape"],
    autoescape=True)

_per_client_email_to_id_cache = {}

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template(
            "templates/index.html")
        self.response.write(template.render())

class HookHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect("/")

    def post(self):
        api_token = self.request.get("api_token")
        if not api_token:
            self.error(400)
            return
        thread_id = self.request.get("thread_id")
        if not thread_id:
            self.error(400)
            return

        client = quip.QuipClient(access_token=api_token)

        service = self.request.get("service")
        payload = json.loads(self.request.body)
        logging.info("Payload: %s", payload)
        if service == "github":
            self._handle_github(client, thread_id, payload)
        elif service == "crashlytics":
            self._handle_crashlytics(client, thread_id, payload)
        elif service == "pagerduty":
            self._handle_pagerduty(client, thread_id, payload)
        else:
            self.error(400)

    def _handle_github(self, client, thread_id, payload):
        if payload.get("zen"):
            client.new_message(
                thread_id,
                u"GitHub Webhook initialized.\nYour moment of GitHub zen: %s" %
                    payload["zen"],
                silent=True)
            return

        if payload.get("commits"):
            self._handle_github_commits(client, thread_id, payload)

    def _handle_github_commits(self, client, thread_id, payload):
        if payload.get("ref") != "refs/heads/master":
            logging.info("Ignored non-master commits")
            return
        commits = payload["commits"]
        for commit in commits:
            message = commit["message"].strip()
            message = re.sub("([^\n])\n([^\n-*])", "\\1 \\2", message)
            committer = self._user_for_email(client, commit["author"]["email"])
            message = u"*Commit by %(commiter)s*\n\n%(message)s\n%(url)s" % {
                "commiter": committer,
                "message": message,
                "url": commit["url"][:-30],
            }
            client.new_message(thread_id, message, silent=True)

    def _handle_crashlytics(self, client, thread_id, payload):
        event = payload.get("event")
        if event == "verification":
            client.new_message(
                thread_id, "Crashlytics Webhook initialized.", silent=True)
            return

        if event == "issue_impact_change":
            issue = payload["payload"]
            if issue["impact_level"] == 1:
                message_template = (
                    u"*New crash in %(title)s*\n\n"
                    u"Method: %(method)s\n"
                    u"%(app_description)s"
                    u"%(url)s")
            else:
                message_template = (
                    u"*%(title)s is up to %(crash_count)d crashes*\n\n"
                    u"Method: %(method)s\n"
                    u"%(app_description)s"
                    u"%(device_count)d devices affected.\n"
                    u"%(url)s")
            app_description = ""
            if issue.get("app", {}).get("bundle_identifier"):
                app_description = \
                    u"In app %s\n" % issue["app"]["bundle_identifier"]
            message = message_template % {
                "title": issue["title"],
                "method": issue["method"],
                "crash_count": issue["crashes_count"],
                "device_count": issue["impacted_devices_count"],
                "app_description": app_description,
                "url": issue["url"],
            }
            client.new_message(thread_id, message, silent=True)

    def _handle_pagerduty(self, client, thread_id, payload):
        messages = payload.get("messages")
        for message in messages:
            incident = message["data"]["incident"]
            url = incident["html_url"]
            title = incident["trigger_summary_data"]["subject"]
            if incident.get("assigned_to_user", None):
                assignee = self._user_for_email(
                    client, incident["assigned_to_user"]["email"])
            else:
                assignee = "nobody"
            if incident.get("resolved_by_user", None):
                resolver = self._user_for_email(
                    client, incident["resolved_by_user"]["email"])
            else:
                resolver = "nobody"
            if message["type"] == "incident.trigger":
                message = (
                    u"New PagerDuty incident '%(title)s' "
                    u"assigned to %(assignee)s \n"
                    u"%(url)s") % {
                    "title": title,
                    "assignee": assignee,
                    "url": url}
                client.new_message(thread_id, message, silent=False)
            elif message["type"] == "incident.resolve":
                message = (
                    u"PagerDuty incident '%(title)s' "
                    u"resolved by %(resolver)s \n"
                    u"%(url)s") % {
                    "title": title,
                    "resolver": resolver,
                    "url": url}
                client.new_message(thread_id, message, silent=True)

    def _user_for_email(self, client, email):
        cache = _per_client_email_to_id_cache.setdefault(
            client.access_token, {})
        if email not in cache:
            try:
                user = client.get_user(email)
                cache[email] = "https://quip.com/%s" % user["id"]
            except quip.QuipError:
                cache[email] = None
        return cache[email] or email



app = webapp2.WSGIApplication([
    ("/hook", HookHandler),
    ("/", MainHandler),
], debug=True)
