import json
from os.path import expanduser


try:
    configFile = expanduser('~/.blackbelt')
    with open(configFile) as f:
        config = json.loads(f.read())
except IOError:
    config = {
        'trello': {},
        'github': {}
    }
# default config, overwrite/modularize

config['trello']['work_board_id'] = '1KsoiV9e'
config['trello']['work_column_name'] = 'Doing'
config['trello']['pause_column_name'] = 'Paused/Waiting'
