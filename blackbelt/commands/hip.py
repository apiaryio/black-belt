import click

from blackbelt.hipchat import (
    post_message,
    get_last_errors,
)


@click.group(help='Handle HipChat-related tasks and integrations.')
def cli():
    pass


@cli.command()
@click.argument('message', required=True)
def post(message):
    post_message(message)


@cli.command()
def last_errors():
    print get_last_errors()
