import click

from blackbelt.papertrail import (
    trello_error as te
)


@click.group(help='Handle Papertrail-related actions and integrations.')
def cli():
    pass


@cli.command()
@click.argument('search_url')
def trello_error(**kwargs):
    """ Store the given (error) search in the trello card """
    te(**kwargs)
