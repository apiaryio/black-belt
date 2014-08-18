from datetime import datetime, timedelta
import json
import re
from subprocess import check_output
from time import sleep
import webbrowser

import requests

from config import config
from handle_trello import get_current_working_ticket, pause_ticket, comment_ticket
from version import VERSION

GITHUB_CLIENT_ID = "c9f51ce9cb320bf86f16"

UA_STRING = "black-belt/%s" % VERSION


def get_github_repo():
    return check_output(['git', 'config', '--get', 'remote.origin.url']).strip()


def get_remote_repo_info(github_repo_info):
    match = re.match(r".*github.com:(?P<owner>[a-zA-Z\_\-]+)/{1}(?P<name>[a-zA-Z\-\_]+)\.git$", github_repo_info)
    if not match:
        raise ValueError("Cannot parse repo info. Bad remote?")
    return match.groupdict()

def get_pr_info(pr_url):
    match = re.match(r".*github.com/(?P<owner>\S+)/{1}(?P<name>\S+)/pull/{1}(?P<number>\d+).*$", pr_url)
    if not match:
        raise ValueError("Cannot parse pull request URL, bad format")
    return match.groupdict()


def pull_request():
    branch = get_current_branch()
    repo = get_github_repo()

    if 'github.com' not in repo:
        raise ValueError("Current git origin not on github.com; aborting")

    ticket = get_current_working_ticket()

    pr_description = """

Pull request for [%(name)s](%(url)s).

    """ % ticket

    repo_info = get_remote_repo_info(repo)

    url = "https://api.github.com/repos/%(owner)s/%(name)s/pulls" % repo_info

    payload = {
        'title': ticket['name'],
        'base': 'master',
        'head': "%(owner)s:%(branch)s" % {'branch': branch, 'owner': repo_info['owner']},
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

    ticket_comment = "Sending [pull request #%(number)s](%(html_url)s)" % pr_info

    comment_ticket(ticket, ticket_comment)

    print "Pull request %(pr_id)s for trello card %(ticket_url)s send!" % {
        'pr_id': pr_info['number'],
        'ticket_url': ticket['url']
    }

    webbrowser.open(pr_info['html_url'])


def get_current_branch():
    return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()

def verify_merge(pr_info, headers, max_waiting_time=30, retry_time=0.1):
    
    merge_url = "https://api.github.com/repos/%(owner)s/%(name)s/pulls/%(number)s/merge" % pr_info
    start_time = datetime.now()
    succeeded = False

    def do_request():
        r = requests.get(merge_url, headers=headers)

        if (r.status_code == 404):
            if datetime.now() < start_time + timedelta(seconds=max_waiting_time):
                sleep(retry_time)
                return False
            else:
                raise ValueError("GitHub says PR hasn't been merged yet and I've reached the waiting time of %s seconds" % max_waiting_time)

        elif (r.status_code not in [200, 204]):
            raise ValueError("Can't get PR merge info with status code %s" % r.status_code)

        else:
            return True


    while not succeeded:
        succeeded = do_request()




def merge(pr_url):
    """ Merge the given pull request...locally """

    pr_info = get_pr_info(pr_url)

    pr_api_url = "https://api.github.com/repos/%(owner)s/%(name)s/pulls/%(number)s" % pr_info

    headers = {
        'Authorization': "token %s" % config['github']['access_token'],
        'User-Agent': UA_STRING
    }

    r = requests.get(pr_api_url, headers=headers)

    if (r.status_code != 200):
        raise ValueError("Cannot retrieve PR info with status code %s: %s" % (r.status_code, r))

    pr = r.json()

    if pr['state'] != 'open':
        raise ValueError("PR is %(state)s instead of still being open; not merging" % pr)

    gh_repo = pr['base']['repo']

    if get_github_repo() not in [
        gh_repo['git_url'],
        gh_repo['ssh_url'],
        gh_repo['clone_url']
    ]:
        raise ValueError("The pull request is for the repository %s, while your origin is set up for %s" % (
                gh_repo['git_url'], get_github_repo()
            ))

    sha = pr['head']['sha']

    if get_current_branch() != 'master':
        check_output(['git', 'checkout', 'master'])

    check_output(['git', 'pull'])

    check_output(['git', 'merge', sha, '-m', "Merging pull request #%(number)s: %(title)s " % pr])

    check_output(['git', 'push', 'origin', 'master'])

    verify_merge(pr_info, headers)

    # All good, delete branch
    branch_url = "https://api.github.com/repos/%(owner)s/%(name)s/git/refs/heads/%(branch)s" % {
        'owner': pr_info['owner'],
        'name': pr_info['name'],
        'branch': pr['head']['ref']

    }
    r = requests.delete(branch_url, headers=headers)

    if (r.status_code != 204):
        raise ValueError("Failed to delete branch after merging pull request, go do it manually")

    print "#%(number)s merged!" % pr_info
