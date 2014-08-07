import os

import click

from blackbelt.handle_github import pull_request

@click.group(help='Handle github-related tasks and integrations.')
def cli():
    pass


@cli.command()
def pr():
	pull_request()
