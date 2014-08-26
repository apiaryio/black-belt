import click

from blackbelt.handle_trello import (
    migrate_cards as mc,
    schedule_list as sl
)


@click.group(help='Handle Trello-related actions and integrations.')
def cli():
    pass


@cli.command(name='migrate-cards')
@click.option('--label', help='Label to migrate from')
@click.option('--user', help='User to migrate from')
@click.option('--board', help='Board to migrate from')
@click.option('--board-to', help='Board to migrate to')
@click.option('--column', help='Column to migrate from')
@click.option('--column-to', help='Column to migrate to')
def migrate_cards(*args, **kwargs):
    mc(**kwargs)


@cli.command(name='schedule-list')
@click.option('--story-list', help='Name of the list that should be converted to cards')
@click.option('--owner', help='Whom to assign a created work card')
@click.option('--label', help='Assign a label to the newly-created card. For now, label must be a color name.')
@click.argument('story_card')
def schedule_list(**kwargs):
    sl(**kwargs)
