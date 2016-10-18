Quip API Python Client
=====

The official [Quip API](https://quip.com/api/) Python client library.

```python
client = quip.QuipClient(access_token="...")
user = client.get_authenticated_user()
starred = client.get_folder(user["starred_folder_id"])
print "There are", len(starred["children"]), "items in your starred folder"
```
