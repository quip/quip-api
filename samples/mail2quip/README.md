# Mail2Quip

Simple (state-less) server that creates Quip messages from emails. Sample server [running here](http://mail2quip.appspot.com/).

## Caveats

API access tokens are embedded in the email. If you generate a new access token, you will need to start using a new email address.

## Running Locally

First, install the App Engine SDK from https://developers.google.com/appengine/downloads and open it to install the symlinks.  Then run:

```
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python dev_appserver.py ./
```

The App Engine admin console has a tool for testing incoming emails without deploying.

## Deploying to App Engine

```
appcfg.py --oauth2 --no_cookies update ./
```
