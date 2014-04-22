Quip API Python Client
=====

The official [Quip API](https://quip.com/api/) Python client library.

```
client = quip.QuipClient(access_token="...")
user = client.get_authenticated_user()
desktop = client.get_folder(user["desktop_folder_id"])
print "There are", len(desktop["children"]), "items on the desktop"
```
