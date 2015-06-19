from slacker import Slacker
from blackbelt.config import config

class Slack(object):
    def __init__(self, token=None):
        if not token:
            token = config['slack']['access_token']
            slack = Slacker(token)
            self.slack = slack
        if not token:
            raise ValueError("Can't do things with Slack without access token. Run bb init.")

        self.token = token

    def get_user_id(self):
        return self.slack.auth.test().body['user_id']

    def post_message(self, message, room):
        return self.slack.chat.post_message(room, message, username = "Black Belt", icon_emoji = ":blackbelt:")


def post_message(message, room='#engine-room'):
    client = Slack()
    msg = "<@%s> %s" % (client.get_user_id(), message)
    client.post_message(msg, room)
