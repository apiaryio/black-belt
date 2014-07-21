import os
from subprocess import check_output
import sys

from github import Github
import json
import requests
import webbrowser

from config import config
from handle_trello import get_current_working_ticket, pause_ticket, comment_ticket

GITHUB_CLIENT_ID = "c9f51ce9cb320bf86f16"

def dispatch_command(args):
    if 'GITHUB_OAUTH_TOKEN' not in os.environ and 'access_token' not in config['github']:
        print "You have to set up GITHUB_OAUTH_TOKEN"
#        print "Please visit this URL to get it: %s" % api.get_token_url("black-belt")
        sys.exit(1)


    if args.action_command in ACTION_COMMAND_MAP:
        ACTION_COMMAND_MAP[args.action_command](args)


def pr_command(args):
    pull_request()

def get_github_repo():
    return check_output(['git', 'config', '--get', 'remote.origin.url']).strip()


def pull_request():
    branch = get_current_branch()
    repo   = get_github_repo()

    if 'github.com' not in repo:
        raise ValueError("Current git origin not on github.com; aborting")

    ticket = get_current_working_ticket()

    api    = Github(config['github']['access_token'])

    pr_description = """

Pull request for [%(name)s](%(url)s).

    """ % ticket

    #FIXME, parser owner as well
    name = repo.split('/')[1].split('.')[0]

    url = "https://api.github.com/repos/apiaryio/%s/pulls" % name

    payload = {
        'title': ticket['name'],
        'base': 'master',
        'head': "apiaryio:%s" % branch,
        'body': pr_description
    }

    headers = {
        'Authorization': "token %s" % config['github']['access_token']
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers)

    if r.status_code != 201:
        print r.json()
        raise ValueError("PR ended with status code %s: %s" % (r.status_code, r))

    pause_ticket(ticket)

    pr_info = r.json()

    ticket_comment = "Sending [pull request #%(number)s](%(url)s)" % pr_info

    comment_ticket(ticket, ticket_comment)

    print "Pull request %(pr_id)s for trello card %(ticket_id)s send!" % {
        'pr_id': pr_info['number'],
        'ticket_id': ticket['id']
    }

    webbrowser.open(pr_info['html_url'])



def get_current_branch():
    return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()



ACTION_COMMAND_MAP = {
    'pr': pr_command
}
