import click

from blackbelt.handle_trello import (
    migrate_label as ml,
    schedule_list as sl,
    next_card as n,
    next_week as nw,
    open_current_working_ticket as cc,
    verify as v,
    order_tea as ot
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
    """
    Usage::

        bb t migrate-label --label="Product: Example" --board="1KsoiV9e" --board-to="lEL8Ch52" --column-to="Prepared buffer"
    """
    ml(**kwargs)


@cli.command(name='schedule-list')
@click.option('--story-list', help='Name of the list that should be converted to cards')
@click.option('--owner', help='Whom to assign a created work card')
@click.option('--label', help='Assign a label to the newly-created card. For now, label must be a color name.')
@click.argument('story_card')
def schedule_list(**kwargs):
    """
    Usage::

        bb t schedule-list [--owner="TrelloUserName" [--story-list="Checklist Name"] [--label="color"] http://trello.com/c/story-card-shortlink

    Takes a TODO checklist on a given Story Card. Converts the items into the Work Overview Cards.

    Story list defaults to "To Do", Owner (that the new work tasks are assigned to) defaults to you.
    """
    sl(**kwargs)


@cli.command()
def next(**kwargs):
    """ Takes the top card from To Do queue, moves it to doing and creates proper branch """
    n(**kwargs)


@cli.command(name='next-week')
def next_week():
    """
    Create new columns on the :term:`Work Board`: `Deployed by <sunday>` and `Verified by <sunday>`::

        bb t next-week
    """
    nw()


@cli.command()
@click.argument('story_card')
def verify(**kwargs):
    """
    Looks through a checklists on :term:`Story`, see whether incomplete items refer to a card and whether the card is in `Deployed by <sunday>` and `Verified by <sunday>` column.

    If so, ask to open them and then to verify them (meaning ticking the checkbox)::

        bb t verify http://trello.com/c/story

    """
    #TODO: Scan through all cards in the "Being worked on" column on story board
    v(**kwargs)


@cli.command(name='gimmetea')
def order_tea():
    """ Gather information about Tea and sent it to Office Manager for order """
    ot()
