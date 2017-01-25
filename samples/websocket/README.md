# Receive Realtime Updates from Quip

A simple script to open up a websocket and listen for updates from a thread in Quip.

## Running

```
./main.py --access_token="..." --thread_id="..."
```

You can obtain a personal access token via [quip.com/api/personal-token](https://quip.com/api/personal-token).

If you wish to target an alternate Quip server, you can use the `--quip_api_base_url` flag.
