# Outlook Add-in

A simple Outlook Add-in that can save an email thread in Outlook as a Quip document and automatically share with the corresponding users on Quip.

## Setup

1. `npm install`
2. Create a file called `config.json` with the following contents. You can find your Quip API token [here](https://quip.com/api/personal-token)
    ```js
    {
        "serverUrl": "https://<YOUR_WEB_SERVER>",
        "accessTokens": {
            "<your.email@outlook.com>": "<QUIP_API_TOKEN>"
        }
    }
    ```
3. `npm run manifest`, this will generate a new file called `manifest.xml`
4. Install the add-in by going to Outlook.com -> Options -> General -> Manage add-ins -> + button -> Add from File
5. Go to any email thread and click on the "Quip It" button
