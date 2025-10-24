import constants
import requests

url,topic=constants.ntfy_url,constants.ntfy_tweet_alerts_topic

#Tweet notification to phone
def send_tweet_notification(tweet_url,new_tweet):
    requests.post("{}{}".format(url,topic),
    data="{}".format(new_tweet).encode(encoding='utf-8'),
    headers={
        "Title":"New Did Tech Die Tweet",
        "Actions": "view, Open Tweet, {}".format(tweet_url) })