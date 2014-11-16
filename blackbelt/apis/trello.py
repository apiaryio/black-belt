import json
import requests
from urllib import quote, quote_plus

from blackbelt.config import config
from blackbelt.errors import ConfigurationError

class Trello(object):
    """
    I represent a authenticated connection to Trello API.
    Dispatch all requests to it through my methods.

    My actions are named from the BlackBelt's POW; I don't aim to be a full,
    usable client.
    """

    API_KEY = "2e4bb3b8ec5fe2ff6c04bf659ee4553b"
    APP_NAME = 'black-belt'
    URL_PREFIX = "https://trello.com/1"

    def __init__(self, access_token=None):
        self._access_token = access_token
        if not self._access_token and config.get('trello') and config['trello'].get('access_token'):
            self._access_token = config['trello']['access_token']

    
    ### Infra
    def do_request(self, url, method='get', data=None):
        if not self._access_token:
            raise ConfigurationError("Trying to talk to Trello without having access token")

        url = self.URL_PREFIX + url
        response = getattr(requests, method)(
            url,
            params={
                'key': self.API_KEY,
                'token': self._access_token
            },
            data=data
        )
        # try:
        #     print response.text
        # except Exception:
        #     print 'Cannot print'
        response.raise_for_status()
        return json.loads(response.content)

    ### Users & Tokens
    def get_token_url(self, app_name, expires='30days'):
        """ Return URL for retrieving access token """
        return 'https://trello.com/1/authorize?key=%(key)s&name=%(name)s&expiration=%(expires)s&response_type=token&scope=%(scope)s' % {
            'key': self.API_KEY,
            'name': quote_plus(self.APP_NAME),
            'expires': expires,
            'scope': 'read,write'
        }


    def get_myself(self):
        return self.do_request("/tokens/%s/member" % self._access_token)

    def get_member(self, member_name):
        return self.do_request("/members/%s" % member_name)

    ### Boards
    def get_board(self, board_id):
        return self.do_request("/boards/%s" % board_id)

    ### Columns
    def get_columns(self, board_id):
        return self.do_request("/boards/%s/lists" % board_id)


    ### Cards
    def get_card(self, card_id=None, card_url=None):
        if card_url:
            card_id = quote(card_url)

        return self.do_request("/cards/%s" % card_id)

    def get_cards(self, column_id):
        return self.do_request("/lists/%s/cards" % column_id)

    def create_card(self, name, description, list_id):
        return self.do_request(
            '/cards',
            method='post',
            data={
                'name': name,
                'desc': description,
                'idList': list_id
            }
        )


    def move_card(self, card_id, board_id=None, column_id=None):
        """
        Move card to the given column on another board.

        If no column is given, it will be placed in the first one.
        If no board is given, column is assumed to be on the same boards.

        """
        if board_id:
            self.do_request("/cards/%s/idBoard" % card_id, data={'value': board_id}, method='put')

        if column_id:
            self.do_request("/cards/%s/idList" %  card_id, data={'value': column_id}, method='put')

    def comment_card(self, card_id, comment):
        self.do_request("/cards/%s/actions/comments" % card_id, method='post', data={'text': comment})

    def add_card_member(self, card_id, member_id):
        self.do_request(
            "/cards/%s/members" % card_id,
            method='post',
            data={
                'value': member_id
            }   
        )

    def label_card(self, card_id, label):
        self.do_request(
            "/cards/%s/labels" % card_id,
            method='post',
            data={
                'value': label
            }
        )


    ### Checklists
    def create_item(self, checklist_id, name, pos):
        """ Create new item in the given checklist on given position """
        return self.do_request(
            url="/checklists/%s/checkItems" % checklist_id,
            method='post',
            data={
                'name': name,
                'post': pos
            }
        )

    def get_card_checklists(self, card_id):
        return self.do_request('/cards/%s/checklists' % card_id)

    def get_checklist_items(self, checklist_id):
        return self.do_request('/checklists/%s/checkItems' % checklist_id)

    def delete_checklist_item(self, checklist_id, checklist_item_id):
        return self.do_request(
            "/checklists/%s/checkItems/%s" % (checklist_id, checklist_item_id),
            method='delete'
        )

    def add_column(self, board_id, name, position):
        """ Add position^th column to the board_id. Position is 1-indexed """
        # Position is not just an integer as in 3 for 3rd from the left,
        # but we ultimately want our API to look act that way
        # Therefore, find out position-1 & increment
        columns = self.get_columns(board_id=board_id)

        trello_position = 'bottom' # default

        if len(columns) >= position - 1 and position > 1:
            # -2: -1 for prev card, additional -1 because list is 0-indexed
            # +1 for pos as we want to have it behind it
            trello_position = columns[position - 2]['pos'] + 1

        return self.do_request(
            "/boards/%s/lists" % (board_id,),
            method='post',
            data={
                'name': name,
                'pos': trello_position
            }
        )
