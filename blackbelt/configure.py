import json
from os.path import expanduser, exists
import re
import webbrowser

import click

import handle_trello

CONFIG_FILE = expanduser('~/.blackbelt')


def get_token(config, token_url, group_name, address_text="Please generate a token for yourself:"):
    print '*' * 3 + ' ' + group_name + ' ' + '*' * 3
    print address_text + ' ' + token_url

    default_token = None
    if group_name in config and config[group_name]['access_token']:
        default_token = str(config[group_name]['access_token'])

    webbrowser.open(token_url)

    token = click.prompt("Please insert an access token", default_token).strip()

    if group_name not in config:
        config[group_name] = {}

    config[group_name]['access_token'] = token


def get_trello_url(config, key, prompt, id_regexp):
    group_name = 'trello'
    default_value = None

    url_key = key + '_url'

    if group_name in config and url_key in config[group_name] and config[group_name][url_key]:
        default_value = str(config[group_name][url_key])

    value = click.prompt(
        prompt,
        default_value
    )

    match = re.match(id_regexp, value)
    if match:
        value_id = match.groupdict()['id']
    else:
        raise ValueError("Cannot recognize URL; doesn't match %s regexp" % id_regexp)

    if group_name not in config:
        config[group_name] = {}

    config[group_name][url_key] = value
    config[group_name][key + '_id'] = value_id


def configure_blackbelt():
    print("Going to collect all the tokens and store them in ~/.blackbelt")

    config = {
        'trello': {
            'access_token': None
        },
        'github': {
            'access_token': None
        },
        'circleci': {
            'access_token': None
        },
        'slack': {
            'access_token': None
        }
    }

    if exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.loads(f.read())

    get_token(
        group_name='trello',
        config=config,
        token_url=handle_trello.get_token_url()
    )

    board_id_regexp = r"^https://trello\.com/b/(?P<id>\w+)/.*$"

    get_trello_url(
        config=config,
        key='product_board',
        prompt="Please provide an URL to your Product Board",
        id_regexp=board_id_regexp
    )

    get_trello_url(
        config=config,
        key='work_board',
        prompt="Please provide an URL to your Work Overview",
        id_regexp=board_id_regexp
    )

    get_token(
        group_name='github',
        config=config,
        token_url="https://github.com/settings/tokens"
    )

    get_token(
        group_name='circleci',
        config=config,
        token_url="https://circleci.com/account/api"
    )

    get_token(
        group_name='slack',
        config=config,
        token_url="https://api.slack.com/custom-integrations/legacy-tokens"
    )

    with open(expanduser('~/.blackbelt'), 'w') as f:
        f.write(json.dumps(config))

    print('All done!')
