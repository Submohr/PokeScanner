from http import client
import urllib
from config import Config


def send_message(message):
    conn = client.HTTPSConnection("api.pushover.net:443")
    message = message[:1000]
    conn.request("POST", "/1/messages.json", urllib.parse.urlencode({"token": Config.PUSHOVER_TOKEN,
                                                                     "user": Config.PUSHOVER_USER,
                                                                     "message": message,
                                                                     "html": "1"}),
                 {"Content-type": "application/x-www-form-urlencoded"})
    Config.LOGGER.info(f"Pushed message: {message}")
    return conn.getresponse()


