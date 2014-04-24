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
    def __init__(self, thread_id, quip_api_base_url):
        self.quip_client = quip.QuipClient(
            access_token=ACCESS_TOKEN, base_url=quip_api_base_url)
        self.thread_id = thread_id
        super(TwitterBot, self).__init__(
            TWITTER_API_KEY, TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    def on_success(self, data):
        name = data["user"]["name"]
        screen_name = data["user"]["screen_name"]
        text = _format_status_text(data)
        url = "https://twitter.com/%s/status/%s" % (screen_name, data["id_str"])
        message = "%s (@%s) tweeted: %s\n%s" % (name, screen_name, text, url)
        try:
            self.quip_client.new_message(self.thread_id, message, silent=True)
        except Exception:
            logging.error("Failed to post tweet to quip - %s." % url)

    def on_timeout(self):
        print "timeout"

    def on_error(self, status, data):
        print status, data


def _format_status_text(status):
    def unescape(t):
        return t.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    urls = status.get("entities", {}).get("urls", [])
    urls.sort(key=lambda url:url["indices"][0])
    last_url_end = 0
    result = ""
    text = status["text"]
    for url in urls:
        url_start, url_end = url["indices"]
        result += unescape(text[last_url_end:url_start])
        result += url.get("expanded_url") or \
            url.get("display_url") or url.get("url")
        last_url_end = url_end
    result += unescape(text[last_url_end:])
    return result


def main():
    parser = argparse.ArgumentParser(description="Twitter gateway for Quip.")
    parser.add_argument("--thread_id", required=True,
        help="The quip thread that mentions should be sent to.")
    parser.add_argument("--search", required=True,
        help="The phrase to search for.  Can include @ or #")
    parser.add_argument("--filter_level", default="medium",
        help="The filter level for Tweets. Can be 'none', 'low', or 'medium'.")
    parser.add_argument("--quip_api_base_url", default=None,
        help="Alternative base URL for the Quip API. If none is provided, "
             "https://platform.quip.com will be used")

    args = parser.parse_args()
    t = TwitterBot(thread_id=args.thread_id,
        quip_api_base_url=args.quip_api_base_url)
    t.statuses.filter(track=args.search, filter_level=args.filter_level)


if __name__ == "__main__":
    main()
