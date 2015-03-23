import click

from blackbelt.handle_github import (
    pull_request,
    merge as do_merge,
    deploy as do_deploy
)


@click.group(help='Handle github-related tasks and integrations.')
def cli():
    pass


@cli.command()
@click.argument('card_url', required=False)
def pr(*args, **kwargs):
    pr_command(*args, **kwargs)


def pr_command(card_url):
    """
    Usage::

        bb gh pr [CARD_URL]

    See :mod:`threading` for more details.
    """
    pull_request(card_url)


@cli.command()
@click.argument('pr_url')
def merge(*args, **kwargs):
    merge_command(*args, **kwargs)


def merge_command(pr_url):
    """
    Usage::

        bb gh merge https://github.com/apiaryio/apiary/pull/1234
    """
    do_merge(pr_url)


@cli.command()
@click.argument('pr_url')
def deploy(*args, **kwargs):
    deploy_command(*args, **kwargs)


def deploy_command(pr_url):
    """
    Usage::

        bb gh deploy https://github.com/apiaryio/apiary/pull/1234
    """
    do_deploy(pr_url)
