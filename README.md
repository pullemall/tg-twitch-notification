# tg-twitch-notification
Sends notification to telegram channel about new videos on youtube and live translations on twitch

## Deployment process on pythonanywhere
Before deploying your web app you must create your own channel and bot which will send notifications to that channel. Create a twitch application and get client id. After taking all that stuff you must set bot token, client id and channel id in config.py file.


1. Create directory and upload project files in there
2. Create a virtual environment and install dependences `pip3 install -r requirements.txt`
3. Go to https://www.pythonanywhere.com/user/username/webapps/
4. Add new web app with manual configuration and python version 3.7
5. Go to "Code" section and enter the path to your web app in source code
6. In "Virtualenv" section enter the path to virtual environment section you've created before
7. Reload your web application


## Subscribing to webhooks on Twitch
1. Authentication process: https://dev.twitch.tv/docs/authentication
2. Get user id for subscribe: 
`curl -H "Client-ID: [your-client-id]" -X GET 'https://api.twitch.tv/helix/users?login=[username]`
3. Subscription: `curl -H "Client-ID: [your-client-id]" -H "Content-Type: application/json" -X POST -d "{\"hub.callback\": \"https://[registraion-username].pythonanywhere.com/\", \"hub.mode\": \"subscribe\", \"hub.topic\":\"https://api.twitch.tv/helix/streams?user_id=[user_id]\", \"hub.lease_seconds\":\"864000\"}" https://api.twitch.tv/helix/webhooks/hub`
(Detailed subscription process: https://dev.twitch.tv/docs/api/webhooks-reference)

If you want to check your subscriptions you must create bearer token. At first generate secret key in your twitch application. Send GET request like this: `https://id.twitch.tv/oauth2/token?client_id=[client-id]&client_secret=[secret-key]&grant_type=client_credentials`. Then you will be able to check your subscriptions by sending request: `curl -H "Authorization: Bearer [TOKEN]" -X GET https://api.twitch.tv/helix/webhooks/subscriptions`

## Subscribing to webhooks on Youtube
1. Use https://pubsubhubbub.appspot.com/subscribe for subscribing to notifications.
Full documentation: https://developers.google.com/youtube/v3/guides/push_notifications
