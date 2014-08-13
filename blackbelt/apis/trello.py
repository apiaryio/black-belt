import json
import requests

"""
Custom function teared up from Trello API package and modified for our purposes
"""


def create_item(api, checklist_id, name, pos):
    resp = requests.post("https://trello.com/1/checklists/%s/checkItems" % (checklist_id), params=dict(key=api._apikey, token=api._token), data=dict(name=name, pos=pos))
    resp.raise_for_status()
    return json.loads(resp.content)


# One would to update_idBoard...IF THEY WOULD'N FORGET TO GENERATE IT :-|
def move_to_board(api, card_id, value):
    resp = requests.put("https://trello.com/1/cards/%s/idBoard" % (card_id), params=dict(key=api._apikey, token=api._token), data=dict(value=value))
    resp.raise_for_status()
    return json.loads(resp.content)
