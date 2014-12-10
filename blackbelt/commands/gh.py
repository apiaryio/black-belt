import click

from blackbelt.handle_github import (
    pull_request,
    merge as do_merge,
    deploy as do_deploy
)

from blackbelt.commands.documented_command import command


@click.group(help='Handle github-related tasks and integrations.')
def cli():
    pass


@command()
@click.argument('card_url', required=False)
def pr(card_url):
    """
    Send current branch for code review with::

        bb gh pr [CARD_URL]

    This:

    #. Inspects current repository for branches
    #. If CARD_URL parameter is not specified, it inspects ``Doing`` on the :term:`Work Board` for the current working ticket (you should have only one working ticket in ``Doing`` that is assigned only to you)
        If CARD_URL parameter is specified, it inspects ``Doing`` on the :term:`Work Board` for the selected working ticket, and will raise an error if ticket is not found.
    #. Creates a pull request that references the trello card and references the PR on the card as well
    #. Moves the card to ``Ready``
    #. Opens the browser with the PR for further editing/review
    """
    pull_request(card_url)


@command()
@click.argument('pr_url')
def merge(pr_url):
    """
    Merge PR on Github into master with::

        bb gh merge https://github.com/apiaryio/apiary/pull/1234

    This:

    #. Inspects the current repository and the pull request
    #. Switches to master and brings it up to date
    #. Merges the PR locally and pushes to master
    #. Deletes the merged branch from the remote repository/github

    TODO:

    * Comment the associated Trello card
    """
    do_merge(pr_url)


@command()
@click.argument('pr_url')
def deploy(pr_url):
    """
    Deploy PR to production with::

        bb gh deploy https://github.com/apiaryio/apiary/pull/1234

    This:

    #. Does :ref:`pr-merge`
    #. Inform people on HipChat about the merge and the deployment intent
    #. Prepares Heroku deploy slugs using ``grunt create-slug``
    #. Waits for CircleCI tests to pass
    #. TODO: If they fail, asks for retry
    #. Asks for deploy confirmation
    #. Notify others on HipChat about deploy
    #. Deploys
    #. If it can figure out related Trello card (looks for "Pull request for <link>"), moves it to "Deployed by" column
    #. Does *not* bring beer yet, unfortunately
    """
    do_deploy(pr_url)
