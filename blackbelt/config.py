import json
from os.path import expanduser


try:
    configFile = expanduser('~/.blackbelt')
    with open(configFile) as f:
        config = json.loads(f.read())
except IOError:
    config = {
        'trello': {
            'access_token': None,
            'work_board_url': None,
            'work_board_id': None,
            'product_board_url': None,
            'product_board_id': None
        },
        'github': {
            'access_token': None
        },
        'circleci': {
            'access_token': None
        },
        'hipchat': {
            'access_token': None
        },
        'slack': {
            'access_token': None
        }
    }

# default config, overwrite/modularize
if not 'work_board_id' in config['trello'] or not config['trello']['work_board_id']:
    config['trello']['work_board_id'] = '1KsoiV9e'

config['trello']['work_column_name'] = 'Doing'
config['trello']['pause_column_name'] = 'Ready'
