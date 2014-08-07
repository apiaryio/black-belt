import os

import click

@click.group(help='Handle Trello-related actions and integrations.')
def cli():
    pass


@cli.command(name='migrate-label')
@click.option('--label', default='', help='Label to migrate away')
@click.option('--board', help='Board to migrate from')
@click.option('--board-to', help='Board to migrate to')
@click.option('--column', help='Column to migrate from')
@click.option('--column-to', help='Column to migrate to')
def migrate_label(*args, **kwargs):
	from blackbelt.handle_trello import migrate_label as ml
	ml(**kwargs)

