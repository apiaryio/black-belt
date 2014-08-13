import os

import click

from blackbelt.handle_trello import migrate_label as ml, schedule_list as sl


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
    ml(**kwargs)


@cli.command(name='schedule-list')
@click.option('--story-card', help='Story Card ID or shortlink')
@click.option('--story-list', help='Name of the list that should be converted to cards')
@click.option('--owner', help='Whom to assign a created work card')
@click.option('--label', help='Assign a label to the newly-created card. For now, label must be a color name.')
def schedule_list(**kwargs):
    sl(**kwargs)
