import click

from blackbelt.handle_trello import (
    migrate_label as ml,
    schedule_list as sl,
    next_card as n,
    next_week as nw,
    open_current_working_ticket as cc,
    verify as v
)


@click.group(help='Handle Trello-related actions and integrations.')
def cli():
    pass


@cli.command(name='curcard')
def curcard():
    """ Open current doing card in browser """
    cc()


@cli.command(name='migrate-label')
@click.option('--label', default='', help='Label to migrate away')
@click.option('--board', help='Board to migrate from')
@click.option('--board-to', help='Board to migrate to')
@click.option('--column', help='Column to migrate from')
@click.option('--column-to', help='Column to migrate to')
def migrate_label(*args, **kwargs):
    ml(**kwargs)


@cli.command(name='schedule-list')
@click.option('--story-list', help='Name of the list that should be converted to cards')
@click.option('--owner', help='Whom to assign a created work card')
@click.option('--label', help='Assign a label to the newly-created card. For now, label must be a color name.')
@click.argument('story_card')
def schedule_list(**kwargs):
    """ Takes a TODO checklist on a given Story Card. Converts the items into the Work Overview Cards. """
    sl(**kwargs)


@cli.command()
def next(**kwargs):
    """ Takes the top card from To Do queue, moves it to doing and creates proper branch """
    n(**kwargs)


@cli.command(name='next-week')
def next_week():
    """ Creates new columns for this week """
    nw()


@cli.command()
@click.argument('story_card')
def verify(**kwargs):
    """ Verify given story card  """
    #TODO: Scan through all cards in the "Being worked on" column on story board
    v(**kwargs)
