from blackbelt.apis.hipchat import HipChat


def post_message(message):
    client = HipChat()
    client.post_message(message)
