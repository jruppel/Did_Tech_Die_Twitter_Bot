import constants
import requests

url, topic = constants.ntfy_url, constants.ntfy_tweet_alerts_topic
logging = constants.logging

# Tweet notification to phone
def send_tweet_notification(tweet_url, new_tweet):
    try:
        response = requests.post(
            f"{url}{topic}",
            data=str(new_tweet).encode(encoding='utf-8'),
            headers={
                "Title": "New Did Tech Die Tweet",
                "Actions": f"view, Open Tweet, {tweet_url}"
            },
            timeout=10
        )
        return response
    except Exception as e:
        logging.warning(f"Failed to send tweet notification via ntfy: {e}")
        return None