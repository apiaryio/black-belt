from blackbelt.hipchat import post_message as hipchat_post_message
from blackbelt.slack import post_message as slack_post_message

def post_message(message):
  slack_post_message(message)
  hipchat_post_message(message)
