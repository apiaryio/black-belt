from blackbelt.slack import post_message as slack_post_message

def post_message(message, room):
  slack_post_message(message, room)
