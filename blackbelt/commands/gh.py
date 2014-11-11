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
@click.option('--card', default='',nargs=1)
def pr(card):
    pull_request(card)


@cli.command()
@click.argument('pr_url')
def merge(pr_url):
    do_merge(pr_url)


@cli.command()
@click.argument('pr_url')
def deploy(pr_url):
    do_deploy(pr_url)
