# Webhooks for Quip

Simple (state-less) server that serves as a [Webhook](http://en.wikipedia.org/wiki/Webhook) endpoint and forwards messages to Quip threads. Currently supported services are:

* [GitHub](https://github.com/): Notifications of commits.
* [Crashlytics](https://crashlytics.com/): Notifications of issues.
* [PagerDuty](https://pagerduty.com/): Notifications of new and resolved incidents.

An instance is running at [http://quip-webhooks.appspot.com](http://quip-webhooks.appspot.com).

## Caveats

API access tokens are embedded in hook URLs. If you generate a new access token, you will need to edit the hook URL at its registered service.

## Running Locally

First, install the App Engine SDK from https://developers.google.com/appengine/downloads and open it to install the symlinks.  Then run:

```
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python dev_appserver.py ./
```

To test changes without having to deploy, you can install [ngrok](https://ngrok.com) which tunnels a localhost port such that it can be accessed from the Internet. Run:

```
ngrok 8080
```

And you'll be given an URL like `27841f20.ngrok.com` which you can use with GitHub, Crashlytics, etc. You can also visit [http://localhost:4040/](http://localhost:4040/) to see all tunneled requests (and to replay them).

## Deploying to App Engine

```
appcfg.py --oauth2 --no_cookies update ./
```
