import os
from subprocess import check_output
import sys

from github import Github

from config import config
from handle_trello import get_current_working_ticket

GITHUB_CLIENT_ID = "c9f51ce9cb320bf86f16"

def dispatch_command(args):
    if 'GITHUB_OAUTH_TOKEN' not in os.environ and 'access_token' not in config['github']:
        print "You have to set up GITHUB_OAUTH_TOKEN"
#        print "Please visit this URL to get it: %s" % api.get_token_url("black-belt")
        sys.exit(1)


    if args.action_command in ACTION_COMMAND_MAP:
        ACTION_COMMAND_MAP[args.action_command](args)


def pr_command(args):
    pull_request(
    )


def pull_request():
    branch = get_current_branch()

    ticket = get_current_working_ticket()

    print(ticket)



def get_current_branch():
    return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])



ACTION_COMMAND_MAP = {
    'pr': pr_command
}
