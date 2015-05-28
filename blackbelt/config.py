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
            'product_board_id': None,
            'tea_board_url': None,
            'tea_board_id': None
        },
        'github': {
            'access_token': None
        },
        'circleci': {
            'access_token': None
        },
        'slack': {
            'access_token': None
        },
        'office': {
            'office_manager_name': None,
            'office_manager_email': None
        }
    }

# default config, overwrite/modularize
if not 'work_board_id' in config['trello'] or not config['trello']['work_board_id']:
    config['trello']['work_board_id'] = '1KsoiV9e'

# default config, overwrite/modularize
if not 'tea_board_id' in config['trello'] or not config['trello']['tea_board_id']:
    config['trello']['tea_board_id'] = '3ShcntV4'

if not 'office' in config:
    config['office'] = {}

if not 'office_manager_name' in config['office'] or not config['office']['office_manager_name']:
    config['office']['office_manager_name'] = 'Alzbeta'

if not 'office_manager_email' in config['office'] or not config['office']['office_manager_email']:
    config['office']['office_manager_email'] = 'alzbeta@apiary.io'

config['trello']['work_column_name'] = 'Doing'
config['trello']['pause_column_name'] = 'Ready'
