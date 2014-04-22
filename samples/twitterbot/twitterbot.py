#!/usr/bin/python2.7
#
# Copyright Quip 2014

"""Updates Quip with new Twitter messages.

This is a sample app for the Quip API - https://quip.com/api/.
"""

import argparse
import logging
import quip
import twython

ACCESS_TOKEN = ""

TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_SECRET = ""


class TwitterBot(twython.TwythonStreamer):
    def __init__(self, thread_id):
        self.quip_client = quip.QuipClient(access_token=ACCESS_TOKEN)
        self.thread_id = thread_id
        super(TwitterBot, self).__init__(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    def on_success(self, data):
        url = "https://twitter.com/%s/status/%s" % (
            data["user"]["screen_name"], data["id_str"])
        message = "%s (@%s) tweeted: %s - %s" % (
            data["user"]["name"], data["user"]["screen_name"],
            data["text"], url)
        try:
            self.quip_client.new_message(self.thread_id, message, silent=True)
        except Exception:
            logging.error("Failed to post tweet to quip - %s." % url)

    def on_timeout(self):
        print "timeout"

    def on_error(self, status, data):
        print status, data


def main():
    parser = argparse.ArgumentParser(description="Twitter gateway for Quip.")
    parser.add_argument("--thread_id", required=True,
        help="The quip thread that mentions should be sent to.")
    parser.add_argument("--search", required=True,
        help="The phrase to search for.  Can include @ or #")
    parser.add_argument("--filter_level", default="medium",
        help="The filter level for Tweets. Can be 'none', 'low', or 'medium'.")

    args = parser.parse_args()
    t = TwitterBot(thread_id=args.thread_id)
    t.statuses.filter(track=args.search, filter_level=args.filter_level)


if __name__ == "__main__":
    main()
