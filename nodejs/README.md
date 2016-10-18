Quip API node.js Client
=====

The official [Quip API](https://quip.com/api/) node.js client library.

```javascript
var client = new quip.Client({accessToken: "..."});
client.getAuthenticatedUser(function(err, user) {
    client.getFolder(user["starred_folder_id"], function(err, folder) {
        console.log("You have", folder["children"].length,
                    "items in your starred folder");
    });
});
```
