import click

from blackbelt.handle_github import pull_request, merge as do_merge


@click.group(help='Handle github-related tasks and integrations.')
def cli():
    pass


@cli.command()
def pr():
    pull_request()


@cli.command()
@click.argument('pr_url')
def merge(pr_url):
    do_merge(pr_url)
