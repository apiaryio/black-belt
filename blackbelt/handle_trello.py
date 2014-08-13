import json
import os
import re
import sys
import urllib

from trello import TrelloApi
import requests

from blackbelt.apis.trello import *
from blackbelt.config import config

__all__ = ("schedule_list", "migrate_label", "schedule_list")

TRELLO_API_KEY = "2e4bb3b8ec5fe2ff6c04bf659ee4553b"

STORY_CARD_TODO_LIST_NAMES = [
    "To Do",
    "ToDo",
    "Engineering ToDo"
]

TODO_QUEUE_NAME = "To Do Queue"


def get_token_url():
    return TrelloApi(apikey=TRELLO_API_KEY).get_token_url("black-belt")


def get_api():
    api = TrelloApi(apikey=TRELLO_API_KEY)
    api.set_token(config['trello']['access_token'])
    return api


def get_column(name, board_id=None):
    api = get_api()

    if not board_id:
        board_id = config['trello']['work_board_id']

    columns = api.boards.get_list(board_id)
    column = None

    for col in columns:
        if col['name'] == name:
            column = col

    if not column:
        raise ValueError("Cannot find column %s" % name)

    return column


def get_current_working_ticket():
    api = get_api()

    column = get_column(name=config['trello']['work_column_name'])

    cards = api.lists.get_card(column['id'])

    me = api.tokens.get_member(config['trello']['access_token'])

    my_cards = [card for card in cards if me['id'] in card['idMembers']]
    work_card = None

    if len(my_cards) < 1:
        raise ValueError("No working card; aborting.")

    if len(my_cards) == 1:
        work_card = my_cards[0]

    if len(my_cards) > 1:
        for card in my_cards:
            if len(card['idMembers']) == 1:
                if not work_card:
                    work_card = card
                else:
                    raise ValueError("Multiple work cards; cannot decide, aborting")

    if not work_card:
        raise ValueError("No work card for me; aborting")

    return work_card


def pause_ticket(ticket):
    api = get_api()
    column = get_column(name=config['trello']['pause_column_name'])
    api.cards.update_idList(ticket['id'], column['id'])


def comment_ticket(ticket, comment):
    api = get_api()
    api.cards.new_action_comment(ticket['id'], comment)


def migrate_label(label, board, board_to, column, column_to):
    api = get_api()

    if column:
        raise ValueError("column is now ignored, you need to program support for it")

    board_info = api.boards.get(board)

    final_label = None

    if label in board_info['labelNames'].keys():
        final_label = label
    else:
        for l in board_info['labelNames']:
            if board_info['labelNames'][l] == label:
                final_label = l

    if not final_label:
        raise ValueError("Cannot find label %s on given board")

    cards = api.boards.get_card(board)

    filtered_cards = []

    for c in cards:
        for l in c['labels']:
            if l['color'] == final_label:
                filtered_cards.append(c)

    board_to_info = api.boards.get(board_to)
    board_to_columns = api.boards.get_list(board_to_info['id'])

    targetColumn = None

    for c in board_to_columns:
        if c['name'] == column_to:
            target_column = c

    if not target_column:
        raise ValueError("Cannot find target column %s" % column_to)


    for card in filtered_cards:
        migrate_card(api, card, target_column)


def migrate_card(api, card, target_column):
    print("Moving card %(id)s: %(name)s" % card)

    move_to_board(api, card['id'], target_column['idBoard'])
    api.cards.update_idList(card['id'], target_column['id'])


def get_conversion_items(api, card_list, story_card, story_list):
    """ Return (todo_list, items_to_convert_from_there) """
    todo_list = None

    for item in card_list:
        if story_list:
            if item['name'] == story_list or item['id'] == story_list:
                todo_list = item
                break
        else:
            for name in STORY_CARD_TODO_LIST_NAMES:
                if item['name'].lower().strip() == name.strip().lower():
                    todo_list = item
                    break

    if not todo_list:
        lists = ', '.join([i['name'] for i in card_list])
        raise ValueError("Cannot find checklist to convert. Please provide a correct --story-list parameter. Available lists are: %s" % lists)

    list_items = api.checklists.get_checkItem(todo_list['id'])
    return (todo_list, [c for c in list_items if c['state'] == 'incomplete' and not c['name'].startswith('https://trello.com/c/')])


def schedule_list(story_card, story_list=None, owner=None, label=None):
    """
    Looks for Story Card, finds a list and migrate all non-card items to card,
    replacing the items with links to them.

    Work cards contain "Part of <parent-card-link>".
    """

    api = get_api()

    match = re.match("^https\:\/\/trello\.com\/c\/(?P<id>\w+)$", story_card)
    if match:
        story_card = match.groupdict()['id']

    story_card = api.cards.get(urllib.quote(story_card))
    card_list = api.cards.get_checklist(story_card['id'])


    if not owner:
        owner = api.tokens.get_member(config['trello']['access_token'])
    else:
        owner = api.members.get(owner)

    work_queue = get_column(TODO_QUEUE_NAME)

    todo_list, conversion_items = get_conversion_items(api, card_list, story_card, story_list)

    for item in conversion_items:
        desc = "Part of %(url)s" % story_card
        card = api.cards.new(name=item['name'], desc=desc, idList=work_queue['id'])

        create_item(api=api, checklist_id=todo_list['id'], name=card['url'], pos=item['pos'])
        api.checklists.delete_checkItem_idCheckItem(idCheckItem=item['id'], checklist_id=todo_list['id'])

        api.cards.new_member(card['id'], owner['id'])
        if label:
            api.cards.new_label(card['id'], label)

    print "Done"
