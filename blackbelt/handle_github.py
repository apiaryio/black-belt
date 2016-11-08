from datetime import datetime, timedelta
import json
import re
from subprocess import check_output
from time import sleep
import webbrowser

import click
import requests

from .config import config
from .handle_trello import (
    get_current_working_ticket,
    get_ticket_ready,
    comment_ticket,
    move_to_deployed
)

from .git import (
    get_current_branch,
    merge as git_merge,
    get_github_repo,
    get_remote_repo_info
)

from .messages import post_message
from .circle import wait_for_tests
from .version import VERSION
from .notify import notify

GITHUB_CLIENT_ID = "c9f51ce9cb320bf86f16"

UA_STRING = "black-belt/%s" % VERSION

PR_PHRASE_PREFIX = "Pull request for"

def get_pr_info(pr_url):
    match = re.match(r".*github.com/(?P<owner>\S+)/{1}(?P<name>\S+)/pull/{1}(?P<number>\d+).*$", pr_url)
    if not match:
        raise ValueError("Cannot parse pull request URL, bad format")
    return match.groupdict()

def get_pr_api_url(pr_url):
    pr_info = get_pr_info(pr_url)
    return "https://api.github.com/repos/%(owner)s/%(name)s/pulls/%(number)s" % pr_info

def get_pr_details(pr_url):
    return get_json_response(get_pr_api_url(pr_url))

def get_branch_url(pr_details):
    return "https://api.github.com/repos/%(repo_full_name)s/git/refs/heads/%(branch)s" % {
        'repo_full_name': pr_details['base']['repo']['full_name'],
        'branch': pr_details['head']['ref']
    }

def get_username():
    url = "https://api.github.com/user"

    res = get_json_response(url)

    return res['login']

def get_request_headers():
    return {
        'Authorization': "token %s" % config['github']['access_token'],
        'User-Agent': UA_STRING
    }

def get_json_response(url):
    r = requests.get(url, headers=get_request_headers())

    if r.status_code != 200:
        raise ValueError("Request to URL %s failed with code %s: %s" % (url, r.status_code, r))

    return r.json()

def pull_request(card_url):
    """
    Sends current branch for code review.

    #. Inspects current repository for branches
    #. If CARD_URL parameter is not specified, it inspects ``Doing`` on the :term:`Work Board` for the current working ticket (you should have only one working ticket in ``Doing`` that is assigned only to you). If it is specified, it inspects ``Doing`` on the :term:`Work Board` for the selected working ticket, and will raise an error if ticket is not found.
    #. Creates a pull request that references the trello card and references the PR on the card as well
    #. Moves the card to ``Ready``
    #. Opens the browser with the PR for further editing/review
    """
    branch = get_current_branch()
    repo = get_github_repo()

    if 'github.com' not in repo:
        raise ValueError("Current git origin not on github.com; aborting")

    ticket = get_current_working_ticket(card_url)
    md_link = "[%(name)s](%(url)s)" % ticket

    pr_description = """

%(phrase)s %(link)s.

    """ % {
        'phrase': PR_PHRASE_PREFIX,
        'link': md_link
    }

    repo_info = get_remote_repo_info(repo)

    url = "https://api.github.com/repos/%(owner)s/%(name)s/pulls" % repo_info

    payload = {
        'title': ticket['name'],
        'base': 'master',
        'head': "%(owner)s:%(branch)s" % {'branch': branch, 'owner': repo_info['owner']},
        'body': pr_description
    }

    r = requests.post(url, data=json.dumps(payload), headers=get_request_headers())

    if r.status_code != 201:
        print r.json()
        raise ValueError("PR ended with status code %s: %s" % (r.status_code, r))

    get_ticket_ready(ticket)

    pr_info = r.json()

    ticket_comment = "Sending [pull request #%(number)s](%(html_url)s)." % pr_info

    comment_ticket(ticket, ticket_comment)

    print "Pull request %(pr_id)s for trello card %(ticket_url)s send!" % {
        'pr_id': pr_info['number'],
        'ticket_url': ticket['url']
    }

    webbrowser.open(pr_info['html_url'])

def verify_merge(pr_url, headers, max_waiting_time=30, retry_time=0.1):
    merge_url = get_pr_api_url(pr_url) + "/merge"  # https://api.github.com/repos/apiaryio/apiary/pulls/1234/merge
    start_time = datetime.now()
    succeeded = False

    def do_request():
        r = requests.get(merge_url, headers=headers)

        if r.status_code == 404:
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
    """
    This merges PR on Github into master:

    #. Inspects the current repository and the pull request
    #. Switches to master and brings it up to date
    #. Merges the PR locally and pushes to master
    #. Deletes the merged branch from the remote repository/github

    TODO:

    * Comment the associated Trello card

    """

    pr_details = get_pr_details(pr_url)

    # Check if PR is ready to merge - OPEN status
    verify_pr_state(pr_details)

    # Check if required status checks passed for the PR
    verify_pr_required_checks(pr_details)

    # Check if PR GitHub repository matches the current repository
    verify_gh_repo(pr_details['base']['repo'])

    # Check if master is ready; if not (e.g. failed, pending), confirm with the user
    try:
        verify_branch_required_checks(branch_name="master")
    except ValueError:
        click.confirm("The master branch hasn't passed the required checks. Do you still want to continue?", abort=True)

    sha = pr_details['head']['sha']

    merge_sha = git_merge(
        sha=sha,
        message="Merging pull request #%(number)s: %(title)s " % pr_details
    )

    headers = get_request_headers()
    verify_merge(pr_url, headers)

    # All good, delete branch
    branch_url = get_branch_url(pr_details)

    r = requests.delete(branch_url, headers=headers)

    if r.status_code != 204:
        raise ValueError("Failed to delete branch after merging pull request, go do it manually")

    print "#%(number)s merged!" % pr_details

    post_message("[%(repo_full_name)s] Merged PR #%(number)s: %(title)s (%(commits)s commits, %(comments)s comments)" % {
        'repo_full_name': pr_details['base']['repo']['full_name'],
        'number': pr_details['number'],
        'title': pr_details['title'],
        'comments': pr_details['comments'],
        'commits': pr_details['commits']
    }, "#deploy-queue")

    return {
        'sha': merge_sha,
        'owner': pr_details['base']['repo']['owner']['login'],
        'name': pr_details['base']['repo']['name'],
        'number': pr_details['number'],
        'description': pr_details['body'],
        'html_url': pr_details['html_url'],
        'title': pr_details['title'],
        'branch': pr_details['head']['ref']
    }

def check_status(pr_url=None, branch_name=None, error_on_failure=False):
    """
    Returns status and required checks status of a given PR or branch.

    This can be used to determine if a PR/branch can be merged without issues. Required checks might involve a status
    of a CI build, status of code reviews, etc. (see https://help.github.com/articles/about-required-status-checks/)

    Pull requests

    #. Checks for Pull Request current state (open/closed)
    #. Retrieves required checks status (success/failure/pending)

    Branches

    #. Retrieves required checks status (success/failure/pending)
    """

    if not (pr_url or branch_name):
        return

    if pr_url:
        pr_details = get_pr_details(pr_url)
        try:
            # Check if PR state is open
            verify_pr_state(pr_details)
            # Check if PR is ready (all required checks passed)
            verify_pr_required_checks(pr_details)
        except ValueError as exc:
            if error_on_failure:
                raise
            else:
                print exc.message

    if branch_name:
        try:
            verify_branch_required_checks(branch_name)
        except ValueError as exc:
            if error_on_failure:
                raise
            else:
                print exc.message

def verify_pr_state(pr_details):
    pr_state = pr_details['state']
    message = "PR state: %s" % pr_state
    if pr_state != 'open':
        raise ValueError(message)

    print message
    return message

def verify_pr_required_checks(pr_details):
    status_url = "https://api.github.com/repos/%(repo_full_name)s/commits/%(head_sha)s/status" % {
        'repo_full_name': pr_details['base']['repo']['full_name'],
        'head_sha': pr_details['head']['sha']}

    pr_checks_info = get_json_response(status_url)
    message = "PR required checks (%(count)g): %(state)s" % {
        'count': len(pr_checks_info['statuses']),
        'state': pr_checks_info['state']}
    if pr_checks_info['state'] != 'success':
        raise ValueError(message)

    print message
    return message

def verify_branch_required_checks(branch_name):
    repo = get_github_repo()
    repo_info = get_remote_repo_info(repo)

    status_url = "https://api.github.com/repos/%(owner)s/%(name)s/commits/%(branch_name)s/status" % {
        'owner': repo_info['owner'],
        'name': repo_info['name'],
        'branch_name': branch_name}
    branch = get_json_response(status_url)
    message = "Branch required checks (%(count)g): %(state)s" % {
        'count': len(branch['statuses']),
        'state': branch['state']}
    if branch['state'] != 'success':
        raise ValueError(message)

    print message
    return message

def verify_gh_repo(pr_gh_repo):
    origin_gh_repo = get_github_repo()

    if origin_gh_repo not in [
        pr_gh_repo['git_url'],
        pr_gh_repo['ssh_url'],
        pr_gh_repo['clone_url']
    ]:
            raise ValueError("The pull request is for the repository %s, while your origin is set up for %s" % (
                pr_gh_repo['git_url'], origin_gh_repo))


def get_pr_ticket_id(description):
    match = re.search(PR_PHRASE_PREFIX + ' ' + r"\[.*\]\(https://trello.com/c/(?P<id>\w+)/.*\)", description)
    if not match or not 'id' in match.groupdict():
        raise ValueError("Can't find URL in the PR description")

    return match.groupdict()['id']

def deploy(pr_url):
    """
    Deploys PR to production

    #. Does :ref:`pr-merge`
    #. Inform people on Slack about the merge and the deployment intent
    #. Prepares Heroku deploy slugs using ``grunt create-slug``
    #. Waits for CircleCI tests to pass
    #. TODO: If they fail, asks for retry
    #. Asks for deploy confirmation
    #. Notify others on Slack about deploy
    #. Deploys
    #. Creates a release on GitHub, using merged branch name as 'ref'.
    #. If it can figure out related Trello card (looks for "Pull request for <link>"), moves it to "Deployed by" column
    #. Does *not* bring beer yet, unfortunately

    """
    merge_info = merge(pr_url)

    repo = get_github_repo()
    repo_info = get_remote_repo_info(repo)

    check_output(['grunt', 'create-slug'])

    print "Waiting for tests to pass..."

    ci_info = wait_for_tests(
        sha=merge_info['sha'],
        owner=merge_info['owner'],
        name=merge_info['name']
    )

    if ci_info['failed']:
        notify('Apiary Deployment', "Tests FAILED for %s" % merge_info['sha'])
        raise ValueError("Circle build failed. TODO: Auto retry.")
    notify('Apiary Deployment', "New version %s ready for deploy" % merge_info['sha'])

    # Insert newline
    print ''

    click.confirm("Ready for deploy! Do you want me to deploy %s as the new version of Apiary?" % merge_info['sha'], abort=True)

    post_message("Deploying \"%(title)s\" in 15 seconds" % merge_info, "#deploy-queue")

    sleep(15)

    check_output(['grunt', 'deploy-slug'])

    comment = "Deployed by me with version %s. Please verify it works." % merge_info['sha']

    try:
        ticket_id = get_pr_ticket_id(merge_info['description'])
        move_to_deployed(card_id=ticket_id, comment=comment)
    except ValueError:
        if click.prompt("Moving card failed. Open PR in browser?", default=True):
            webbrowser.open(merge_info['html_url'])

    create_release(ref=merge_info['branch'], payload='', description="Deployed to production", repo_info=repo_info)

def create_release(ref, payload, description, repo_info):
    """ Create release in github after deploy to production """

    url = "https://api.github.com/repos/%(owner)s/%(name)s/deployments" % repo_info

    body = {
        'ref': ref,
        'payload': payload,
        'description': description
    }

    r = requests.post(url, data=json.dumps(body), headers=get_request_headers())

    if r.status_code != 201:
        print r.json()
        raise ValueError("Create github release ended with status code %s: %s" % (r.status_code, r))
