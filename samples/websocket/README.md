# Receive messages from Quip in real time

A simple script to open up a websocket and listen for updates from Quip.

## Running

```
./main.py --access_token="..."
```

You can obtain a personal access token via [quip.com/api/personal-token](https://quip.com/api/personal-token).

If you wish to target an alternate Quip server, you can use the `--quip_api_base_url` flag.
