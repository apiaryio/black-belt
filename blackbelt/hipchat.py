from blackbelt.apis.hipchat import HipChat


def post_message(message):
    client = HipChat()
    client.post_message(message)


def get_last_errors():
    client = HipChat()

    return client.get_last_errors()
