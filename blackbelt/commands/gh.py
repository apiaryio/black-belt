import os

import click

from blackbelt.handle_github import pull_request

@click.group()
def cli():
    pass


@cli.command()
def pr():
	pull_request()
