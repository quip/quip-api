# Publish from Quip to WordPress

A simple script that publishes Quip documents as WordPress posts.

To use the script:

1. Get your [Quip access token](https://quip.com/api/personal-token)
2. Find your WordPress XML-RPC URL (usually `http://blogname.wordpress.com/xmlrpc.php`)
3. Get the ID for the Quip document you want to publish. This is the last part of the Quip URL, i.e., `https://quip.com/thread_id`

Then you can publish the document to your WordPress blog with:

```
./quiptowordpress.py \
  --wordpress_xmlrpc_url=http://example.wordpress.com/xmlrpc.php \
  --wordpress_username=... \
  --wordpress_password=... \
  --quip_access_token=... \
  thread_id
```
