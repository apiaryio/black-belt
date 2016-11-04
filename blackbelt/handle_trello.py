import datetime
from email.mime.text import MIMEText
import re
import smtplib
from subprocess import check_output
import webbrowser

import click

#from blackbelt.apis.trello import *
from blackbelt.config import config

from .apis.trello import Trello as TrelloApi

__all__ = ("schedule_list", "migrate_label", "schedule_list")


STORY_CARD_TODO_LIST_NAMES = [
    "To Do",
    "ToDo",
    "Engineering ToDo"
]

TODO_QUEUE_NAME = "To Do Queue"
DEPLOY_QUEUE_NAME = "Ready"
DEPLOYED_PREFIX = "Deployed by"
VERIFIED_PREFIX = "Verified by"

TEA_ORDER_QUEUE_NAME = "Order next"


def get_token_url():
    return TrelloApi().get_token_url("black-belt", "never")


def get_api():
    return TrelloApi()


def get_column(name, board_id=None):
    api = get_api()

    if not board_id:
        board_id = config['trello']['work_board_id']

    columns = api.get_columns(board_id)
    column = None

    for col in columns:
        if col['name'] == name:
            column = col

    if not column:
        raise ValueError("Cannot find column %s" % name)

    return column


def get_next_todo_card():
    api = get_api()

    column = get_column(name=TODO_QUEUE_NAME)
    cards = api.get_cards(column_id=column['id'])

    me = api.get_myself()

    my_cards = [card for card in cards if me['id'] in card['idMembers']]

    if len(my_cards) < 1:
        raise ValueError("No card assigned to you in the To Do Queue -- be happy, your job is done!")

    return my_cards[0]


def get_current_working_ticket(card_url=None):
    api = get_api()

    column = get_column(name=config['trello']['work_column_name'])

    cards = api.get_cards(column_id=column['id'])

    me = api.get_myself()

    my_cards = [card for card in cards if me['id'] in card['idMembers']]
    work_card = None

    if len(my_cards) < 1:
        raise ValueError("No working card in your DOING list; aborting.")

    if not card_url:

        if len(my_cards) == 1:
            work_card = my_cards[0]

        if len(my_cards) > 1:
            for card in my_cards:
                if len(card['idMembers']) == 1:
                    if not work_card:
                        work_card = card
                    else:
                        raise ValueError("Multiple available work cards; Try bb gh pr <card_url> ")
    else:
        url_cards = [card for card in my_cards if card['url'] == card_url]

        if len(url_cards) > 0:
            work_card = url_cards[0]

    if not work_card:
        raise ValueError("The specified card_url is not in your DOING list")

    return work_card


def open_current_working_ticket():
    ticket = get_current_working_ticket()
    webbrowser.open(ticket['url'])


def get_ticket_ready(ticket):
    api = get_api()
    column = get_column(name=DEPLOY_QUEUE_NAME)
    api.move_card(card_id=ticket['id'], column_id=column['id'])


def comment_ticket(ticket, comment):
    api = get_api()
    api.comment_card(card_id=ticket['id'], comment=comment)


def migrate_label(label, board, board_to, column, column_to):
    """
    All cards with the given label is moved from :term:`Work Board` into given column in the :term:`Product Board`. ::
    """
    api = get_api()

    if column:
        raise ValueError("column is now ignored, you need to program support for it")

    board_info = api.get_board(board_id=board)

    final_label = None

    if label in board_info['labelNames'].keys():
        final_label = label
    else:
        for l in board_info['labelNames']:
            if board_info['labelNames'][l] == label:
                final_label = l

    if not final_label:
        raise ValueError("Cannot find label %s on given board")

    cards = api.get_cards(board_id=board)

    filtered_cards = []

    for c in cards:
        for l in c['labels']:
            if l['color'] == final_label:
                filtered_cards.append(c)

    board_to_info = api.get_board(board_id=board_to)
    board_to_columns = api.get_columns(board_id=board_to_info['id'])

    for c in board_to_columns:
        if c['name'] == column_to:
            target_column = c

    if not target_column:
        raise ValueError("Cannot find target column %s" % column_to)

    for card in filtered_cards:
        print("Moving card %(id)s: %(name)s" % card)
        api.move_card(
            card_id=card['id'],
            board_id=target_column['idBoard'],
            list_id=target_column['id']
        )


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

    list_items = api.get_checklist_items(checklist_id=todo_list['id'])
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

    story_card = api.get_card(card_url=story_card)
    #FIXME: list vs. lists
    card_list = api.get_card_checklists(card_id=story_card['id'])

    if owner:
        owner = api.get_member(member_name=owner)

    work_queue = get_column(TODO_QUEUE_NAME)

    todo_list, conversion_items = get_conversion_items(api, card_list, story_card, story_list)

    for item in conversion_items:
        desc = "Part of %(url)s" % story_card
        card = api.create_card(
            name=item['name'],
            description=desc,
            list_id=work_queue['id']
        )

        api.create_item(checklist_id=todo_list['id'], name=card['url'], pos=item['pos'])

        api.delete_checklist_item(checklist_id=todo_list['id'], checklist_item_id=item['id'])

        if owner:
            api.add_card_member(card_id=card['id'], member_id=owner['id'])

        if label:
            api.label_card(card_id=card['id'], label=label)

    print "Done"


def infer_branch_name(url):
    return '-'.join(url.split('/')[~0].split('-')[1:])


def next_card():
    card = get_next_todo_card()

    ticket_urlname = infer_branch_name(card['url'])

    # set up local branch
    from .handle_github import get_username, get_current_branch

    prefix = get_username().lower()

    branch_name = prefix + '/' + ticket_urlname

    if get_current_branch() != 'master':
        check_output(['git', 'checkout', 'master'])

    check_output(['git', 'fetch', 'origin'])

    # You think you might do git checkout branch origin/branch?
    # Oh my, silly you. All of those require the origin branch to exists,
    # therefore pushing. We don't want to push at this stage only to trigger
    # a duplicate CI check on what is basically a master.
    # Therefore, time for some dark magic. If it breaks your git, please
    # carry on and sacrifice a chicken to the daemons of Linux/s

    check_output(['git', 'branch', branch_name, 'origin/master'])
    check_output(['git', 'checkout', branch_name])
    check_output(['git', 'config', 'branch."%s".remote' % branch_name, 'origin'])
    check_output(['git', 'config', 'branch."%s".merge' % branch_name, "refs/heads/\"%s\"" % branch_name])
    check_output(['git', 'config', 'branch."%s".rebase' % branch_name, 'true'])

    # move to Doing
    api = get_api()
    api.move_card(
        card_id=card['id'],
        column_id=get_column(name=config['trello']['work_column_name'])['id']
    )

    # open card for review
    webbrowser.open(card['url'])


def move_to_deployed(card_id, comment=None):
    """ If the card is in Ready column, move it to deployed """
    api = get_api()

    column = get_column(name=DEPLOY_QUEUE_NAME)
    card = api.get_card(card_id=card_id)

    if card['idList'] != column['id']:
        print "The card is not in column %(column)s. NOT moving to Deployed for you." % {
            'column': DEPLOY_QUEUE_NAME
        }
    else:

        columns = api.get_columns(board_id=config['trello']['work_board_id'])
        deployed = None

        for col in columns:
            if col['name'].startswith(DEPLOYED_PREFIX):
                deployed = col
                # Use the first "Deployed by" as the old ones are
                # sometimes "trailing" at the end of the board
                break

        if not column:
            print "Can't find \"Deployed by\" column, NOT moving the card for you"
        else:
            api.move_card(card_id=card_id, column_id=deployed['id'])
            if comment:
                api.comment_card(card_id=card_id, comment=comment)


def get_next_sunday():
    diff = datetime.date.today().weekday()
    # On sunday, add week instead
    if diff == 6:
        diff = -1

    return datetime.date.today() + datetime.timedelta(
        days=6 - diff
    )


def next_week():
    sunday = get_next_sunday().isoformat()

    api = get_api()
    api.add_column(
        board_id=config['trello']['work_board_id'],
        name="Deployed by %s" % sunday,
        position=5
    )
    api.add_column(
        board_id=config['trello']['work_board_id'],
        name="Verified by %s" % sunday,
        position=6
    )


def verify(story_card):
    api = get_api()

    story_card = api.get_card(card_url=story_card)
    checklists = api.get_card_checklists(card_id=story_card['id'])

    # We actually don't care how the checklists are structured, only about the card links
    checklist_cards = []
    index = -1
    for l in checklists:
        index += 1
        for list_item in l['checkItems']:
            # We accept the first link in the checklist item
            match = re.match("^.*https://trello.com/c/(?P<id>\w+)/?(.*)", list_item['name'])
            if match:
                if list_item['state'] == u'incomplete':
                    list_item['_black_belt'] = {
                        'card_id': match.groupdict()['id'],
                        'checklist_index': index,  # Not needed now, but preserved for future list updates
                        'checklist_id': l['id']
                    }
                    checklist_cards.append(list_item)

                elif list_item['state'] != u'complete':
                    print "Unknown checklist state %s, skipping" % list_item['state']

    # We have list of cards to check, go through them and discover whether
    # they are Deployed / Verified
    COLUMN_CACHE = {}

    items_done = []
    for item in checklist_cards:
        work_card = api.get_card(card_id=item['_black_belt']['card_id'])
        column_id = work_card['idList']

        if column_id not in COLUMN_CACHE:
            COLUMN_CACHE[column_id] = api.get_column(column_id)

        name = COLUMN_CACHE[column_id]['name']
        if name.startswith(DEPLOYED_PREFIX) or name.startswith(VERIFIED_PREFIX):
            item['_black_belt']['name'] = work_card['name']
            item['_black_belt']['url'] = work_card['url']
            items_done.append(item)
        else:
            pass
            #print "%s still not done" % work_card['name'].encode('utf-8')

    # Go through the done items, ask for review and ask for completing them
    for item in items_done:
        if click.confirm("Do you want to show card %s?" % item['_black_belt']['name'], default=True):
            webbrowser.open(item['_black_belt']['url'])
        if click.confirm("Do you want to check it as verified?"):
            api.check_item(
                checklist_id=item['_black_belt']['checklist_id'],
                item_id=item['id'],
                card_id=story_card['id']
            )


def get_tea_from_card(card):
    return {
        'name': card['name'],
        'url': [word for word in card['desc'].split() if word.startswith('http')][0]
    }

def get_tea_email(teas, sender_name):

    tea_text = ''
    for tea in teas:
        tea_text += """
%(name)s
%(url)s
""" % tea

    return u"""Hi %(office_manager_name)s,

we are running out of tea, please rescue us!

Here are the teas we'd love to try:

%(teas)s

Thanks a lot!

%(name)s

    """ % {
        'name': sender_name,
        'teas': tea_text,
        'office_manager_name': config['office']['office_manager_name']
    }

def order_tea():
    api = get_api()

    column = get_column(name=TEA_ORDER_QUEUE_NAME, board_id=config['trello']['tea_board_id'])
    cards = api.get_cards(column_id=column['id'])

    me = api.get_myself()

    teas = [get_tea_from_card(card) for card in cards]

    text = get_tea_email(teas, me['fullName'])

    print text.encode('utf-8')

    if click.confirm("Do you want to send the email above?"):
        email = me['email'] or 'no-reply@apiary.io'

        message = MIMEText(text.encode('utf-8'))
        message['Subject'] = 'Tea order'
        message['From'] = email
        message['To'] = config['office']['office_manager_email']

        #FIXME: Use sendgrid
        s = smtplib.SMTP('localhost')
        s.sendmail(email, [config['office']['office_manager_email']], message.as_string('utf-8'))
        s.quit()
