import os
import sys

from trello import TrelloApi


def dispatch_command(args):
    if 'TRELLO_API_KEY' not in os.environ:
        raise ValueError('TRELLO_API_KEY environment variable must be set')

    if 'TRELLO_OAUTH_TOKEN' not in os.environ:
        print "You have to set up TRELLO_OAUTH_TOKEN"
        print "Please visit this URL to get it: %s" % api.get_token_url("black-belt")
        sys.exit(1)


    if args.action_command in ACTION_COMMAND_MAP:
        ACTION_COMMAND_MAP[args.action_command](args)



def migrate_label_command(args):
    migrate_label(
        label     = args.label,
        board     = args.board,
        board_to  = args.board_to,
        column    = args.column,
        column_to = args.column_to
    )


def migrate_label(label, board, board_to, column, column_to):
    api = TrelloApi(apikey=os.environ['TRELLO_API_KEY'])

    api.set_token(os.environ['TRELLO_OAUTH_TOKEN'])

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
