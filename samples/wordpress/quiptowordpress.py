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

"""Publishes a Quip document as a WordPress post.

This is an sample app for the Quip API - https://quip.com/api/.
"""

import argparse
import quip
import xmlrpclib


def main():
    parser = argparse.ArgumentParser(description="Backup of a Quip account")
    parser.add_argument("--quip_access_token", required=True,
        help="Access token for your Quip account")
    parser.add_argument("--wordpress_xmlrpc_url", required=True,
        help="XML-RPC endpoint for your WordPress blog")
    parser.add_argument("--wordpress_username", required=True,
        help="Username for your WordPress blog")
    parser.add_argument("--wordpress_password", required=True,
        help="Password for your WordPress blog")
    parser.add_argument("--publish", type=bool, default=True,
        help="Publish the post immediately")
    parser.add_argument("thread_ids", metavar="thread_id", nargs="+",
        help="The thread IDs of the documents you want to publish")
    args = parser.parse_args()

    client = quip.QuipClient(access_token=args.quip_access_token)
    server = xmlrpclib.ServerProxy(args.wordpress_xmlrpc_url)
    threads = client.get_threads(args.thread_ids)
    for thread in threads.values():
        # Remove the title from the top of the document HTML
        html = thread["html"][thread["html"].index("</h1>") + 5:].strip()
        post_id = server.wp.newPost(
            0, args.wordpress_username, args.wordpress_password, {
                "post_title": thread["thread"]["title"],
                "post_content": html,
            })
        if args.publish:
            server.mt.publishPost(
                post_id, args.wordpress_username, args.wordpress_password)


if __name__ == '__main__':
    main()
