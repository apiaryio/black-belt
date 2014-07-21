import os
import sys

from config import config
from trello import TrelloApi

TRELLO_API_KEY = "2e4bb3b8ec5fe2ff6c04bf659ee4553b"

def dispatch_command(args):
    if 'TRELLO_API_KEY' not in os.environ:
        raise ValueError('TRELLO_API_KEY environment variable must be set')

    if 'TRELLO_OAUTH_TOKEN' not in os.environ:
        print "You have to set up TRELLO_OAUTH_TOKEN"
        print "Please visit this URL to get it: %s" % api.get_token_url("black-belt")
        sys.exit(1)


    if args.action_command in ACTION_COMMAND_MAP:
        ACTION_COMMAND_MAP[args.action_command](args)


def get_token_url():
    return TrelloApi(apikey=TRELLO_API_KEY).get_token_url("black-belt")

def get_api():
    api = TrelloApi(apikey=TRELLO_API_KEY)
    api.set_token(config['trello']['access_token'])
    return api

def migrate_label_command(args):
    migrate_label(
        label     = args.label,
        board     = args.board,
        board_to  = args.board_to,
        column    = args.column,
        column_to = args.column_to
    )


def get_column(name, board_id=None):
    api = get_api()

    if not board_id:
        board_id = config['trello']['work_board_id']

    columns = api.boards.get_list(board_id)
    column  = None

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

    myCards = [card for card in cards if me['id'] in card['idMembers']]
    work_card = None

    if len(myCards) < 1:
        raise ValueError("No working card; aborting.")

    if len(myCards) == 1:
        workCard = myCards[0]

    if len(myCards) > 1:
        for card in myCards:
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

    # One would to update_idBoard...IF THEY WOULD'N FORGET TO GENERATE IT :-|
    def update_idBoard(card_id, value):
        import json
        import requests
        resp = requests.put("https://trello.com/1/cards/%s/idBoard" % (card_id), params=dict(key=api._apikey, token=api._token), data=dict(value=value))
        resp.raise_for_status()
        return json.loads(resp.content)

    update_idBoard(card['id'], target_column['idBoard'])
    api.cards.update_idList(card['id'], target_column['id'])


ACTION_COMMAND_MAP = {
    'migrate-label': migrate_label_command
}
