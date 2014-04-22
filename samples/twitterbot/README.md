# Quip Twitter Bot

Simple Python process to listen for Twitter updates and post them
to a Quip thread.

## Running

```
./twitter_bot.py --thread_id="..." --search="..."
```

To install [Twython](https://twython.readthedocs.org/), run

```
pip install twython
```

You can obtain a personal access token via
[quip.com/api/personal-token](https://quip.com/api/personal-token).

You also need to configure a Twitter API token.

* Log in to https://dev.twitter.com/
* Select "My Applications" on the menu at the top right.
* Create a new application.
* Under "API Keys", enter the API key and API secret.
* Click "Create my access token" to generate an Access token and Access token secret.
