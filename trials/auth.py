#!/usr/bin/python

# Simple emulation of oauth codepath. Gets new tokens for client
# ex python3 auth.py --client_id='<id>' --client_secret='<secret>'
import argparse
import json
import logging
import quip

from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Queue
from threading import Thread
from urllib.parse import urlparse, parse_qs

# use a queue to pass messages from the worker thread to the main thread
q = Queue()  
httpd = None


# HTTPRequestHandler class
class OAuthServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query_args = parse_qs(url.query)
        if "code" in query_args:
            q.put(query_args["code"][0])
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("got it", "utf8"))
        return


def run_http_server():
    global httpd
    server_address = ('127.0.0.1', 8900)
    httpd = HTTPServer(server_address, OAuthServerHandler)
    print("Running http://%s:%s" % server_address)
    httpd.serve_forever()


def start_server_in_thread():
    thrd = Thread(target=run_http_server)
    thrd.start()


def main():
    # logging.getLogger().setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description="Simulate oauth client")

    parser.add_argument("--client_id",
        help="Client id to use in oauth call")
    parser.add_argument("--client_secret",
        help="Client secret to be used in oauth call")
    parser.add_argument("--redirect_uri",
        default='http://localhost:8900',
        help="Client secret to be used in oauth call")
    parser.add_argument("--quip_api_base_url", 
        default="http://platform.docker.qa:10000",
        help="Alternative base URL for the Quip API. If none is provided, "
             "http://platform.docker.qa:10000 will be used")

    args = parser.parse_args()
    start_server_in_thread()

    client = quip.QuipClient(
        client_id=args.client_id,
        client_secret=args.client_secret,
        base_url=args.quip_api_base_url,
        request_timeout=120
    )
    
    authorization_url = client.get_authorization_url(args.redirect_uri)
    print('Authorize access using the following url: %s' % authorization_url)

    # Wait for auth code from http server
    code = q.get()
    token_info = client.get_access_token(args.redirect_uri, code)
    print("token_info: %s" % json.dumps(token_info, indent=1))
    client.access_token = token_info['access_token']
    user = client.get_authenticated_user()
    print('user: %s(%s)' % (user['name'], user['emails'][0]))
    httpd.shutdown()


if __name__ == '__main__':
    main()
