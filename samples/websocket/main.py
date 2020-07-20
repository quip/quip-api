#!/usr/bin/python2.7
#
# Copyright Quip 2016

"""Opens a websocket and listens for updates from Quip

This is a sample app for the Quip API - https://quip.com/api/.
"""

import argparse
import json
import quip
import sys
import time
import websocket

PY3 = sys.version_info > (3,)
if PY3:
    import _thread as thread
else:
    import thread

HEARTBEAT_INTERVAL = 20


def open_websocket(url):
    def on_message(ws, message):
        print("message:")
        print(json.dumps(json.loads(message), indent=4))

    def on_error(ws, error):
        print("error:")
        print(error)

    def on_close(ws):
        print("### connection closed ###")

    def on_open(ws):
        print("### connection established ###")

        def run(*args):
            while True:
                time.sleep(HEARTBEAT_INTERVAL)
                ws.send(json.dumps({"type": "heartbeat"}))

        thread.start_new_thread(run, ())

    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()


def main():
    parser = argparse.ArgumentParser(description="Twitter gateway for Quip.")
    parser.add_argument("--access_token", required=True,
        help="User's access token")
    parser.add_argument("--quip_api_base_url", default=None,
        help="Alternative base URL for the Quip API. If none is provided, "
             "https://platform.quip.com will be used")

    args = parser.parse_args()

    quip_client = quip.QuipClient(
        access_token=args.access_token,
        base_url=args.quip_api_base_url or "https://platform.quip.com")

    websocket_info = quip_client.new_websocket()
    open_websocket(websocket_info["url"])


if __name__ == "__main__":
    main()
