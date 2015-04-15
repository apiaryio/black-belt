import click

from blackbelt.slack import (
    post_message
)


@click.group(help='Handle Slack-related tasks and integrations.')
def cli():
    pass


@cli.command()
@click.argument('message', required=True)
def post(message):
    post_message(message)
