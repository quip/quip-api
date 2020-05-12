# Examine, audit, and quaratine Quip content in real-time based on the Events API feed.

A simple webserver to manage [Events API](https://quip.com/dev/admin/documentation#events-requires-subscription) cursors, audit messages, examine threads, and quarantine content.

## Requirements
Uses the [tornado](https://pypi.org/project/tornado/) networking library to run a local server.

```
pip install -r requirements.txt
```

## Running

```
./quarantine_demo.py
```

Requires an admin [access token](https://quip.com/dev/automation) and Events API subscription.