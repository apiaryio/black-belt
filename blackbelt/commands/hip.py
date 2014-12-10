import click

from blackbelt.hipchat import (
    post_message,
)


@click.group(help='Handle HipChat-related tasks and integrations.')
def cli():
    pass


@cli.command()
@click.argument('message', required=True)
def post(message):
    post_message(message)
